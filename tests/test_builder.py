"""Goal 2: the Topic Builder makes cases for any topic, and a whole session
runs on a generated case with no quant content."""
import copy

import pytest
from fastapi.testclient import TestClient

from app import builder, limits, llm_client, main, orchestrator, prompts, reasoning
from app.knowledge import KNOWLEDGE_TYPES, RELATIONS, graph as knowledge_graph, types_in


@pytest.fixture(autouse=True)
def _mock(monkeypatch):
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    monkeypatch.setattr(limits, "DAILY_CALL_BUDGET", 0)
    builder._CACHE.clear()


def raw_case(**changes):
    case = {
        "title": "Does sugar cause hyperactivity?", "mission": "Test a common belief about sugar.", "tag": "Health",
        "scenario": "A parent sees children run wild at a party and says, \"The cake did it, sugar makes kids hyper.\"",
        "notes": [{"text": "Careful studies gave some children sugar and others none without telling anyone.", "type": "factual"},
                  {"text": "A blind test means nobody knows who got the real thing — so beliefs cannot change the result.", "type": "conceptual"},
                  {"text": "First give the two groups different drinks, then rate the behaviour.", "type": "procedural"},
                  {"text": "Parties are exciting, so excitement can cause the running around.", "type": "causal"},
                  {"text": "Expecting a result can change what parents notice.", "type": "metacognitive"}],
        "reading": {"idea": ["Many people believe sugar makes children hyper.", "Blind tests found no clear effect."],
                    "example": "Parents who were told their child had sugar rated the child as more hyper.",
                    "key_words": [["Blind test", "nobody knows who got what"]],
                    "think": "What else happens at a party besides cake?"},
        "more_knowledge": [{"id": "Rate", "text": "Then compare the ratings of both groups.", "type": "procedural"},
                           {"id": "lonely", "text": "Not linked to anything.", "type": "factual"},
                           {"id": "bad", "text": "A wrong type.", "type": "magic"}],
        "links": [["n1", "weakens", "n4"], ["n3", "then", "rate"], ["n4", "causes", "n5"], ["n2", "defines", "n1"],
                  ["n5", "supports", "nowhere"], ["n1", "likes", "n2"]],
    }
    case.update(changes)
    return case


def test_clean_case_has_the_quant_case_shape():
    case = builder.clean_case(raw_case(), "Sugar and children", "t0123456789-1")
    for key in ["title", "mission", "tag", "scenario", "notes", "reading", "topic"]:
        assert case[key]
    assert case["tool"] is None and case["generated"] is True
    assert len(case["notes"]) == builder.NOTES_PER_CASE
    assert "thing, so beliefs" in case["notes"][1]  # dash became a comma
    g = case["knowledge"]
    ids = [n["id"] for n in g["nodes"]]
    assert "rate" in ids and "lonely" not in ids and "bad" not in ids  # unlinked and badly typed facts are dropped
    assert all(n["type"] in KNOWLEDGE_TYPES for n in g["nodes"])
    assert all(a in ids and b in ids and rel in RELATIONS for a, rel, b in g["edges"])
    assert ["n1", "likes", "n2"] not in g["edges"]
    assert knowledge_graph(case)["nodes"][0]["text"] == case["notes"][0]
    assert {"factual", "conceptual", "procedural", "causal"} <= set(types_in(case))
    assert reasoning.note_types(case) == ["factual", "conceptual", "procedural", "causal", "metacognitive"]


def test_broken_cases_are_refused_or_dropped():
    with pytest.raises(builder.TopicError):
        builder.clean_case(raw_case(notes=[{"text": "Only one.", "type": "factual"}]), "x", "t0123456789-1")
    with pytest.raises(builder.TopicError):
        builder.clean_case(raw_case(scenario="word " * 80), "x", "t0123456789-1")
    topic = builder.clean_topic({"topic": "Sugar", "cases": [raw_case(), {"title": "broken"}]}, "sugar")
    assert len(topic["cases"]) == 1  # the good case is kept
    with pytest.raises(builder.TopicError, match="cannot help"):
        builder.clean_topic({"refuse": "I cannot help with that topic."}, "how to make a bomb")
    with pytest.raises(builder.TopicError):
        builder.clean_topic(None, "anything")


def test_recheck_accepts_its_own_cases_and_rejects_tampering():
    case = builder.clean_topic({"topic": "Sugar", "cases": [raw_case()]}, "sugar")["cases"][0]
    assert builder.recheck(copy.deepcopy(case)) == case
    bad = copy.deepcopy(case)
    bad["scenario"] = "word " * 200
    with pytest.raises(builder.TopicError):
        builder.recheck(bad)
    bad = copy.deepcopy(case)
    bad["id"] = "pattern_or_luck"
    with pytest.raises(builder.TopicError):
        builder.recheck(bad)


def test_build_is_cached_and_needs_a_topic(monkeypatch):
    first = builder.build("Photosynthesis")
    calls = []
    monkeypatch.setattr(builder, "_mock", lambda r: calls.append(r))
    assert builder.build("  photosynthesis ") is first and not calls
    with pytest.raises(builder.TopicError):
        builder.build(" ")
    assert len(first["cases"]) == builder.CASES_PER_TOPIC


