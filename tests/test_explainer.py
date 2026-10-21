"""Explainer agent (Goal 1 step 6): cleaning, fallback, caching and the API."""
from fastapi.testclient import TestClient

from app import explainer, llm_client, main
from app.knowledge import KNOWLEDGE_TYPES
from app.reasoning import REASONING_TYPES

GOOD = {"why": "It matters — a lot!", "scenario": "A quant sees 15 streaks.", "steps": ["Count.", "Compare.", "Check.", "Extra."],
        "try": "What would you check?"}


def test_clean_tidies_and_rejects_bad_replies():
    c = explainer.clean(GOOD)
    assert c["why"] == "It matters, a lot." and len(c["steps"]) == 3 and c["source"] == "agent"
    assert explainer.clean({**GOOD, "steps": ["only one"]}) is None
    assert explainer.clean({**GOOD, "try": "No question mark"}) is None
    assert explainer.clean("not a dict") is None


def test_fallback_covers_every_pair_and_follows_the_rules():
    for r in REASONING_TYPES:
        for k in KNOWLEDGE_TYPES:
            f = explainer.fallback(r, [k])
            text = " ".join([f["why"], f["scenario"], *f["steps"], f["try"]])
            assert ":" not in text and "!" not in text and "—" not in text and f["try"].endswith("?")
            assert len(f["steps"]) == 2


def test_agent_reply_is_cached(monkeypatch):
    calls = []
    monkeypatch.setattr(llm_client, "PROVIDER", "gemini")
    monkeypatch.setattr(llm_client, "_generate", lambda *a, **k: calls.append(1) or __import__("json").dumps(GOOD))
    monkeypatch.setattr(explainer, "_cache", {})
    a = explainer.explain("abductive", ["causal", "factual"])
    b = explainer.explain("abductive", ["factual", "causal"])
    assert a == b and a["source"] == "agent" and a["knowledge"] == ["factual", "causal"] and len(calls) == 1


def test_failed_call_falls_back_and_is_not_cached(monkeypatch):
    monkeypatch.setattr(llm_client, "PROVIDER", "gemini")
    monkeypatch.setattr(llm_client, "_generate", lambda *a, **k: "not json")
    monkeypatch.setattr(explainer, "_cache", {})
    assert explainer.explain("inductive", ["causal"])["source"] == "fallback" and explainer._cache == {}


def test_background_comes_from_the_knowledge_graph():
    assert "BACKGROUND" in explainer.user_payload("deductive", ["procedural"])


def test_api(monkeypatch):
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    c = TestClient(main.app)
    r = c.get("/api/explain", params={"reasoning": "deductive", "knowledge": ["procedural"]})
    assert r.status_code == 200 and r.json()["source"] == "fallback"
    assert c.get("/api/explain", params={"reasoning": "guessing", "knowledge": ["causal"]}).status_code == 400
    assert c.get("/api/explain", params={"reasoning": "deductive",
                                         "knowledge": ["causal", "factual", "procedural"]}).status_code == 400


def test_overall_status_uses_the_saved_bank(monkeypatch):
    """Overall status mixes topics, so it shows the bank, with no model call."""
    assert len(explainer.all_mixes()) == 108
    assert explainer.bank_key("inductive", ["strategic", "factual"]) == "inductive|factual,strategic"
    saved = {"why": "Why.", "scenario": "A story.", "steps": ["One.", "Two."], "try": "What next?"}
    monkeypatch.setattr(explainer, "BANK", {"inductive|factual,strategic": saved})
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    c = TestClient(main.app)
    r = c.get("/api/explain", params={"reasoning": "inductive", "knowledge": ["strategic", "factual"], "general": 1}).json()
    assert r["source"] == "bank" and r["why"] == "Why."
    # not in the bank: the everyday fallback, not a quant story
    r = c.get("/api/explain", params={"reasoning": "inductive", "knowledge": ["causal"], "general": 1}).json()
    assert r["source"] == "fallback" and "stock" not in r["scenario"]
