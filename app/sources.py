"""Sources for the Topic Builder (Goal 2, simple RAG). Plain code, plus one
small model call that names the articles.

Before the Builder writes cases on a topic, the app fetches 1 or 2 English
Wikipedia articles about it, and the Builder must take every fact from them.
The Tutor and Assessor only use the case notes, so grounding the notes grounds
the whole session. Wikipedia is free and needs no key.

Steps: a small model call names the best article titles (Wikipedia's own
search handles questions badly, for example "is coffee bad for you" found
"Kopi luwak"), each title is fetched with its redirects, and a disambiguation
page or a missing page falls back to the search. Any failure returns None, and
the Builder then writes from the model's own knowledge, as before.
"""
import json
import logging
import re

import httpx

from . import llm_client

API = "https://en.wikipedia.org/w/api.php"
# Wikimedia asks every app to name itself in the User-Agent.
HEADERS = {"User-Agent": "SocraticAI/1.0 (https://socratic-ai-qlk6.onrender.com; FYP project)"}
TIMEOUT_SECONDS = 8
MAX_ARTICLES = 2
MAX_CHARS = 12000  # all articles together, so the Builder call stays small
READING_CHARS = 400  # a request this long is the learner's own reading, so Wikipedia is not used

# Sections that are lists of links, not facts.
_SKIP_SECTIONS = {"see also", "references", "external links", "further reading", "notes", "bibliography",
                  "sources", "citations", "footnotes", "works cited", "gallery"}

TITLE_SYSTEM = """You help a tutor find reading for a topic. Name the English Wikipedia articles that best cover the REQUEST for a beginner: 1 article, or 2 when a second one adds the main idea (for example "Coffee" and "Health effects of coffee"). Give exact article titles as they appear on Wikipedia.
Reply with ONLY this JSON: {"titles": [""]}"""

log = logging.getLogger("socratic.sources")

# Words around a topic name that are not part of it ("i want to think about
# photosynthesis" is the topic "photosynthesis").
_FILLER = re.compile(r"^(i\s+(want|would like|wanna)\s+to\s+(think|learn|talk|know)\s+(about|more about)|"
                     r"(tell|teach)\s+me\s+about|let'?s\s+(think|talk)\s+about|think\s+about|about)\s+", re.I)
_QUESTION = re.compile(r"\?|^(why|how|what|when|where|who|which|is|are|do|does|can|should)\b", re.I)
DIRECT_WORDS = 5  # a topic name this short is tried as an article title first


def _get(params):
    r = httpx.get(API, params={**params, "format": "json", "formatversion": "2"}, headers=HEADERS,
                  timeout=TIMEOUT_SECONDS)
    r.raise_for_status()
    return r.json()


def clean_text(text):
    """The article text without its link lists, headings or empty lines."""
    out, skipping = [], False
    for line in text.splitlines():
        line = line.strip()
        heading = re.fullmatch(r"(=+)\s*(.*?)\s*\1", line)
        if heading:
            level, name = len(heading.group(1)), heading.group(2).lower()
            if level == 2:
                skipping = name in _SKIP_SECTIONS
            continue
        if line and not skipping:
            out.append(line)
    return "\n".join(out)


def _article(title):
    """{"title", "url", "text"} for a real article (after redirects), else None."""
    pages = _get({"action": "query", "titles": title, "prop": "extracts|pageprops|info", "explaintext": 1,
                  "inprop": "url", "redirects": 1, "ppprop": "disambiguation"})["query"].get("pages") or []
    page = pages[0] if pages else {}
    if page.get("missing") or "disambiguation" in (page.get("pageprops") or {}):
        return None
    text = clean_text(page.get("extract") or "")
    if len(text) < 500:  # a stub has too little to build cases from
        return None
    return {"title": page["title"], "url": page.get("fullurl") or "", "text": text}


def _search(request):
    hits = _get({"action": "query", "list": "search", "srsearch": request[:200], "srlimit": 3, "srprop": ""})
    return [h["title"] for h in hits["query"]["search"]]


def _titles(request):
    """Article titles named by a small model call. [] in mock mode or if it fails."""
    if llm_client.PROVIDER == "mock":
        return []
    try:
        data = llm_client._parse_json(llm_client._generate(
            TITLE_SYSTEM, json.dumps({"REQUEST": request[:300]}, ensure_ascii=False), max_tokens=100, json_mode=True,
            thinking="minimal"))  # a tiny job, so the least thinking
    except Exception as e:  # any model problem: the search below still runs
        log.warning("Naming articles failed: %s", e)
        return []
    titles = data.get("titles") if isinstance(data, dict) else None
    return [t.strip()[:120] for t in titles if isinstance(t, str) and t.strip()][:MAX_ARTICLES] if isinstance(titles, list) else []


def _direct(request):
    """The article whose title is the topic itself ("Photosynthesis", "The
    water cycle"), so no model call is needed. Seen 21 October 2026: the small
    title call alone took 7 to 38 seconds on the free tier, while a Wikipedia
    lookup takes under 1 second. Questions and longer requests still go to
    the model, because their words are not a title."""
    name = _FILLER.sub("", request.strip().rstrip(".!")).strip()
    if not name or _QUESTION.search(name) or len(name.split()) > DIRECT_WORDS:
        return None
    return _article(name)


def find(request):
    """{"kind": "wikipedia", "articles": [{"title", "url"}], "text"} for the
    topic, or None. A long request is the learner's own reading, so it is used
    as it is and nothing is fetched."""
    request = (request or "").strip()
    if len(request) >= READING_CHARS:
        return None
    try:
        direct = _direct(request)
        articles = [direct] if direct else []
        for title in [] if direct else _titles(request) or _search(request)[:MAX_ARTICLES]:
            a = _article(title)
            if a and a["title"] not in [x["title"] for x in articles]:
                articles.append(a)
        if not articles:  # the named titles did not exist: try the search once more
            for title in _search(request):
                if (a := _article(title)):
                    articles.append(a)
                    break
    except (httpx.HTTPError, KeyError, ValueError) as e:
        log.warning("Wikipedia failed, so the topic is built without a source: %s", e)
        return None
    if not articles:
        return None
    share = MAX_CHARS // len(articles)
    text = "\n\n".join(f"ARTICLE: {a['title']}\n{a['text'][:share]}" for a in articles)
    return {"kind": "wikipedia", "articles": [{"title": a["title"], "url": a["url"]} for a in articles], "text": text}
