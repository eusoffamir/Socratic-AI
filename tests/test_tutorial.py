import pytest
from fastapi.testclient import TestClient

from app import llm_client, main, tutorial
from app.content import STANDARDS, TUTORIAL

FULL = ("I would test it on new days. 5 ups in a row is about a 3% chance, so it can be luck. "
        "But maybe there was news, so I would check that too.")


@pytest.fixture(autouse=True)
def mock_provider(monkeypatch):
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")


def test_every_round_covers_all_9_standards():
    for i, r in enumerate(TUTORIAL["rounds"]):
        met = [k for _, ks in r["answer"] for k in ks] + r.get("pick_standards", [])
        assert sorted(met) == sorted(STANDARDS), i


def test_code_check_full_answer_meets_all_9():
    a = tutorial.code_assess(FULL)
    assert sum(a["standards"].values()) == 9 and a["reasoning_move"] == "evidence"


def test_code_check_giving_up_meets_none():
    for text in ["", "idk", "i dont know", "no idea really honestly"]:
        a = tutorial.code_assess(text)
        assert sum(a["standards"].values()) == 0 and a["confused_or_frustrated"]


def test_code_check_whole_words_only():
    # "also" must not count as "so", "butter" not as "but"
    a = tutorial.code_assess("the stock price also went up like butter today")
    assert not a["standards"]["depth"] and not a["standards"]["fairness"]


def test_socrates_example_passes_code_check():
    text = " ".join(s for s, _ in TUTORIAL["rounds"][2]["answer"])
    assert sum(tutorial.code_assess(text)["standards"].values()) == 9


def test_round_2_pick_earns_accuracy():
    best = TUTORIAL["rounds"][1]["best"]
    assert sum(tutorial.example_assessment(1, best)["standards"].values()) == 9
    wrong = tutorial.example_assessment(1, 1 - best)["standards"]
    assert sum(wrong.values()) == 8 and not wrong["accuracy"]


def test_final_result_scores_and_level():
    best = TUTORIAL["rounds"][1]["best"]
    top = tutorial.final_result(best, FULL)
    assert top["total"] == top["max"] == 27 and top["stars"] == 3 and top["source"] == "code"
    assert top["level"] == "Evidence"  # the level of the last question asked, as in the cases
    low = tutorial.final_result(1 - best, "idk")
    assert low["rounds"] == [9, 8, 0] and low["stars"] == 1 and low["level"] == "Evidence"
    assert "17 of 27" in low["stats"]["comment"]


def test_assessor_failure_falls_back_to_code(monkeypatch):
    monkeypatch.setattr(llm_client, "PROVIDER", "gemini")
    def broken(*a, **k):
        raise llm_client.LLMError("down")
    monkeypatch.setattr(llm_client, "call_assessor", broken)
    assert tutorial.assess_answer(FULL)["source"] == "code"


def test_assessor_reply_is_cleaned(monkeypatch):
    monkeypatch.setattr(llm_client, "PROVIDER", "gemini")
    monkeypatch.setattr(llm_client, "call_assessor",
                        lambda s, a: {"standards": {"clarity": 1, "made_up": 1}, "reasoning_move": "dance"})
    a = tutorial.assess_answer(FULL)
    assert a["source"] == "assessor" and a["reasoning_move"] == "none"
    assert set(a["standards"]) == set(STANDARDS) and sum(a["standards"].values()) == 1


def test_tutorial_endpoints():
    client = TestClient(main.app)
    t = client.get("/api/tutorial").json()
    assert len(t["rounds"]) == 3 and t["max"] == 27 and len(t["levels"]) == 6 and len(t["standards"]) == 9
    r = client.post("/api/tutorial/score", json={"answer": FULL, "r2_pick": 0}).json()
    assert r["total"] == 27 and r["stats"]["summary"]["rounds_completed"] == 3


def test_copied_hint_scores_zero_and_is_called_out_first():
    hint = TUTORIAL["rounds"][2]["key_idea"]
    for answer in [hint, "I think " + hint.lower(), hint + " So I would wait."]:
        r = tutorial.final_result(0, answer)
        assert r["copied"] and r["rounds"][2] == 0
        assert r["stats"]["comment"].startswith("You copied the hint")


def test_own_answer_is_not_flagged_as_copied():
    assert tutorial.copied_share(FULL) < tutorial.COPY_LIMIT
    # using a few of the hint's words inside your own reasoning is fine
    own = "One streak is not enough for me, so I would test the stock on 20 new days and check the news too."
    assert not tutorial.final_result(0, own)["copied"]
