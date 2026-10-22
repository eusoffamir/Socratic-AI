import copy

from app.content import CONCEPTS
from app.heuristics import TREES, problems, rules, walk
from app.knowledge import case_graph


def test_every_case_has_a_proper_tree_joined_to_its_graph():
    assert set(TREES) == set(CONCEPTS)
    for case_id, tree in TREES.items():
        assert problems(tree, case_graph(case_id)) == [], case_id


def test_text_follows_the_app_rules():
    for case_id, tree in TREES.items():
        for n in tree["nodes"]:
            assert not any(bad in n["text"] for bad in ("—", "--", "!", ":")), (case_id, n["id"])
            assert n["text"].endswith("?" if n["kind"] == "question" else "."), (case_id, n["id"])


def test_walk_reaches_the_decision_for_each_scenario():
    luck = walk("pattern_or_luck", {"q_beats_luck": "no"})
    assert luck["done"] and luck["at"] == "d_luck"
    assert walk("holds_on_new_data", {"q_tested": "No", "q_how_many": " yes "})["at"] == "d_luck"
    rain = walk("together_not_cause", {"q_reason": "no", "q_repeats_no_reason": "no"})
    assert rain["at"] == "d_do_not_buy"
    assert rain["path"] == [["q_reason", "no"], ["q_repeats_no_reason", "no"]]


def test_walk_stops_at_the_next_question_to_ask():
    first = walk("pattern_or_luck", {})
    assert first == {"path": [], "at": "q_beats_luck", "text": first["text"], "done": False}
    half = walk("pattern_or_luck", {"q_beats_luck": "yes", "q_repeats": "maybe"})
    assert half["at"] == "q_repeats" and not half["done"]


def test_rules_cover_every_decision_once():
    for case_id, tree in TREES.items():
        decisions = sorted(n["id"] for n in tree["nodes"] if n["kind"] == "decision")
        found = rules(case_id)
        assert sorted(r["then"] for r in found) == decisions, case_id
        for r in found:
            assert walk(case_id, dict(r["if"]))["at"] == r["then"], (case_id, r["then"])


def test_a_generated_case_can_carry_its_own_tree():
    tree = {"root": "q", "nodes": [{"id": "q", "kind": "question", "text": "Is it?"},
                                    {"id": "a", "kind": "decision", "text": "Yes."},
                                    {"id": "b", "kind": "decision", "text": "No."}],
            "edges": [["q", "yes", "a"], ["q", "no", "b"]]}
    assert problems(tree) == []
    assert walk({"id": "own", "heuristics": tree}, {"q": "no"})["at"] == "b"


def test_problems_catch_broken_trees():
    good = TREES["pattern_or_luck"]
    one_answer = copy.deepcopy(good)
    one_answer["edges"].remove(["q_repeats", "no", "d_faded"])
    assert any("q_repeats needs at least 2 answers" in p for p in problems(one_answer))
    assert any("d_faded" in p for p in problems(one_answer))  # now has no parent

    loop = copy.deepcopy(good)
    loop["edges"].append(["q_repeats", "maybe", "q_beats_luck"])
    assert any("q_beats_luck needs no parent" in p for p in problems(loop))

    branching_decision = copy.deepcopy(good)
    branching_decision["edges"].append(["d_luck", "yes", "d_faded"])
    assert any("d_luck is a decision" in p for p in problems(branching_decision))

    bad_why = copy.deepcopy(good)
    bad_why["nodes"][0]["why"] = "nowhere"
    assert problems(bad_why) == []
    assert problems(bad_why, case_graph("pattern_or_luck")) == ["q_beats_luck rests on an unknown knowledge node"]
