"""Which way of building the knowledge graph works best? (28 November 2026)

The same milling machine (AI4I 2020, see eval/pgm_ai4i.py) is built several
ways, matching families from the review (docs/thesis/drafts/kg-generation-review.md),
and every build is scored on the same failed test machines.

Builds
  rules_draft  the published rules in the checking order Claude drafted for the
             Knowledge page (tool wear first), families 2.1 and 2.12, "from books"
  rules      the same rules in the order that does best on the training runs
             (books for the rules, data for the order)
  nb         naive Bayes on raw readings, no graph learned (baseline)
  net_raw    Bayesian network learned from data, nodes are the raw readings (2.11)
  net_eng    the same, nodes are the readings an engineer would compute (2.11)
  net_blind  the engineer nodes, but the bands are cut at the data's own thirds,
             so no number from the book is used at all (data only)
  ai_rules   rules an AI model drafted from the dataset page text (family 2.9, saved
             drafts from eval/graph_build_ai.py), in the order best on the training runs
  ai_mix     net_eng ranks the faults, the AI-drafted rules may only rule one out
  mix        net_eng ranks the faults, and a rule may only rule a fault out:
             the top fault is named unless its rule can be checked and fails

Tests
  1 right cause, all readings known
  2 right cause, the torque sensor is missing (so torque, power and strain are unknown)
  3 right cause, the engineer remembers every limit 10% wrong (too strict, too loose)
  4 records needed, network learned on fewer past runs
  5 same every run, network learned on 5 different random splits
  6 arrows match the true causes (precision and recall)

Important limit. AI4I is synthetic and its failures were made by exactly the
published rules, so "rules" is right by design here. On a real plant the
rules are fuzzier, which test 3 imitates.

Run from the project folder (a few minutes):
    python -m eval.graph_build_test
"""
import itertools
import time

import csv

from eval import graph_build_ai as ai
from eval import pgm_ai4i as net

M = net.MODES
OSF_LIMIT = {"L": 11000, "M": 12000, "H": 13000}
DRAFT_ORDER = ["TWF", "OSF", "PWF", "HDF"]  # the checklist order first drafted in app/diagnose.TREE
NEEDS = {"TWF": ["wear"], "HDF": ["gap", "speed"], "PWF": ["power"], "OSF": ["strain"]}
NO_TORQUE = {"torque", "power", "strain"}
ALL = ["gap", "speed", "torque", "wear", "power", "strain"]


def failed(rows):
    return [r for r in rows if any(r[m] for m in M)]


# ---------- the rule builds ----------

def rule_holds(r, mode, k=0.0):
    """The published rule with every limit moved by k (k > 0 stricter, k < 0 looser)."""
    x = r["raw"]
    if mode == "TWF":
        return x["wear"] >= 200 * (1 + k)
    if mode == "HDF":
        return x["gap"] < 8.6 * (1 - k) and x["speed"] < 1380 * (1 - k)
    if mode == "PWF":
        return x["power"] < 3500 * (1 - k) or x["power"] > 9000 * (1 + k)
    if mode == "OSF":
        return x["strain"] > OSF_LIMIT[r["type"]] * (1 + k)


def rules_guess(r, known, k=0.0, order=DRAFT_ORDER):
    for m in order:
        if all(c in known for c in NEEDS[m]) and rule_holds(r, m, k):
            return m
    return "RNF"  # no rule fits, so the checklist ends at "random"


# ---------- the network builds ----------

def build(train, readings):
    t = time.time()
    parents = net.learn_structure(train, readings)
    return parents, net.learn_tables(parents, train), time.time() - t


def net_guess(model, r, known):
    parents, tables = model[0], model[1]
    ev = {"type": r["type"], "failed": 1, **{c: r[c] for c in known if c in parents}}
    ch = net.mode_chances(parents, tables, ev)
    return max(ch, key=ch.get), ch


def best_order(rows):
    """The checking order that names the right fault most often on these runs."""
    f = failed(rows)
    return list(max(itertools.permutations(DRAFT_ORDER),
                    key=lambda o: sum(r[rules_guess(r, ALL, 0.0, o)] == 1 for r in f)))


