"""Catches an answer that copies text the learner can see on screen (a hint,
the case notes, the reading, a tool result) instead of their own thinking.
Plain code, no AI: it is free, instant and gives the same result every time.
A rule guards; the agents never see a copied answer as real reasoning."""
import os
import re

from . import reasoning
from .content import STANDARDS, case_of

# Most of the answer copied = not the learner's own thinking.
COPY_LIMIT = 0.6

# Words in a row that must match to count as copied. 6, not 4: with 4, short
# facts every honest answer repeats ("up 5 days in a row", "just by luck")
# were counted as copying (audit, 14 October 2026). A pasted hint is a whole
# sentence, so 6 still catches it.
RUN = 6

# The exact words the Tutor's feedback uses after a copied answer (set by code, so it never varies).
CALL_OUT = "You copied the hint, please answer in your own words."
AI_CALL_OUT = "That answer reads like an AI chatbot wrote it, so please answer in your own words."


def _words(text):
    return re.findall(r"[a-z0-9%]+", (text or "").lower())


def _grams(texts):
    grams = set()
    for text in texts:
        w = _words(text)
        grams |= {tuple(w[i:i + RUN]) for i in range(len(w) - RUN + 1)}
    return grams


def _covered(words, grams):
    """For each word of the answer: is it inside a run found in grams?"""
    covered = [False] * len(words)
    for i in range(len(words) - RUN + 1):
        if tuple(words[i:i + RUN]) in grams:
            covered[i:i + RUN] = [True] * RUN
    return covered


def copied_share(answer, sources, story=""):
    """The share of the answer's own words that sit inside a run of RUN or
    more words copied from one of the sources (0 to 1). Words that repeat the
    case story are left out of the count, even if a hint repeats the story
    too, because to answer, the learner has to say what happened ("it went up
    5 days in a row")."""
    words = _words(answer)
    if len(words) < RUN:
        return 0.0
    copied = _covered(words, _grams(sources))
    from_story = _covered(words, _grams([story]))
    rest = [c for c, s in zip(copied, from_story) if not s]
    return sum(rest) / len(rest) if rest else 0.0


def is_copied(answer, sources, story=""):
    return copied_share(answer, sources, story) >= COPY_LIMIT


def copied_assessment():
    """What a copied answer scores: nothing, because none of it is the learner's own."""
    return {"standards": {k: 0 for k in STANDARDS}, "reasoning_move": "none", "learner_points": [],
            "confused_or_frustrated": False, "evidence_quote": "", "confidence": 1.0, "copied_hint": True,
            "reasoning": reasoning.empty() if reasoning.enabled() else None}


def session_sources(session):
    """The hints and facts the learner of a real case has been shown so far.
    Not the case story: it is the question itself, and learners must repeat
    its facts to answer it."""
    c = case_of(session)
    r = c["reading"]
    sources = [*c["notes"], r["example"], r["think"], *r["idea"]]
    for t in session.get("turns", []):
        sources.append((t.get("parts") or {}).get("key_idea") or "")
        sources += [run.get("summary") or "" for run in t.get("tool_runs") or []]
    return sources


def session_story(session):
    """The case story. Repeating its facts is answering, not copying."""
    return case_of(session)["scenario"]


# ---------- answers that look like they came from an AI chatbot (cases and skill check) ----------
# A free code check, no model call. It looks for things chatbots write and
# learners almost never do. It cannot catch an AI answer that was retyped by
# hand, so it is one guard among several (paste is off and answers are short).

AI_PHRASES = [
    "would you like to", "would you like me to", "let me know if", "ai responses may include mistakes",
    "ai can make mistakes", "double-check responses", "for financial advice, consult", "here is the breakdown",
    "here's the breakdown", "great question", "as an ai", "i hope this helps", "in summary,", "key takeaway",
    "source preferences", "skip to main content", "here is exactly why", "here's exactly why",
]
_AI_LAYOUT = [
    re.compile(r"(?m)^\s*(?:[-*•]|\d+\.)\s+\S"),      # bullet or numbered list lines
    re.compile(r"(?m)^\s*#{1,6}\s"),                   # markdown headings
    re.compile(r"\*\*[^*]+\*\*"),                      # **bold**
    re.compile(r"(?m)^\s*\+\d+\s*$|\s\+\d+\s*$"),      # search result source counts like "+3"
    re.compile(r"(?m)^[A-Z][\w ,'()&-]{2,60}:\s+\S"),  # "Shared Sector Risk: Because ..." title lines
    re.compile(r"(?m)^\s*•\s*[A-Z][\w ,'()&-]{2,60}:"),  # "• Random Luck (Most Common): ..." bullet titles
    re.compile(r"\u2014"),                # an em dash, which keyboards do not type easily
]


def ai_guard_on():
    """AI_GUARD in .env: 1 (the default) turns on this check AND turns paste off
    in the skill check, 0 turns both off for testing. Read each time, so tests
    and a restart can switch it."""
    return os.getenv("AI_GUARD", "1") != "0"


def ai_reason(answer):
    """ai_like(), but only when the guard is on. The agents call this one."""
    return ai_like(answer) if ai_guard_on() else None


def ai_like(answer):
    """The reason an answer looks AI-written, or None."""
    low = " ".join(answer.lower().split())
    for p in AI_PHRASES:
        if p in low:
            return f'it contains "{p}"'
    hits = sum(1 for rx in _AI_LAYOUT if rx.search(answer))
    lines = [l for l in answer.splitlines() if l.strip()]
    if hits >= 2 or (hits and len(lines) >= 3):
        return "it is laid out like a chatbot reply"
    return None


def ai_assessment(reason):
    """An AI-looking answer scores nothing, like a copied hint."""
    return {**copied_assessment(), "copied_hint": False, "ai_like": reason}
