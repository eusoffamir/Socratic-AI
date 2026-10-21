"""Explainer agent (Goal 1, step 6).

When a learner clicks a cell of a grid, it explains in plain words why that
type of reasoning matters, and how to use it with the chosen mix of knowledge
types (1 or 2), through one short quant scenario. Dr Ho's "why you need to
know this" pop-up.

It only runs when asked, and each answer is kept in memory, so the same pair
costs one model call per server start. In mock mode, when the daily budget is
used up, or when the call fails, a hand-written explanation is used instead,
so the pop-up never breaks.
"""
import json
import threading

from . import limits, llm_client
from .knowledge import KNOWLEDGE, KNOWLEDGE_TYPES, node_text
from .reasoning import KNOWLEDGE_SIGNS, REASONING_TYPES

MAX_KNOWLEDGE = 2
WORDS = {"why": 30, "scenario": 50, "step": 18, "try": 22}

SYSTEM = """You are the Explainer agent for Socratic AI, a tutor that teaches university beginners how quants find real patterns in data. You never mark the learner. You explain ONE type of reasoning used on ONE or TWO types of knowledge, so the learner sees why it matters and when to use it.

Write for a beginner. Use easy English and short, smooth sentences joined with words like "because", "so", "and" and "but". Be calm and helpful. No slang, no emoji, no exclamation marks, no colons and no dashes. Put numbers inside sentences and write chances as percentages, never fractions. Keep to simple quant ideas from BACKGROUND, such as streaks, luck, backtests, new data and correlation, with no complex maths or machine learning.

Fields:
- why: why this reasoning matters with this knowledge, at most """ + str(WORDS["why"]) + """ words.
- scenario: one short, concrete quant story where a person uses this reasoning on this knowledge, at most """ + str(WORDS["scenario"]) + """ words.
- steps: 2 or 3 short steps to do it yourself, each at most """ + str(WORDS["step"]) + """ words.
- try: one question the learner can practise on, at most """ + str(WORDS["try"]) + """ words, ending with a question mark.

Return ONLY this JSON:
{"why": "", "scenario": "", "steps": ["", ""], "try": ""}"""

# Hand-written fallback. DRAFT by Claude, 21 October 2026.
_WHY = {
    "inductive": "Inductive reasoning turns many cases into one general idea, and that is how a quant spots a pattern worth testing.",
    "deductive": "Deductive reasoning applies a rule you trust to a new case, so you can tell quickly what must follow.",
    "abductive": "Abductive reasoning finds the best explanation when information is missing, so you know what to check next.",
}
_SCENARIO = {
    "inductive": "A quant counts streaks in 500 stocks for 4 weeks and sees about 15 each week, so she concludes that streaks like this are normal luck.",
    "deductive": "A quant knows that trying many rules makes one look great by luck, so when a fund shows only its best rule out of 500, he expects it to do worse on new data.",
    "abductive": "A stock goes up 10 days in a row right after a new product, so a quant guesses the news is the best explanation and checks other stocks that had news.",
}
_STEP = {
    "factual": "Start from the facts and numbers you are sure of.",
    "conceptual": "Be clear about what the key words mean before you use them.",
    "procedural": "Follow the steps of the method in order, such as split the data and then test.",
    "causal": "Ask what could make this happen, and look for a hidden third cause.",
    "relational": "Ask how one thing changes when the other changes.",
    "strategic": "Decide what to do next, given what you found.",
    "metacognitive": "Ask yourself how you know this, and what you assumed.",
    "epistemic": "Ask how strong the evidence is before you believe it.",
}
_TRY = {
    "inductive": "What general idea would you take from seeing the same result in 5 different years?",
    "deductive": "If a rule only worked on old data, what should you expect on new data?",
    "abductive": "Two stocks moved together for years, so what is the best explanation?",
}

_cache = {}
_lock = threading.Lock()


def _key(reasoning, knowledge):
    return reasoning, tuple(sorted(set(knowledge)))


def valid(reasoning, knowledge):
    return (reasoning in REASONING_TYPES and 1 <= len(set(knowledge)) <= MAX_KNOWLEDGE
            and all(k in KNOWLEDGE_TYPES for k in knowledge))


def user_payload(reasoning, knowledge):
    """The pair to explain, plus BACKGROUND from the knowledge graphs, so the
    scenario stays inside what the cases teach."""
    background = [node_text(cid, n) for cid, g in KNOWLEDGE.items() for n in g["nodes"] if n["type"] in knowledge]
    return json.dumps({"reasoning_type": {reasoning: REASONING_TYPES[reasoning]},
                       "knowledge_types": {k: f"{KNOWLEDGE_TYPES[k]} The learner {KNOWLEDGE_SIGNS[k]}." for k in knowledge},
                       "BACKGROUND": background[:12]}, indent=1, ensure_ascii=False)


def fallback(reasoning, knowledge):
    return {"why": _WHY[reasoning], "scenario": _SCENARIO[reasoning],
            "steps": [_STEP[k] for k in knowledge] + ([_STEP["epistemic"]] if len(knowledge) == 1 else []),
            "try": _TRY[reasoning], "source": "fallback"}


def _tidy(text):
    text = str(text or "")
    for bad in ("—", "–", "--"):
        text = text.replace(bad, ", ")
    text = " ".join(text.replace("!", ".").split())
    return text.replace(" ,", ",").replace(",,", ",").strip()


def clean(data):
    """A safe shape from the model reply, or None if it is not usable."""
    if not isinstance(data, dict):
        return None
    steps = data.get("steps")
    steps = [_tidy(s) for s in steps if _tidy(s)][:3] if isinstance(steps, list) else []
    out = {"why": _tidy(data.get("why")), "scenario": _tidy(data.get("scenario")), "steps": steps,
           "try": _tidy(data.get("try")), "source": "agent"}
    if not (out["why"] and out["scenario"] and len(steps) >= 2 and out["try"].endswith("?")):
        return None
    return out


def explain(reasoning, knowledge):
    knowledge = sorted(set(knowledge), key=list(KNOWLEDGE_TYPES).index)
    key = _key(reasoning, knowledge)
    with _lock:
        if key in _cache:
            return _cache[key]
    result = None
    if llm_client.PROVIDER != "mock" and limits.budget_left():
        try:
            text = llm_client._generate(SYSTEM, user_payload(reasoning, knowledge), max_tokens=500, json_mode=True)
            result = clean(llm_client._parse_json(text))
        except Exception:  # any model problem: use the hand-written one, never break the pop-up
            result = None
    if result is None:
        return {"reasoning": reasoning, "knowledge": knowledge, **fallback(reasoning, knowledge)}  # not cached, so a later call can still use the agent
    result = {"reasoning": reasoning, "knowledge": knowledge, **result}
    with _lock:
        _cache[key] = result
    return result
