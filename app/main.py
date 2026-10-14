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

from . import graph, llm_client, orchestrator, storage, tutorial
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


# Longest answer sent to the agents. A real answer is a few sentences; this
# stops a huge paste from using up the free model quota on a public link.
MAX_ANSWER_CHARS = 2000


class AnswerRequest(BaseModel):
    answer: str


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


def _get_session(sid):
    """The live session from memory, else from storage, else 404."""
    sid = _clean_id(sid)
    if sid is None:
        raise HTTPException(404, NOT_FOUND)
    if sid not in SESSIONS:
        session = storage.load_session(sid)
        if session is None:
            raise HTTPException(404, NOT_FOUND)
        SESSIONS[sid] = session
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
    return JSONResponse({"ok": ok, "saving": {"ok": saving_ok, "message": saving}, "ai": {"ok": ai_ok, "message": ai}},
                        status_code=200 if ok else 503)


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
    sid = str(uuid.uuid4())
    session, result = _run_turn_safely(orchestrator.new_session(req.concept_id, max(req.total_rounds, 0), req.ab_only,
                                                            max(0, min(req.reading_seconds, 3600))), None)
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
    session, result = _run_turn_safely(session, req.answer[:MAX_ANSWER_CHARS])
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


@app.post("/api/overview")
def overview(req: OverviewRequest):
    """The learner's overall status across every case they played in this
    browser: highest level, the 9 standards over all answers, and the best
    level per case. Same summary shape as /stats, so the page reuses its
    drawings. Unknown or broken ids are skipped. The tutorial is practice and
    is not saved, so it never counts here."""
    history, best_idx, played, finished, per_case = [], 0, 0, 0, {}
    sids = list(dict.fromkeys(filter(None, map(_clean_id, req.session_ids[:300]))))
    # one storage call for every session not in memory yet
    SESSIONS.update(storage.load_sessions([sid for sid in sids if sid not in SESSIONS]))
    for sid in sids:
        s = SESSIONS.get(sid)
        if s is None:
            continue  # unknown id
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
    if not session.get("ended"):
        return None
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
