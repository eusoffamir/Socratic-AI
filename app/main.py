import copy
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # must run before `from . import graph` below, since llm_client
                # picks its provider (mock/gemini/anthropic) at import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import graph, limits, llm_client, orchestrator, skillcheck, storage, tutorial
from .llm_client import LLMError
from .content import CONCEPTS, LEVELS, STANDARDS, TUTORIAL

app = FastAPI(title="Socratic AI")

# Live sessions are kept in memory and also saved after every turn (see
# storage.py: files on this computer, a free database online), so a learner
# can leave and continue later, even after a server restart. One session is
# about 5 to 20 KB. Each turn also adds one transcript line with the full
# agent trace. No names or personal data are stored. Kept for the thesis Results.
SESSIONS: dict[str, dict] = {}

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class StartRequest(BaseModel):
    concept_id: str = "pattern_or_luck"
    total_rounds: int = 6  # 3, 6, or 0 for no limit (the "∞" option)
    ab_only: bool = False
    reading_seconds: int = 0  # seconds the reading pop-up was open before "Start this case"
    participant_code: str = ""  # study mode only (see study_codes)
    consent: bool = False       # study mode only: the learner ticked "I agree to take part"


def study_codes():
    """Study mode for the research project: on when STUDY_CODES lists the
    participant codes the lecturer hands out (e.g. "P001,P002"). Then only
    those codes can start a session, after agreeing to take part, and each
    session is saved with its code, so a student's sessions can be linked
    (pre and post) without a name. Off (empty) by default, until the
    supervisor and the ethics approval agree. Read each time, so tests can
    switch it."""
    return {c.strip().upper() for c in os.getenv("STUDY_CODES", "").split(",") if c.strip()}


class CodeRequest(BaseModel):
    code: str = ""


# Longest answer sent to the agents. A real answer is a few sentences; this
# stops a huge paste from using up the free model quota on a public link.
MAX_ANSWER_CHARS = 2000


class AnswerRequest(BaseModel):
    answer: str
    hint_opened: bool = False  # the learner opened the hint of this question before answering


class OverviewRequest(BaseModel):
    session_ids: list[str] = []  # the sessions this browser has started (no logins, so no per-user history)


class TutorialScoreRequest(BaseModel):
    answer: str = ""
    r2_pick: int | None = None  # 0 = A, 1 = B


def _run_turn_safely(session, answer):
    """Run one turn on a copy of the session, so that if a model call fails
    halfway through, the stored session is left exactly as it was and the
    learner can simply resend. Returns (updated_session, result)."""
    working = copy.deepcopy(session)
    try:
        result = graph.run_turn(working, answer=answer)
    except LLMError as e:
        raise HTTPException(503, str(e)) from e
    return working, result


def _save_turn(sid, session, result):
    line = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_id": sid, "concept_id": session["concept_id"], "ab_only": session.get("ab_only", False),
            "total_rounds": session["total_rounds"],  # 0 = no limit
            "reading_seconds": session.get("reading_seconds", 0),
            "participant_code": session.get("participant_code"),  # None outside study mode
            "provider": llm_client.PROVIDER,
            **result["trace"]}
    storage.append_transcript(sid, line)


def _persist(sid, session):
    """Save the session so it can be continued later."""
    storage.save_session(sid, session)


NOT_FOUND = "This session could not be found, so please start a new one."


def _clean_id(sid):
    """The id in standard form, or None if it is not a real id, so a saved
    path or database query can never point anywhere else."""
    try:
        return str(uuid.UUID(sid))
    except (ValueError, TypeError, AttributeError):
        return None


def _get_session(sid, mode=None):
    """The live session from memory, else from storage, else 404. A case
    session and a skill check never stand in for each other."""
    sid = _clean_id(sid)
    if sid is None:
        raise HTTPException(404, NOT_FOUND)
    if sid not in SESSIONS:
        session = storage.load_session(sid)
        if session is None:
            raise HTTPException(404, NOT_FOUND)
        SESSIONS[sid] = session
    if SESSIONS[sid].get("mode") != mode:
        raise HTTPException(404, NOT_FOUND)
    return sid, SESSIONS[sid]


