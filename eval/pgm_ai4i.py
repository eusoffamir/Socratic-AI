"""A small Bayesian network on an open dataset (Meeting 3, task 8).

Proof of concept for Dr Ho, using what we read in Koller and Friedman (2009)
(notes in docs/industrial/pgm-reading.md, results in docs/industrial/pgm-ai4i.md).

Data: the AI4I 2020 Predictive Maintenance Dataset (UCI, CC BY 4.0,
https://doi.org/10.24432/C5HS5C, introduced by Matzka, 2020). 10,000 machine
runs with readings and five failure modes. It is synthetic, and the rule behind
each failure mode is published, so we know the true causes and can check
whether the network finds them.

What it does, all in plain Python (no numpy, like eval/dina.py):
1. Cuts each reading into a few named values (the "clarity test", Box 3.C).
   Two sets of variables: RAW readings only, and ENGINEER variables that add
   the temperature gap, the power and the strain an engineer would compute.
2. Learns the arrows with the BIC score and greedy hill climbing (Ch 18),
   with the time order as knowledge: readings may point to failure modes, a
   failure mode never points back.
3. Learns the chances by counting plus 1 imaginary record per value (Ch 17).
4. Tests on held-out records (Box 16.A): which failure mode, and which machines
   to look at first.
5. Picks the next reading to check for a failed machine by value of
   information (Ch 23.7), using exact inference by variable elimination (Ch 9).

Run from the project folder:
    python eval/pgm_ai4i.py
"""
import csv
import itertools
import math
import random
from pathlib import Path

DATA = Path(__file__).parent / "data" / "ai4i2020.csv"
MODES = ["TWF", "HDF", "PWF", "OSF", "RNF"]
MODE_NAMES = {"TWF": "tool wear", "HDF": "heat dissipation", "PWF": "power",
              "OSF": "overstrain", "RNF": "random"}
# The causes as the dataset page describes them (the "truth" we check against).
TRUE_PARENTS = {"TWF": {"wear"}, "HDF": {"gap", "speed"}, "PWF": {"power"},
                "OSF": {"strain", "type"}, "RNF": set()}
SEED = 7
MAX_PARENTS = 3


# ---------- 1. Variables ----------

def _band(x, cuts, names):
    for cut, name in zip(cuts, names):
        if x < cut:
            return name
    return names[-1]


def load(path=DATA):
    """Each record as named values. RAW and ENGINEER variables are both kept."""
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            air, proc = float(r["Air temperature [K]"]), float(r["Process temperature [K]"])
            speed, torque = float(r["Rotational speed [rpm]"]), float(r["Torque [Nm]"])
            wear = float(r["Tool wear [min]"])
            power = torque * speed * 2 * math.pi / 60
            row = {
                "type": r["Type"],
                "air": _band(air, [299, 301], ["cool", "mid", "warm"]),
                "process": _band(proc, [309.5, 311], ["cool", "mid", "warm"]),
                "speed": _band(speed, [1380, 1800], ["slow", "normal", "fast"]),
                "torque": _band(torque, [30, 50], ["low", "mid", "high"]),
                "wear": _band(wear, [200, 240], ["new", "worn", "old"]),
                "gap": _band(proc - air, [8.6], ["small", "normal"]),
                "power": _band(power, [3500, 9000], ["low", "normal", "high"]),
                "strain": _band(wear * torque, [11000, 13000], ["low", "mid", "high"]),
            }
            row.update({m: int(r[m]) for m in MODES})
            # the real numbers, for showing a reading on the diagnosis page (app/diagnose.py)
            row["udi"], row["pid"] = int(r["UDI"]), r["Product ID"]
            row["raw"] = {"gap": proc - air, "speed": speed, "torque": torque, "wear": wear,
                          "power": power, "strain": wear * torque}
            rows.append(row)
    return rows


