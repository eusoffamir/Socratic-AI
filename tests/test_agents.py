"""Tests for the agent parts: the guard on the Planner, JSON parsing, the
free code checks, and a full mock turn with each agent switched off."""
import pytest

from app import checker, graph, llm_client, orchestrator as orc
from app.content import FORMATS, STANDARDS
from tests.test_orchestrator import frustrated_assessment, good_assessment, weak_assessment

AB = FORMATS[-1]


def opened():
    s = orc.new_session("pattern_or_luck", total_rounds=8)
    orc.decide(s, None)
    return s


def plan(change="stay", fmt=FORMATS[1], **extra):
    return {"level_change": change, "format": fmt, "hint": False, "suggest_tool": None, "reason": "test", **extra}


# ---------- guard ----------

def test_guard_accepts_a_sensible_plan():
    s = opened()
    ins, overrides = orc.apply_plan(s, plan("up", FORMATS[2]), good_assessment())
    assert s["level_idx"] == 1 and ins["format"] == FORMATS[2] and overrides == []


def test_guard_frustration_wins_over_the_plan():
    s = opened()
    ins, overrides = orc.apply_plan(s, plan("up", FORMATS[2]), frustrated_assessment())
    assert s["level_idx"] == 0
    assert ins["format"] == AB and ins["acknowledge_frustration"] and ins["hint"]
    assert len(overrides) == 2


def test_guard_blocks_moving_up_after_a_weak_answer():
    s = opened()
    orc.apply_plan(s, plan("up"), weak_assessment())
    assert s["level_idx"] == 0


def test_guard_blocks_same_format_twice():
    s = opened()
    ins, overrides = orc.apply_plan(s, plan("stay", s["last_format"]), good_assessment())
    assert ins["format"] != FORMATS[0] and overrides


def test_guard_falls_back_to_rules_on_bad_plan():
    s = opened()
    ins, overrides = orc.apply_plan(s, {"level_change": "jump to the top"}, good_assessment())
    assert ins["action"] == "continue" and "fixed rules" in overrides[0]
    ins, _ = orc.apply_plan(s, None, good_assessment())
    assert ins["action"] == "continue"


def test_guard_drops_unknown_tools_and_ends_on_time():
    s = orc.new_session("pattern_or_luck", total_rounds=2)
    orc.decide(s, None)
    ins, _ = orc.apply_plan(s, plan(suggest_tool="rm_rf"), good_assessment())
    assert ins["suggest_tool"] is None
    ins, _ = orc.apply_plan(s, plan(), good_assessment())
    assert ins["action"] == "end"


def test_profile_keeps_the_highest_level_after_moving_down():
    # Audit, 15 Oct 2026: a learner who reached Evidence and then got stuck was
    # moved down by the Planner, and the profile said "You reached Assumptions".
    s = opened()
    orc.apply_plan(s, plan("up", FORMATS[1]), good_assessment())
    orc.apply_plan(s, plan("up", FORMATS[2]), good_assessment())
    assert s["level_idx"] == 2
    orc.apply_plan(s, plan("down", AB), frustrated_assessment())
    assert s["level_idx"] == 1  # the teaching still moves down to help
    assert orc.summarize(s)["highest_level_reached"] == "Evidence"


def test_old_saved_sessions_without_best_level_still_work():
    s = opened()
    s["level_idx"] = 3
    del s["best_level_idx"]
    assert orc.summarize(s)["highest_level_reached"] == "Viewpoints"


# ---------- parsing ----------

def test_parse_json_handles_fences_and_prose():
    assert llm_client._parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert llm_client._parse_json("Sure! {\"a\": 1} hope this helps") == {"a": 1}
    assert llm_client._parse_json("no json here") is None


def test_clean_parts_keeps_options_only_for_ab():
    data = {"question": "Which?", "options": ["A) Luck", "B) Pattern", "C) extra"]}
    assert llm_client.clean_parts(data, {"format": AB})["options"] == ["Luck", "Pattern"]
    assert llm_client.clean_parts(data, {"format": FORMATS[0]})["options"] == []


