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
