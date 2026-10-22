"""Topic Builder agent (Goal 2: the same tutor works on any topic).

The learner types any topic, or pastes a short reading, and one model call
writes 3 cases in the same shape as the quant cases in content.py: a story,
5 notes, a reading pop-up and a small knowledge graph per case. Plain code
then checks the shape, so the rest of the app can trust it. A generated case
has no simulation tool, and it is kept inside each session that uses it.

Generated cases are a DRAFT: no expert has checked them, so the page says so.
"""
import hashlib
import json
import re
import threading

from . import limits, llm_client, sources
from .knowledge import KNOWLEDGE_TYPES, RELATIONS
from .llm_client import LLMError
from .reasoning import CORE_KNOWLEDGE, KNOWLEDGE_SIGNS, REASONING_TYPES

MAX_REQUEST_CHARS = 4000  # a topic name or a short reading
CASES_PER_TOPIC = 3
NOTES_PER_CASE = 5
MAX_AVOID = 30  # earlier case titles sent with a request for one more case

# The picture of a generated case is one of these icons, drawn by the page
# (PICTURE_ICONS in static/index.html), so no image is generated or paid for.
PICTURES = {
    "leaf": "plants, nature, farming", "sun": "light, energy, weather, summer", "water": "water, rain, rivers, drinks",
    "fire": "fire, heat, burning, energy use", "globe": "the world, countries, climate, travel",
    "heart": "the body, health, feelings, care", "atom": "physics, chemistry, matter",
    "scales": "law, justice, fairness, ethics", "columns": "history, government, old empires",
    "book": "reading, language, learning, stories", "people": "society, groups, families, culture",
    "chart": "data, statistics, economics, growth", "coin": "money, prices, trade, business",
    "flask": "experiments, science labs, medicine making", "gear": "engineering, machines, technology",
    "shield": "safety, defence, immunity, security", "crown": "kings, power, rulers, war",
    "clock": "time, habits, schedules, ageing", "bulb": "ideas, the mind, inventions, thinking",
    "moon": "sleep, night, space, the sky", "mountain": "geography, the earth, volcanoes, climbing",
    "virus": "germs, disease, cells, biology", "music": "music, art, sound, creativity",
    "apple": "food, eating, diet, cooking",
}

# Word limits for each part, a little above what the prompt asks, so one extra
# word does not throw a whole topic away.
WORDS = {"topic": 12, "title": 6, "mission": 12, "tag": 2, "scenario": 45, "note": 35,
         "idea": 35, "example": 40, "think": 30, "question": 25, "key_word": 4, "meaning": 12, "node": 35,
         "label": 5, "quote": 40}

