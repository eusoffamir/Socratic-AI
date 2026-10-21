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

from . import limits, llm_client
from .knowledge import KNOWLEDGE_TYPES, RELATIONS
from .llm_client import LLMError

MAX_REQUEST_CHARS = 4000  # a topic name or a short reading
CASES_PER_TOPIC = 3
NOTES_PER_CASE = 5

# Word limits for each part, a little above what the prompt asks, so one extra
# word does not throw a whole topic away.
WORDS = {"topic": 12, "title": 6, "mission": 12, "tag": 2, "scenario": 45, "note": 35,
         "idea": 35, "example": 40, "think": 30, "key_word": 4, "meaning": 12, "node": 35}

SYSTEM = """You are the Topic Builder for Socratic AI, a calm tutor that helps university beginners practise critical thinking on any topic. A learner gives you a REQUEST: a topic name, a question, or a short reading. You write the material the tutor will use. You never write the questions; the tutor does that.

Write 3 cases about the topic. Each case is one short, real situation where a person makes a claim or a choice that is worth questioning, so the learner can practise clarifying, finding assumptions, weighing evidence, seeing other viewpoints and thinking about consequences. The 3 cases should test different ideas from the topic, from easier to harder.

Facts:
- Use only well known, widely agreed facts that a good textbook would state. If the REQUEST is a reading, take the facts from it.
- Never invent studies, quotes, names of real people or exact numbers you are not sure of. Round numbers are fine when they are well known.
- Write chances as percentages, never fractions, and write numbers as digits inside normal sentences, not with symbols like →, = or ≠.

Voice:
- Easy English for a beginner. Short, smooth sentences joined with "because", "so", "and" or "but".
- No colons joining two parts of a sentence, no dashes, no emoji, no exclamation marks, no slang.
- Explain any specialist word in a few simple words.

Each case has:
- title: 2 to 5 words, often a question, like "Pattern or luck?"
- mission: at most 8 words, what the learner will learn, like "Tell a real pattern from luck."
- tag: 1 word
- scenario: at most 35 words, the situation with a claim worth questioning, like "A stock went up 5 days in a row. Your friend says, \\"It is a pattern, so buy it now.\\""
- notes: exactly 5 facts the tutor may use, at most 25 words each, in teaching order. Each has a knowledge type.
- reading: what the learner reads before the case
  - idea: 4 short sentences that teach the key idea
  - example: 1 concrete example sentence
  - key_words: 3 pairs of [word, meaning in at most 10 words]
  - think: 1 question to think about while reading
- more_knowledge: 3 to 5 extra facts or steps, each with an id, text and knowledge type, so the knowledge graph is complete
- links: 6 to 12 links [from_id, relation, to_id] between the notes (ids n1 to n5) and the more_knowledge ids. Every note and every extra fact is in at least 1 link.

Knowledge types (use these names only):
""" + "\n".join(f"- {k}: {v}" for k, v in KNOWLEDGE_TYPES.items()) + """
Across its notes and more_knowledge, each case has at least 1 factual, 1 conceptual, 1 procedural and 1 causal piece. A procedural piece is a step someone does, and steps are joined with "then".

Relations (use these names only):
""" + "\n".join(f"- {k}: {v}" for k, v in RELATIONS.items()) + """

If the REQUEST asks for help to harm people, such as weapons, hurting someone or crime, or is not something a learner can reason about, reply with ONLY {"refuse": "one short, kind sentence saying why"}.

Otherwise reply with ONLY this JSON and nothing else:
{"topic": "the topic in at most 8 words",
 "cases": [{"title": "", "mission": "", "tag": "", "scenario": "",
            "notes": [{"text": "", "type": ""}],
            "reading": {"idea": [""], "example": "", "key_words": [["", ""]], "think": ""},
            "more_knowledge": [{"id": "", "text": "", "type": ""}],
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


def _type(value):
    value = str(value or "").strip().lower()
    return value if value in KNOWLEDGE_TYPES else None


def clean_case(raw, topic, case_id):
    """The case in the same shape as a content.CONCEPTS case, with its graph
    under "knowledge" in the same shape as knowledge.KNOWLEDGE. Raises
    TopicError when something important is missing or broken."""
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

    nodes = [{"id": f"n{i + 1}", "type": _type(n.get("type")) or "factual", "note": i} for i, n in enumerate(notes)]
    for extra in raw.get("more_knowledge") or []:
        if not isinstance(extra, dict):
            continue
        nid = re.sub(r"[^a-z0-9_]", "_", str(extra.get("id") or "").strip().lower())[:30]
        kind = _type(extra.get("type"))
        if nid and kind and nid not in {n["id"] for n in nodes} and len(nodes) < NOTES_PER_CASE + 6:
            try:
                nodes.append({"id": nid, "type": kind, "text": _text(extra.get("text"), WORDS["node"], "fact")})
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
        "scenario": _text(raw.get("scenario"), WORDS["scenario"], "story"),
        "notes": [_text(n.get("text"), WORDS["note"], "note") for n in notes],
        "reading": {"idea": ideas, "example": _text(r.get("example"), WORDS["example"], "example"),
                    "key_words": words, "think": _text(r.get("think"), WORDS["think"], "reading question")},
        "knowledge": {"nodes": nodes, "edges": edges},
        "generated": True,  # a DRAFT no expert has checked
    }


def clean_topic(data, request):
    """The whole topic from the model reply, or TopicError."""
    if not isinstance(data, dict):
        raise TopicError("The topic could not be built, so please try again.")
    if data.get("refuse"):
        raise TopicError(str(data["refuse"])[:200])
    topic = _text(data.get("topic") or request[:60], WORDS["topic"], "topic name")
    tid = "t" + hashlib.sha1(_key(request).encode()).hexdigest()[:10]
    raw_cases = [c for c in data.get("cases") or [] if isinstance(c, dict)][:CASES_PER_TOPIC]
    cases = []
    for i, raw in enumerate(raw_cases):
        try:
            cases.append(clean_case(raw, topic, f"{tid}-{i + 1}"))
        except TopicError:
            continue  # keep the good cases if one is broken
    if not cases:
        raise TopicError("The topic could not be built, so please try again or word it another way.")
    return {"id": tid, "topic": topic, "cases": cases}


def recheck(case):
    """A generated case the page sends back to start a session, checked again
    by the same rules, so the page cannot slip in anything the Builder could
    not have made. Returns the clean case, or raises TopicError."""
    if not isinstance(case, dict) or not isinstance(case.get("knowledge"), dict):
        raise TopicError("This case is broken, so please build the topic again.")
    texts = {n.get("id"): n for n in case["knowledge"].get("nodes") or [] if isinstance(n, dict)}
    notes = case.get("notes") or []
    types = {n.get("note"): n.get("type") for n in texts.values() if "note" in n}
    raw = {**case,
           "notes": [{"text": t, "type": types.get(i)} for i, t in enumerate(notes)],
           "more_knowledge": [n for n in texts.values() if "text" in n],
           "links": case["knowledge"].get("edges") or []}
    case_id = str(case.get("id") or "")
    if not re.fullmatch(r"t[0-9a-f]{10}-[1-9]", case_id):
        raise TopicError("This case is broken, so please build the topic again.")
    return clean_case(raw, _text(case.get("topic"), WORDS["topic"], "topic name"), case_id)


def _mock(request):
    """A fixed topic with no model call, for PROVIDER=mock and the tests."""
    name = request.strip()[:60]
    def case(i):
        return {
            "title": f"Case {i} on {name[:20]}", "mission": "Question a claim about this topic.", "tag": "Claims",
            "scenario": f"[mock] A friend makes a bold claim about {name[:30]}, and says everyone agrees.",
            "notes": [{"text": f"[mock] Fact {j} about the topic.", "type": t}
                      for j, t in enumerate(["factual", "conceptual", "procedural", "causal", "epistemic"], 1)],
            "reading": {"idea": ["[mock] The first idea.", "[mock] The second idea."], "example": "[mock] An example.",
                        "key_words": [["Claim", "something said to be true"]], "think": "[mock] What would you check first?"},
            "more_knowledge": [{"id": "check", "text": "[mock] Then check the evidence.", "type": "procedural"}],
            "links": [["n1", "supports", "n2"], ["n3", "then", "check"], ["n4", "causes", "n1"], ["n5", "weakens", "n2"]],
        }
    return {"topic": name, "cases": [case(i) for i in range(1, CASES_PER_TOPIC + 1)]}


def build(request):
    """3 cases for any topic. Raises TopicError (or LLMError if the model fails)."""
    request = (request or "").strip()[:MAX_REQUEST_CHARS]
    if len(request) < 2:
        raise TopicError("Please type a topic first.")
    key = _key(request)
    with _lock:
        if key in _CACHE:
            return _CACHE[key]
    if llm_client.PROVIDER == "mock":
        data = _mock(request)
    else:
        if not limits.budget_left():
            raise TopicError(limits.FULL_MESSAGE)
        text = llm_client._generate(SYSTEM, json.dumps({"REQUEST": request}, ensure_ascii=False),
                                    max_tokens=6000, json_mode=True)
        data = llm_client._parse_json(text)
    topic = clean_topic(data, request)
    with _lock:
        _CACHE[key] = topic
    return topic


__all__ = ["build", "clean_case", "clean_topic", "TopicError", "LLMError"]
