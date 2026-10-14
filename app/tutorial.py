"""The "Learn with Socrates" tutorial. Rounds 1 and 2 are scripted (Socrates
answers, so all 9 standards are met). Round 3 is the learner's own answer,
checked by the real Assessor, the same agent used in the cases. In mock mode,
or if the model call fails, a rough plain-code check is used instead. Nothing
is saved: the tutorial is practice, not thesis data."""
import re

from . import copycheck, llm_client, orchestrator
from .content import LEVELS, STANDARD_TIPS, STANDARDS, TUTORIAL

MOVES = [k for k, _, _ in LEVELS]
MAX_SCORE = len(STANDARDS) * len(TUTORIAL["rounds"])  # 27

# Word lists for the code backup. They only guess at the standards from signs
# you can see (a number, "because", "but"). They cannot really judge accuracy
# or significance, so the result says which checker was used.
_GIVE_UP = ["idk", "i don't know", "i dont know", "not sure", "no idea", "stuck"]
_REASON = ["because", "so", "since", "means", "therefore", "if"]
_OTHER_VIEW = ["but", "unless", "however", "maybe", "might", "could be wrong", "although"]
_EVIDENCE = ["test", "check", "data", "new days", "repeat", "repeats", "proof", "compare"]
_TOPIC = ["stock", "rise", "rose", "rises", "pattern", "luck", "days", "streak", "price"]


def _has_any(text, words):
    # whole words only, so "so" does not match "also"
    return any(re.search(r"\b" + re.escape(w) + r"\b", text) for w in words)


def code_assess(answer):
    """Rough backup check of one answer against the 9 standards."""
    t = (answer or "").strip().lower()
    n_words = len(t.split())
    if n_words < 3 or _has_any(t, _GIVE_UP):
        return {"standards": {k: 0 for k in STANDARDS}, "reasoning_move": "none", "confused_or_frustrated": True}
    number = bool(re.search(r"\d", t)) or _has_any(t, ["for example", "such as"])
    reason, other = _has_any(t, _REASON), _has_any(t, _OTHER_VIEW)
    topic, evidence = _has_any(t, _TOPIC), _has_any(t, _EVIDENCE)
    met = {
        "clarity": n_words >= 8,
        "accuracy": topic and (evidence or number),
        "precision": number,
        "relevance": topic,
        "depth": reason,
        "breadth": other,
        "logic": reason and n_words >= 8,
        "significance": evidence,
        "fairness": other,
    }
    move = "evidence" if evidence else "viewpoint" if other else "clarify"
    return {"standards": {k: int(v) for k, v in met.items()}, "reasoning_move": move, "confused_or_frustrated": False}


def _clean(data):
    """Keep only what the stats need, in a safe shape."""
    std = data.get("standards") or {}
    move = data.get("reasoning_move")
    return {"standards": {k: int(bool(std.get(k))) for k in STANDARDS},
            "reasoning_move": move if move in MOVES else "none",
            "confused_or_frustrated": bool(data.get("confused_or_frustrated"))}


# Text the learner can see before round 3 and could paste instead of thinking:
# the round 3 hint and the tutorial reading.
def _copy_sources():
    r = TUTORIAL["reading"]
    return [TUTORIAL["rounds"][2]["key_idea"], r["example"], r["think"], *r["idea"]]


def copied_share(answer, sources=None):
    # Repeating the coin story ("4 heads in a row") is answering, not copying.
    return copycheck.copied_share(answer, sources if sources is not None else _copy_sources(), TUTORIAL["scenario"])


COPY_LIMIT = copycheck.COPY_LIMIT


def assess_answer(answer):
    """Round 3: a copied hint scores 0 (checked first, no AI call); otherwise
    the real Assessor, else the code backup."""
    if copied_share(answer) >= COPY_LIMIT:
        return {"standards": {k: 0 for k in STANDARDS}, "reasoning_move": "none",
                "confused_or_frustrated": False, "source": "copy_check", "copied": True}
    if llm_client.PROVIDER != "mock":
        try:
            session = {"last_tutor": TUTORIAL["rounds"][2]["question"]}
            return {**_clean(llm_client.call_assessor(session, answer)), "source": "assessor"}
        except Exception:  # any model problem: fall back, never block the tutorial
            pass
    return {**code_assess(answer), "source": "code"}


def example_assessment(i, pick=None):
    """Rounds 1 and 2: the standards Socrates's example meets (plus the pick in round 2)."""
    r = TUTORIAL["rounds"][i]
    met = {k for _, ks in r["answer"] for k in ks}
    if pick is not None and pick == r.get("best"):
        met |= set(r.get("pick_standards", []))
    return {"standards": {k: int(k in met) for k in STANDARDS}, "reasoning_move": r["level"],
            "confused_or_frustrated": False}


def _comment(r3, total, source):
    if r3.get("copied"):  # called out first, before anything else
        return ("You copied the hint instead of answering in your own words, so your round 3 answer scored 0. "
                "Please do not do that next time. Use the hint as a clue, and then explain your own thinking. "
                f"You met {total} of {MAX_SCORE} standards in this tutorial.")
    n = sum(r3["standards"].values())
    text = f"You met {total} of {MAX_SCORE} standards in this tutorial"
    if n == len(STANDARDS):
        text += ", and your own answer met all 9, which is exactly how a critical thinker answers."
    else:
        tips = [STANDARD_TIPS[k] for k in STANDARDS if not r3["standards"][k]][:3]
        text += f", and your own answer met {n} of 9. Next time, {tips[0][0].lower() + tips[0][1:]}"
        text += "".join(f" {t}" for t in tips[1:])
    checker = "the Assessor AI" if source == "assessor" else "a simple word check instead of the AI"
    return f"{text} Your round 3 answer was checked by {checker}."


def final_result(r2_pick, answer):
    r3 = assess_answer(answer)
    history = [example_assessment(0), example_assessment(1, r2_pick), r3]
    # "Reached" = the level of the last question asked, the same rule as the
    # cases (a session ends before the level can move up again). Round 3 is an
    # Evidence question, so the tutorial ends at Evidence, never Viewpoints.
    level_idx = MOVES.index(TUTORIAL["rounds"][-1]["level"])
    per_round = [sum(a["standards"].values()) for a in history]
    total = sum(per_round)
    session = {"history": [{"assessment": a} for a in history], "level_idx": level_idx}
    return {
        "rounds": per_round, "total": total, "max": MAX_SCORE,
        "stars": 3 if total == MAX_SCORE else 2 if total >= 23 else 1,
        "assessment": r3, "source": r3["source"], "copied": bool(r3.get("copied")), "pick_right": r2_pick == TUTORIAL["rounds"][1]["best"],
        "level": LEVELS[session["level_idx"]][1],
        # same shape as /api/session/{id}/stats, so the page can draw the normal profile
        "stats": {"levels": [{"key": k, "name": name} for k, name, _ in LEVELS], "standards": STANDARDS,
                  "summary": orchestrator.summarize(session), "comment": _comment(r3, total, r3["source"])},
    }
