"""Free checks on a Tutor reply, in plain code, before the (paid-for-in-quota)
Checker agent call. If any of these fail, the Tutor rewrites without needing
the Checker agent at all.
"""
from .prompts import AB_FORMAT, WORD_LIMITS

# Allow a few words over the limit given to the Tutor, so one extra word does
# not cost a whole rewrite call.
WORD_SLACK = 5


def _norm(text):
    return " ".join(text.lower().split()).rstrip("?")


def code_check(parts, instruction, asked_questions):
    """Return a list of short problems. Empty list means the reply passed."""
    problems = []
    for field, limit in WORD_LIMITS.items():
        if len(parts.get(field, "").split()) > limit + WORD_SLACK:
            problems.append(f"{field} is too long. Keep it under {limit} words.")

    question = parts.get("question", "")
    if not question:
        problems.append("question is missing. Ask exactly one question.")
    elif question.count("?") != 1:
        problems.append("question must contain exactly one question mark.")
    elif _norm(question) in {_norm(q) for q in asked_questions}:
        problems.append("This question was already asked. Ask a new one.")

    if instruction.get("format") == AB_FORMAT and len(parts.get("options", [])) != 2:
        problems.append("Format is A or B. Give exactly 2 short options.")
    return problems
