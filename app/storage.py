"""Where sessions and transcripts are saved. Two options, picked at start:

  files     sessions/<id>.json and transcripts/<id>.jsonl in this folder
            (the default, used on your own computer)
  supabase  a free Supabase Postgres database, used when SUPABASE_URL and
            SUPABASE_SECRET_KEY are set. Needed online, because free hosts
            like Render wipe their files on every restart.

Tables for the database are in deploy/supabase.sql. Only the server holds the
secret key, and the tables let nobody else in, so learner data stays private.
"""
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
SESSION_DIR = ROOT / "sessions"
TRANSCRIPT_DIR = ROOT / "transcripts"

# The project URL, e.g. https://abc.supabase.co. If the API address was pasted
# instead (ending in /rest/v1/), that end is cut off, since it is added below.
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/").removesuffix("/rest/v1")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "")
BACKEND = "supabase" if SUPABASE_URL and SUPABASE_SECRET_KEY else "files"

log = logging.getLogger("socratic.storage")


# ---------- files ----------

def _file_save(sid, session):
    """Written to a temp file first, then renamed, so a crash never leaves half a file."""
    SESSION_DIR.mkdir(exist_ok=True)
    tmp = SESSION_DIR / f"{sid}.json.tmp"
    tmp.write_text(json.dumps(session, ensure_ascii=False), encoding="utf-8")
    tmp.replace(SESSION_DIR / f"{sid}.json")


def _file_load(sid):
    path = SESSION_DIR / f"{sid}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _file_append(sid, line):
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    with open(TRANSCRIPT_DIR / f"{sid}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


# ---------- supabase ----------

def _headers(extra=None):
    h = {"apikey": SUPABASE_SECRET_KEY, "Content-Type": "application/json"}
    if SUPABASE_SECRET_KEY.startswith("eyJ"):  # an older service_role key also goes here
        h["Authorization"] = f"Bearer {SUPABASE_SECRET_KEY}"
    return {**h, **(extra or {})}


def _db(method, table, **kwargs):
    r = httpx.request(method, f"{SUPABASE_URL}/rest/v1/{table}", timeout=10, **kwargs)
    r.raise_for_status()
    return r


def _db_save(sid, session):
    _db("POST", "sessions", headers=_headers({"Prefer": "resolution=merge-duplicates,return=minimal"}),
        json={"id": sid, "data": session, "updated_at": datetime.now(timezone.utc).isoformat()})


def _db_load_many(sids):
    if not sids:
        return {}
    r = _db("GET", "sessions", headers=_headers(),
            params={"select": "id,data", "id": f"in.({','.join(sids)})"})
    return {row["id"]: row["data"] for row in r.json()}


def _db_append(sid, line):
    _db("POST", "transcript_lines", headers=_headers({"Prefer": "return=minimal"}),
        json={"session_id": sid, "line": line})


# ---------- what main.py calls ----------
# Ids are checked as UUIDs in main.py before they reach here.

def _try_twice(fn, *args):
    """A save that fails is tried once more, then logged. The learner is not
    blocked: the session stays in memory and the next turn saves it again."""
    for attempt in range(2):
        try:
            return fn(*args)
        except (httpx.HTTPError, OSError) as e:
            if attempt:
                log.error("Saving failed (%s): %s", fn.__name__, e)


def save_session(sid, session):
    _try_twice(_db_save if BACKEND == "supabase" else _file_save, sid, session)


def append_transcript(sid, line):
    _try_twice(_db_append if BACKEND == "supabase" else _file_append, sid, line)


def load_sessions(sids):
    """{id: session} for the ids that exist. Missing ones are left out."""
    if BACKEND == "supabase":
        try:
            return _db_load_many(list(sids))
        except httpx.HTTPError as e:
            log.error("Loading failed: %s", e)
            return {}
    found = {sid: _file_load(sid) for sid in sids}
    return {sid: s for sid, s in found.items() if s is not None}


def load_session(sid):
    return load_sessions([sid]).get(sid)


def all_sessions():
    """Every saved session as (id, session, updated_at), for the data export."""
    if BACKEND == "supabase":
        rows, page = [], 1000  # the database sends at most 1000 rows per request
        while True:
            r = _db("GET", "sessions", headers=_headers(),
                    params={"select": "id,data,updated_at", "order": "updated_at", "limit": str(page),
                            "offset": str(len(rows))})
            batch = r.json()
            rows += batch
            if len(batch) < page:
                return [(row["id"], row["data"], row["updated_at"]) for row in rows]
    out = []
    for path in sorted(SESSION_DIR.glob("*.json")):
        mtime = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")
        out.append((path.stem, json.loads(path.read_text(encoding="utf-8")), mtime))
    return out


# What a failed database check most likely means, by HTTP status.
_DB_PROBLEMS = {401: "the secret key is wrong", 403: "the secret key is not allowed to read the tables",
                404: "the tables are missing, so run deploy/supabase.sql in Supabase"}


def check():
    """(ok, message) for the /api/health page. It only reads, so it never adds
    test rows to the thesis data. Failed saves are otherwise only logged."""
    if BACKEND == "supabase":
        try:
            for table in ("sessions", "transcript_lines"):
                _db("GET", table, headers=_headers(), params={"select": "id", "limit": "1"})
        except httpx.HTTPStatusError as e:
            code = e.response.status_code
            return False, f"Saving to Supabase is broken, because {_DB_PROBLEMS.get(code, f'it replied with error {code}')}."
        except httpx.HTTPError:
            return False, "Saving to Supabase is broken, because the database could not be reached."
        return True, "Saving to Supabase works."
    if os.getenv("RENDER"):  # Render sets this on its servers
        return False, ("Saving to files, but Render wipes them on every restart, so set SUPABASE_URL and "
                       "SUPABASE_SECRET_KEY on Render.")
    try:
        for folder in (SESSION_DIR, TRANSCRIPT_DIR):
            folder.mkdir(exist_ok=True)
    except OSError:
        return False, "Saving to files is broken, because the folders could not be made."
    return True, "Saving to files on this computer works."
