"""The daily budget of AI calls that protects the free Gemini quota."""
from fastapi.testclient import TestClient

from app import limits, llm_client, main


def fresh(monkeypatch, budget):
    monkeypatch.setattr(limits, "DAILY_CALL_BUDGET", budget)
    monkeypatch.setattr(limits, "_day", None)
    monkeypatch.setattr(limits, "_calls", 0)


def test_new_sessions_stop_when_the_budget_is_used(monkeypatch):
    fresh(monkeypatch, 3)
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    client = TestClient(main.app)
    assert client.post("/api/session", json={}).status_code == 200
    for _ in range(3):
        limits.count_call()
    r = client.post("/api/session", json={})
    assert r.status_code == 429 and r.json()["detail"] == limits.FULL_MESSAGE


def test_blank_answers_are_refused_and_empty_sessions_skip_the_coach(monkeypatch):
    # Audit, 15 Oct 2026: a blank answer used a round, and ending before any
    # answer still called the Coach AI.
    fresh(monkeypatch, 0)
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    coach = []
    monkeypatch.setattr(llm_client, "call_coach", lambda s: coach.append(1) or "comment")
    client = TestClient(main.app)
    sid = client.post("/api/session", json={"total_rounds": 0}).json()["session_id"]
    assert client.post(f"/api/session/{sid}/answer", json={"answer": "   "}).status_code == 400
    client.post(f"/api/session/{sid}/end")
    assert client.get(f"/api/session/{sid}/stats").json()["comment"] is None and coach == []


def test_hint_opened_is_saved_with_the_answer(monkeypatch):
    fresh(monkeypatch, 0)
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    client = TestClient(main.app)
    sid = client.post("/api/session", json={}).json()["session_id"]
    client.post(f"/api/session/{sid}/answer", json={"answer": "luck, since many stocks do it", "hint_opened": True})
    client.post(f"/api/session/{sid}/answer", json={"answer": "test it on new days"})
    turns = main.SESSIONS[sid]["turns"]
    assert [t.get("hint_opened") for t in turns] == [None, True, False]


def test_a_streamed_answer_sends_its_real_steps_then_the_reply(monkeypatch):
    import json
    fresh(monkeypatch, 0)
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    client = TestClient(main.app)
    sid = client.post("/api/session", json={}).json()["session_id"]
    r = client.post(f"/api/session/{sid}/answer", json={"answer": "luck, since many stocks do it", "stream": True})
    lines = [json.loads(x) for x in r.text.splitlines() if x.strip()]
    steps = [x["step"] for x in lines if "step" in x]
    assert steps[:4] == ["Reading your answer", "Planning the next question",
                         "Writing the next question", "Checking the question"]
    assert len(main.SESSIONS[sid]["history"]) == 1  # saved like a normal answer
    normal = client.post(f"/api/session/{sid}/answer", json={"answer": "test it on new days"}).json()
    assert set(lines[-1]["result"]) == set(normal)  # the same reply as without streaming


def test_the_count_starts_again_on_a_new_day(monkeypatch):
    fresh(monkeypatch, 2)
    limits.count_call()
    limits.count_call()
    assert not limits.budget_left()
    monkeypatch.setattr(limits, "_day", limits._today().replace(year=2000))  # yesterday, as far as the count knows
    assert limits.calls_today() == 0 and limits.budget_left()


def test_zero_means_no_limit(monkeypatch):
    fresh(monkeypatch, 0)
    for _ in range(1000):
        limits.count_call()
    assert limits.budget_left()
