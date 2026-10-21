"""Goal 2, simple RAG: the Builder writes cases from Wikipedia articles. No
real network here: Wikipedia and the model are faked."""
import copy

import httpx
import pytest

from app import builder, llm_client, sources

LONG = "A real fact about the topic. " * 40

PAGES = {
    "Sleep": {"title": "Sleep", "fullurl": "https://en.wikipedia.org/wiki/Sleep",
              "extract": f"{LONG}\n== History ==\n{LONG}\n== See also ==\nList of sleep things\n== References ==\n[1] A book"},
    "Mercury": {"title": "Mercury", "fullurl": "https://en.wikipedia.org/wiki/Mercury", "extract": "Mercury may refer to",
                "pageprops": {"disambiguation": ""}},
    "Mercury (planet)": {"title": "Mercury (planet)", "fullurl": "https://en.wikipedia.org/wiki/Mercury_(planet)", "extract": LONG},
    "Stub": {"title": "Stub", "fullurl": "https://en.wikipedia.org/wiki/Stub", "extract": "Too short."},
}


@pytest.fixture
def wiki(monkeypatch):
    searches = {"mercury": ["Mercury", "Mercury (planet)"], "nothing": []}
    def fake_get(params):
        if params.get("list") == "search":
            return {"query": {"search": [{"title": t} for t in searches.get(params["srsearch"].lower(), ["Sleep"])]}}
        page = PAGES.get(params["titles"], {"missing": True})
        return {"query": {"pages": [page]}}
    monkeypatch.setattr(sources, "_get", fake_get)
    monkeypatch.setattr(llm_client, "PROVIDER", "gemini")
    titles = []
    monkeypatch.setattr(sources, "_titles", lambda request: list(titles))
    return titles


def test_clean_text_drops_link_lists_and_headings():
    text = sources.clean_text(PAGES["Sleep"]["extract"])
    assert "A real fact" in text and "History" not in text
    assert "List of sleep things" not in text and "A book" not in text


def test_find_uses_the_named_titles(wiki):
    wiki += ["Sleep", "Stub"]  # the stub is too short, so it is left out
    found = sources.find("Why we need sleep")
    assert found["kind"] == "wikipedia" and found["articles"] == [{"title": "Sleep", "url": "https://en.wikipedia.org/wiki/Sleep"}]
    assert found["text"].startswith("ARTICLE: Sleep") and len(found["text"]) <= sources.MAX_CHARS + 100


def test_find_falls_back_to_the_search_and_skips_disambiguation(wiki):
    wiki += ["Nonexistent page"]
    assert sources.find("mercury")["articles"][0]["title"] == "Mercury (planet)"


def test_find_gives_none_for_readings_failures_and_no_hits(wiki, monkeypatch):
    assert sources.find("x " * sources.READING_CHARS) is None  # the learner's own reading
    assert sources.find("nothing") is None
    def down(params):
        raise httpx.ConnectError("offline")
    monkeypatch.setattr(sources, "_get", down)
    assert sources.find("Sleep") is None


def test_clean_source_only_keeps_wikipedia_links():
    good = {"kind": "wikipedia", "articles": [{"title": "Sleep", "url": "https://en.wikipedia.org/wiki/Sleep"}]}
    assert builder.clean_source(good) == good
    assert builder.clean_source({"kind": "wikipedia", "articles": [{"title": "x", "url": "javascript:alert(1)"}]}) is None
    assert builder.clean_source({"kind": "wikipedia", "articles": [{"title": "x", "url": "https://evil.com/wiki/x"}]}) is None
    assert builder.clean_source({"kind": "reading", "extra": 1}) == {"kind": "reading"}
    assert builder.clean_source("anything") is None


def test_build_sends_the_source_and_keeps_it_with_each_case(wiki, monkeypatch):
    from tests.test_builder import raw_case
    wiki += ["Sleep"]
    sent = {}
    def fake_generate(system, user, **kw):
        sent["user"] = user
        return "{}"
    monkeypatch.setattr(llm_client, "_generate", fake_generate)
    monkeypatch.setattr(llm_client, "_parse_json", lambda text: {"topic": "Sleep", "cases": [raw_case()]})
    builder._CACHE.clear()
    topic = builder.build("Why we need sleep")
    assert '"SOURCE"' in sent["user"] and "A real fact" in sent["user"]
    assert topic["source"]["articles"][0]["title"] == "Sleep" == topic["cases"][0]["source"]["articles"][0]["title"]
    case = topic["cases"][0]
    assert builder.recheck(copy.deepcopy(case))["source"] == case["source"]
    builder._CACHE.clear()
    assert builder.build("word " * 100)["source"] == {"kind": "reading"}  # a pasted reading is its own source
    builder._CACHE.clear()


def test_build_asks_once_more_after_a_broken_reply(wiki, monkeypatch):
    from tests.test_builder import raw_case
    replies = [None, {"topic": "Sleep", "cases": [raw_case()]}]
    calls = []
    monkeypatch.setattr(llm_client, "_generate", lambda *a, **k: calls.append(1) or "")
    monkeypatch.setattr(llm_client, "_parse_json", lambda text: replies[len(calls) - 1])
    builder._CACHE.clear()
    assert builder.build("Sleep")["topic"] == "Sleep" and len(calls) == 2
    builder._CACHE.clear()
    calls.clear()
    replies[:] = [{"refuse": "I cannot help with that."}, None]
    with pytest.raises(builder.TopicError, match="cannot help"):
        builder.build("something harmful")
    assert len(calls) == 1  # a refusal is not asked again
    builder._CACHE.clear()
