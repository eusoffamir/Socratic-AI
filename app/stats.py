"""Statistics on the skill check trials (Goal 1, step 5).

Each skill check answer is one trial with a 1 or 0 (attained or not). This
module turns one learner's trials into:

1. A mastery estimate per skill (Beta-Binomial). Start from a flat prior,
   Beta(1, 1), add the 1s and 0s, and read off the most likely share, a 90%
   range, and the chance that the true share is at least MASTERY_LEVEL. This
   works with few trials and says honestly how unsure it is.
2. A Hamming distance between the learner's pattern of mastered skills and the
   all-mastered pattern, so "how far from full mastery" is one number, and the
   same distance before the last check shows the change.

The class-level model (DINA, across many learners) is in eval/dina.py, because
it needs many learners and runs offline.

Pure Python on purpose, because the server does not install numpy.
The thresholds are placeholders for Dr Ho to set.
"""
import math

from .reasoning import CORE_KNOWLEDGE, REASONING_TYPES

MASTERY_LEVEL = 0.6  # a skill counts as mastered when it is shown in at least 60% of questions
SURE = 0.8           # how sure the estimate must be before it says mastered or not mastered
MIN_TRIALS = 3       # fewer answers than this on a skill gives no verdict at all
SKILLS = [("reasoning", r) for r in REASONING_TYPES] + [("knowledge", k) for k in CORE_KNOWLEDGE]

_GRID = 2000  # points for the numeric integral, plenty for 2 decimal places


def hamming(a, b):
    """How many places two equal-length strings of 1s and 0s differ."""
    if len(a) != len(b):
        raise ValueError("Hamming distance needs two patterns of the same length.")
    return sum(x != y for x, y in zip(a, b))


def beta_estimate(attained, asked, prior=(1, 1)):
    """Most likely share, 90% range and chance of mastery, all as whole percentages."""
    a, b = prior[0] + attained, prior[1] + asked - attained
    log_norm = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    xs = [(i + 0.5) / _GRID for i in range(_GRID)]
    dens = [math.exp(log_norm + (a - 1) * math.log(x) + (b - 1) * math.log(1 - x)) / _GRID for x in xs]
    total = sum(dens)
    cdf, run = [], 0.0
    for d in dens:
        run += d / total
        cdf.append(run)
    low = next(x for x, c in zip(xs, cdf) if c >= 0.05)
    high = next(x for x, c in zip(xs, cdf) if c >= 0.95)
    chance = sum(d for x, d in zip(xs, dens) if x >= MASTERY_LEVEL) / total
    return {"mean": round(100 * a / (a + b)), "low": round(100 * low), "high": round(100 * high),
            "chance_mastered": round(100 * chance)}


def verdict(asked, chance_mastered):
    if asked < MIN_TRIALS:
        return "not enough answers"
    if chance_mastered >= 100 * SURE:
        return "mastered"
    if chance_mastered <= 100 * (1 - SURE):
        return "not mastered yet"
    return "not sure yet"


def _skill_rows(turns):
    rows = []
    for kind, name in SKILLS:
        mine = [t for t in turns if t[kind] == name]
        attained = sum(t["attained"] for t in mine)
        est = beta_estimate(attained, len(mine))
        rows.append({"skill": name, "kind": kind, "attained": attained, "asked": len(mine), **est,
                     "status": verdict(len(mine), est["chance_mastered"])})
    return rows


def _pattern(rows):
    return [int(r["status"] == "mastered") for r in rows]


def mastery(checks):
    """checks: the learner's skill checks in order, each a list of answered turns."""
    turns = [t for c in checks for t in c]
    rows = _skill_rows(turns)
    pattern, target = _pattern(rows), [1] * len(SKILLS)
    distance = hamming(pattern, target)
    before = None
    if len(checks) > 1:
        before = hamming(_pattern(_skill_rows([t for c in checks[:-1] for t in c])), target)
    return {"answers": len(turns), "checks": len(checks), "skills": rows, "pattern": pattern,
            "distance": distance, "previous_distance": before, "mastery_level": round(100 * MASTERY_LEVEL),
            "messages": _messages(rows, distance, before)}


def _messages(rows, distance, before):
    if not any(r["asked"] for r in rows):
        return []
    done = len(rows) - distance
    out = [f"You have mastered {done} of {len(rows)} skills, so {distance} are left."]
    if before is not None and before != distance:
        change = before - distance
        word = "more" if change > 0 else "fewer"
        out.append(f"That is {abs(change)} {word} than before your last check.")
    if all(r["asked"] < MIN_TRIALS for r in rows):
        out.append(f"Each skill needs at least {MIN_TRIALS} answers before it gets a verdict, so try another check.")
    return out
