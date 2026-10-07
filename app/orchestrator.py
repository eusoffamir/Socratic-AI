"""Plain-code rules for the session. Deliberately not an LLM: these decisions
should be the same every time given the same state, and easy to unit test.
See thesis Chapter 3, Table 3 (design requirements R1-R9) for where each rule
comes from.

Two ways to pick the next move:
  decide()      the fixed rules alone (used when the Planner agent is off or fails)
  apply_plan()  the guard: takes the Planner agent's proposal and enforces the
                fixed rules on it. "Agents decide, rules guard."
"""
from .content import FORMATS, LEVELS, STANDARD_TIPS, STANDARDS
from .tools import TOOLS

GOOD_STANDARDS_THRESHOLD = 2  # standards met to count an answer as "good"
STREAK_TO_ADVANCE = 2         # good answers in a row to move up a level
STREAK_TO_SCAFFOLD = 2        # weak answers in a row to add a hint


def new_session(concept_id, total_rounds=5, ab_only=False, reading_seconds=0):
    return {
        "concept_id": concept_id,
        "round": 0,                # rounds completed
        "total_rounds": total_rounds,
        "ab_only": ab_only,        # learner picked "A/B only" mode: every question is A or B
        "reading_seconds": reading_seconds,  # seconds the reading pop-up was open before Start
        "level_idx": 0,
        "good_streak": 0,
        "weak_streak": 0,
        "last_format": None,
        "last_tutor": None,
        "asked": [],                # (level_idx, format) pairs already used      (R6, R9)
        "said": [],                 # short paraphrases of things the learner told us (R3)
        "history": [],              # one entry per round: {"answer":..., "assessment":...}
        "questions": [],            # question texts already asked, so the tutor never repeats one (R3)
        "turns": [],                # full agent trace per turn, saved as the transcript
        "ended": False,
    }


def _is_good(assessment):
    if assessment["confused_or_frustrated"]:
        return False
    met = sum(assessment["standards"].values())
    return assessment["reasoning_move"] != "none" and met >= GOOD_STANDARDS_THRESHOLD


def _next_format(session, force_easy):
    if force_easy:
        return FORMATS[-1]  # "choose A or B and defend the choice"
    # Rotate through every format in order (R6), starting after the last one used.
    last = session["last_format"]
    i = FORMATS.index(last) + 1 if last in FORMATS else 0
    return FORMATS[i % len(FORMATS)]


def decide(session, assessment=None):
    """Given the current state and the assessment of the learner's last
    answer (None on the very first turn), decide what the tutor should do
    next, and update the session state in place. Returns an instruction dict
    for prompts.tutor_user.
    """
    level_key, level_name, level_desc = LEVELS[session["level_idx"]]

    _record(session, assessment)
    end = _end_if_done(session)
    if end:
        return end

    if assessment is None:
        # R1: first turn states the mission; handled in prompts.tutor_user via `mission`.
        instruction = {
            "action": "open", "round": session["round"] + 1, "total_rounds": session["total_rounds"],
            "level_name": level_name, "level_desc": level_desc, "format": FORMATS[0], "hint": True,
        }
    else:
        # R5: notice frustration and back off, rather than plough ahead.
        if assessment["confused_or_frustrated"]:
            session["weak_streak"] = 0
            session["good_streak"] = 0
            fmt = _next_format(session, force_easy=True)
            instruction = {
                "action": "continue", "round": session["round"] + 1, "total_rounds": session["total_rounds"],
                "level_name": level_name, "level_desc": level_desc, "format": fmt,
                "hint": True, "acknowledge_frustration": True,
            }
        else:
            good = _is_good(assessment)
            session["good_streak"] = session["good_streak"] + 1 if good else 0
            session["weak_streak"] = 0 if good else session["weak_streak"] + 1

            advanced = False
            if session["good_streak"] >= STREAK_TO_ADVANCE and session["level_idx"] < len(LEVELS) - 1:
                session["level_idx"] += 1
                session["good_streak"] = 0
                advanced = True
                level_key, level_name, level_desc = LEVELS[session["level_idx"]]

            needs_hint = session["weak_streak"] >= STREAK_TO_SCAFFOLD
            if needs_hint:
                session["weak_streak"] = 0

            fmt = _next_format(session, force_easy=needs_hint)
            instruction = {
                "action": "continue", "round": session["round"] + 1, "total_rounds": session["total_rounds"],
                "level_name": level_name, "level_desc": level_desc, "format": fmt,
                "hint": needs_hint or advanced,
            }

    return _finish(session, instruction)


def _record(session, assessment):
    # Record the answer before the end check, so the last round's answer
    # still counts in the summary and stats (R8).
    if assessment is not None:
        session["history"].append({"assessment": assessment})
        session["said"].extend(assessment.get("learner_points", []))


def _end_if_done(session):
    # R2: fixed number of rounds, decided here, never by an LLM.
    if session["round"] >= session["total_rounds"]:
        session["ended"] = True
        return {"action": "end", "round": session["round"], "total_rounds": session["total_rounds"],
                "summary": summarize(session)}
    return None


def _finish(session, instruction):
    # "A/B only" mode wins over every other format choice (rules and Planner alike).
    if session.get("ab_only") and instruction["action"] != "end":
        instruction["format"] = FORMATS[-1]
    # R6/R9: remember what's been asked so the tutor prompt can avoid repeats.
    session["asked"].append((session["level_idx"], instruction["format"]))
    session["last_format"] = instruction["format"]
    session["round"] += 1
    return instruction


