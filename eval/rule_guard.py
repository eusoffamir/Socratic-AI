"""A data guard for rules an AI model drafts (graph build test, 28 November 2026).

The AI-drafted graph test found that 1 of 5 Gemini drafts had a hidden mistake
(the overstrain limit 11,000 for every product type), and the real manual test
found rules mapped to the wrong sensor. A person reading the rule may not see
it. So before a drafted rule is used, it is checked against past records:

    caught       of the past runs with this fault, how many the rule fires on
    false alarm  of the past runs without this fault (healthy or another
                 fault), how many it fires on

The app lets a rule only rule a fault out (app/diagnose.py), and for that it
must almost never miss its fault, so a rule may RULE OUT when it catches at
least MIN_CAUGHT. It may also NAME the fault on its own only when its false
alarms stay under MAX_FALSE_ALARM and every limit sits close to where the
faults really start in the data, for each product type (a limit more than
LIMIT_GAP looser than the data needs is a sign of a wrong number, like 11,000
for type M, whose faults start near 12,000). Otherwise it is FLAGGED for a person to fix.
The limits are set from the rules the dataset's authors published (every one
of them may rule out), not tuned on the AI drafts. A rule whose readings are
missing cannot be checked.

    python -m eval.rule_guard          the published rules and the 5 saved AI drafts
"""
import json

MIN_CAUGHT = 0.95
MAX_FALSE_ALARM = 0.02
MIN_RECORDS = 10  # fewer past runs of a fault than this, and the rule cannot be judged
LIMIT_GAP = 0.05  # a limit this much looser than the data's edge is reported
MIN_GROUP = 5     # fewer fault runs of a type than this, and its limit is not judged


def loose_limits(rule, records, fault, values):
    """Limits that are much looser than where the faults start in the data, per
    product type, as plain sentences. values(record) gives every reading."""
    from eval.graph_build_ai import holds as alt_holds
    out = []
    for alt in rule or []:
        for t in sorted({r["type"] for r in records}):
            fault_vals = [values(r) for r in records if r[fault] == 1 and r["type"] == t]
            fault_vals = [v for v in fault_vals if alt_holds([alt], v)]
            if len(fault_vals) < MIN_GROUP:
                continue
            for c in alt:
                limit = c.get("value_by_type") or c.get("value")
                limit = limit.get(t) if isinstance(limit, dict) else limit
                if limit is None:
                    continue
                xs = [v[c["reading"]] for v in fault_vals]
                if c["op"] in (">", ">="):
                    edge, loose = min(xs), min(xs) > limit + LIMIT_GAP * abs(limit)
                else:
                    edge, loose = max(xs), max(xs) < limit - LIMIT_GAP * abs(limit)
                if loose:
                    out.append(f"for type {t} the limit {c['reading']} {c['op']} {limit:,g} is loose, "
                               f"since its faults start at {edge:,.0f}" if abs(edge) >= 100 else f"since its faults start at {edge:.2f}")
    return out


def check(holds, records, fault, rule=None, values=None):
    """holds(record) gives True, False or None (a reading is missing).
    records have the fault flags (1 or 0). Returns the verdict "name",
    "rule_out", "flag" or None (cannot be checked), with the numbers and why."""
    with_fault = [r for r in records if r[fault] == 1]
    without = [r for r in records if r[fault] != 1]
    if len(with_fault) < MIN_RECORDS:
        return {"verdict": None, "why": f"only {len(with_fault)} past runs have this fault, so it cannot be judged"}
    got = [holds(r) for r in with_fault]
    if None in got:
        return {"verdict": None, "why": "a reading the rule needs is missing from the records"}
    caught = sum(got) / len(with_fault)
    false_alarm = sum(bool(holds(r)) for r in without) / len(without)
    loose = loose_limits(rule, records, fault, values) if rule and values else []
    verdict = ("flag" if caught < MIN_CAUGHT
               else "name" if false_alarm <= MAX_FALSE_ALARM and not loose else "rule_out")
    why = (f"it fires on {caught:.0%} of the {len(with_fault)} past runs with this fault "
           f"and on {false_alarm:.1%} of the others") + "".join(f", and {x}" for x in loose)
    return {"verdict": verdict, "caught": round(caught, 3), "false_alarm": round(false_alarm, 4),
            "loose": loose, "why": why}


def _records(rows, raw):
    """The AI4I runs with raw numbers, fault flags and "failed"."""
    from eval.pgm_ai4i import MODES
    return [{**raw[r["udi"]], **{m: r[m] for m in MODES}} for r in rows]


def main():
    from eval import graph_build_ai as ai
    from eval import pgm_ai4i as net
    from eval.graph_build_test import raw_numbers
    train, test = net.split(net.load())
    raw = raw_numbers()
    faults = ["TWF", "HDF", "PWF", "OSF"]  # RNF is random, so it has no rule to check
    published = {  # the dataset page's own rules, as in app/diagnose.rule_check
        "TWF": [[{"reading": "wear", "op": ">=", "value": 200}]],
        "HDF": [[{"reading": "gap", "op": "<", "value": 8.6}, {"reading": "speed", "op": "<", "value": 1380}]],
        "PWF": [[{"reading": "power", "op": "<", "value": 3500}], [{"reading": "power", "op": ">", "value": 9000}]],
        "OSF": [[{"reading": "strain", "op": ">", "value_by_type": {"L": 11000, "M": 12000, "H": 13000}}]],
    }
    derived = [{"name": "gap", "a": "process", "op": "minus", "b": "air"},
               {"name": "power", "a": "torque", "op": "times", "b": "speed", "factor": 0.10471975511965977},
               {"name": "strain", "a": "wear", "op": "times", "b": "torque"}]
    # The guard judges a rule on the past records it has, here the 7,000 training runs.
    # (The 3,000 test runs alone have too few faults of each type to judge a limit.)
    for name, rows in (("training runs", train),):
        recs = _records(rows, raw)
        print(f"\n== {name}, {len(recs)} runs ==")
        print("published rules")
        for m in faults:
            res = check(lambda r: ai.holds(published[m], ai.values(r, derived)), recs, m,
                        published[m], lambda r: ai.values(r, derived))
            print(f"  {m} {res['verdict']:8s} {res['why']}")
        drafts = [ai.parse(x["reply"]) for x in json.loads(ai.SAVED.read_text(encoding="utf-8"))]
        for i, d in enumerate(drafts, 1):
            if not d:
                continue
            rules = {f.get("id"): f.get("rule") for f in d["faults"]}
            out = []
            for m in faults:
                res = check(lambda r: ai.holds(rules.get(m), ai.values(r, d.get("derived"))), recs, m,
                            rules.get(m), lambda r: ai.values(r, d.get("derived")))
                out.append(f"{m} {res['verdict']}")
                if res["verdict"] != "name":
                    out[-1] += f" ({res['why']})"
            print(f"  AI draft {i}: " + "; ".join(out))


if __name__ == "__main__":
    main()