SYSTEM = """You are the Topic Builder for Socratic AI, a calm tutor that helps university beginners practise critical thinking on any topic. A learner gives you a REQUEST: a topic name, a question, or a short reading. You write the material the tutor will use. You never write the questions; the tutor does that.

Write COUNT cases about the topic (3 if COUNT is missing). Each case is one short, real situation where a person makes a claim or a choice that is worth questioning, so the learner can practise clarifying, finding assumptions, weighing evidence, seeing other viewpoints and thinking about consequences. Several cases test different ideas from the topic, from easier to harder. If AVOID lists cases the learner has already done, each new case tests a different idea from all of them.

Facts:
- If SOURCE is given, take every fact and number from SOURCE only, and add nothing that SOURCE does not say. Pick the clearest, most important ideas in it for a beginner.
- If the REQUEST is a reading, take the facts from it in the same way.
- If SOURCE comes from the learner's own file, REQUEST may say which part to focus on. If REQUEST is empty, write about the main ideas of SOURCE.
- With neither, use only well known, widely agreed facts that a good textbook would state.
- When there is a SOURCE or a reading, give each note and each more_knowledge item a quote, which is 5 to 25 words copied exactly from it, word for word, that backs the fact up. With neither, leave quote empty.
- Never invent studies, quotes, names of real people or exact numbers you are not sure of. Round numbers are fine when they are well known.
- Write chances and shares as percentages, like 50% or 33%, never as fractions or words like "half", "a third" or "one in three". Write numbers as digits inside normal sentences, not with symbols like →, = or ≠.

Voice:
- Easy English for a beginner. Short, smooth sentences joined with "because", "so", "and" or "but".
- No colons joining two parts of a sentence, no dashes, no emoji, no exclamation marks, no slang.
- Explain any specialist word in a few simple words.

Each case has:
- title: 2 to 5 words, often a question, like "Pattern or luck?"
- mission: at most 8 words, what the learner will learn, like "Tell a real pattern from luck."
- tag: 1 word
- picture: the 1 word from PICTURES that best fits the case
- scenario: at most 35 words, the situation in which a person SAYS a claim or makes a choice, with their words in quotes, so there is something to question. Never only describe facts. Like "A stock went up 5 days in a row. Your friend says, \\"It is a pattern, so buy it now.\\""
- notes: exactly 5 facts the tutor may use, at most 25 words each, in teaching order. Each has a knowledge type and a label of 2 to 4 words for a diagram box, like "Green light reflects".
- reading: what the learner reads before the case
  - idea: 4 short sentences that teach the key idea
  - example: 1 concrete example sentence
  - key_words: 3 pairs of [word, meaning in at most 10 words]
  - think: 1 question to think about while reading
- more_knowledge: 3 to 5 extra facts or steps, each with an id, text, knowledge type and a label of 2 to 4 words, so the knowledge graph is complete
- links: 6 to 12 links [from_id, relation, to_id] between the notes (ids n1 to n5) and the more_knowledge ids. Every note and every extra fact is in at least 1 link.

PICTURES (use these names only):
""" + "\n".join(f"- {k}: {v}" for k, v in PICTURES.items()) + """

Knowledge types (use these names only):
""" + "\n".join(f"- {k}: {v}" for k, v in KNOWLEDGE_TYPES.items()) + """
Across its notes and more_knowledge, EACH case has at least 1 factual, 1 conceptual, 1 procedural and 1 causal piece, so check every case before you reply. A conceptual piece explains what an idea means or how ideas group together. A procedural piece is a step someone does, and steps are joined with "then".

Relations (use these names only):
""" + "\n".join(f"- {k}: {v}" for k, v in RELATIONS.items()) + """

If the REQUEST asks for help to harm people, such as weapons, hurting someone or crime, or is not something a learner can reason about, reply with ONLY {"refuse": "one short, kind sentence saying why"}.

Otherwise reply with ONLY this JSON and nothing else:
{"topic": "the topic in at most 8 words",
 "cases": [{"title": "", "mission": "", "tag": "", "scenario": "",
            "picture": "",
            "notes": [{"text": "", "type": "", "label": "", "quote": ""}],
            "reading": {"idea": [""], "example": "", "key_words": [["", ""]], "think": ""},
            "more_knowledge": [{"id": "", "text": "", "type": "", "label": "", "quote": ""}],
            "links": [["n1", "supports", ""]]}]}"""


class TopicError(ValueError):
    """The topic could not be built. The message is safe to show the learner."""


# Topics already built since the server started, so asking twice costs no call.
_CACHE: dict[str, dict] = {}
_lock = threading.Lock()


def _key(request):
    return re.sub(r"\s+", " ", request.strip().lower())


def _text(value, limit, what):
    """One clean string within the word limit. Dashes become commas (app text rule)."""
    if not isinstance(value, str) or not value.strip():
        raise TopicError(f"The {what} is missing.")
    text = re.sub(r"\s*(—|–|--)\s*", ", ", value.strip())
    if len(text.split()) > limit:
        raise TopicError(f"The {what} is too long.")
    return text


def _label(value):
    """A short diagram label, or None (the page then makes one from the text)."""
    try:
        return _text(value, WORDS["label"], "label")
    except TopicError:
        return None


def _type(value):
    value = str(value or "").strip().lower()
    return value if value in KNOWLEDGE_TYPES else None