def mix_guess(model, r, known, k=0.0):
    """Rules guard: walk the network's ranking and skip a fault only when its rule
    can be checked and does not hold (a rule can refute, it never jumps the queue)."""
    _, ch = net_guess(model, r, known)
    for m in sorted(ch, key=ch.get, reverse=True):
        if m in NEEDS and (not all(c in known for c in NEEDS[m]) or rule_holds(r, m, k)):
            return m
    return max(ch, key=ch.get)  # every rule refuted, so trust the network (random failure included)


def blind(rows, train):
    """Copies of the rows with the engineer readings cut at the training data's thirds
    (half for the gap), instead of at the book's limits."""
    cuts = {}
    for c in ["gap", "speed", "torque", "wear", "power", "strain"]:
        vals = sorted(r["raw"][c] for r in train)
        parts = 2 if c == "gap" else 3
        cuts[c] = [vals[len(vals) * i // parts] for i in range(1, parts)]
    out = []
    for r in rows:
        r2 = dict(r)
        for c, cs in cuts.items():
            r2[c] = net._band(r["raw"][c], cs, net.VALUES[c])
        out.append(r2)
    return out


# ---------- the AI-drafted builds ----------

def raw_numbers():
    """The raw readings of every run as numbers, by run id, for the AI's rules."""
    out = {}
    with open(net.DATA, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            out[int(r["UDI"])] = {"type": r["Type"], "air": float(r["Air temperature [K]"]),
                                  "process": float(r["Process temperature [K]"]),
                                  "speed": float(r["Rotational speed [rpm]"]), "torque": float(r["Torque [Nm]"]),
                                  "wear": float(r["Tool wear [min]"])}
    return out


RAW_NUM = None


def ai_values(r, d, no_torque=False):
    v = dict(RAW_NUM[r["udi"]])
    if no_torque:
        v.pop("torque")
    return ai.values(v, d.get("derived"))


def ai_rules_of(d):
    return {f.get("id"): f.get("rule") for f in d["faults"] if f.get("id") in NEEDS}


def ai_guess(d, r, no_torque, order):
    v, rules = ai_values(r, d, no_torque), ai_rules_of(d)
    for m in order:
        if m in rules and ai.holds(rules[m], v):
            return m
    return "RNF"


def ai_order(d, rows):
    f = failed(rows)
    return list(max(itertools.permutations(DRAFT_ORDER),
                    key=lambda o: sum(r[ai_guess(d, r, False, o)] == 1 for r in f)))


def ai_mix_guess(d, model, r, known, no_torque):
    _, ch = net_guess(model, r, known)
    v, rules = ai_values(r, d, no_torque), ai_rules_of(d)
    for m in sorted(ch, key=ch.get, reverse=True):
        if m in rules and ai.holds(rules[m], v) is not False:
            return m
    return max(ch, key=ch.get)


def ai_report(train, test, eng):
    global RAW_NUM
    if not ai.SAVED.exists():
        print("AI-drafted graph: no saved drafts, run eval.graph_build_ai first\n")
        return
    RAW_NUM = raw_numbers()
    runs = __import__("json").loads(ai.SAVED.read_text(encoding="utf-8"))
    drafts = [ai.parse(x["reply"]) for x in runs]
    ok = [d for d in drafts if d]
    print(f"AI-drafted graph (family 2.9), {len(runs)} runs, {len(ok)} usable, "
          f"{len({x['reply'] for x in runs if x['reply']})} different replies, models {sorted({m for x in runs for m in x['models']})}")
    tokens = sum(x["chars_in"] + x["chars_out"] for x in runs) / len(runs) / 4
    print(f"  about {tokens:,.0f} tokens per draft (characters / 4)")
    known_nt = [c for c in ALL if c not in NO_TORQUE]
    for i, d in enumerate(drafts, 1):
        if not d:
            print(f"  run {i}: not usable")
            continue
        cz = ai.canonical(d)
        right = sum(len(cz.get(m, set()) & net.TRUE_PARENTS[m]) for m in M)
        got = sum(len(cz.get(m, set())) for m in M)
        order = ai_order(d, train)
        a, n = score(lambda r: ai_guess(d, r, False, order), test)
        b, _ = score(lambda r: ai_guess(d, r, True, order), test)
        c, _ = score(lambda r: ai_mix_guess(d, eng, r, ALL, False), test)
        e, _ = score(lambda r: ai_mix_guess(d, eng, r, known_nt, True), test)
        print(f"  run {i}: arrows right {right} of 6, {got - right} extra, power factor ok {ai.check_power_factor(d)}"
              f" | ai_rules {pct(a, n)} all, {pct(b, n)} no torque | ai_mix {pct(c, n)} all, {pct(e, n)} no torque")
    print()


def score(guess, rows):
    f = failed(rows)
    return sum(r[guess(r)] == 1 for r in f), len(f)


def arrows(parents):
    got = {(p, m) for m in M for p in parents[m]}
    true = {(p, m) for m, ps in net.TRUE_PARENTS.items() for p in ps}
    right = len(got & true)
    return right, len(got), len(true)


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "-"


def main():
    rows = net.load()
    train, test = net.split(rows)
    known_all, known_nt = ALL, [c for c in ALL if c not in NO_TORQUE]
    print(f"Learn on {len(train)} runs, test on {len(failed(test))} failed machines\n")

    raw = build(train, net.RAW)
    eng = build(train, net.ENGINEER)
    btrain, btest = blind(train, train), blind(test, train)
    bl = build(btrain, net.ENGINEER)
    nb = net.naive_bayes(train, net.RAW)
    raw_known = {"all": net.RAW[1:], "nt": [c for c in net.RAW[1:] if c != "torque"]}

    order = best_order(train)
    print("Checking order learned from the training runs:", ", ".join(order), "\n")
    builds = {
        "rules_draft": (lambda r, kn: rules_guess(r, kn), test),
        "rules": (lambda r, kn: rules_guess(r, kn, 0.0, order), test),
        "nb": (lambda r, kn: nb(r), test),
        "net_raw": (lambda r, kn: net_guess(raw, r, raw_known["all" if kn is known_all else "nt"])[0], test),
        "net_eng": (lambda r, kn: net_guess(eng, r, kn)[0], test),
        "net_blind": (lambda r, kn: net_guess(bl, r, kn)[0], btest),
        "mix": (lambda r, kn: mix_guess(eng, r, kn), test),
    }
    print("Tests 1 and 2, right cause")
    print(f"  {'build':12} {'all readings':>14} {'no torque':>12}")
    for name, (g, rs) in builds.items():
        a, n = score(lambda r: g(r, known_all), rs)
        b, _ = score(lambda r: g(r, known_nt), rs) if name != "nb" else (None, n)
        print(f"  {name:12} {a:>4} of {n} {pct(a, n):>4}   " + (f"{b:>3} of {n} {pct(b, n):>4}" if b is not None else "   (needs all)"))
    print()

    ai_report(train, test, eng)

    print("Test 3, every limit 10% wrong (all readings)")
    for k, word in ((0.1, "too strict"), (-0.1, "too loose")):
        a, n = score(lambda r: rules_guess(r, known_all, k, order), test)
        b, _ = score(lambda r: mix_guess(eng, r, known_all, k), test)
        print(f"  {word:10}  rules {a} of {n} {pct(a, n)}   mix {b} of {n} {pct(b, n)}")
    print()

    print("Test 4, records needed (network, all readings)")
    for size in (250, 500, 1000, 2000, 4000, 7000):
        part = train[:size]
        line = f"  {size:>5} runs ({len(failed(part)):>3} failures)"
        for name, readings, kn in (("raw", net.RAW, net.RAW[1:]), ("eng", net.ENGINEER, known_all)):
            mdl = build(part, readings)
            a, n = score(lambda r: net_guess(mdl, r, kn)[0], test)
            line += f"   {name} {pct(a, n):>4}"
        print(line)
    print()

    print("Tests 5 and 6, five random splits: arrows into the faults vs the true causes")
    for name, readings in (("raw", net.RAW), ("eng", net.ENGINEER)):
        sets = []
        for seed in range(1, 6):
            tr, _ = net.split(rows, seed=seed)
            p, _, secs = build(tr, readings)
            sets.append(frozenset((q, m) for m in M for q in p[m]))
            right, got, true = arrows(p)
            print(f"  {name} seed {seed}  right {right} of {true} true arrows, {got - right} extra, {secs:.0f} s")
        print(f"  {name}: {len(set(sets))} different graph(s) from 5 splits")
    for name, mdl in (("blind", bl),):
        right, got, true = arrows(mdl[0])
        print(f"  {name} (seed 7)  right {right} of {true} true arrows, {got - right} extra")
    print("\nCost: every build here is plain code, 0 model tokens.")


if __name__ == "__main__":
    main()
