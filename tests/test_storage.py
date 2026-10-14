"""The Supabase backend, checked against a fake database (no account needed)."""
import httpx

from app import storage

SID = "6f1c2c1e-3f0a-4a8e-9c55-0d6f1d9b2a11"


def fake_db(monkeypatch):
    tables, calls = {"sessions": {}, "transcript_lines": []}, []

    def _db(method, table, headers=None, json=None, params=None):
        calls.append(headers)
        if method == "POST" and table == "sessions":
            tables["sessions"][json["id"]] = json["data"]  # upsert
        elif method == "POST":
            tables[table].append(json)
        else:
            ids = params["id"].removeprefix("in.(").removesuffix(")").split(",")
            rows = [{"id": i, "data": tables["sessions"][i]} for i in ids if i in tables["sessions"]]
            return httpx.Response(200, json=rows)
    monkeypatch.setattr(storage, "BACKEND", "supabase")
    monkeypatch.setattr(storage, "SUPABASE_SECRET_KEY", "sb_secret_test")
    monkeypatch.setattr(storage, "_db", _db)
    return tables, calls


def test_supabase_saves_and_loads_sessions(monkeypatch):
    tables, calls = fake_db(monkeypatch)
    storage.save_session(SID, {"round": 1})
    storage.save_session(SID, {"round": 2})  # same id: replaced, not added
    assert storage.load_session(SID) == {"round": 2}
    assert storage.load_session("00000000-0000-0000-0000-000000000000") is None
    assert storage.load_sessions([]) == {}
    storage.append_transcript(SID, {"round": 1})
    assert tables["transcript_lines"] == [{"session_id": SID, "line": {"round": 1}}]
    assert all(h["apikey"] == "sb_secret_test" and "Authorization" not in h for h in calls)


def test_health_check_reads_the_tables_and_explains_problems(monkeypatch):
    fake_db(monkeypatch)
    monkeypatch.setattr(storage, "_db", lambda *a, **k: httpx.Response(200, json=[]))
    assert storage.check() == (True, "Saving to Supabase works.")

    def refused(*a, **k):
        request = httpx.Request("GET", "https://example.supabase.co/rest/v1/sessions")
        raise httpx.HTTPStatusError("no", request=request, response=httpx.Response(401, request=request))
    monkeypatch.setattr(storage, "_db", refused)
    ok, message = storage.check()
    assert not ok and "secret key is wrong" in message


def test_health_check_warns_when_render_would_wipe_the_files(monkeypatch):
    monkeypatch.delenv("RENDER", raising=False)
    assert storage.check()[0]
    monkeypatch.setenv("RENDER", "true")
    ok, message = storage.check()
    assert not ok and "SUPABASE_URL" in message


def test_a_failed_save_does_not_block_the_learner(monkeypatch):
    def broken(*a, **k):
        raise httpx.ConnectError("no internet")
    monkeypatch.setattr(storage, "BACKEND", "supabase")
    monkeypatch.setattr(storage, "_db", broken)
    storage.save_session(SID, {"round": 1})  # logged, not raised
    assert storage.load_session(SID) is None
