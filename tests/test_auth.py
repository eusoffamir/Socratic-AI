"""Optional Sign in with Google: hidden until GOOGLE_CLIENT_ID is set, Google's
check is faked here, and only a hash of the account id is stored."""
import time

import httpx
from fastapi.testclient import TestClient

from app import auth, main, storage

CLIENT = "123-test.apps.googleusercontent.com"
REAL_TOKENINFO = auth._tokeninfo


def claims(**extra):
    return {"aud": CLIENT, "iss": "https://accounts.google.com", "sub": "1234567890", "exp": str(int(time.time()) + 600),
            "given_name": "Eusoff", "picture": "https://example.com/me.png", "email": "secret@example.com", **extra}


def client(monkeypatch, tmp_path, google=None):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", CLIENT)
    monkeypatch.setattr(storage, "PROFILE_DIR", tmp_path)
    monkeypatch.setattr(auth, "_tokeninfo", lambda cred: google if google is not None else claims())
    return TestClient(main.app)


def test_sign_in_is_hidden_until_a_client_id_is_set(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    c = TestClient(main.app)
    assert c.get("/api/config").json()["google_client_id"] == ""
    assert c.post("/api/auth/google", json={"credential": "x"}).status_code == 401
    assert c.get("/api/me").json() == {"user": None}


def test_sign_in_sets_a_cookie_and_the_profile_follows_the_learner(monkeypatch, tmp_path):
    c = client(monkeypatch, tmp_path)
    assert c.get("/api/config").json()["google_client_id"] == CLIENT
    r = c.post("/api/auth/google", json={"credential": "token"})
    assert r.status_code == 200 and r.json()["user"] == {"name": "Eusoff", "picture": "https://example.com/me.png"}
    assert r.json()["profile"] == {} and auth.COOKIE in r.cookies
    data = {"ask-chats": [{"id": "a", "sid": "a", "name": "Volcanoes"}], "my-sessions": ["a"], "theme": "dark"}
    assert c.post("/api/me/profile", json={"data": data}).json() == {"ok": True}
    # another device: a fresh sign-in gets the same lists back, without unknown keys
    other = client(monkeypatch, tmp_path)
    got = other.post("/api/auth/google", json={"credential": "token"}).json()["profile"]
    assert got == {"ask-chats": data["ask-chats"], "my-sessions": ["a"]}
    assert other.get("/api/me").json()["profile"] == got


def test_no_name_or_email_is_stored(monkeypatch, tmp_path):
    c = client(monkeypatch, tmp_path)
    c.post("/api/auth/google", json={"credential": "token"})
    c.post("/api/me/profile", json={"data": {"my-checks": ["x"]}})
    files = list(tmp_path.glob("*.json"))
    assert [f.stem for f in files] == [auth.user_id("1234567890")]
    text = files[0].read_text(encoding="utf-8")
    assert "Eusoff" not in text and "secret@example.com" not in text and "1234567890" not in text


def test_tokens_for_another_app_or_expired_are_refused(monkeypatch, tmp_path):
    for bad in (claims(aud="someone-else"), claims(iss="evil.com"), claims(exp="1"), claims(sub="")):
        c = client(monkeypatch, tmp_path, google=bad)
        assert c.post("/api/auth/google", json={"credential": "token"}).status_code == 401


def test_google_refusing_the_token_is_a_401(monkeypatch, tmp_path):
    c = client(monkeypatch, tmp_path)
    monkeypatch.setattr(auth, "_tokeninfo", REAL_TOKENINFO)  # the real check, with Google's reply faked
    monkeypatch.setattr(auth.httpx, "get", lambda *a, **k: httpx.Response(400, json={"error": "invalid_token"}))
    r = c.post("/api/auth/google", json={"credential": "token"})
    assert r.status_code == 401 and "did not accept" in r.json()["detail"]


def test_saving_needs_a_valid_cookie(monkeypatch, tmp_path):
    c = client(monkeypatch, tmp_path)
    assert c.post("/api/me/profile", json={"data": {}}).status_code == 401
    c.cookies.set(auth.COOKIE, "made.up")
    assert c.post("/api/me/profile", json={"data": {}}).status_code == 401
    assert c.get("/api/me").json() == {"user": None}


def test_cookie_is_signed_and_expires():
    value = auth.make_cookie(claims(), now=1000)
    assert auth.read_cookie(value, now=1001)["uid"] == auth.user_id("1234567890")
    body, sig = value.split(".")
    assert auth.read_cookie(body + "x." + sig, now=1001) is None  # changed
    assert auth.read_cookie(value, now=1000 + auth.MAX_AGE + 1) is None  # expired
    assert auth.read_cookie("", now=1001) is None and auth.read_cookie("no-dot") is None


def test_logout_clears_the_cookie(monkeypatch, tmp_path):
    c = client(monkeypatch, tmp_path)
    c.post("/api/auth/google", json={"credential": "token"})
    assert c.get("/api/me").json()["user"]
    c.post("/api/auth/logout")
    assert c.get("/api/me").json() == {"user": None}


def test_a_too_big_profile_is_refused(monkeypatch, tmp_path):
    c = client(monkeypatch, tmp_path)
    c.post("/api/auth/google", json={"credential": "token"})
    big = {"my-sessions": ["x" * 1000] * (auth.MAX_PROFILE_BYTES // 1000 + 1)}
    assert c.post("/api/me/profile", json={"data": big}).status_code == 413


def test_supabase_profile_round_trip(monkeypatch):
    rows = {}

    def _db(method, table, headers=None, json=None, params=None):
        assert table == "profiles"
        if method == "POST":
            rows[json["id"]] = json["data"]
            return httpx.Response(201)
        uid = params["id"].removeprefix("eq.")
        return httpx.Response(200, json=[{"data": rows[uid]}] if uid in rows else [])
    monkeypatch.setattr(storage, "BACKEND", "supabase")
    monkeypatch.setattr(storage, "_db", _db)
    assert storage.load_profile("u1") == {}
    assert storage.save_profile("u1", {"my-checks": ["c"]}) is True
    assert storage.load_profile("u1") == {"my-checks": ["c"]}


def test_a_database_failure_is_reported_not_raised(monkeypatch):
    def _db(*a, **k):
        raise httpx.ConnectError("down")
    monkeypatch.setattr(storage, "BACKEND", "supabase")
    monkeypatch.setattr(storage, "_db", _db)
    assert storage.save_profile("u1", {}) is False and storage.load_profile("u1") is None