def _plan_is_usable(plan):
    return (isinstance(plan, dict)
            and plan.get("level_change") in ("stay", "up", "down")
            and plan.get("format") in FORMATS)


def apply_plan(session, plan, assessment):
    """The guard. Takes the Planner agent's proposed move and enforces the
    fixed rules on it. Returns (instruction, overrides), where overrides is a
    list of short notes on anything the guard changed. Updates the session in
    place, like decide().
    """
    if assessment is None or not _plan_is_usable(plan):
        notes = [] if assessment is None else ["Plan missing or invalid. Used fixed rules."]
        return decide(session, assessment), notes

    _record(session, assessment)
    end = _end_if_done(session)
    if end:
        return end, []

    overrides = []
    change = plan["level_change"]
    fmt = plan["format"]
    hint = bool(plan.get("hint"))
    frustrated = assessment["confused_or_frustrated"]

    if frustrated:
        # R5: always back off. The Planner cannot override this.
        session["good_streak"] = session["weak_streak"] = 0
        if change == "up":
            overrides.append("Learner is frustrated. Did not move up.")
            change = "stay"
        if fmt != FORMATS[-1]:
            overrides.append("Learner is frustrated. Switched to A or B.")
            fmt = FORMATS[-1]
        hint = True
    else:
        good = _is_good(assessment)
        session["good_streak"] = session["good_streak"] + 1 if good else 0
        session["weak_streak"] = 0 if good else session["weak_streak"] + 1
        if change == "up" and not good:
            overrides.append("Answer was weak. Did not move up.")
            change = "stay"
        if fmt == session["last_format"] and not session.get("ab_only"):
            # R6: never the same format twice in a row (except in "A/B only" mode).
            fmt = _next_format(session, force_easy=False)
            overrides.append("Same format as last turn. Rotated.")

    # Level moves at most one step, and stays inside the ladder.
    step = {"stay": 0, "up": 1, "down": -1}[change]
    new_idx = min(max(session["level_idx"] + step, 0), len(LEVELS) - 1)
    if new_idx != session["level_idx"] + step:
        overrides.append("Already at the end of the ladder. Level kept.")
    if new_idx != session["level_idx"]:
        session["level_idx"] = new_idx
        session["good_streak"] = session["weak_streak"] = 0
        hint = hint or step > 0  # a new, harder level gets a helpful fact first
    level_key, level_name, level_desc = LEVELS[session["level_idx"]]

    tool = plan.get("suggest_tool")
    instruction = {
        "action": "continue", "round": session["round"] + 1, "total_rounds": session["total_rounds"],
        "level_name": level_name, "level_desc": level_desc, "format": fmt, "hint": hint,
        "suggest_tool": tool if tool in TOOLS else None,
        "plan_reason": str(plan.get("reason", ""))[:200],
    }
    if frustrated:
        instruction["acknowledge_frustration"] = True
    return _finish(session, instruction), overrides


def summarize(session):
    met_counts = {k: 0 for k in STANDARDS}
    move_counts = {k: 0 for k, _, _ in LEVELS}
    n = 0
    for turn in session["history"]:
        a = turn["assessment"]
        n += 1
        for k, v in a["standards"].items():
            met_counts[k] += v
        if a["reasoning_move"] in move_counts:
            move_counts[a["reasoning_move"]] += 1
    strongest = max(met_counts, key=met_counts.get) if n else None
    weakest = min(met_counts, key=met_counts.get) if n else None
    highest_level = LEVELS[session["level_idx"]][1]
    return {
        "rounds_completed": n,
        "highest_level_reached": highest_level,
        "standards_met_count": met_counts,
        "reasoning_move_count": move_counts,
        "strongest_standard": strongest,
        "weakest_standard": weakest,
    }



def fallback_comment(session):
    """A plain-code paragraph on how the learner answered, used when the Coach
    AI is off (mock mode) or its call fails. Same answers, same text."""
    answers = [t["answer"] for t in session.get("turns", []) if t.get("answer") is not None]
    history = [t["assessment"] for t in session["history"]]
    if not answers or not history:
        return None
    n = len(history)
    words = round(sum(len(a.split()) for a in answers) / len(answers))
    good = sum(_is_good(a) for a in history)
    stuck = sum(bool(a.get("confused_or_frustrated")) for a in history)
    met = {k: sum(a["standards"].get(k, 0) for a in history) for k in STANDARDS}
    worst = min(met, key=met.get)

    if good / n >= 0.7:
        text = f"Solid work. {good} of {n} answers showed clear reasoning."
    elif good / n >= 0.4:
        text = f"A fair start. {good} of {n} answers showed clear reasoning."
    else:
        text = f"Your reasoning was hard to see. Only {good} of {n} answers showed it clearly."
    if words < 8:
        text += f" Your answers were short, about {words} words each. Short answers hide your thinking, so add one reason."
    elif words > 40:
        text += f" Your answers were long, about {words} words each. Lead with your main point, then one reason."
    else:
        text += f" Your answers were a good length, about {words} words each."
    if met[worst] < n:
        text += f" Next time, focus on {worst}. {STANDARD_TIPS[worst]}"
    if stuck:
        text += " When you feel stuck, open the hint before you give up."
    return text
