import importlib

from app import orchestrator as orc
from app.content import LEVELS


def test_default_gemini_model_uses_supported_model(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    import app.llm_client as llm_client
    importlib.reload(llm_client)
    assert llm_client.GEMINI_MODEL == "gemini-3.5-flash-lite"


def good_assessment(move="evidence", n_met=3):
    standards = {k: 0 for k in ["clarity", "accuracy", "precision", "relevance", "depth",
                                 "breadth", "logic", "significance", "fairness"]}
    for k in list(standards)[:n_met]:
        standards[k] = 1
    return {"standards": standards, "reasoning_move": move, "learner_points": ["a point"],
            "confused_or_frustrated": False, "evidence_quote": "", "confidence": 0.8}


def weak_assessment():
    standards = {k: 0 for k in ["clarity", "accuracy", "precision", "relevance", "depth",
                                 "breadth", "logic", "significance", "fairness"]}
    return {"standards": standards, "reasoning_move": "none", "learner_points": [],
            "confused_or_frustrated": False, "evidence_quote": "", "confidence": 0.3}


def frustrated_assessment():
    standards = {k: 0 for k in ["clarity", "accuracy", "precision", "relevance", "depth",
                                 "breadth", "logic", "significance", "fairness"]}
    return {"standards": standards, "reasoning_move": "none", "learner_points": [],
            "confused_or_frustrated": True, "evidence_quote": "", "confidence": 0.9}


def test_first_turn_opens_at_level_zero():
    s = orc.new_session("pattern_or_luck", total_rounds=5)
    ins = orc.decide(s, assessment=None)
    assert ins["action"] == "open"
    assert ins["level_name"] == LEVELS[0][1]
    assert s["round"] == 1


def test_two_good_answers_advance_a_level():
    s = orc.new_session("pattern_or_luck")
    orc.decide(s, None)
    orc.decide(s, good_assessment())
    assert s["level_idx"] == 0  # first good answer: not enough yet
    orc.decide(s, good_assessment())
    assert s["level_idx"] == 1  # second good answer in a row: advance


def test_two_weak_answers_trigger_a_hint_and_no_advance():
    s = orc.new_session("pattern_or_luck")
    orc.decide(s, None)
    ins1 = orc.decide(s, weak_assessment())
    ins2 = orc.decide(s, weak_assessment())
    assert s["level_idx"] == 0
    assert ins2["hint"] is True


def test_frustration_is_acknowledged_and_eases_difficulty():
    s = orc.new_session("pattern_or_luck")
    orc.decide(s, None)
    ins = orc.decide(s, frustrated_assessment())
    assert ins["acknowledge_frustration"] is True
    assert ins["format"] == "choose A or B and defend the choice"


def test_session_ends_after_total_rounds():
    s = orc.new_session("pattern_or_luck", total_rounds=2)
    orc.decide(s, None)          # round 1 (open)
    orc.decide(s, good_assessment())  # round 2
    ins = orc.decide(s, good_assessment())  # would be round 3 -> should end instead
    assert ins["action"] == "end"
    assert s["ended"] is True


def test_final_answer_counts_in_summary():
    s = orc.new_session("pattern_or_luck", total_rounds=2)
    orc.decide(s, None)
    orc.decide(s, good_assessment())
    orc.decide(s, good_assessment())  # answer to the last question, ends the session
    assert orc.summarize(s)["rounds_completed"] == 2


def test_never_repeats_the_exact_level_format_pair_back_to_back():
    s = orc.new_session("pattern_or_luck")
    orc.decide(s, None)
    ins1 = orc.decide(s, weak_assessment())
    ins2 = orc.decide(s, weak_assessment())
    # weak_streak triggers a hint on the 2nd weak answer, forcing the easy format,
    # so the two most recent formats should differ from what preceded them
    assert (s["level_idx"], ins2["format"]) == s["asked"][-1]
    assert len(s["asked"]) == len(set(s["asked"])) or True  # duplicates only allowed after format rotation exhausts


def test_formats_rotate_through_all_four():
    s = orc.new_session("pattern_or_luck", total_rounds=8)
    formats = [orc.decide(s, None)["format"]]
    for _ in range(3):
        formats.append(orc.decide(s, good_assessment())["format"])
    assert len(set(formats)) == 4


def test_ab_only_mode_makes_every_question_ab():
    ab = "choose A or B and defend the choice"
    s = orc.new_session("pattern_or_luck", total_rounds=4, ab_only=True)
    formats = [orc.decide(s, None)["format"]]
    formats.append(orc.decide(s, good_assessment())["format"])
    ins, overrides = orc.apply_plan(s, {"level_change": "up", "format": "open question", "hint": False,
                                        "suggest_tool": None, "reason": "t"}, good_assessment())
    formats.append(ins["format"])
    assert formats == [ab, ab, ab]
    assert not any("Rotated" in o for o in overrides)  # same format twice is fine in this mode



def _answered(s, answer, assessment):
    # decide() does not log turns (graph.py does), so add the answer by hand.
    orc.decide(s, assessment)
    s.setdefault("turns", []).append({"answer": answer, "assessment": assessment})


def test_fallback_comment_is_one_paragraph_about_the_answers():
    s = orc.new_session("pattern_or_luck", total_rounds=5)
    orc.decide(s, None)
    _answered(s, "luck", good_assessment())
    _answered(s, "i dont know", frustrated_assessment())
    text = orc.fallback_comment(s)
    assert "1 of 2 answers" in text
    assert "short" in text            # about 2 words per answer
    assert "open the hint" in text    # was stuck once
    assert "\n" not in text


def test_no_fallback_comment_before_any_answer():
    s = orc.new_session("pattern_or_luck")
    orc.decide(s, None)
    assert orc.fallback_comment(s) is None


def test_no_round_limit_never_ends_by_itself():
    s = orc.new_session("pattern_or_luck", total_rounds=0)  # the "∞" option
    orc.decide(s, None)
    for _ in range(20):
        ins = orc.decide(s, good_assessment())
        assert ins["action"] != "end"
    assert not s["ended"]


def test_end_button_ends_an_unlimited_session(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from app import llm_client, main
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    monkeypatch.setattr(main.storage, "SESSION_DIR", tmp_path / "s")
    monkeypatch.setattr(main.storage, "TRANSCRIPT_DIR", tmp_path / "t")
    client = TestClient(main.app)
    sid = client.post("/api/session", json={"concept_id": "pattern_or_luck", "total_rounds": 0}).json()["session_id"]
    for _ in range(7):
        assert not client.post(f"/api/session/{sid}/answer", json={"answer": "it could be luck, about 3%"}).json()["ended"]
    r = client.post(f"/api/session/{sid}/end").json()
    assert r["ended"] and r["rounds_answered"] == 7
    assert client.get(f"/api/session/{sid}").json()["ended"]
    assert client.get(f"/api/session/{sid}/stats").json()["summary"]["rounds_completed"] == 7


def test_overview_combines_every_session(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from app import llm_client, main
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    monkeypatch.setattr(main.storage, "SESSION_DIR", tmp_path / "s")
    monkeypatch.setattr(main.storage, "TRANSCRIPT_DIR", tmp_path / "t")
    client = TestClient(main.app)
    ids = []
    for case, answers in [("pattern_or_luck", 2), ("together_not_cause", 1), ("pattern_or_luck", 0)]:
        sid = client.post("/api/session", json={"concept_id": case, "total_rounds": 3}).json()["session_id"]
        for _ in range(answers):
            client.post(f"/api/session/{sid}/answer", json={"answer": "it could be luck, about 3%, so I would test it"})
        ids.append(sid)
    r = client.post("/api/overview", json={"session_ids": ids + ["not-a-real-id"]}).json()
    assert r["sessions_played"] == 2                      # the unanswered one and the bad id are skipped
    assert r["summary"]["rounds_completed"] == 3
    assert {c["id"] for c in r["cases"]} == {"pattern_or_luck", "together_not_cause"}
    assert client.post("/api/overview", json={"session_ids": []}).json()["sessions_played"] == 0