def test_clean_assessment_gives_a_safe_shape():
    # A messy Assessor reply: odd key names, scores as text, missing fields.
    messy = {"standards": {"Clarity ": "1", "depth": True, "logic": "0", "made_up": 1, "accuracy": 0.0},
             "reasoning_move": "Evidence", "learner_points": "only one point"}
    a = llm_client.clean_assessment(messy)
    assert a["standards"] == {k: int(k in ("clarity", "depth")) for k in STANDARDS}
    assert a["reasoning_move"] == "evidence"
    assert a["confused_or_frustrated"] is False and a["learner_points"] == ["only one point"]
    # The cleaned reply works everywhere the session uses it.
    s = opened()
    orc.apply_plan(s, plan(), a)
    assert orc.summarize(s)["standards_met_count"]["clarity"] == 1
    assert llm_client.clean_assessment({"standards": {}, "reasoning_move": "guessing"})["reasoning_move"] == "none"


# ---------- free code checks ----------

def test_code_check():
    ok = {"feedback": "You used 1 in 32.", "key_idea": "Streaks happen.", "question": "Why?", "options": []}
    assert checker.code_check(ok, {"format": FORMATS[0]}, []) == []
    assert checker.code_check({**ok, "question": "Why? How?"}, {"format": FORMATS[0]}, [])
    assert checker.code_check(ok, {"format": FORMATS[0]}, ["why"])  # repeat
    assert checker.code_check(ok, {"format": AB}, [])  # missing options
    assert checker.code_check({**ok, "key_idea": "word " * 40}, {"format": FORMATS[0]}, [])


def test_tutor_asking_for_a_tool_with_none_left_is_asked_again(monkeypatch):
    # Without this, a tool request with no tools left became an empty question card.
    monkeypatch.setattr(llm_client, "PROVIDER", "gemini")
    replies = iter(['{"tool": "simulate_streaks", "args": {}}',
                    '{"feedback": "You gave a reason.", "key_idea": "Luck is common.", "question": "Why?"}'])
    monkeypatch.setattr(llm_client, "_generate", lambda *a, **k: next(replies))
    s = opened()
    ins = orc.decide(s, good_assessment())
    parts, runs = llm_client.call_tutor(s, ins, "luck", good_assessment(), use_tools=False)
    assert parts["question"] == "Why?" and runs == []


# ---------- whole turns in mock mode ----------

@pytest.mark.parametrize("off", [None, "AGENT_PLANNER", "AGENT_TOOLS", "AGENT_CHECKER"])
def test_full_session_with_each_agent_off(monkeypatch, off):
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    if off:
        monkeypatch.setenv(off, "0")
    s = orc.new_session("pattern_or_luck", total_rounds=3)
    r = graph.run_turn(s, None)
    for answer in ["about 1 in 32, so streaks are rare", "idk", "test it on new data"]:
        r = graph.run_turn(r["session"], answer)
    assert r["session"]["ended"] and len(r["session"]["turns"]) == 4
    used_tool = any(t["tool_runs"] for t in r["session"]["turns"])
    assert used_tool == (off not in ("AGENT_PLANNER", "AGENT_TOOLS"))


def test_planner_suggested_tool_is_run_by_code_once_per_session(monkeypatch):
    # Seen 15 Oct 2026: the Planner suggested simulate_streaks, the Tutor ignored it.
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    monkeypatch.setattr(llm_client, "call_planner", lambda *a: plan(suggest_tool="simulate_streaks"))
    seen = []
    def tutor(session, ins, answer, assessment, **k):
        seen.append(k["tool_runs"])
        return {"feedback": "", "key_idea": "", "question": f"Q{len(seen)}?", "options": ["X", "Y"]}, k["tool_runs"]
    monkeypatch.setattr(llm_client, "call_tutor", tutor)
    s = graph.run_turn(orc.new_session("pattern_or_luck", total_rounds=8), None)["session"]
    s = graph.run_turn(s, "it could be luck because many stocks rise")["session"]
    assert [r["tool"] for r in seen[-1]] == ["simulate_streaks"] and seen[-1][0]["run_by"] == "planner"
    graph.run_turn(s, "so a streak is not proof of a pattern")
    assert seen[-1] in (None, [])  # already run once this session: not again


@pytest.mark.parametrize("rounds, expected", [(6, "We have 6 rounds"), (0, "no round limit")])
def test_welcome_line_is_written_by_code(monkeypatch, rounds, expected):
    # Seen 15 Oct 2026: a 6-round session got the no-limit welcome from the Tutor.
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    r = graph.run_turn(orc.new_session("pattern_or_luck", total_rounds=rounds), None)
    assert expected in r["parts"]["feedback"]


