"""Wraps whichever LLM provider is configured. Three options:

  PROVIDER=mock     canned responses, no key, no internet needed
  PROVIDER=gemini   Google's free API tier (get a key at https://aistudio.google.com/apikey,
                     no credit card needed for the free-tier models)
  PROVIDER=anthropic  needs a paid Anthropic API key

If PROVIDER is not set, it's picked automatically: GOOGLE_API_KEY present -> gemini,
else ANTHROPIC_API_KEY present -> anthropic, else mock.
"""
import json
import os
import random
import time

from . import limits, reasoning, tools
from .content import FORMATS, MOVES, STANDARDS, case_of
from .prompts import (AB_FORMAT, ASSESSOR_REASONING_SYSTEM, ASSESSOR_SYSTEM, CHECKER_SYSTEM, COACH_SYSTEM, PLANNER_SYSTEM, TUTOR_SYSTEM,
                      assessor_user, checker_user, coach_user, planner_user, tutor_user)


def _pick_provider():
    explicit = os.getenv("PROVIDER")
    if explicit:
        return explicit
    if os.getenv("MOCK", "0") == "1":
        return "mock"
    if os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "mock"


PROVIDER = _pick_provider()
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Gemini 3.x models "think" before answering, and those thinking tokens count
# against max_output_tokens. With a tight cap the visible reply gets cut off
# mid-sentence (or the Assessor's JSON is truncated), so Gemini gets this much
# extra room on top of each call's own limit. Reply length is still kept short
# by the prompts themselves.
GEMINI_THINKING_HEADROOM = 2048

# How many times to retry when the provider says it's overloaded (HTTP 503).
OVERLOAD_RETRIES = 2

# Fixed seed for the Assessor, so the same answer gets the same marks (the
# grant proposal needs reproducible scoring). The Tutor keeps some variety.
# The temperature is left at Gemini's default on purpose: Google's advice for
# its thinking models is not to lower it (from memory, not checked again).
ASSESSOR_SEED = 26004

# Most tool runs the Tutor agent may make in one turn.
MAX_TOOLS_PER_TURN = 2

# Give up on a single model call after this many seconds, so the page shows an
# error instead of spinning forever when the provider stalls.
REQUEST_TIMEOUT_SECONDS = 45

_anthropic_client = None
_gemini_client = None


class LLMError(RuntimeError):
    """The model call failed in a way the learner should be told about.
    main.py turns this into an HTTP 503 with this message."""


def _get_anthropic():
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic
        _anthropic_client = anthropic.Anthropic(timeout=REQUEST_TIMEOUT_SECONDS)  # reads ANTHROPIC_API_KEY
    return _anthropic_client


def _get_gemini():
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        from google.genai import types
        _gemini_client = genai.Client(
            api_key=os.environ["GOOGLE_API_KEY"],
            http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_SECONDS * 1000),  # milliseconds
        )
    return _gemini_client


def _generate_gemini(system, user, max_tokens, json_mode, seed=None):
    import httpx
    from google.genai import errors, types
    config = types.GenerateContentConfig(
        system_instruction=system,
        max_output_tokens=max_tokens + GEMINI_THINKING_HEADROOM,
        response_mime_type="application/json" if json_mode else "text/plain",
        # Short tutoring replies don't need deep thinking; "low" cuts each call
        # from ~20s to a few seconds.
        thinking_config=types.ThinkingConfig(thinking_level="low"),
        seed=seed,
    )
    for attempt in range(OVERLOAD_RETRIES + 1):
        try:
            resp = _get_gemini().models.generate_content(model=GEMINI_MODEL, contents=user, config=config)
            break
        except httpx.TimeoutException as e:
            raise LLMError(f"Gemini ({GEMINI_MODEL}) took longer than {REQUEST_TIMEOUT_SECONDS}s to reply. "
                           f"Try again.") from e
        except httpx.TransportError as e:
            raise LLMError("Couldn't reach the Gemini API. Check your internet connection.") from e
        except errors.APIError as e:
            if e.code == 503 and attempt < OVERLOAD_RETRIES:
                time.sleep(2 ** (attempt + 1))
                continue
            if e.code == 503:
                raise LLMError(f"Gemini ({GEMINI_MODEL}) is overloaded right now. Wait a moment and try again.") from e
            if e.code == 429:
                raise LLMError(f"Gemini quota used up for {GEMINI_MODEL}. Wait a minute (or until tomorrow for the "
                               f"daily limit), or set GEMINI_MODEL in .env to another model.") from e
            if e.code == 404:
                raise LLMError(f"Gemini model {GEMINI_MODEL!r} not found. Check GEMINI_MODEL in .env.") from e
            raise LLMError(f"Gemini error {e.code}: {e.message}") from e
    if not resp.text:
        reason = resp.candidates[0].finish_reason if resp.candidates else "no candidates"
        raise LLMError(f"Gemini returned an empty reply (finish reason: {reason}). Try again.")
    return resp.text.strip()