def clean_source(source):
    """Where the facts came from, kept with each case so the page can show it:
    {"kind": "wikipedia", "articles": [{"title", "url"}]}, {"kind": "reading"}
    or None (the model's own knowledge). Anything else becomes None."""
    if not isinstance(source, dict):
        return None
    if source.get("kind") == "reading":
        return {"kind": "reading"}
    if source.get("kind") == "file":
        name = re.sub(r"[^\w .()-]", "", str(source.get("name") or ""))[:80].strip()
        return {"kind": "file", "name": name or "your file"}
    if source.get("kind") != "wikipedia":
        return None
    articles = [{"title": str(a.get("title"))[:120], "url": a["url"]} for a in source.get("articles") or []
                if isinstance(a, dict) and a.get("title") and isinstance(a.get("url"), str)
                and re.fullmatch(r"https://en\.wikipedia\.org/wiki/[^\s\"'<>]+", a["url"])][:sources.MAX_ARTICLES]
    return {"kind": "wikipedia", "articles": articles} if articles else None


def _quote(item, text):
    """{"quote", "from"} for a node whose quote is really in the source text, else
    {} (Goal 3, step 4). "from" is the Wikipedia article it sits in. With no text,
    as in recheck(), a quote already on the node is kept, since it was checked
    when the topic was built."""
    quote = item.get("quote")
    if not isinstance(quote, str) or len(quote.split()) < sources.MIN_QUOTE_WORDS:
        return {}
    where = sources.locate(quote, text) if text is not None else str(item.get("from") or "")[:120]
    if where is None:
        return {}
    try:
        quote = _text(quote, WORDS["quote"], "quote")
    except TopicError:
        return {}
    return {"quote": quote, **({"from": where} if where else {})}


def clean_case(raw, topic, case_id, source=None, text=None):
    """The case in the same shape as a content.CONCEPTS case, with its graph
    under "knowledge" in the same shape as knowledge.KNOWLEDGE. text is the
    source the Builder read, so each node's quote can be checked against it.
    Raises TopicError when something important is missing or broken."""
    if not isinstance(raw, dict):
        raise TopicError("A case is broken.")
    notes = [n for n in raw.get("notes") or [] if isinstance(n, dict)][:NOTES_PER_CASE]
    if len(notes) < NOTES_PER_CASE:
        raise TopicError("A case has too few notes.")
    r = raw.get("reading") if isinstance(raw.get("reading"), dict) else {}
    ideas = [_text(i, WORDS["idea"], "reading") for i in (r.get("idea") or [])[:4]]
    words = [[_text(w, WORDS["key_word"], "key word"), _text(m, WORDS["meaning"], "key word meaning")]
             for w, m in (p for p in (r.get("key_words") or [])[:3] if isinstance(p, list) and len(p) == 2)]
    if len(ideas) < 2 or not words:
        raise TopicError("A reading is too short.")

    nodes = [{"id": f"n{i + 1}", "type": _type(n.get("type")) or "factual", "note": i,
              **({"label": lab} if (lab := _label(n.get("label"))) else {}), **_quote(n, text)}
             for i, n in enumerate(notes)]
    for extra in raw.get("more_knowledge") or []:
        if not isinstance(extra, dict):
            continue
        nid = re.sub(r"[^a-z0-9_]", "_", str(extra.get("id") or "").strip().lower())[:30]
        kind = _type(extra.get("type"))
        if nid and kind and nid not in {n["id"] for n in nodes} and len(nodes) < NOTES_PER_CASE + 6:
            try:
                nodes.append({"id": nid, "type": kind, "text": _text(extra.get("text"), WORDS["node"], "fact"),
                              **({"label": lab} if (lab := _label(extra.get("label"))) else {}), **_quote(extra, text)})
            except TopicError:
                continue  # one broken extra fact is dropped, not the whole topic
    ids = {n["id"] for n in nodes}
    edges = []
    for link in raw.get("links") or []:
        if isinstance(link, list) and len(link) == 3:
            a, rel, b = (re.sub(r"[^a-z0-9_]", "_", str(x).strip().lower()) for x in link)
            if a in ids and b in ids and a != b and rel in RELATIONS and [a, rel, b] not in edges:
                edges.append([a, rel, b])
    # A node no link reaches is not part of the graph, so it is dropped (notes stay: the tutor reads them).
    linked = {x for a, _, b in edges for x in (a, b)}
    nodes = [n for n in nodes if "note" in n or n["id"] in linked]

    return {
        "id": case_id,
        "topic": topic,
        "title": _text(raw.get("title"), WORDS["title"], "title"),
        "mission": _text(raw.get("mission"), WORDS["mission"], "mission"),
        "tag": _text(raw.get("tag"), WORDS["tag"], "tag").capitalize(),
        "tool": None,
        "picture": picture if (picture := str(raw.get("picture") or "").strip().lower()) in PICTURES else "bulb",
        "scenario": _text(raw.get("scenario"), WORDS["scenario"], "story"),
        "notes": [_text(n.get("text"), WORDS["note"], "note") for n in notes],
        "reading": {"idea": ideas, "example": _text(r.get("example"), WORDS["example"], "example"),
                    "key_words": words, "think": _text(r.get("think"), WORDS["think"], "reading question")},
        "knowledge": {"nodes": nodes, "edges": edges},
        "generated": True,  # a DRAFT no expert has checked
        "source": clean_source(source),
    }


