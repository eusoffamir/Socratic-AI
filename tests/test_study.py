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
    assert c.get("/api/config").json()["study_mode"] is False
    r = c.post("/api/session", json={})
    assert r.status_code == 200 and main.SESSIONS[r.json()["session_id"]].get("participant_code") is None


def test_study_mode_needs_a_listed_code_and_consent(monkeypatch):
    c = client(monkeypatch, "P001, p002")
    assert c.get("/api/config").json()["study_mode"] is True
    assert c.post("/api/participant/check", json={"code": " p002 "}).json() == {"ok": True, "group": "tool"}
    assert c.post("/api/participant/check", json={"code": "P999"}).json() == {"ok": False, "group": None}
    assert c.post("/api/session", json={"participant_code": "P999", "consent": True}).status_code == 403
    assert c.post("/api/session", json={"participant_code": "P001"}).status_code == 403  # no consent
    r = c.post("/api/session", json={"participant_code": "p001", "consent": True})
    assert r.status_code == 200
    s = main.SESSIONS[r.json()["session_id"]]
    assert s["participant_code"] == "P001" and s["consent_at"]
    assert "2 participant codes" in c.get("/api/health").json()["study_mode"]


def study_client(monkeypatch, tmp_path):
    """Tool group P001, control group C001, and a study topic built in mock mode."""
    import json
    from app import builder, study
    c = client(monkeypatch, "P001")
    monkeypatch.setenv("STUDY_CONTROL", "C001")
    path = tmp_path / "topic.json"
    path.write_text(json.dumps(builder.build("photosynthesis")), encoding="utf-8")
    monkeypatch.setenv("STUDY_TOPIC_FILE", str(path))
    return c, study.topic()


def test_groups_get_the_same_study_cases(monkeypatch, tmp_path):
    c, t = study_client(monkeypatch, tmp_path)
    assert c.post("/api/participant/check", json={"code": "c001"}).json() == {"ok": True, "group": "control"}
    tool = c.post("/api/study/topic", json={"code": "P001"}).json()
    ctrl = c.post("/api/study/topic", json={"code": "C001"}).json()
    assert tool["group"] == "tool" and ctrl["group"] == "control"
    assert [x["id"] for x in tool["cases"]] == [x["id"] for x in ctrl["cases"]] == [x["id"] for x in t["cases"]]
    assert ctrl["cases"][0]["notes"] == t["cases"][0]["notes"]
    assert "knowledge" not in ctrl["cases"][0]  # the control group reads only
    assert c.post("/api/study/topic", json={"code": "X1"}).status_code == 403


def test_control_group_cannot_chat_and_its_reading_is_saved(monkeypatch, tmp_path):
    from app import storage
    c, t = study_client(monkeypatch, tmp_path)
    first = t["cases"][0]["id"]
    assert c.post("/api/session", json={"participant_code": "C001", "consent": True,
                                        "concept_id": first}).status_code == 403
    saved = {}
    monkeypatch.setattr(storage, "save_session", lambda sid, s: saved.update({sid: s}))
    assert c.post("/api/study/read", json={"code": "C001", "case_id": first}).status_code == 403  # no consent
    assert c.post("/api/study/read", json={"code": "C001", "consent": True, "case_id": "nope"}).status_code == 400
    assert c.post("/api/study/read", json={"code": "P001", "consent": True, "case_id": first}).status_code == 403
    r = c.post("/api/study/read", json={"code": "c001", "consent": True, "case_id": first, "seconds": 600})
    assert r.status_code == 200
    (s,) = saved.values()
    assert s["mode"] == "control_reading" and s["participant_code"] == "C001"
    assert s["reading_seconds"] == 600 and s["turns"] == []


def test_tool_group_only_starts_study_cases(monkeypatch, tmp_path):
    c, t = study_client(monkeypatch, tmp_path)
    ok = {"participant_code": "P001", "consent": True}
    assert c.post("/api/session", json={**ok, "concept_id": "pattern_or_luck"}).status_code == 400
    r = c.post("/api/session", json={**ok, "concept_id": t["cases"][1]["id"]})
    assert r.status_code == 200
    s = main.SESSIONS[r.json()["session_id"]]
    assert s["case"]["id"] == t["cases"][1]["id"] and s["participant_code"] == "P001"
