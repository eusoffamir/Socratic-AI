"""Skill check (Goal 1 step 4): the tagged question bank, picking, marking and the API."""
import random

from fastapi.testclient import TestClient

from app import limits, llm_client, main, skillcheck
from app.content import CONCEPTS
from app.reasoning import CORE_KNOWLEDGE, REASONING_TYPES


def client(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDY_CODES", "")
    monkeypatch.setattr(limits, "DAILY_CALL_BUDGET", 0)
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    monkeypatch.setattr(main.storage, "SESSION_DIR", tmp_path / "s")
    monkeypatch.setattr(main.storage, "TRANSCRIPT_DIR", tmp_path / "t")
    return TestClient(main.app)


def test_bank_has_two_questions_per_pair():
    for r in REASONING_TYPES:
        for k in CORE_KNOWLEDGE:
            assert len([i for i in skillcheck.ITEMS.values() if i["reasoning"] == r and i["knowledge"] == k]) == 2
    assert all(i["case"] in CONCEPTS for i in skillcheck.ITEMS.values())


def test_bank_text_follows_the_writing_rules():
    for i in skillcheck.ITEMS.values():
        text = i["situation"] + " " + i["question"]
        assert "--" not in text and "—" not in text and "!" not in text and ":" not in text, i["id"]
        assert i["question"].endswith("?"), i["id"]


def test_pick_is_balanced_and_prefers_new_questions():
    ids = skillcheck.pick(rng=random.Random(1))
    items = [skillcheck.ITEMS[i] for i in ids]
    assert len(ids) == skillcheck.QUESTIONS_PER_CHECK == len(set(ids))
    for r in REASONING_TYPES:
        mine = [i for i in items if i["reasoning"] == r]
        assert len(mine) == 2 and mine[0]["knowledge"] != mine[1]["knowledge"]
    again = skillcheck.pick(seen=ids, rng=random.Random(2))
    assert not set(again) & set(ids)


def test_attained_needs_both_the_reasoning_and_the_knowledge(monkeypatch):
    check = skillcheck.new_check()
    item = skillcheck.ITEMS[check["items"][0]]
    marks = {"types": {r: int(r == item["reasoning"]) for r in REASONING_TYPES},
             "knowledge": {k: 0 for k in CORE_KNOWLEDGE}, "evidence": ""}
    monkeypatch.setattr(llm_client, "call_assessor", lambda s, a: {"standards": {}, "reasoning": marks})
    assert skillcheck.answer(check, "a real answer of my own words here")["attained"] == 0
    marks["knowledge"] = {**marks["knowledge"], skillcheck.ITEMS[check["items"][1]]["knowledge"]: 1}
    nxt = skillcheck.ITEMS[check["items"][1]]
    marks["types"] = {r: int(r == nxt["reasoning"]) for r in REASONING_TYPES}
    assert skillcheck.answer(check, "another real answer of my own words")["attained"] == 1


def test_summary_counts_asked_and_attained():
    turns = [{"reasoning": "inductive", "knowledge": "causal", "attained": 1},
             {"reasoning": "inductive", "knowledge": "causal", "attained": 0},
             {"reasoning": "deductive", "knowledge": "factual", "attained": 0}]
    d = skillcheck.summarize(turns)
    assert d["grid"]["causal"]["inductive"] == {"asked": 2, "attained": 1}
    assert d["reasoning"]["deductive"] == {"asked": 1, "attained": 0}
    assert d["messages"] == ["Your strongest reasoning so far is inductive, shown in 1 of 2 questions.",
                             "You have not shown deductive reasoning on factual knowledge yet."]


def test_api_runs_a_whole_check(monkeypatch, tmp_path):
    c = client(monkeypatch, tmp_path)
    r = c.post("/api/check", json={}).json()
    cid, q = r["check_id"], r["question"]
    assert q["number"] == 1 and q["total"] == skillcheck.QUESTIONS_PER_CHECK
    assert c.get(f"/api/session/{cid}").status_code == 404  # a check is not a case session
    for _ in range(q["total"]):
        r = c.post(f"/api/check/{cid}/answer", json={"answer": "Many stocks do this, so it is probably luck"}).json()
    assert r["ended"] and r["question"] is None and r["results"]["answers"] == q["total"]
    assert c.post(f"/api/check/{cid}/answer", json={"answer": "more"}).status_code == 400
    ov = c.post("/api/overview", json={"session_ids": [cid]}).json()
    assert ov["skill_check"]["answers"] == q["total"] and ov["sessions_played"] == 0
    # the next check avoids the questions already answered
    nxt = c.post("/api/check", json={"past_check_ids": [cid]}).json()
    assert nxt["question"]["id"] not in main.SESSIONS[cid]["items"]


# ---------- answers from an AI chatbot (found by Eusoff on 21 October 2026) ----------

AI_ANSWERS = [  # shortened from the Gemini replies Eusoff pasted into a check
    "Your friend is mistaking random streaks of luck for real, repeatable patterns. Once that random luck runs out, "
    "the streak ends.\nWould you like to look at a quick way to test if a streak is real or just a fluke?",
    "These 3 cases suggest that a great backtest does not guarantee future success.\n"
    "AI responses may include mistakes. For financial advice, consult a professional. Learn more",
    "In the context of the case, this co-movement is best explained by:\nCommon Macroeconomic Sensitivities: Both banks "
    "respond to the same forces.\nShared Sector Risk: Because they operate within the same industry, sentiment moves both.",
    "The rule overfitted. Here is the breakdown of why:\n- The expected rate is 19.\n- You found 1.",
]
HUMAN_ANSWERS = [
    "I think it is luck, because about 15 out of 500 stocks do this anyway, so one streak is not proof.",
    "Both banks follow interest rates, so when rates move they both move. I would check if it holds on new years.",
    "First I would split the data. Then I test the rule on the second half to see if it still works.",
    "idk",
    "In 2014 many stocks fell together, so I think a hidden cause hit them all.",  # a year is not an em dash
]


def test_ai_like_catches_chatbot_replies_but_not_learners():
    from app import copycheck
    assert all(copycheck.ai_like(a) for a in AI_ANSWERS)
    assert not any(copycheck.ai_like(a) for a in HUMAN_ANSWERS)


def test_ai_answer_scores_zero_without_a_model_call(monkeypatch):
    def no_call(*a):
        raise AssertionError("the model must not be called")
    monkeypatch.setattr(llm_client, "call_assessor", no_call)
    check = skillcheck.new_check()
    turn = skillcheck.answer(check, AI_ANSWERS[0], seconds=4)
    assert turn["attained"] == 0 and turn["ai_like"] and turn["seconds"] == 4
    d = skillcheck.summarize(check["turns"])
    assert d["ai_like"] == 1 and d["messages"][0].startswith("1 of your answers looked like it came from an AI chatbot")


def test_api_refuses_long_answers(monkeypatch, tmp_path):
    c = client(monkeypatch, tmp_path)
    cid = c.post("/api/check", json={}).json()["check_id"]
    r = c.post(f"/api/check/{cid}/answer", json={"answer": "word " * (skillcheck.MAX_WORDS + 1)})
    assert r.status_code == 400 and "under 100 words" in r.json()["detail"]
    ok = c.post(f"/api/check/{cid}/answer", json={"answer": HUMAN_ANSWERS[0], "seconds": 40})
    assert ok.status_code == 200 and main.SESSIONS[cid]["turns"][0]["seconds"] == 40


def test_ai_guard_switch(monkeypatch, tmp_path):
    from app import copycheck
    c = client(monkeypatch, tmp_path)
    monkeypatch.delenv("AI_GUARD", raising=False)
    assert c.get("/api/config").json()["ai_guard"] is True and copycheck.ai_reason(AI_ANSWERS[0])
    monkeypatch.setenv("AI_GUARD", "0")
    assert c.get("/api/config").json()["ai_guard"] is False and copycheck.ai_reason(AI_ANSWERS[0]) is None
    turn = skillcheck.answer(skillcheck.new_check(), AI_ANSWERS[0])
    assert turn["ai_like"] is None  # marked by the agents as usual