def test_checker_triggers_one_rewrite(monkeypatch):
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    calls = []
    monkeypatch.setattr(llm_client, "call_checker", lambda *a: calls.append(1) or ["Gives the answer away."])
    s = orc.new_session("pattern_or_luck", total_rounds=3)
    s = graph.run_turn(s, None)["session"]
    calls.clear()  # the opening turn is checked too; count only the answer turn
    r = graph.run_turn(s, "it is luck because of many stocks")
    assert r["trace"]["rewrites"] == 1 and len(calls) == 2
    assert r["trace"]["shipped_with_problems"]  # still failing after 1 rewrite: shipped and logged


def test_rewrite_that_drops_ab_options_falls_back_to_first_draft(monkeypatch):
    # Seen with real Gemini (7 Oct 2026): the first A/B draft had 2 options, the
    # Checker asked for a wording fix, and the rewrite came back with no options.
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    monkeypatch.setenv("AGENT_PLANNER", "0")  # fixed rules: "idk" -> A/B format
    good = {"feedback": "I hear you.", "key_idea": "5 ups = 1/32.", "question": "Pattern or luck: which, and why?",
            "options": ["Real pattern", "Just luck"]}
    broken = {**good, "question": "What does 1/32 mean to you?", "options": []}
    drafts = iter([good, broken])
    monkeypatch.setattr(llm_client, "call_tutor", lambda *a, **k: (next(drafts), []))
    monkeypatch.setattr(llm_client, "call_checker", lambda *a: ["Question does not match the level."])
    s = orc.new_session("pattern_or_luck", total_rounds=3)
    orc.decide(s, None)  # open the session without a model call
    s["questions"].append("opening question?")
    r = graph.run_turn(s, "idk")
    assert r["instruction"]["format"] == AB
    assert r["parts"]["options"] == ["Real pattern", "Just luck"]
    assert r["trace"]["check"]["reverted_to_first_draft"] is True


def test_ab_only_session_shows_options_every_turn(monkeypatch):
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    s = orc.new_session("pattern_or_luck", total_rounds=3, ab_only=True)
    r = graph.run_turn(s, None)
    options = [r["parts"]["options"]]
    for answer in ["A: Real pattern. Why: 1/32 is rare", "B: Just luck. Why: many stocks"]:
        r = graph.run_turn(r["session"], answer)
        options.append(r["parts"]["options"])
    assert all(len(o) == 2 for o in options)


# ---------- reading pop-up ----------

def test_every_case_has_a_full_reading():
    from app.content import CONCEPTS
    for cid, c in CONCEPTS.items():
        r = c["reading"]
        assert r["idea"] and r["example"] and r["think"], cid
        assert all(len(kw) == 2 for kw in r["key_words"]), cid


