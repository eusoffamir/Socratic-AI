"""Reasoning agent (Goal 1, step 2).

For each learner answer it marks which type of reasoning was shown (inductive,
deductive, abductive) and which types of knowledge were used, each as 1 or 0,
with an evidence quote. These 1s and 0s are the trials for the statistics later.

It has its own prompt part and its own cleaning, but it runs in the SAME model
call as the Assessor, because the free Gemini quota is small. Switch it off with
AGENT_REASONING=0 in .env, and the Assessor then runs exactly as before.
"""
import os
import re

from .knowledge import KNOWLEDGE, KNOWLEDGE_TYPES

# Dr Ho's top three. Analogic, counterfactual and triangulation are a bonus for later.
REASONING_TYPES = {
    "inductive": "from several cases or observations to a general idea or pattern",
    "deductive": "from a rule or known fact to a specific conclusion for this case",
    "abductive": "from what was seen to the best explanation of why it happened, when information is missing",
}

# What counts as USING each knowledge type in an answer, not just naming it.
KNOWLEDGE_SIGNS = {
    "factual": "states a specific fact, number or observation",
    "conceptual": "uses or explains what an idea or term means",
    "procedural": "describes steps or a method to do or check something",
    "causal": "says why something happens, that one thing makes another happen",
    "relational": "links two or more things, such as how one changes when another changes",
    "strategic": "chooses what to do next, given the situation",
    "metacognitive": "reflects on how they know, or on their own thinking",
    "epistemic": "judges how strong the evidence is, or what is justified to believe",
}
assert set(KNOWLEDGE_SIGNS) == set(KNOWLEDGE_TYPES)

PROMPT = """You also do a second job, as the Reasoning agent. Mark which TYPES of reasoning and which TYPES of knowledge the learner used in the answer. Give 1 only if it is clearly shown, otherwise 0. More than one can be 1, and all can be 0.

reasoning_types:
""" + "\n".join(f"- {k}: {v}" for k, v in REASONING_TYPES.items()) + """

knowledge_used, give 1 if the answer:
""" + "\n".join(f"- {k}: {v}" for k, v in KNOWLEDGE_SIGNS.items()) + """

Rules for this job:
- A claim with no reason shows no reasoning type. "I don't know" or a single word is all 0.
- Naming a word is not using that knowledge. "It is causal" with no cause named is 0 for causal.
- Repeating a fact from the question is not factual knowledge of the learner's own.
- NOTE_TYPES gives the knowledge type of each item in NOTES, as a guide only.
reasoning_evidence: a short quote from the answer that shows the reasoning type, or "" if none."""

JSON_FIELDS = ('"reasoning_types": {' + ", ".join(f'"{k}": 0' for k in REASONING_TYPES) + '}, '
               '"knowledge_used": {' + ", ".join(f'"{k}": 0' for k in KNOWLEDGE_TYPES) + '}, '
               '"reasoning_evidence": ""')


def enabled():
    """Read at call time so tests can switch it on and off."""
    return os.getenv("AGENT_REASONING", "1") != "0"


def note_types(case_id):
    """The knowledge type of each case note, in note order, for the prompt."""
    nodes = sorted((n for n in KNOWLEDGE[case_id]["nodes"] if "note" in n), key=lambda n: n["note"])
    return [n["type"] for n in nodes]


def _flags(raw, keys):
    from .llm_client import _flag  # late import, llm_client imports this module
    raw = raw if isinstance(raw, dict) else {}
    raw = {str(k).strip().lower(): v for k, v in raw.items()}
    return {k: _flag(raw.get(k)) for k in keys}


def clean(data):
    """One safe shape from the model reply, like clean_assessment does for the standards."""
    return {"types": _flags(data.get("reasoning_types"), REASONING_TYPES),
            "knowledge": _flags(data.get("knowledge_used"), KNOWLEDGE_TYPES),
            "evidence": str(data.get("reasoning_evidence") or "")}


def empty():
    """All 0, for an answer that is not the learner's own (copied) or not reasoned."""
    return {"types": {k: 0 for k in REASONING_TYPES},
            "knowledge": {k: 0 for k in KNOWLEDGE_TYPES}, "evidence": ""}


# Mock mode only: rough keyword signs, so the app and the dashboard can be tried
# offline. These are NOT how the real agent marks answers.
_MOCK_SIGNS = {
    "inductive": r"\b(many|all|every time|most|usually|pattern|often)\b",
    "deductive": r"\b(so|therefore|must|if .+ then|which means)\b",
    "abductive": r"\b(maybe|probably|could be|might be|best explanation)\b",
    "factual": r"\d",
    "conceptual": r"\b(means|is when|is called)\b",
    "procedural": r"\b(first|then|test|split|check|count)\b",
    "causal": r"\b(because|causes?|makes?|leads? to)\b",
    "relational": r"\b(together|linked|the more|related)\b",
    "strategic": r"\b(should|would buy|would not buy|next step)\b",
    "metacognitive": r"\b(i think|i assumed|i am not sure|my reasoning)\b",
    "epistemic": r"\b(proof|prove|evidence|justified|not enough)\b",
}


def mock(answer):
    text = (answer or "").lower()
    if len(text.split()) < 3:
        return empty()
    hit = {k: int(bool(re.search(p, text))) for k, p in _MOCK_SIGNS.items()}
    return {"types": {k: hit[k] for k in REASONING_TYPES},
            "knowledge": {k: hit[k] for k in KNOWLEDGE_TYPES}, "evidence": answer[:80]}