VALUES = {"type": ("L", "M", "H"), "air": ("cool", "mid", "warm"), "process": ("cool", "mid", "warm"),
          "speed": ("slow", "normal", "fast"), "torque": ("low", "mid", "high"),
          "wear": ("new", "worn", "old"), "gap": ("small", "normal"),
          "power": ("low", "normal", "high"), "strain": ("low", "mid", "high"),
          **{m: (0, 1) for m in MODES}, "failed": (0, 1)}
RAW = ["type", "air", "process", "speed", "torque", "wear"]
ENGINEER = ["type", "gap", "speed", "torque", "wear", "power", "strain"]


def split(rows, share=0.7, seed=SEED):
    rows = rows[:]
    random.Random(seed).shuffle(rows)
    cut = int(len(rows) * share)
    return rows[:cut], rows[cut:]


# ---------- 2. Learning the arrows (BIC, hill climbing) ----------

def bic_family(x, parents, rows):
    """Fit of x given its parents minus half log(records) per free number (Ch 18.3.5)."""
    counts = {}
    for r in rows:
        key = tuple(r[p] for p in parents)
        counts.setdefault(key, {})
        counts[key][r[x]] = counts[key].get(r[x], 0) + 1
    fit = sum(c * math.log(c / sum(row.values())) for row in counts.values() for c in row.values())
    free = (len(VALUES[x]) - 1) * math.prod(len(VALUES[p]) for p in parents)
    return fit - math.log(len(rows)) / 2 * free


def _allowed(a, b, readings):
    """Knowledge as a rule: readings come first, so a failure mode never points
    to a reading, and failure modes do not point to each other."""
    return a in readings and a != b


def _cyclic(parents):
    seen, stack = set(), set()

    def visit(v):
        if v in stack:
            return True
        if v in seen:
            return False
        seen.add(v)
        stack.add(v)
        found = any(visit(p) for p in parents[v])
        stack.discard(v)
        return found
    return any(visit(v) for v in parents)


def learn_structure(rows, readings):
    """Greedy hill climbing over single arrow changes (add, remove, reverse)."""
    nodes = readings + MODES
    parents = {v: () for v in nodes}
    cache = {}

    def fam(x, ps):
        key = (x, ps)
        if key not in cache:
            cache[key] = bic_family(x, list(ps), rows)
        return cache[key]

    while True:
        best_gain, best = 1e-9, None
        for a, b in itertools.permutations(nodes, 2):
            pb = parents[b]
            if a in pb:
                options = [(b, tuple(p for p in pb if p != a), None)]
                if _allowed(b, a, readings) and len(parents[a]) < MAX_PARENTS:
                    options.append((b, tuple(p for p in pb if p != a), (a, tuple(sorted(parents[a] + (b,))))))
            elif _allowed(a, b, readings) and len(pb) < MAX_PARENTS and b not in parents[a]:
                options = [(b, tuple(sorted(pb + (a,))), None)]
            else:
                continue
            for node, new_ps, other in options:
                trial = dict(parents)
                trial[node] = new_ps
                gain = fam(node, new_ps) - fam(node, parents[node])
                if other:
                    trial[other[0]] = other[1]
                    gain += fam(other[0], other[1]) - fam(other[0], parents[other[0]])
                if gain > best_gain and not _cyclic(trial):
                    best_gain, best = gain, trial
        if best is None:
            return parents
        parents = best


# ---------- 3. Learning the chances ----------

def learn_tables(parents, rows):
    """Counts plus 1 imaginary record per value (Laplace, Ch 17.3)."""
    tables = {}
    for x, ps in parents.items():
        counts = {}
        for r in rows:
            key = tuple(r[p] for p in ps)
            counts.setdefault(key, {})
            counts[key][r[x]] = counts[key].get(r[x], 0) + 1
        table = {}
        for key in itertools.product(*(VALUES[p] for p in ps)):
            row = counts.get(key, {})
            total = sum(row.values()) + len(VALUES[x])
            for v in VALUES[x]:
                table[key + (v,)] = (row.get(v, 0) + 1) / total
        tables[x] = table
    return tables