def _tools_view(tool_runs):
    return [{"tool": r["tool"], "args": r["args"], "summary": r["summary"], "chart": r["chart"]} for r in tool_runs]


def _turn_response(session, result):
    trace = result["trace"]
    return {
        "reply": result["reply"],
        "parts": result["parts"],
        "format": result["instruction"].get("format"),
        "round": session["round"],
        "total_rounds": session["total_rounds"],
        "level": LEVELS[session["level_idx"]][1],
        "ended": session["ended"],
        # tool results for the case file chart, newest last
        "tools": _tools_view(result["tool_runs"]),
        # a short view of what the agents did this turn (for the researcher, not shown as scores)
        "trace": {"plan_reason": (trace["plan"] or {}).get("reason"),
                  "guard_overrides": trace["guard_overrides"], "rewrites": trace["rewrites"]},
    }


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    """A check page to open before a testing day: is saving working, and which
    AI is in use? It never calls the AI, so it costs no quota."""
    saving_ok, saving = storage.check()
    if llm_client.PROVIDER == "mock":
        ai_ok, ai = not os.getenv("RENDER"), "Using mock replies, so no real AI. Set GOOGLE_API_KEY to use Gemini."
    else:
        model = llm_client.GEMINI_MODEL if llm_client.PROVIDER == "gemini" else llm_client.ANTHROPIC_MODEL
        ai_ok, ai = True, f"Using {llm_client.PROVIDER} ({model}). This page does not call it, to save quota."
    ok = saving_ok and ai_ok
    budget = limits.DAILY_CALL_BUDGET or "no limit"
    return JSONResponse({"ok": ok, "saving": {"ok": saving_ok, "message": saving}, "ai": {"ok": ai_ok, "message": ai},
                         "study_mode": f"on, {len(study_codes())} participant codes" if study_codes() else "off",
                         "today": {"ai_calls": limits.calls_today(), "budget": budget,
                                   "new_sessions_allowed": limits.budget_left()}},
                        status_code=200 if ok else 503)


@app.get("/api/config")
def config():
    """What the page needs to know at start: is study mode on (consent and code first)?"""
    return {"study_mode": bool(study_codes())}


@app.post("/api/participant/check")
def check_participant(req: CodeRequest):
    """Lets the consent screen say "wrong code" before a session starts."""
    return {"ok": req.code.strip().upper() in study_codes()}


@app.get("/api/concepts")
def list_concepts():
    return [{"id": k, "title": v["title"], "mission": v["mission"], "scenario": v["scenario"], "tag": v["tag"],
             "reading": v["reading"]}
            for k, v in CONCEPTS.items()]


# The tutorial is a fixed script. Only round 3 calls a model (the Assessor,
# once). Nothing is saved to disk: it is practice, not thesis data.
@app.get("/api/tutorial")
def get_tutorial():
    return {**TUTORIAL, "max": tutorial.MAX_SCORE,
            "levels": [{"key": k, "name": name} for k, name, _ in LEVELS], "standards": STANDARDS}


@app.post("/api/tutorial/score")
def score_tutorial(req: TutorialScoreRequest):
    return tutorial.final_result(req.r2_pick, req.answer[:MAX_ANSWER_CHARS])