def clean_topic(data, request, source=None, count=CASES_PER_TOPIC, done=0, text=None):
    """The whole topic from the model reply, or TopicError. done: cases
    already made on this topic, so the new ids carry on after them."""
    if not isinstance(data, dict):
        raise TopicError("The topic could not be built, so please try again.")
    if data.get("refuse"):
        raise TopicError(str(data["refuse"])[:200])
    fallback = (source or {}).get("name") if (source or {}).get("kind") == "file" else request[:60]
    topic = _text(data.get("topic") or fallback, WORDS["topic"], "topic name")
    tid = "t" + hashlib.sha1(_key(request).encode()).hexdigest()[:10]
    raw_cases = [c for c in data.get("cases") or [] if isinstance(c, dict)][:count]
    cases = []
    for i, raw in enumerate(raw_cases):
        try:
            cases.append(clean_case(raw, topic, f"{tid}-{done + i + 1}", source, text))
        except TopicError:
            continue  # keep the good cases if one is broken
    if not cases:
        raise TopicError("The topic could not be built, so please try again or word it another way.")
    return {"id": tid, "topic": topic, "cases": cases}


# ---------- skill check questions for a generated topic ----------

SKILL_SYSTEM = """You write skill check questions for Socratic AI, a tutor that helps university beginners practise critical thinking on any topic. You get a TOPIC and its CASES. Write 1 question for EACH pair in PAIRS, so """ + str(len(REASONING_TYPES) * len(CORE_KNOWLEDGE)) + """ questions in all.

Each question invites the learner to use ONE type of reasoning on ONE type of knowledge, in a few sentences of their own. Never name the reasoning type or the knowledge type in the question.

Reasoning types:
""" + "\n".join(f"- {k}: {v}" for k, v in REASONING_TYPES.items()) + """

Knowledge types, and what using them looks like:
""" + "\n".join(f"- {k}: the learner {KNOWLEDGE_SIGNS[k]}" for k in CORE_KNOWLEDGE) + """

Examples from another topic:
- inductive, factual. situation "Over 4 weeks you count how many of 500 stocks went up 5 days in a row, and you get 14, 17, 15 and 16." question "What general idea do these counts suggest about 5 day streaks?"
- deductive, causal. situation "Hot weather makes people buy more ice cream and also makes more people swim." question "If a town has a heatwave next week, what should happen to both, and why?"
- abductive, relational. situation "Two bank stocks have moved together almost every day for 5 years." question "What is the most likely explanation for this link?"

Rules:
- situation: at most 35 words, concrete, giving the facts the learner needs. Inductive gives at least 3 separate cases or observations (3 places, 3 years, 3 people or 3 results) and asks what general idea they suggest, so 1 example alone is never inductive. Deductive gives a rule and a new case. Abductive gives a surprising observation with information missing.
- question: at most 20 words, exactly one question, ending with "?".
- Use only well known facts about the topic. Easy English, short smooth sentences, no colons joining parts, no dashes, no emoji. Chances and shares as percentages, never fractions or words like "half" or "one in three".
- case: the number (1, 2 or 3) of the case it fits best.

Reply with ONLY this JSON:
{"questions": [{"reasoning": "", "knowledge": "", "case": 1, "situation": "", "question": ""}]}"""