def test_reading_seconds_is_saved_in_the_transcript(monkeypatch, tmp_path):
    import json
    from fastapi.testclient import TestClient
    from app import main
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    monkeypatch.setattr(main.storage, "TRANSCRIPT_DIR", tmp_path)
    monkeypatch.setattr(main.storage, "SESSION_DIR", tmp_path / "sessions")
    client = TestClient(main.app)
    assert "reading" in client.get("/api/concepts").json()[0]
    sid = client.post("/api/session", json={"concept_id": "pattern_or_luck", "reading_seconds": 42}).json()["session_id"]
    line = json.loads((tmp_path / f"{sid}.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert line["reading_seconds"] == 42
    sid = client.post("/api/session", json={"concept_id": "pattern_or_luck", "reading_seconds": 999999}).json()["session_id"]
    line = json.loads((tmp_path / f"{sid}.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert line["reading_seconds"] == 3600  # capped


# ---------- saved progress ----------

def _client(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from app import main
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    monkeypatch.setattr(main.storage, "TRANSCRIPT_DIR", tmp_path / "transcripts")
    monkeypatch.setattr(main.storage, "SESSION_DIR", tmp_path / "sessions")
    return main, TestClient(main.app)


def test_very_long_answer_is_cut(monkeypatch, tmp_path):
    main, client = _client(monkeypatch, tmp_path)
    sid = client.post("/api/session", json={"concept_id": "pattern_or_luck"}).json()["session_id"]
    assert client.post(f"/api/session/{sid}/answer", json={"answer": "luck " * 2000}).status_code == 200
    assert len(main.SESSIONS[sid]["turns"][-1]["answer"]) == main.MAX_ANSWER_CHARS


def test_session_survives_a_server_restart(monkeypatch, tmp_path):
    main, client = _client(monkeypatch, tmp_path)
    sid = client.post("/api/session", json={"concept_id": "pattern_or_luck", "total_rounds": 4}).json()["session_id"]
    client.post(f"/api/session/{sid}/answer", json={"answer": "5 ups is 1/32, so it could be luck"})
    assert (tmp_path / "sessions" / f"{sid}.json").exists()
    main.SESSIONS.clear()  # like restarting the server
    r = client.post(f"/api/session/{sid}/answer", json={"answer": "we need more data on new days"})
    assert r.status_code == 200 and r.json()["round"] == 3


def test_get_session_rebuilds_the_chat(monkeypatch, tmp_path):
    main, client = _client(monkeypatch, tmp_path)
    sid = client.post("/api/session", json={"concept_id": "holds_on_new_data", "ab_only": True}).json()["session_id"]
    client.post(f"/api/session/{sid}/answer", json={"answer": "A: Real pattern. Why: it made money"})
    main.SESSIONS.clear()
    data = client.get(f"/api/session/{sid}").json()
    assert data["concept_id"] == "holds_on_new_data" and data["round"] == 2 and not data["ended"]
    assert data["ab_only"] is True
    assert [t["answer"] for t in data["turns"]] == [None, "A: Real pattern. Why: it made money"]
    assert all(t["parts"]["question"] for t in data["turns"])
    assert len(data["turns"][-1]["parts"]["options"]) == 2


def test_unknown_or_bad_session_id_is_404(monkeypatch, tmp_path):
    _, client = _client(monkeypatch, tmp_path)
    assert client.get("/api/session/00000000-0000-0000-0000-000000000000").status_code == 404
    assert client.get("/api/session/..%2F..%2Fapp%2Fmain").status_code == 404
    assert client.post("/api/session/not-a-uuid/answer", json={"answer": "x"}).status_code == 404


def test_copied_hint_in_a_real_case_is_called_out(monkeypatch):
    from app import copycheck
    from app.content import CONCEPTS
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    called = []
    monkeypatch.setattr(llm_client, "call_assessor", lambda *a: called.append(1) or {})
    s = orc.new_session("pattern_or_luck", total_rounds=3)
    graph.run_turn(s, None)
    hint = s["turns"][-1]["parts"]["key_idea"] or CONCEPTS["pattern_or_luck"]["notes"][0]
    r = graph.run_turn(s, hint)
    assert r["assessment"]["copied_hint"] and sum(r["assessment"]["standards"].values()) == 0
    assert not called                           # the Assessor is skipped
    assert "copied" in r["parts"]["feedback"]   # the Tutor calls it out
    assert orc.fallback_comment(s).startswith("You copied the hint")


def test_own_answer_in_a_real_case_is_not_flagged():
    from app import copycheck
    s = orc.new_session("pattern_or_luck")
    own = "I think it could be luck, because many stocks go up for a few days, so I would test it on new days."
    assert not copycheck.is_copied(own, copycheck.session_sources(s), copycheck.session_story(s))


# Honest answers that repeat short facts from the case (found in the audit of
# 14 October 2026: they used to be flagged as copied and scored 0).
@pytest.mark.parametrize("own", [
    "The stock went up 5 days in a row, so my friend thinks it is a pattern",
    "It went up 5 days in a row but that could be luck",
    "My friend means a stock went up 5 days in a row, so it will keep going up",
    "A stock went up 5 days in a row",
])
def test_repeating_case_facts_is_not_copying(own):
    from app import copycheck
    s = orc.new_session("pattern_or_luck")
    assert not copycheck.is_copied(own, copycheck.session_sources(s), copycheck.session_story(s))


@pytest.mark.parametrize("cid", ["pattern_or_luck", "holds_on_new_data", "together_not_cause"])
def test_pasting_a_note_or_reading_line_is_still_copying(cid):
    from app import copycheck
    from app.content import CONCEPTS
    s = orc.new_session(cid)
    c = CONCEPTS[cid]
    for pasted in [*c["notes"], *c["reading"]["idea"]]:
        if len(pasted.split()) >= copycheck.RUN:  # a line shorter than one run cannot be caught
            assert copycheck.is_copied(pasted, copycheck.session_sources(s), copycheck.session_story(s)), pasted
