"""The Azure provider (Meeting 3, task 1), checked against a fake server, since the
UTP access has not arrived yet."""
import httpx
import pytest

from app import llm_client


class _Res:
    def __init__(self, code, data=None, text=""):
        self.status_code, self._data, self.text = code, data, text

    def json(self):
        return self._data


@pytest.fixture
def azure(monkeypatch):
    monkeypatch.setattr(llm_client, "PROVIDER", "azure")
    monkeypatch.setattr(llm_client, "AZURE_ENDPOINT", "https://utp.openai.azure.com")
    monkeypatch.setattr(llm_client, "AZURE_DEPLOYMENT", "gpt-test")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "k")
    monkeypatch.setattr(llm_client.time, "sleep", lambda s: None)
    calls = []

    def post(url, json, timeout, headers):
        calls.append({"url": url, "body": json, "headers": headers})
        return replies.pop(0)
    replies = []
    monkeypatch.setattr(httpx, "post", post)
    return calls, replies


def ok(text):
    return _Res(200, {"choices": [{"message": {"content": text}}]})


def test_classic_route(azure, monkeypatch):
    calls, replies = azure
    monkeypatch.setattr(llm_client, "AZURE_API_VERSION", "2024-10-21")
    replies.append(ok(' {"a": 1} '))
    used = llm_client.track_models()
    assert llm_client._generate("sys", "user", 100, json_mode=True, seed=7) == '{"a": 1}'
    c = calls[0]
    assert c["url"] == "https://utp.openai.azure.com/openai/deployments/gpt-test/chat/completions?api-version=2024-10-21"
    assert c["headers"] == {"api-key": "k"} and "model" not in c["body"]
    assert c["body"]["response_format"] == {"type": "json_object"} and c["body"]["seed"] == 7
    assert used == ["azure:gpt-test"]


def test_v1_route_puts_the_model_in_the_body(azure, monkeypatch):
    calls, replies = azure
    monkeypatch.setattr(llm_client, "AZURE_API_VERSION", "v1")
    replies.append(ok("hi"))
    llm_client._generate("s", "u", 50)
    assert calls[0]["url"].endswith("/openai/v1/chat/completions") and calls[0]["body"]["model"] == "gpt-test"


def test_busy_is_retried_then_errors_are_plain(azure):
    calls, replies = azure
    replies.extend([_Res(503), ok("back")])
    assert llm_client._generate("s", "u", 50) == "back" and len(calls) == 2
    replies.extend([_Res(429)] * 3)
    with pytest.raises(llm_client.LLMError, match="limit"):
        llm_client._generate("s", "u", 50)


def test_missing_settings(azure, monkeypatch):
    monkeypatch.setattr(llm_client, "AZURE_DEPLOYMENT", "")
    with pytest.raises(llm_client.LLMError, match="not set up"):
        llm_client._generate("s", "u", 50)
