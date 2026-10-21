from app.content import CONCEPTS
from app.knowledge import KNOWLEDGE, KNOWLEDGE_TYPES, RELATIONS, graph, types_in


def test_every_case_has_a_graph():
    assert set(KNOWLEDGE) == set(CONCEPTS)


def test_nodes_have_known_types_and_unique_ids():
    for case_id, g in KNOWLEDGE.items():
        ids = [n["id"] for n in g["nodes"]]
        assert len(ids) == len(set(ids)), case_id
        for n in g["nodes"]:
            assert n["type"] in KNOWLEDGE_TYPES, (case_id, n["id"])
            assert ("note" in n) != ("text" in n), (case_id, n["id"])


def test_every_note_is_a_node_once():
    for case_id, g in KNOWLEDGE.items():
        notes = sorted(n["note"] for n in g["nodes"] if "note" in n)
        assert notes == list(range(len(CONCEPTS[case_id]["notes"]))), case_id


def test_edges_join_real_nodes_with_known_relations():
    for case_id, g in KNOWLEDGE.items():
        ids = {n["id"] for n in g["nodes"]}
        for a, rel, b in g["edges"]:
            assert a in ids and b in ids and a != b, (case_id, a, b)
            assert rel in RELATIONS, (case_id, rel)


def test_every_node_is_linked():
    for case_id, g in KNOWLEDGE.items():
        linked = {x for a, _, b in g["edges"] for x in (a, b)}
        assert linked == {n["id"] for n in g["nodes"]}, case_id


def test_graph_fills_note_text():
    g = graph("pattern_or_luck")
    assert g["nodes"][0]["text"] == CONCEPTS["pattern_or_luck"]["notes"][0]
    assert all(n["text"] for n in g["nodes"])


def test_each_case_covers_the_main_knowledge_types():
    for case_id in KNOWLEDGE:
        assert {"factual", "conceptual", "procedural", "causal"} <= set(types_in(case_id)), case_id


# ---------- Reasoning agent (step 2) ----------

from app import copycheck, llm_client, orchestrator as orc, prompts, reasoning  # noqa: E402


def test_reasoning_prompt_and_json_list_every_type():
    for k in [*reasoning.REASONING_TYPES, *KNOWLEDGE_TYPES]:
        assert f'"{k}": 0' in prompts.ASSESSOR_REASONING_SYSTEM
        assert f'"{k}": 0' not in prompts.ASSESSOR_SYSTEM.split("Return ONLY")[1]
    assert prompts.ASSESSOR_REASONING_SYSTEM.startswith(prompts.ASSESSOR_SYSTEM.split("Return ONLY")[0])


def test_note_types_follow_the_notes():
    for case_id in KNOWLEDGE:
        assert len(reasoning.note_types(case_id)) == len(CONCEPTS[case_id]["notes"])


def test_clean_reasoning_gives_a_safe_shape():
    messy = {"reasoning_types": {"Inductive ": "1", "abductive": True, "guessing": 1},
             "knowledge_used": "causal", "reasoning_evidence": None}
    r = reasoning.clean(messy)
    assert r["types"] == {"inductive": 1, "deductive": 0, "abductive": 1}
    assert set(r["knowledge"]) == set(KNOWLEDGE_TYPES) and sum(r["knowledge"].values()) == 0
    assert r["evidence"] == ""


def test_mock_marks_short_answers_as_nothing():
    assert reasoning.mock("idk") == reasoning.empty()
    r = reasoning.mock("Many stocks do this, so it is probably luck because of the 500 stocks")
    assert r["types"] == {"inductive": 1, "deductive": 1, "abductive": 1}
    assert r["knowledge"]["causal"] == 1 and r["knowledge"]["factual"] == 1


def test_assessor_adds_reasoning_and_can_be_switched_off(monkeypatch):
    s = orc.new_session("pattern_or_luck", total_rounds=8)
    s["last_tutor"] = "Why might this streak be luck?"
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    assert set(llm_client.call_assessor(s, "Many stocks do this by luck")["reasoning"]) == {"types", "knowledge", "evidence"}
    assert "NOTE_TYPES" in prompts.assessor_user(s, "x", with_reasoning=True)
    monkeypatch.setenv("AGENT_REASONING", "0")
    assert llm_client.call_assessor(s, "Many stocks do this by luck")["reasoning"] is None
    assert copycheck.copied_assessment()["reasoning"] is None
    monkeypatch.delenv("AGENT_REASONING")
    assert copycheck.copied_assessment()["reasoning"] == reasoning.empty()


# ---------- dashboard counts (step 3) ----------

def _marked(types, knowledge, met=3):
    std = {k: int(i < met) for i, k in enumerate(llm_client.STANDARDS)}
    return {"standards": std, "reasoning_move": "none", "reasoning": {"types": {r: int(r in types) for r in reasoning.REASONING_TYPES},
                                            "knowledge": {k: int(k in knowledge) for k in KNOWLEDGE_TYPES},
                                            "evidence": ""}}


def test_summarize_counts_pairs_and_quality():
    old = {"standards": {k: 1 for k in llm_client.STANDARDS}, "reasoning_move": "none"}  # saved before step 2
    d = reasoning.summarize([_marked(["deductive"], ["procedural", "causal"], met=4),
                             _marked(["deductive", "abductive"], ["causal"], met=2), old, None])
    assert d["answers"] == 2
    assert d["grid"]["causal"] == {"inductive": 0, "deductive": 2, "abductive": 1}
    assert d["grid"]["procedural"]["deductive"] == 1
    assert d["quality"] == {"inductive": None, "deductive": 3.0, "abductive": 2.0}
    assert d["messages"] == ["You used deductive reasoning on causal knowledge most often.",
                             "You have not shown inductive reasoning on procedural knowledge yet."]
    assert reasoning.summarize([])["messages"] == []


def test_session_summary_includes_reasoning():
    s = orc.new_session("pattern_or_luck", total_rounds=8)
    s["history"] = [{"assessment": _marked(["inductive"], ["factual"])}]
    assert orc.summarize(s)["reasoning"]["grid"]["factual"]["inductive"] == 1
