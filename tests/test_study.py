"""Study mode: off by default; when STUDY_CODES is set, only listed codes with
consent can start, and the code is saved with the session."""
from fastapi.testclient import TestClient

from app import limits, llm_client, main


def client(monkeypatch, codes=""):
    monkeypatch.setenv("STUDY_CODES", codes)
    monkeypatch.setattr(limits, "DAILY_CALL_BUDGET", 0)
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    return TestClient(main.app)


def test_study_mode_is_off_by_default(monkeypatch):
    c = client(monkeypatch)
    assert c.get("/api/config").json() == {"study_mode": False}
    r = c.post("/api/session", json={})
    assert r.status_code == 200 and main.SESSIONS[r.json()["session_id"]].get("participant_code") is None


def test_study_mode_needs_a_listed_code_and_consent(monkeypatch):
    c = client(monkeypatch, "P001, p002")
    assert c.get("/api/config").json() == {"study_mode": True}
    assert c.post("/api/participant/check", json={"code": " p002 "}).json() == {"ok": True}
    assert c.post("/api/participant/check", json={"code": "P999"}).json() == {"ok": False}
    assert c.post("/api/session", json={"participant_code": "P999", "consent": True}).status_code == 403
    assert c.post("/api/session", json={"participant_code": "P001"}).status_code == 403  # no consent
    r = c.post("/api/session", json={"participant_code": "p001", "consent": True})
    assert r.status_code == 200
    s = main.SESSIONS[r.json()["session_id"]]
    assert s["participant_code"] == "P001" and s["consent_at"]
    assert "2 participant codes" in c.get("/api/health").json()["study_mode"]