# ---------- 4. Held-out tests ----------

def chance_of_mode(m, parents, tables, row):
    return tables[m][tuple(row[p] for p in parents[m]) + (1,)]


def diagnose(parents, tables, row):
    """The failure mode with the highest chance given all readings."""
    return max(MODES, key=lambda m: chance_of_mode(m, parents, tables, row))


def chance_of_failure(parents, tables, row):
    """At least one mode happens. Modes are independent once the readings are known."""
    return 1 - math.prod(1 - chance_of_mode(m, parents, tables, row) for m in MODES)


def naive_bayes(train, readings):
    """Baseline (Box 3.A, 17.A): one fault class for failed records, readings
    independent given the class."""
    failed = [r for r in train if any(r[m] for m in MODES)]
    label = lambda r: next(m for m in MODES if r[m])
    prior = {m: (sum(label(r) == m for r in failed) + 1) / (len(failed) + len(MODES)) for m in MODES}
    cond = {}
    for m in MODES:
        group = [r for r in failed if label(r) == m]
        for x in readings:
            for v in VALUES[x]:
                cond[m, x, v] = (sum(r[x] == v for r in group) + 1) / (len(group) + len(VALUES[x]))
    return lambda row: max(MODES, key=lambda m: math.log(prior[m]) + sum(math.log(cond[m, x, row[x]]) for x in readings))


def accuracy(guess, rows):
    failed = [r for r in rows if any(r[m] for m in MODES)]
    return sum(r[guess(r)] == 1 for r in failed) / len(failed), len(failed)


def top_k_hits(score, rows):
    """Rank machines by chance of failure and count real failures in the top k,
    where k is the number of real failures."""
    k = sum(any(r[m] for m in MODES) for r in rows)
    ranked = sorted(rows, key=score, reverse=True)[:k]
    return sum(any(r[m] for m in MODES) for r in ranked), k


# ---------- 5. Exact inference and value of information ----------

def _factors(parents, tables, evidence):
    """One factor per node, with the evidence put in, plus a fixed OR node
    "failed" over the five modes (Ch 5.2)."""
    fs = []
    for x, ps in parents.items():
        scope = list(ps) + [x]
        fs.append((tuple(scope), {k: v for k, v in tables[x].items()
                                  if all(evidence.get(s, k[i]) == k[i] for i, s in enumerate(scope))}))
    scope = tuple(MODES) + ("failed",)
    fs.append((scope, {k: float(k[-1] == int(any(k[:-1])))
                       for k in itertools.product(*(VALUES[s] for s in scope))
                       if all(evidence.get(s, k[i]) == k[i] for i, s in enumerate(scope))}))
    return fs


def _multiply(fs):
    scope = tuple(dict.fromkeys(v for s, _ in fs for v in s))
    table = {}
    domains = [VALUES[v] for v in scope]
    for k in itertools.product(*domains):
        a = dict(zip(scope, k))
        p = 1.0
        for s, t in fs:
            p *= t.get(tuple(a[v] for v in s), 0.0)
            if p == 0.0:
                break
        if p:
            table[k] = p
    return scope, table


def _sum_out(factor, var):
    scope, table = factor
    i = scope.index(var)
    out = {}
    for k, p in table.items():
        key = k[:i] + k[i + 1:]
        out[key] = out.get(key, 0.0) + p
    return scope[:i] + scope[i + 1:], out


def query(parents, tables, targets, evidence):
    """Chance of each value of each target given the evidence, by variable
    elimination (Ch 9), eliminating first the variable in the fewest factors."""
    fs = _factors(parents, tables, evidence)
    hidden = {v for s, _ in fs for v in s} - set(evidence) - set(targets)
    while hidden:
        var = min(hidden, key=lambda v: sum(v in s for s, _ in fs))
        use = [f for f in fs if var in f[0]]
        fs = [f for f in fs if var not in f[0]] + [_sum_out(_multiply(use), var)]
        hidden.discard(var)
    scope, table = _multiply(fs)
    total = sum(table.values())
    out = {}
    for t in targets:
        i = scope.index(t)
        out[t] = {v: sum(p for k, p in table.items() if k[i] == v) / total for v in VALUES[t]}
    return out


