"""Gemini model fallback: a used-up or busy model hands the call to the next one."""
import pytest
from google.genai import errors

from app import llm_client


class FakeModels:
    def __init__(self, codes):
        self.codes, self.asked = codes, []  # model -> error code, or missing for a reply

    def generate_content(self, model, contents, config):
        self.asked.append(model)
        if model in self.codes:
            raise errors.APIError(self.codes[model], {"error": {"message": "x"}})
        return type("R", (), {"text": f"reply from {model}", "candidates": []})()


@pytest.fixture
def fake(monkeypatch):
    def make(codes):
        models = FakeModels(codes)
        monkeypatch.setattr(llm_client, "_get_gemini", lambda: type("C", (), {"models": models})())
        monkeypatch.setattr(llm_client, "GEMINI_MODEL", "main")
        monkeypatch.setattr(llm_client, "GEMINI_FALLBACK_MODELS", ["second", "third"])
        monkeypatch.setattr(llm_client, "_gemini_resting", {})
        monkeypatch.setattr(llm_client.time, "sleep", lambda s: None)
        return models
    return make


def test_quota_moves_to_the_next_model(fake):
    models = fake({"main": 429})
    assert llm_client._generate_gemini("s", "u", 50, False) == "reply from second"
    # the used-up model rests, so the next call goes straight to the fallback
    assert llm_client._generate_gemini("s", "u", 50, False) == "reply from second"
    assert models.asked == ["main", "second", "second"]


def test_busy_and_missing_fallbacks_are_skipped(fake):
    models = fake({"main": 503, "second": 404})
    assert llm_client._generate_gemini("s", "u", 50, False) == "reply from third"
    assert models.asked == ["main", "main", "second", "third"]  # a busy model gets one quick retry


def test_busy_everywhere_gives_the_busy_message(fake):
    fake({"main": 429, "second": 503, "third": 503})
    with pytest.raises(llm_client.LLMError, match="overloaded"):
        llm_client._generate_gemini("s", "u", 50, False)


def test_all_used_up_gives_the_quota_message(fake):
    fake({"main": 429, "second": 429, "third": 429})
    with pytest.raises(llm_client.LLMError, match="quota used up"):
        llm_client._generate_gemini("s", "u", 50, False)
