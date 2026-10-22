from app.content import CONCEPTS
from app.knowledge import RELATIONS, case_graph
from app.pgm import NETWORKS, chance, findings, graph, learn, model, order


def _percent(case_id, target, given):
    return next(f["percent"] for f in findings(case_id) if f["target"] == target and f["given"] == given)


def test_every_case_has_a_network_joined_to_its_graph():
    assert set(NETWORKS) == set(CONCEPTS)
    for case_id, net in NETWORKS.items():
        ids = {n["id"] for n in net["nodes"]}
        known = {n["id"] for n in case_graph(case_id)["nodes"]}
        assert all(n["why"] in known for n in net["nodes"]), case_id
        assert all(a in ids and b in ids and rel in RELATIONS for a, rel, b in net["edges"]), case_id
        assert order(net)[0] not in {b for _, _, b in net["edges"]}, case_id
        for ask in net["asks"]:
            assert ask["move"] in ("inductive", "deductive", "abductive")
            assert {ask["target"], *ask["given"]} <= ids


def test_learning_counts_the_data():
    net = {"nodes": [{"id": "a"}, {"id": "b"}], "edges": [["a", "causes", "b"]]}
    data = [{"a": True, "b": True}] * 8 + [{"a": True, "b": False}] * 2
    table = learn(net, data)
    assert table["a"][()] == 11 / 12
    assert table["b"][(True,)] == 9 / 12
    assert table["b"][(False,)] == 0.5  # never seen, so 50%


def test_chances_add_up_in_both_directions():
    for case_id, net in NETWORKS.items():
        table = model(case_id)
        for n in net["nodes"]:
            yes = chance(net, table, n["id"])
            assert 0 < yes < 1
        first = net["nodes"][0]["id"]
        assert abs(chance(net, table, first) - table[first][()]) < 1e-9


def test_the_lessons_of_each_case():
    # A streak alone leaves a real pattern unlikely, and a repeat makes it much more likely.
    assert _percent("pattern_or_luck", "streak", {"real": False}) == 3
    alone = _percent("pattern_or_luck", "real", {"streak": True})
    assert 2 < alone < 30 < _percent("pattern_or_luck", "real", {"streak": True, "repeats": True})
    # A great old result that fails on new data is no better than a random rule.
    assert _percent("holds_on_new_data", "edge", {"great_old": True, "wins_new": False}) <= 5
    # Ice cream and sunburns move together, but once the weather is known the link is gone.
    assert _percent("together_not_cause", "sunburn", {"ice_cream": True}) > _percent("together_not_cause", "sunburn", {}) + 10
    assert abs(_percent("together_not_cause", "sunburn", {"ice_cream": True, "hot": True})
               - _percent("together_not_cause", "sunburn", {"hot": True})) <= 2


def test_graph_has_the_shared_shape():
    g = graph("pattern_or_luck")
    assert g["edges"] == [["real", "causes", "streak"], ["real", "causes", "repeats"]]
    streak = next(n for n in g["nodes"] if n["id"] == "streak")
    assert streak["parents"] == ["real"] and len(streak["chances"]) == 2
    assert all(n["text"].endswith(".") for n in g["nodes"])
