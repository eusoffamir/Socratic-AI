"""Class-level mastery with the DINA model (Goal 1, step 5).

Why DINA and not plain factor analysis: the skill check answers are 1s and 0s,
and every question is already tagged with the skills it needs (its reasoning
type and its knowledge type). That table of tags is called a Q-matrix. DINA
("deterministic inputs, noisy and gate") uses it directly. A learner should
get a question right only if they have mastered ALL the skills it needs, but
they can still slip (wrong although mastered) or guess (right although not
mastered). The model estimates the slip and guess of every question and, for
every learner, the chance they have mastered each skill. Factor analysis would
have to discover the skills from scratch and is built for continuous scores.
Please check the source before citing (DINA is usually credited to Junker and
Sijtsma, 2001).

It needs many learners, so it runs offline, not in the app. Pure Python, so
it runs on both laptops without numpy.

Run from the project folder:
    python eval/dina.py --simulate             -> checks the method on fake learners with known skills
    python eval/dina.py                        -> real skill checks from wherever the app saves
                                                  -> eval/exports/dina_<date>.csv
"""
import argparse
import csv
import math
import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.skillcheck import ITEMS  # noqa: E402
from app.stats import SKILLS  # noqa: E402

ATTRS = [name for _, name in SKILLS]
LIMIT = (0.01, 0.49)  # slip and guess stay below 50%, so mastering a skill always helps


def q_matrix(items=ITEMS, attrs=ATTRS):
    """{item id: bit mask of the skills it needs}."""
    return {i: (1 << attrs.index(it["reasoning"])) | (1 << attrs.index(it["knowledge"])) for i, it in items.items()}


def fit(responses, q, n_attrs, iters=100, tol=1e-5):
    """EM for DINA. responses: one {item id: 0 or 1} per learner (questions not
    asked are simply missing). Returns slip, guess, the class weights and, per
    learner, the chance of mastering each skill."""
    classes = range(1 << n_attrs)
    items = sorted(q)
    slip = {j: 0.2 for j in items}
    guess = {j: 0.2 for j in items}
    prior = [1 / (1 << n_attrs)] * (1 << n_attrs)
    eta = {j: [int(c & q[j] == q[j]) for c in classes] for j in items}
    last = -math.inf
    for _ in range(iters):
        # E-step: each learner's chance of being in each skill profile
        post, loglik = [], 0.0
        for resp in responses:
            logs = []
            for c in classes:
                lp = math.log(prior[c] + 1e-300)
                for j, x in resp.items():
                    p = 1 - slip[j] if eta[j][c] else guess[j]
                    lp += math.log(p if x else 1 - p)
                logs.append(lp)
            top = max(logs)
            w = [math.exp(v - top) for v in logs]
            total = sum(w)
            loglik += top + math.log(total)
            post.append([v / total for v in w])
        # M-step: new slip, guess and class weights
        for j in items:
            n1 = r1 = n0 = r0 = 0.0
            for resp, pc in zip(responses, post):
                if j not in resp:
                    continue
                m = sum(pc[c] for c in classes if eta[j][c])
                n1 += m
                r1 += m * resp[j]
                n0 += 1 - m
                r0 += (1 - m) * resp[j]
            if n1 > 0:
                slip[j] = min(max(1 - r1 / n1, LIMIT[0]), LIMIT[1])
            if n0 > 0:
                guess[j] = min(max(r0 / n0, LIMIT[0]), LIMIT[1])
        prior = [sum(pc[c] for pc in post) / len(post) for c in classes]
        if loglik - last < tol:
            break
        last = loglik
    skills = [[sum(pc[c] for c in classes if c >> k & 1) for k in range(n_attrs)] for pc in post]
    return {"slip": slip, "guess": guess, "prior": prior, "skills": skills, "loglik": loglik}


def simulate(n_learners, per_learner, q, n_attrs, slip=0.1, guess=0.2, seed=0):
    """Fake learners with known skills, each answering a random set of questions."""
    rng = random.Random(seed)
    truth, responses = [], []
    items = sorted(q)
    for _ in range(n_learners):
        profile = rng.randrange(1 << n_attrs)
        resp = {}
        for j in rng.sample(items, per_learner):
            p = 1 - slip if profile & q[j] == q[j] else guess
            resp[j] = int(rng.random() < p)
        truth.append(profile)
        responses.append(resp)
    return truth, responses


def accuracy(truth, skills, n_attrs):
    """Share of (learner, skill) pairs where the model's call matches the truth."""
    hits = sum(int((p >= 0.5) == bool(t >> k & 1)) for t, row in zip(truth, skills) for k, p in enumerate(row))
    return hits / (len(truth) * n_attrs)


def real_responses():
    """One respondent per skill check, or per participant code when there is one."""
    from app import storage
    by = {}
    for sid, s, _ in storage.all_sessions():
        if s.get("mode") != "skill_check":
            continue
        key = s.get("participant_code") or sid
        for t in s.get("turns", []):
            by.setdefault(key, {})[t["item"]] = t["attained"]
    return by


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--simulate", action="store_true")
    ap.add_argument("--learners", type=int, default=100)
    ap.add_argument("--per-learner", type=int, default=18, help="questions per fake learner (3 checks = 18)")
    ap.add_argument("out", nargs="?")
    args = ap.parse_args()
    q = q_matrix()
    if args.simulate:
        truth, responses = simulate(args.learners, args.per_learner, q, len(ATTRS))
        model = fit(responses, q, len(ATTRS), iters=40)
        acc = accuracy(truth, model["skills"], len(ATTRS))
        print(f"{args.learners} fake learners, {args.per_learner} questions each, true slip 10% and guess 20%.")
        print(f"The model called {round(100 * acc)}% of the learner and skill pairs right (50% would be chance).")
        print(f"Average slip found {round(100 * sum(model['slip'].values()) / len(q))}%, "
              f"average guess found {round(100 * sum(model['guess'].values()) / len(q))}%.")
        return
    by = real_responses()
    if len(by) < 2:
        print(f"Only {len(by)} skill check respondents saved so far, so there is nothing to fit yet.")
        return
    keys = sorted(by)
    model = fit([by[k] for k in keys], q, len(ATTRS))
    out = Path(args.out or ROOT / "eval" / "exports" / f"dina_{date.today()}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["respondent", "answers", *[f"p_{a}" for a in ATTRS]])
        for k, row in zip(keys, model["skills"]):
            w.writerow([k, len(by[k]), *[round(p, 3) for p in row]])
    print(f"{len(keys)} respondents written to {out}.")
    if len(keys) < 50:
        print("Fewer than 50 respondents, so treat these numbers as a rough first look only.")


if __name__ == "__main__":
    main()