_SKILL_CACHE: dict[str, dict] = {}


def clean_items(data, tid, case_ids):
    """{item id: item} with at most 1 question per pair, in the same shape as
    skillcheck.ITEMS. Raises TopicError if too few pairs are covered."""
    items = {}
    questions = data.get("questions") if isinstance(data, dict) else None
    for q in questions if isinstance(questions, list) else []:
        if not isinstance(q, dict):
            continue
        r, k = str(q.get("reasoning", "")).strip().lower(), str(q.get("knowledge", "")).strip().lower()
        iid = f"{tid}:{r[:3]}-{k[:4]}"
        if r not in REASONING_TYPES or k not in CORE_KNOWLEDGE or iid in items:
            continue
        try:
            situation = _text(q.get("situation"), WORDS["scenario"], "situation")
            question = _text(q.get("question"), WORDS["question"], "question")
        except TopicError:
            continue
        if not question.endswith("?"):
            continue
        n = q.get("case")
        n = n if isinstance(n, int) and 1 <= n <= len(case_ids) else 1
        items[iid] = {"id": iid, "reasoning": r, "knowledge": k, "case": case_ids[n - 1],
                      "situation": situation, "question": question}
    # a check asks 2 questions per reasoning type, each on a different knowledge type
    if any(sum(i["reasoning"] == r for i in items.values()) < 2 for r in REASONING_TYPES):
        raise TopicError("The skill check questions could not be written, so please try again.")
    return items


def skill_items(cases):
    """The skill check bank for a generated topic (one model call, then cached)."""
    tid = cases[0]["id"].split("-")[0]
    with _lock:
        if tid in _SKILL_CACHE:
            return _SKILL_CACHE[tid]
    if llm_client.PROVIDER == "mock":
        data = {"questions": [{"reasoning": r, "knowledge": k, "case": 1,
                               "situation": f"[mock] A situation about {cases[0]['topic']}.",
                               "question": f"[mock] What {r} idea about this {k} fact can you give?"}
                              for r in REASONING_TYPES for k in CORE_KNOWLEDGE]}
    else:
        if not limits.budget_left():
            raise TopicError(limits.FULL_MESSAGE)
        payload = {"TOPIC": cases[0]["topic"],
                   "CASES": [{"case": i + 1, "title": c["title"], "scenario": c["scenario"], "notes": c["notes"]}
                             for i, c in enumerate(cases)],
                   "PAIRS": [[r, k] for r in REASONING_TYPES for k in CORE_KNOWLEDGE]}
        text = llm_client._generate(SKILL_SYSTEM, json.dumps(payload, ensure_ascii=False), max_tokens=4000, json_mode=True)
        data = llm_client._parse_json(text)
    items = clean_items(data, tid, [c["id"] for c in cases])
    with _lock:
        _SKILL_CACHE[tid] = items
    return items


def recheck(case):
    """A generated case the page sends back to start a session, checked again
    by the same rules, so the page cannot slip in anything the Builder could
    not have made. Returns the clean case, or raises TopicError."""
    if not isinstance(case, dict) or not isinstance(case.get("knowledge"), dict):
        raise TopicError("This case is broken, so please build the topic again.")
    texts = {n.get("id"): n for n in case["knowledge"].get("nodes") or [] if isinstance(n, dict)}
    notes = case.get("notes") or []
    by_note = {n.get("note"): n for n in texts.values() if "note" in n}
    raw = {**case,
           "notes": [{"text": t, **{k: by_note.get(i, {}).get(k) for k in ("type", "label", "quote", "from")}}
                     for i, t in enumerate(notes)],
           "more_knowledge": [n for n in texts.values() if "text" in n],
           "links": case["knowledge"].get("edges") or []}
    case_id = str(case.get("id") or "")
    if not re.fullmatch(r"t[0-9a-f]{10}-[1-9][0-9]{0,2}", case_id):
        raise TopicError("This case is broken, so please build the topic again.")
    return clean_case(raw, _text(case.get("topic"), WORDS["topic"], "topic name"), case_id, case.get("source"))


