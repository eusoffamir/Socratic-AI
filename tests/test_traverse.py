"""Goal 3, step 5: reasoning as moves on the knowledge graph."""
import json

from app import llm_client, orchestrator as orc, prompts
from app.traverse import agreement, clean_steps, read


def test_steps_keep_only_real_node_pairs():
    raw = [["count_500", "Many_Tries"], ["x", "coin"], ["coin", "coin"], "bad", ["count_500", "many_tries"],
           ["coin", "multiply"], ["multiply", "streak_chance"], ["streak_chance", "count_500"], ["a", "b", "c"]]
    assert clean_steps(raw, "pattern_or_luck") == [["count_500", "many_tries"], ["coin", "multiply"],
                                                   ["multiply", "streak_chance"], ["streak_chance", "count_500"]]
    assert clean_steps(None, "pattern_or_luck") == []


def test_forward_chain_is_deductive():
    # coin supports multiply supports streak_chance: a rule applied step by step.
    r = read("pattern_or_luck", [["coin", "multiply"], ["multiply", "streak_chance"]])
    assert [s["dir"] for s in r["steps"]] == ["forward", "forward"]
    assert r["types"] == {"inductive": 0, "deductive": 1, "abductive": 0}


def test_backward_step_is_abductive():
    # many_tries causes count_500. Seeing the count and going back to its cause is abduction.
    r = read("pattern_or_luck", [["count_500", "many_tries"]])
    assert r["steps"] == [{"from": "count_500", "to": "many_tries", "dir": "backward", "rel": "causes"}]
    assert r["types"] == {"inductive": 0, "deductive": 0, "abductive": 1}


def test_counted_data_or_many_into_one_is_inductive():
    # count_500 is counted by a simulation, so going on from it is inductive.
    assert read("pattern_or_luck", [["count_500", "not_proof"]])["types"]["inductive"] == 1
    # random_pairs and ice_cream both support luck_or_hidden: two cases, one idea.
    r = read("together_not_cause", [["ice_cream", "luck_or_hidden"], ["random_pairs", "luck_or_hidden"]])
    assert r["types"] == {"inductive": 1, "deductive": 0, "abductive": 0}


def test_jumps_show_no_type():
    r = read("pattern_or_luck", [["coin", "check_repeat"]])
    assert r["steps"][0]["dir"] == "jump" and r["types"] == {"inductive": 0, "deductive": 0, "abductive": 0}


def test_agreement_counts_only_answers_on_the_graph():
    def a(agent, steps):
        return {"reasoning": {"types": agent, "graph": read("pattern_or_luck", steps)}}
    both = a({"inductive": 0, "deductive": 0, "abductive": 1}, [["count_500", "many_tries"]])
    differ = a({"inductive": 0, "deductive": 1, "abductive": 0}, [["count_500", "many_tries"]])
    off = a({"inductive": 1, "deductive": 0, "abductive": 0}, [["coin", "check_repeat"]])
    out = agreement([both, differ, off, {"reasoning": None}])
    assert out == {"answers": 2, "agree": {"inductive": 2, "deductive": 1, "abductive": 1}}


def test_the_shared_call_sends_the_graph_and_reads_the_steps(monkeypatch):
    s = orc.new_session("pattern_or_luck", total_rounds=8)
    s["last_tutor"] = "Why might this streak be luck?"
    sent = json.loads(prompts.assessor_user(s, "x", with_reasoning=True))
    assert "many_tries" in sent["GRAPH"]["nodes"] and ["many_tries", "causes", "count_500"] in sent["GRAPH"]["links"]
    assert "GRAPH" not in json.loads(prompts.assessor_user(s, "x"))
    reply = {"standards": {}, "reasoning_types": {"abductive": 1}, "graph_steps": [["count_500", "many_tries"]]}
    monkeypatch.setattr(llm_client, "PROVIDER", "gemini")
    monkeypatch.setattr(llm_client, "_generate", lambda *a, **k: json.dumps(reply))
    out = llm_client.call_assessor(s, "15 of 500 streak, because there are so many stocks")
    assert out["reasoning"]["graph"]["types"]["abductive"] == 1
