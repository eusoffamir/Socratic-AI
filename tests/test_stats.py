"""Statistics (Goal 1 step 5): Hamming distance, the Beta-Binomial mastery estimate, and DINA."""
import random

import pytest

from app import stats
from tests.test_eval import _load

dina = _load("dina")


def test_hamming():
    assert stats.hamming([1, 0, 1, 1], [1, 1, 1, 0]) == 2
    assert stats.hamming("1010", "1010") == 0
    with pytest.raises(ValueError):
        stats.hamming([1], [1, 0])


def test_beta_estimate_matches_known_values():
    flat = stats.beta_estimate(0, 0)  # no answers: a flat prior
    assert flat["mean"] == 50 and flat["low"] == 5 and flat["high"] == 95 and flat["chance_mastered"] == 40
    strong = stats.beta_estimate(9, 10)  # Beta(10, 2), values checked with scipy.stats.beta
    assert strong == {"mean": 83, "low": 64, "high": 97, "chance_mastered": 97}


def test_verdicts():
    assert stats.verdict(2, 99) == "not enough answers"
    assert stats.verdict(10, 98) == "mastered"
    assert stats.verdict(10, 5) == "not mastered yet"
    assert stats.verdict(10, 50) == "not sure yet"


def _turn(r, k, a):
    return {"reasoning": r, "knowledge": k, "attained": a}


def test_mastery_pattern_distance_and_change():
    first = [_turn("inductive", "causal", 1), _turn("inductive", "factual", 1)]
    second = [_turn("inductive", "procedural", 1), _turn("inductive", "relational", 1), _turn("deductive", "causal", 0)]
    m = stats.mastery([first, second])
    rows = {r["skill"]: r for r in m["skills"]}
    assert rows["inductive"]["asked"] == 4 and rows["inductive"]["status"] == "mastered"
    assert rows["causal"]["asked"] == 2 and rows["causal"]["status"] == "not enough answers"
    assert m["pattern"][0] == 1 and m["distance"] == 7 and m["previous_distance"] == 8
    assert m["messages"][:2] == ["You have mastered 1 of 8 skills, so 7 are left.",
                                 "That is 1 more than before your last check."]


def test_dina_recovers_known_skills_on_a_small_case():
    # 3 skills and 6 questions: 3 need one skill, 3 need two
    q = {"a": 1, "b": 2, "c": 4, "ab": 3, "bc": 6, "ac": 5}
    truth, responses = dina.simulate(150, 6, q, 3, slip=0.05, guess=0.1, seed=3)
    model = dina.fit(responses, q, 3, iters=60)
    assert dina.accuracy(truth, model["skills"], 3) > 0.85
    assert all(v < 0.2 for v in model["slip"].values()) and all(v < 0.25 for v in model["guess"].values())


def test_q_matrix_tags_two_skills_per_question():
    q = dina.q_matrix()
    assert len(q) == 30 and all(bin(m).count("1") == 2 for m in q.values())


def test_export_checks_rows():
    exp = _load("export_checks")
    from app import skillcheck
    check = skillcheck.new_check()
    turn = {"item": check["items"][0], "reasoning": "inductive", "knowledge": "causal", "answer": "x",
            "attained": 1, "assessment": {"standards": {"clarity": 1},
                                          "reasoning": {"types": {"inductive": 1}, "knowledge": {"causal": 1}}}}
    check["turns"] = [turn]
    [row] = list(exp.rows_of("id1", check, "now"))
    assert set(row) == set(exp.COLUMNS)
    assert row["attained"] == 1 and row["clarity"] == 1 and row["shows_inductive"] == 1 and row["uses_causal"] == 1
    assert list(exp.rows_of("id2", {"turns": []}, "now")) == []  # a case session is not a check