def mode_chances(parents, tables, evidence):
    got = query(parents, tables, MODES, evidence)
    return {m: got[m][1] for m in MODES}


def value_of_information(parents, tables, evidence, checks):
    """For each check, how much it raises the chance of naming the right mode
    (the utility is 1 for a right diagnosis), Ch 23.7."""
    now = max(mode_chances(parents, tables, evidence).values())
    out = {}
    for c in checks:
        p_c = query(parents, tables, [c], evidence)[c]
        after = sum(p * max(mode_chances(parents, tables, {**evidence, c: v}).values())
                    for v, p in p_c.items() if p > 1e-12)
        out[c] = after - now
    return now, out


# ---------- Report ----------

def _arrows(parents):
    return {m: set(parents[m]) for m in MODES}


def main():
    rows = load()
    train, test = split(rows)
    print(f"Records {len(rows)}, learn on {len(train)}, test on {len(test)} (seed {SEED})\n")

    nets = {}
    for name, readings in (("raw", RAW), ("engineer", ENGINEER)):
        parents = learn_structure(train, readings)
        nets[name] = (parents, learn_tables(parents, train))
        print(f"{name.upper()} variables, learned parents of each failure mode:")
        for m in MODES:
            true = TRUE_PARENTS[m]
            print(f"  {m} ({MODE_NAMES[m]}): {sorted(parents[m]) or '-'}   true causes: {sorted(true) or '-'}")
        print()

    print("Which failure mode, on failed test records (right if the named mode really happened):")
    nb = naive_bayes(train, RAW)
    common = max(MODES, key=lambda m: sum(r[m] for r in train))
    for name, guess in (("most common mode only", lambda r: common),
                        ("naive Bayes, raw readings", nb),
                        ("network, raw variables", lambda r: diagnose(*nets["raw"], r)),
                        ("network, engineer variables", lambda r: diagnose(*nets["engineer"], r))):
        acc, n = accuracy(guess, test)
        print(f"  {name:30} {acc:6.1%} of {n}")
    print()

    print("Which machines to look at first (real failures in the top k, k = number of real failures):")
    base = sum(any(r[m] for m in MODES) for r in test) / len(test)
    for name in ("raw", "engineer"):
        hits, k = top_k_hits(lambda r: chance_of_failure(*nets[name], r), test)
        print(f"  network, {name:9} variables  {hits} of {k}  (random order would find about {base * k:.0f})")
    print()

    parents, tables = nets["engineer"]
    checks = ["gap", "speed", "torque", "wear", "power", "strain"]
    print("A machine has failed and only its type is known. Value of each check (engineer network):")
    for t in VALUES["type"]:
        now, voi = value_of_information(parents, tables, {"type": t, "failed": 1}, checks)
        ranked = sorted(voi.items(), key=lambda kv: -kv[1])
        print(f"  type {t}: right now {now:.0%}; " + ", ".join(f"{c} +{v:.0%}" for c, v in ranked))
    print()

    print("Myopic check sequence on the first 5 failed test machines (stop at 90 percent):")
    for r in [r for r in test if any(r[m] for m in MODES)][:5]:
        evidence, steps = {"type": r["type"], "failed": 1}, []
        left = checks[:]
        while left:
            now, voi = value_of_information(parents, tables, evidence, left)
            if now >= 0.9:
                break
            best = max(left, key=voi.get)
            evidence[best] = r[best]
            left.remove(best)
            steps.append(f"{best}={r[best]}")
        chances = mode_chances(parents, tables, evidence)
        named = max(chances, key=chances.get)
        truth = [m for m in MODES if r[m]]
        print(f"  checks {', '.join(steps) or 'none'} -> {named} {chances[named]:.0%}  (really {', '.join(truth)})")


if __name__ == "__main__":
    main()
