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


def test_timeout_moves_to_the_next_model(fake):
    models = fake({"main": 504})
    assert llm_client._generate_gemini("s", "u", 50, False) == "reply from second"
    assert models.asked == ["main", "second"]


def test_busy_everywhere_gives_the_busy_message(fake):
    fake({"main": 429, "second": 503, "third": 503})
    with pytest.raises(llm_client.LLMError, match="used up or busy"):
        llm_client._generate_gemini("s", "u", 50, False)


def test_all_used_up_gives_the_quota_message(fake):
    fake({"main": 429, "second": 429, "third": 429})
    with pytest.raises(llm_client.LLMError, match="quota used up"):
        llm_client._generate_gemini("s", "u", 50, False)


def test_main_model_is_asked_once_more_when_all_are_busy(monkeypatch):
    monkeypatch.setattr(llm_client, "GEMINI_LAST_TRY_WAIT", 0)
    calls = []
    def call(model, user, config, last):
        calls.append(model)
        if len(calls) <= 2:
            raise llm_client._GeminiBusy(503)
        return type("R", (), {"text": "late reply"})()
    monkeypatch.setattr(llm_client, "GEMINI_MODEL", "main")
    monkeypatch.setattr(llm_client, "GEMINI_FALLBACK_MODELS", ["second"])
    monkeypatch.setattr(llm_client, "_gemini_resting", {})
    monkeypatch.setattr(llm_client, "_gemini_call", call)
    assert llm_client._generate_gemini("s", "u", 50, False) == "late reply"
    assert calls == ["main", "second", "main"]


def test_groq_answers_when_gemini_fails(monkeypatch):
    def gemini_down(*a, **k):
        raise llm_client.LLMError("The free Gemini models are used up or busy right now.")
    monkeypatch.setattr(llm_client, "PROVIDER", "gemini")
    monkeypatch.setattr(llm_client, "_generate_gemini", gemini_down)
    monkeypatch.setattr(llm_client, "_generate_groq", lambda *a, **k: (llm_client._note_model("groq:x"), "groq reply")[1])
    monkeypatch.setenv("GROQ_API_KEY", "test")
    used = llm_client.track_models()
    assert llm_client._generate("s", "u", 50) == "groq reply"
    assert used == ["groq:x"]


def test_without_a_groq_key_the_gemini_error_shows(monkeypatch):
    def gemini_down(*a, **k):
        raise llm_client.LLMError("Gemini busy")
    monkeypatch.setattr(llm_client, "PROVIDER", "gemini")
    monkeypatch.setattr(llm_client, "_generate_gemini", gemini_down)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    import pytest
    with pytest.raises(llm_client.LLMError, match="Gemini busy"):
        llm_client._generate("s", "u", 50)
