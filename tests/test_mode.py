from fastapi.testclient import TestClient

from app import llm_client, main


def test_ab_mode_can_be_switched_during_a_session(monkeypatch, tmp_path):
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    monkeypatch.setattr(main.storage, "SESSION_DIR", tmp_path / "s")
    monkeypatch.setattr(main.storage, "TRANSCRIPT_DIR", tmp_path / "t")
    client = TestClient(main.app)
    sid = client.post("/api/session", json={"concept_id": "pattern_or_luck", "total_rounds": 0}).json()["session_id"]
    assert client.get(f"/api/session/{sid}").json()["ab_only"] is False
    assert client.post(f"/api/session/{sid}/mode", json={"ab_only": True}).json() == {"ab_only": True}
    assert client.get(f"/api/session/{sid}").json()["ab_only"] is True