def test_prompts_use_the_generated_case_and_no_quant_words():
    case = builder.clean_topic({"topic": "Sugar and children", "cases": [raw_case()]}, "sugar")["cases"][0]
    s = orchestrator.new_session(case["id"], 3)
    s["case"] = case
    s["last_tutor"] = "Why do you think so?"
    ins = {"action": "open", "round": 1, "total_rounds": 3}
    tutor = prompts.tutor_user(s, ins, None, None)
    assert "Sugar and children" in tutor and case["notes"][0] in tutor and '"case_tool": null' in tutor
    assert '"NOTE_TYPES"' in prompts.assessor_user(s, "an answer", with_reasoning=True)
    for system in (prompts.TUTOR_SYSTEM.split("Tools:")[0], prompts.COACH_SYSTEM):
        assert "quant" not in system.lower() and "finance" not in system.lower()
    assert orchestrator.case_tool(s) is None


def test_whole_session_on_any_topic_through_the_api(monkeypatch):
    c = TestClient(main.app)
    monkeypatch.setenv("STUDY_CODES", "")
    assert c.post("/api/topic", json={"text": ""}).status_code == 400
    topic = c.post("/api/topic", json={"text": "The French Revolution"}).json()
    assert len(topic["cases"]) == 3 and topic["cases"][0]["id"].startswith(topic["id"])
    case = topic["cases"][0]
    r = c.post("/api/session", json={"case": case, "total_rounds": 3})
    assert r.status_code == 200
    sid = r.json()["session_id"]
    for answer in ["Because the claim has no evidence, I would check the facts first.", "It could be wrong."]:
        assert c.post(f"/api/session/{sid}/answer", json={"answer": answer}).status_code == 200
    s = main.SESSIONS[sid]
    assert s["case"]["id"] == case["id"] == s["concept_id"]
    assert not any(t["tool_runs"] for t in s["turns"])  # a generated case has no simulation
    assert c.get(f"/api/session/{sid}").json()["case"]["title"] == case["title"]
    over = c.post("/api/overview", json={"session_ids": [sid]}).json()
    assert over["cases"][0]["title"] == case["title"]
    tampered = {**case, "id": "pattern_or_luck"}
    assert c.post("/api/session", json={"case": tampered}).status_code == 400



# ---------- step D: skill check and Explainer on any topic ----------

from app import explainer, skillcheck  # noqa: E402


def test_clean_items_needs_two_per_reasoning_type():
    ids = ["t0123456789-1", "t0123456789-2"]
    good = {"questions": [{"reasoning": r, "knowledge": k, "case": 2, "situation": "Some facts.", "question": "Why?"}
                          for r in ["inductive", "deductive", "abductive"] for k in ["factual", "causal"]]}
    good["questions"].append({"reasoning": "inductive", "knowledge": "factual", "situation": "Repeat.", "question": "Again?"})
    good["questions"].append({"reasoning": "magic", "knowledge": "factual", "situation": "x", "question": "x?"})
    items = builder.clean_items(good, "t0123456789", ids)
    assert len(items) == 6 and all(i["case"] == ids[1] for i in items.values())
    assert items["t0123456789:ind-fact"]["situation"] == "Some facts."  # the first of a repeated pair is kept
    with pytest.raises(builder.TopicError):
        builder.clean_items({"questions": good["questions"][:2]}, "t0123456789", ids)


def test_skill_check_on_any_topic_through_the_api(monkeypatch):
    monkeypatch.setenv("STUDY_CODES", "")
    c = TestClient(main.app)
    topic = c.post("/api/topic", json={"text": "Volcanoes"}).json()
    d = c.post("/api/check", json={"cases": topic["cases"]}).json()
    assert d["topic"] == topic["topic"] and topic["topic"] in d["question"]["situation"]
    assert d["question"]["case"] in [x["title"] for x in topic["cases"]]
    for _ in range(skillcheck.QUESTIONS_PER_CHECK):
        d = c.post(f"/api/check/{d['check_id']}/answer",
                   json={"answer": "Because the evidence shows a pattern, I would test it on new cases."}).json()
    assert d["ended"] and d["results"]["answers"] == skillcheck.QUESTIONS_PER_CHECK
    quant = c.post("/api/check", json={}).json()
    assert quant["topic"] is None and quant["question"]["id"] in skillcheck.ITEMS
    mixed = [topic["cases"][0], c.post("/api/topic", json={"text": "Rivers"}).json()["cases"][0]]
    assert c.post("/api/check", json={"cases": mixed}).status_code == 400


def test_explainer_uses_the_learners_topic():
    import json
    quant = json.loads(explainer.user_payload("deductive", ["procedural"]))
    mine = json.loads(explainer.user_payload("deductive", ["procedural"], "Volcanoes"))
    assert quant["BACKGROUND"] and not mine["BACKGROUND"] and mine["TOPIC"] == "Volcanoes"
    assert "quant" not in explainer.SYSTEM.lower()
    assert "stock" not in explainer.explain("inductive", ["causal"], "Volcanoes")["scenario"]


def test_every_picture_has_an_icon_on_the_page():
    import re
    from pathlib import Path
    page = Path(main.STATIC_DIR, "index.html").read_text(encoding="utf-8")
    block = page[page.index("const PICTURE_ICONS = {"):page.index("};", page.index("const PICTURE_ICONS = {"))]
    assert set(re.findall(r"^\s+(\w+): '", block, re.M)) == set(builder.PICTURES)
    assert builder.clean_case(raw_case(picture="Leaf"), "x", "t0123456789-1")["picture"] == "leaf"
    assert builder.clean_case(raw_case(picture="dragon"), "x", "t0123456789-1")["picture"] == "bulb"