@app.post("/api/session")
def start_session(req: StartRequest):
    if req.concept_id not in CONCEPTS:
        raise HTTPException(400, f"Unknown concept_id. Choose one of {list(CONCEPTS)}")
    new = orchestrator.new_session(req.concept_id, max(req.total_rounds, 0), req.ab_only,
                                   max(0, min(req.reading_seconds, 3600)))
    codes = study_codes()
    if codes:
        code = req.participant_code.strip().upper()
        if code not in codes:
            raise HTTPException(403, "This participant code is not on the study list, so please check it with your lecturer.")
        if not req.consent:
            raise HTTPException(403, "Please agree to take part before you start.")
        new["participant_code"] = code
        new["consent_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if not limits.budget_left():
        raise HTTPException(429, limits.FULL_MESSAGE)
    sid = str(uuid.uuid4())
    session, result = _run_turn_safely(new, None)
    SESSIONS[sid] = session
    _persist(sid, session)
    _save_turn(sid, session, result)
    return {"session_id": sid, **_turn_response(session, result)}


@app.get("/api/session/{sid}")
def get_session(sid: str):
    """Everything the page needs to rebuild the chat and continue a saved case."""
    sid, session = _get_session(sid)
    return {
        "session_id": sid,
        "concept_id": session["concept_id"],
        "round": session["round"],
        "total_rounds": session["total_rounds"],
        "level": LEVELS[session["level_idx"]][1],
        "ended": session["ended"],
        "ab_only": session.get("ab_only", False),
        # one entry per tutor turn: the learner answer that led to it (None for the opening), then the reply
        "turns": [{"answer": t["answer"], "parts": t["parts"], "format": t["instruction"].get("format"),
                   "tools": _tools_view(t["tool_runs"])} for t in session["turns"]],
    }


@app.post("/api/session/{sid}/answer")
def submit_answer(sid: str, req: AnswerRequest):
    sid, session = _get_session(sid)
    if session["ended"]:
        raise HTTPException(400, "This session has already ended.")
    if not req.answer.strip():  # the page blocks this too; a blank answer would waste a round and AI calls
        raise HTTPException(400, "Please type an answer first.")
    session, result = _run_turn_safely(session, req.answer[:MAX_ANSWER_CHARS])
    # saved with the answer, for a "with vs without hint" comparison in the thesis
    result["trace"]["hint_opened"] = session["turns"][-1]["hint_opened"] = req.hint_opened
    SESSIONS[sid] = session
    _persist(sid, session)
    _save_turn(sid, session, result)
    # last_assessment is for the stats screen; never shown to the learner mid-question
    return {**_turn_response(session, result), "last_assessment": result["assessment"]}


@app.post("/api/session/{sid}/end")
def end_session(sid: str):
    """Sessions with no round limit end when the learner presses End session.
    The last question, still unanswered, is left out; every answered round counts."""
    sid, session = _get_session(sid)
    if not session["ended"]:
        session["ended"] = True
        session["ended_by_learner"] = True
        _persist(sid, session)
    return {"ended": True, "rounds_answered": len(session["history"])}


# ---------- skill check (Goal 1): set questions, each tagged with one skill ----------

class CheckRequest(BaseModel):
    past_check_ids: list[str] = []  # earlier checks from this browser, so new questions come first


def _check_view(check):
    return {"question": skillcheck.current(check), "ended": check["ended"],
            "results": skillcheck.summarize(check["turns"]) if check["ended"] else None}


def _get_check(sid):
    return _get_session(sid, mode="skill_check")


@app.post("/api/check")
def start_check(req: CheckRequest):
    if study_codes():
        raise HTTPException(403, "The skill check is not part of the study yet.")
    ids = list(filter(None, map(_clean_id, req.past_check_ids[:100])))
    SESSIONS.update(storage.load_sessions([i for i in ids if i not in SESSIONS]))
    seen = [t["item"] for i in ids for t in (SESSIONS.get(i) or {}).get("turns", [])
            if (SESSIONS.get(i) or {}).get("mode") == "skill_check"]
    check = skillcheck.new_check(seen)
    sid = str(uuid.uuid4())
    SESSIONS[sid] = check
    _persist(sid, check)
    return {"check_id": sid, **_check_view(check)}


@app.get("/api/check/{sid}")
def get_check(sid: str):
    sid, check = _get_check(sid)
    return {"check_id": sid, **_check_view(check)}


@app.post("/api/check/{sid}/answer")
def answer_check(sid: str, req: AnswerRequest):
    sid, check = _get_check(sid)
    if check["ended"]:
        raise HTTPException(400, "This skill check has already ended.")
    if not req.answer.strip():
        raise HTTPException(400, "Please type an answer first.")
    if not limits.budget_left():
        raise HTTPException(429, limits.FULL_MESSAGE)
    working = copy.deepcopy(check)  # a failed model call leaves the saved check as it was
    try:
        turn = skillcheck.answer(working, req.answer[:MAX_ANSWER_CHARS])
    except LLMError as e:
        raise HTTPException(503, str(e)) from e
    SESSIONS[sid] = working
    _persist(sid, working)
    storage.append_transcript(sid, {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                    "session_id": sid, "mode": "skill_check", "provider": llm_client.PROVIDER, **turn})
    return {"check_id": sid, **_check_view(working)}


@app.post("/api/overview")
def overview(req: OverviewRequest):
    """The learner's overall status across every case they played in this
    browser: highest level, the 9 standards over all answers, and the best
    level per case. Same summary shape as /stats, so the page reuses its
    drawings. Unknown or broken ids are skipped. The tutorial is practice and
    is not saved, so it never counts here."""
    history, best_idx, played, finished, per_case, checks = [], 0, 0, 0, {}, []
    sids = list(dict.fromkeys(filter(None, map(_clean_id, req.session_ids[:300]))))
    # one storage call for every session not in memory yet
    SESSIONS.update(storage.load_sessions([sid for sid in sids if sid not in SESSIONS]))
    for sid in sids:
        s = SESSIONS.get(sid)
        if s is None:
            continue  # unknown id
        if s.get("mode") == "skill_check":
            checks += s["turns"]
            continue
        if not s["history"]:
            continue  # opened but never answered
        played += 1
        finished += bool(s["ended"])
        history += s["history"]
        reached = orchestrator.best_level_idx(s)
        best_idx = max(best_idx, reached)
        c = per_case.setdefault(s["concept_id"], {"sessions": 0, "level_idx": 0, "rounds": 0, "history": []})
        c["sessions"] += 1
        c["rounds"] += len(s["history"])
        c["history"] += s["history"]
        c["level_idx"] = max(c["level_idx"], reached)
    summary = orchestrator.summarize({"history": history, "level_idx": best_idx})
    return {
        "levels": [{"key": k, "name": name} for k, name, _ in LEVELS],
        "standards": STANDARDS,
        "summary": summary,
        "sessions_played": played, "sessions_finished": finished,
        "skill_check": skillcheck.summarize(checks) if checks else None,
        "cases": [{"id": cid, "title": CONCEPTS[cid]["title"], "sessions": v["sessions"], "rounds": v["rounds"],
                   "level": LEVELS[v["level_idx"]][1],
                   # for the standards filter in the overall status panel
                   "standards_met_count": orchestrator.summarize(
                       {"history": v["history"], "level_idx": v["level_idx"]})["standards_met_count"]}
                  for cid, v in per_case.items()],
    }


# Only one Coach call per session, even if the stats panel and the final
# profile ask at the same moment.
_comment_lock = threading.Lock()


def _final_comment(sid, session):
    """One paragraph on how the learner answered. Written once when the
    session ends, then saved with the session. If the Coach AI is off or
    fails, a plain-code paragraph is used, so the profile never breaks."""
    if not session.get("ended") or not session["history"]:
        return None  # nothing answered, so nothing to comment on (and no wasted AI call)
    with _comment_lock:
        if not session.get("comment"):
            try:
                session["comment"] = llm_client.call_coach(session)
            except Exception:  # any model problem: fall back, never block the profile
                session["comment"] = None
            session["comment"] = session["comment"] or orchestrator.fallback_comment(session)
            _persist(sid, session)
    return session["comment"]


@app.get("/api/session/{sid}/stats")
def get_stats(sid: str):
    sid, session = _get_session(sid)
    return {
        "round": session["round"],
        "total_rounds": session["total_rounds"],
        "level": LEVELS[session["level_idx"]][1],
        "levels": [{"key": k, "name": name} for k, name, _ in LEVELS],
        "standards": STANDARDS,
        "summary": orchestrator.summarize(session),
        "comment": _final_comment(sid, session),
        "history": session["history"],
    }