def _generate_anthropic(system, user, max_tokens):
    import anthropic  # the SDK already retries overload/rate-limit errors itself
    try:
        resp = _get_anthropic().messages.create(
            model=ANTHROPIC_MODEL, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}],
        )
    except anthropic.APIStatusError as e:
        raise LLMError(f"Claude API error {e.status_code}: {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise LLMError("Couldn't reach the Claude API. Check your internet connection.") from e
    return resp.content[0].text.strip()


def _generate(system, user, max_tokens, json_mode=False, seed=None):
    """Dispatch one call to whichever provider is active. Returns raw text.
    A fixed seed asks the model to give the same reply to the same input."""
    limits.count_call()
    if PROVIDER == "gemini":
        return _generate_gemini(system, user, max_tokens, json_mode, seed)
    if PROVIDER == "anthropic":
        return _generate_anthropic(system, user, max_tokens)
    raise RuntimeError(f"Unknown PROVIDER: {PROVIDER!r}")  # mock is handled by the callers


def _parse_json(text):
    """Read a JSON object from a model reply. Some models wrap JSON in prose
    or a ```json fence despite instructions, so fall back to the outermost
    {...} block. Returns None if there is no usable object."""
    for candidate in (text, text[text.find("{"):text.rfind("}") + 1]):
        try:
            data = json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(data, dict):
            return data
    return None


def clean_parts(data, instruction):
    """Turn a Tutor reply into the four parts the page shows. Missing or
    odd fields become empty, so a messy reply never breaks the page."""
    parts = {k: str(data.get(k) or "").strip() for k in ("feedback", "key_idea", "question")}
    options = data.get("options") if isinstance(data.get("options"), list) else []
    options = [str(o).strip().removeprefix("A)").removeprefix("B)").strip() for o in options if str(o).strip()]
    parts["options"] = options[:2] if instruction.get("format") == AB_FORMAT else []
    return parts


def parts_text(parts):
    """The reply as one plain text, for the Assessor and the transcript."""
    text = " ".join(parts[k] for k in ("feedback", "key_idea", "question") if parts.get(k))
    if parts.get("options"):
        text += " Options: " + " / ".join(f"{l}) {o}" for l, o in zip("AB", parts["options"]))
    return text


def call_tutor(session, instruction, answer, assessment, use_tools=True, tool_runs=None, draft=None, problems=None):
    """The Tutor agent. It may run up to MAX_TOOLS_PER_TURN runs of this case's
    own tool before it answers (a small think, act, observe loop). Returns
    (parts, tool_runs)."""
    tool_runs = list(tool_runs or [])
    can_use_tools = use_tools and instruction["action"] == "continue" and not problems
    nudge = None
    while True:
        tools_left = MAX_TOOLS_PER_TURN - len(tool_runs) if can_use_tools else 0
        payload = tutor_user(session, instruction, answer, assessment, tool_runs, max(tools_left, 0), draft,
                             problems or nudge)
        if PROVIDER == "mock":
            data = _mock_tutor(json.loads(payload))
        else:
            text = _generate(TUTOR_SYSTEM, payload, max_tokens=400, json_mode=True)
            data = _parse_json(text) or {"question": text}  # plain text still works as a reply
        if data.get("tool"):
            if tools_left > 0 and data["tool"] == case_of(session).get("tool"):
                tool_runs.append(tools.run_tool(data["tool"], data.get("args")))
                continue
            if nudge is None:
                # It asked for a tool with none left, or another case's tool,
                # which would leave an empty question card. Ask once more for a
                # normal reply.
                nudge = ["No more tools now. Reply with feedback, key_idea and question."]
                continue
        return clean_parts(data, instruction), tool_runs


def _flag(value):
    """1 or 0 from a score the model may write as 1, true, "1" or "yes"."""
    if isinstance(value, str):
        return int(value.strip().lower() in ("1", "true", "yes"))
    return int(bool(value))


def clean_assessment(data):
    """Turn an Assessor reply into one safe shape: all 9 standards as 0 or 1,
    a known move, and every field the rules and stats read. Odd key names or
    scores written as text would otherwise crash the turn, or be saved and
    break the stats later."""
    raw = data.get("standards") if isinstance(data.get("standards"), dict) else {}
    raw = {str(k).strip().lower(): v for k, v in raw.items()}
    move = str(data.get("reasoning_move") or "").strip().lower()
    points = data.get("learner_points")
    points = points if isinstance(points, list) else [points] if points else []
    try:
        confidence = float(data.get("confidence") or 0)
    except (TypeError, ValueError):
        confidence = 0.0
    return {"standards": {k: _flag(raw.get(k)) for k in STANDARDS},
            "reasoning_move": move if move in MOVES else "none",
            "learner_points": [str(p) for p in points][:3],
            "confused_or_frustrated": _flag(data.get("confused_or_frustrated")) == 1,
            "evidence_quote": str(data.get("evidence_quote") or ""),
            "confidence": confidence}


def call_assessor(session, answer):
    """The Assessor, plus the Reasoning agent in the same call when it is on.
    "reasoning" is None when the Reasoning agent is switched off."""
    with_reasoning = reasoning.enabled()
    user_payload = assessor_user(session, answer, with_reasoning)
    if PROVIDER == "mock":
        return {**_mock_assessor(answer), "reasoning": reasoning.mock(answer) if with_reasoning else None}
    system = ASSESSOR_REASONING_SYSTEM if with_reasoning else ASSESSOR_SYSTEM
    data = _parse_json(_generate(system, user_payload, max_tokens=650 if with_reasoning else 400,
                                 json_mode=True, seed=ASSESSOR_SEED))
    if data is None or "standards" not in data:
        raise LLMError("The assessor returned a reply that isn't valid JSON. Try sending your answer again.")
    return {**clean_assessment(data), "reasoning": reasoning.clean(data) if with_reasoning else None}


def call_planner(session, assessment):
    """The Planner agent. Returns its proposal, or None if it failed. A failed
    plan is not an error: the guard falls back to the fixed rules."""
    if PROVIDER == "mock":
        return _mock_planner(session, assessment)
    try:
        return _parse_json(_generate(PLANNER_SYSTEM, planner_user(session, assessment), max_tokens=200, json_mode=True))
    except LLMError:
        return None


def call_checker(instruction, answer, parts, asked_questions=()):
    """The Checker agent. Returns a list of problems (empty means OK). If the
    call fails, the reply is let through rather than blocking the learner."""
    if PROVIDER == "mock":
        return []
    try:
        data = _parse_json(_generate(CHECKER_SYSTEM, checker_user(instruction, answer, parts, asked_questions),
                                     max_tokens=200, json_mode=True))
    except LLMError:
        return []
    if not data or data.get("ok", True):
        return []
    return [str(p) for p in data.get("problems", [])][:4]


def call_coach(session):
    """The Coach: one paragraph on how the learner answered, written once at
    the end of a session. Returns None in mock mode, so the caller uses the
    plain-code paragraph instead."""
    if PROVIDER == "mock":
        return None
    text = _generate(COACH_SYSTEM, coach_user(session), max_tokens=300)
    return " ".join(text.split()) or None  # one paragraph, no stray line breaks


def _mock_tutor(payload):
    # Shows the tool loop working in mock mode: run the suggested tool once.
    if payload.get("suggest_tool") and payload["tools_left"] > 0 and not payload["TOOL_RESULTS"]:
        return {"tool": payload["suggest_tool"], "args": {}}
    if payload["action"] == "open":
        rounds = payload['total_rounds']
        return {"feedback": f"Welcome. We have {rounds} rounds." if isinstance(rounds, int)
                            else "Welcome. Keep going as long as you like.",
                "key_idea": payload["NOTES"][0],
                "question": "[mock] What do you think is going on here?",
                "options": ["Real pattern", "Just luck"]}  # kept only if the format is A/B
    if payload["action"] == "end":
        return {"feedback": "[mock] You gave clear reasons.",
                "key_idea": "Next time, think about other viewpoints.",
                "question": "What would change your mind?"}
    feedback = ("You copied the hint, please answer in your own words." if payload.get("learner_copied_hint")
                else "I hear you. Let's slow down." if payload.get("acknowledge_frustration") else "[mock] You gave a reason.")
    key_idea = payload["TOOL_RESULTS"][-1]["summary"] if payload["TOOL_RESULTS"] else payload["NOTES"][-1]
    n = len(payload["ASKED_QUESTIONS"]) + 1
    return {"feedback": feedback, "key_idea": key_idea,
            "question": f"[mock {n}] {payload['socratic_level']}: what do you think happens next?",
            "options": ["Real pattern", "Just luck"]}


def _mock_planner(session, assessment):
    good = sum(assessment["standards"].values()) >= 2 and assessment["reasoning_move"] != "none"
    i = FORMATS.index(session["last_format"]) + 1 if session["last_format"] in FORMATS else 0
    return {
        "level_change": "up" if good else "stay",
        "format": FORMATS[-1] if assessment["confused_or_frustrated"] else FORMATS[i % len(FORMATS)],
        "hint": not good,
        "suggest_tool": case_of(session).get("tool") if session["round"] == 1 else None,
        "reason": "[mock] Good answer, push up." if good else "[mock] Weak answer, stay and help.",
    }


def _mock_assessor(answer):
    random.seed(len(answer))
    frustrated = any(w in answer.lower() for w in ["idk", "i don't know", "dont know", "too many", "confus", "stuck", "not sure"])
    standards = {k: (1 if random.random() > 0.5 else 0) for k in STANDARDS}
    move = "none" if frustrated or len(answer.split()) < 3 else random.choice(
        ["clarify", "assumption", "evidence", "viewpoint", "implication"])
    return {
        "standards": standards,
        "reasoning_move": move,
        "learner_points": [answer[:60]] if answer else [],
        "confused_or_frustrated": frustrated,
        "evidence_quote": answer[:80],
        "confidence": 0.5,
    }
