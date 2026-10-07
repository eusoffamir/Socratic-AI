import copy
import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # must run before `from . import graph` below, since llm_client
                # picks its provider (mock/gemini/anthropic) at import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import graph, llm_client, orchestrator
from .llm_client import LLMError
from .content import CONCEPTS, LEVELS, STANDARDS

app = FastAPI(title="Socratic AI")

# Live sessions are kept in memory and also saved to sessions/<id>.json after
# every turn, so a learner can leave and continue later, even after a server
# restart. One file is about 5 to 20 KB.
SESSIONS: dict[str, dict] = {}

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
# One .jsonl file per session, one line per turn, with the full agent trace.
# No names or personal data are stored. Kept for the thesis Results.
TRANSCRIPT_DIR = Path(__file__).resolve().parent.parent / "transcripts"
SESSION_DIR = Path(__file__).resolve().parent.parent / "sessions"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class StartRequest(BaseModel):
    concept_id: str = "pattern_or_luck"
    total_rounds: int = 5
    ab_only: bool = False
    reading_seconds: int = 0  # seconds the reading pop-up was open before "Start this case"


class AnswerRequest(BaseModel):
    answer: str


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
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    line = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_id": sid, "concept_id": session["concept_id"], "ab_only": session.get("ab_only", False),
            "reading_seconds": session.get("reading_seconds", 0),
            "provider": llm_client.PROVIDER,
            **result["trace"]}
    with open(TRANSCRIPT_DIR / f"{sid}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def _persist(sid, session):
    """Save the session so it can be continued later. Written to a temp file
    first, then renamed, so a crash never leaves half a file."""
    SESSION_DIR.mkdir(exist_ok=True)
    tmp = SESSION_DIR / f"{sid}.json.tmp"
    tmp.write_text(json.dumps(session, ensure_ascii=False), encoding="utf-8")
    tmp.replace(SESSION_DIR / f"{sid}.json")


def _get_session(sid):
    """The live session from memory, else from disk, else 404."""
    try:
        sid = str(uuid.UUID(sid))  # only real ids, so the path can't point anywhere else
    except ValueError:
        raise HTTPException(404, "Session not found. Start a new one.")
    if sid not in SESSIONS:
        path = SESSION_DIR / f"{sid}.json"
        if not path.exists():
            raise HTTPException(404, "Session not found. Start a new one.")
        SESSIONS[sid] = json.loads(path.read_text(encoding="utf-8"))
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


@app.get("/api/concepts")
def list_concepts():
    return [{"id": k, "title": v["title"], "mission": v["mission"], "scenario": v["scenario"], "tag": v["tag"],
             "reading": v["reading"]}
            for k, v in CONCEPTS.items()]


@app.post("/api/session")
def start_session(req: StartRequest):
    if req.concept_id not in CONCEPTS:
        raise HTTPException(400, f"Unknown concept_id. Choose one of {list(CONCEPTS)}")
    sid = str(uuid.uuid4())
    session, result = _run_turn_safely(orchestrator.new_session(req.concept_id, req.total_rounds, req.ab_only,
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
    session, result = _run_turn_safely(session, req.answer)
    SESSIONS[sid] = session
    _persist(sid, session)
    _save_turn(sid, session, result)
    # last_assessment is for the stats screen; never shown to the learner mid-question
    return {**_turn_response(session, result), "last_assessment": result["assessment"]}


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