def _mock(request, count=CASES_PER_TOPIC):
    """A fixed topic with no model call, for PROVIDER=mock and the tests."""
    name = request.strip()[:60]
    def case(i):
        return {
            "title": f"Case {i} on {' '.join(name.split()[-2:])[:20]}", "mission": "Question a claim about this topic.", "tag": "Claims",
            "picture": "book",
            "scenario": f"[mock] A friend makes a bold claim about {name[:30]}, and says everyone agrees.",
            "notes": [{"text": f"[mock] Fact {j} about the topic.", "type": t}
                      for j, t in enumerate(["factual", "conceptual", "procedural", "causal", "epistemic"], 1)],
            "reading": {"idea": ["[mock] The first idea.", "[mock] The second idea."], "example": "[mock] An example.",
                        "key_words": [["Claim", "something said to be true"]], "think": "[mock] What would you check first?"},
            "more_knowledge": [{"id": "check", "text": "[mock] Then check the evidence.", "type": "procedural"}],
            "links": [["n1", "supports", "n2"], ["n3", "then", "check"], ["n4", "causes", "n1"], ["n5", "weakens", "n2"]],
        }
    return {"topic": name, "cases": [case(i) for i in range(1, count + 1)]}


def build(request, file=None, count=CASES_PER_TOPIC, avoid=()):
    """3 cases for any topic, written from 1 or 2 Wikipedia articles when they
    can be found (sources.py), from the learner's own reading, or from their
    own file. file: {"name", "text"} from files.read(); then request is
    optional and says which part to focus on. count: how many cases (the
    Ask chat asks for 1, so the wait is about a third). avoid: titles of the
    cases already done on this topic, so a new case tests a new idea; the new
    case ids then carry on after them. Raises TopicError (or LLMError if the
    model fails)."""
    count = max(1, min(int(count), CASES_PER_TOPIC))
    avoid = [str(a)[:80] for a in avoid if isinstance(a, str) and a.strip()][:MAX_AVOID]
    request = (request or "").strip()[:MAX_REQUEST_CHARS]
    if len(request) < 2 and not file:
        raise TopicError("Please type a topic first.")
    if file:
        from . import files
        picked = files.select(file["text"], request)
        digest = hashlib.sha1(file["text"].encode()).hexdigest()[:12]
        key = _key(f"file:{digest}:{request}")
        request_for_id = key
    else:
        key = request_for_id = _key(request)
    key = f"{key}|{count}|{'|'.join(avoid)}"  # the topic id stays the same for every case on it
    with _lock:
        if key in _CACHE:
            return _CACHE[key]
    if file:
        source = {"kind": "file", "name": file["name"]}
    else:
        source = {"kind": "reading"} if len(request) >= sources.READING_CHARS else None
    text = ""  # no source, so no quote can be checked and every quote is dropped
    if llm_client.PROVIDER == "mock":
        data = _mock(request or file["name"], count)
    else:
        if not limits.budget_left():
            raise TopicError(limits.FULL_MESSAGE)
        found = {"text": picked} if file else None if source else sources.find(request)
        payload = {"REQUEST": request, "COUNT": count, **({"AVOID": avoid} if avoid else {}),
                   **({"SOURCE": found["text"]} if found else {})}
        source = source or found
        text = found["text"] if found else request if source else ""
        # Seen 21 October 2026: a long reply now and then comes back as broken
        # JSON, so a reply with no usable case is asked for once more. A
        # refusal is final.
        for attempt in range(2):
            reply = llm_client._generate(SYSTEM, json.dumps(payload, ensure_ascii=False),
                                         max_tokens=2600 * count, json_mode=True)  # quotes need about 400 more
            data = llm_client._parse_json(reply)
            if isinstance(data, dict) and data.get("refuse"):
                break
            try:
                clean_topic(data, request_for_id, source, count, len(avoid), text)
                break
            except TopicError:
                if attempt or not limits.budget_left():
                    raise
    topic = clean_topic(data, request_for_id, source, count, len(avoid), text)
    topic["source"] = topic["cases"][0]["source"]
    with _lock:
        _CACHE[key] = topic
    return topic


__all__ = ["build", "clean_case", "clean_topic", "clean_items", "recheck", "skill_items", "TopicError", "LLMError"]
