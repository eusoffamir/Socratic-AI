"""The graph build test on real data: MetroPT-3 (28 November 2026).

Real sensor data from the air production unit (compressor) of a metro train in
Porto, February to August 2020, about one reading every 10 seconds. Davari, Veloso,
Ribeiro and Gama (2021), UCI, https://doi.org/10.24432/C5VW3R, CC BY 4.0.
The only labels are the operator's 4 failure reports, all air leaks (FAILURES below,
as printed on the UCI page). So this test asks "is this hour a leak?", not "which
fault is it?", and with only 4 leaks every number here is weak evidence.

Builds (the same families as eval/graph_build_test.py)
  rule      leak physics from the sensor notes: a leak makes the compressor load more,
            so score an hour by its share of time under load (no training)
  ai_rule   Gemini reads the UCI sensor notes and picks which hourly readings rise or
            fall in a leak (saved in eval/data/metropt_ai_rule.json); score is the sum of
            how far each one is from normal, in its direction
  net_raw   naive Bayes network on the hourly mean of the 7 analogue sensors (data only)
  net_eng   the same, on readings an engineer would compute: share of time under load,
            compressor starts, lowest panel pressure, share of time under 7 bar
  mix       net_eng, but an hour whose load share is not above normal scores 0
            (the rule may only rule a leak out)

Networks are trained leaving one leak out and tested on that leak plus the 3 days
either side. Scores per build
  rank     chance a leak hour scores above a normal hour of the same test block (AUC)
  caught   leaks with an alarm in them, at a limit allowing about 1 false alarm a day
            in the other data

Run (the CSV is 208 MB, kept outside the repo):
    python -m eval.metropt_test "path/to/MetroPT3(AirCompressor).csv"
"""
import csv
import json
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path

FAILURES = [("2020-04-18 00:00", "2020-04-18 23:59"), ("2020-05-29 23:30", "2020-05-30 06:00"),
            ("2020-06-05 10:00", "2020-06-07 14:30"), ("2020-07-15 14:30", "2020-07-15 19:00")]
ANALOG = ["TP2", "TP3", "H1", "DV_pressure", "Reservoirs", "Oil_temperature", "Motor_current"]
DIGITAL = ["COMP", "DV_eletric", "Towers", "MPG", "LPS", "Pressure_switch", "Oil_level", "Caudal_impulses"]
ENG = ["load_share", "starts", "tp3_min", "lps_share"]
LOADED = 5.5  # A, between "about 4 A offloaded" and "about 7 A under load" (UCI page)
MIN_SAMPLES = 120  # an hour with fewer readings (gaps in logging) is left out
FLIPPED = {"MPG_share", "COMP_share"}  # signals that read 0 when "active" in this data
AI_RULE = Path(__file__).parent / "data" / "metropt_ai_rule.json"
FMT = "%Y-%m-%d %H:%M"


def hours(path):
    """Hourly features from the 10-second readings."""
    acc = {}
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            t = datetime.fromisoformat(r["timestamp"][:19])
            h = t.replace(minute=0, second=0)
            a = acc.get(h)
            if a is None:
                a = acc[h] = {"n": 0, "sum": {k: 0.0 for k in ANALOG}, "min": {k: math.inf for k in ANALOG},
                              "max": {k: -math.inf for k in ANALOG}, "on": {k: 0 for k in DIGITAL},
                              "loaded": 0, "starts": 0, "prev": None}
            a["n"] += 1
            for k in ANALOG:
                v = float(r[k])
                a["sum"][k] += v
                a["min"][k] = min(a["min"][k], v)
                a["max"][k] = max(a["max"][k], v)
            for k in DIGITAL:
                a["on"][k] += float(r[k]) > 0.5
            loaded = float(r["Motor_current"]) > LOADED
            a["loaded"] += loaded
            a["starts"] += bool(loaded and a["prev"] is False)
            a["prev"] = loaded
    out = []
    for h, a in sorted(acc.items()):
        if a["n"] < MIN_SAMPLES:
            continue
        x = {f"{k}_mean": a["sum"][k] / a["n"] for k in ANALOG}
        x.update({f"{k}_min": a["min"][k] for k in ANALOG})
        x.update({f"{k}_max": a["max"][k] for k in ANALOG})
        x.update({f"{k}_share": a["on"][k] / a["n"] for k in DIGITAL})
        x.update({"load_share": a["loaded"] / a["n"], "starts": a["starts"], "tp3_min": a["min"]["TP3"],
                  "lps_share": a["on"]["LPS"] / a["n"]})
        out.append({"hour": h, "x": x, "leak": leak_at(h)})
    return out


SPANS = [(datetime.strptime(a, FMT), datetime.strptime(b, FMT)) for a, b in FAILURES]


def leak_at(h):
    """Which leak (0 to 3) an hour overlaps, or None."""
    for i, (a, b) in enumerate(SPANS):
        if h <= b and h + timedelta(hours=1) > a:
            return i
    return None


def block(i, rows):
    a, b = SPANS[i]
    return [r for r in rows if a - timedelta(days=3) <= r["hour"] <= b + timedelta(days=3)]


# ---------- builds ----------

def normal_cuts(rows, feats):
    """Alarm style bands from the first month (no leaks there): under its middle value,
    normal, over its top 1%."""
    first = rows[0]["hour"] + timedelta(days=30)
    cuts = {}
    for k in feats:
        v = sorted(r["x"][k] for r in rows if r["hour"] < first)
        cuts[k] = [v[len(v) // 2], v[len(v) * 99 // 100]]
    return cuts


def naive_bayes(train, feats, cuts=None):
    """Each feature cut in 3 bands (the training data's thirds unless cuts are given),
    chances counted plus 1 (Laplace)."""
    if cuts is None:
        cuts = {}
        for k in feats:
            v = sorted(r["x"][k] for r in train)
            cuts[k] = [v[len(v) // 3], v[2 * len(v) // 3]]
    band = lambda k, x: sum(x >= c for c in cuts[k])
    pos = [r for r in train if r["leak"] is not None]
    neg = [r for r in train if r["leak"] is None]
    prior = (len(pos) + 1) / (len(train) + 2)
    cond = {}
    for k in feats:
        for lab, grp in ((1, pos), (0, neg)):
            for b in range(3):
                cond[k, lab, b] = (sum(band(k, r["x"][k]) == b for r in grp) + 1) / (len(grp) + 3)

    def score(r):
        lp = math.log(prior) + sum(math.log(cond[k, 1, band(k, r["x"][k])]) for k in feats)
        ln = math.log(1 - prior) + sum(math.log(cond[k, 0, band(k, r["x"][k])]) for k in feats)
        return 1 / (1 + math.exp(ln - lp))
    return score


def normal_stats(rows, keys):
    """Mean and spread of each reading in the first month (no leaks there)."""
    first = rows[0]["hour"] + timedelta(days=30)
    base = [r for r in rows if r["hour"] < first]
    out = {}
    for k in keys:
        v = [r["x"][k] for r in base]
        m = sum(v) / len(v)
        out[k] = (m, math.sqrt(sum((x - m) ** 2 for x in v) / len(v)) or 1e-9)
    return out


def ai_score(rule, stats):
    return lambda r: sum(d * (r["x"][k] - stats[k][0]) / stats[k][1] for k, d in rule.items())


# ---------- scores ----------

def auc(score, rows):
    pos = [score(r) for r in rows if r["leak"] is not None]
    neg = [score(r) for r in rows if r["leak"] is None]
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def limit_for(score, rows):
    """The score limit that gives about 1 alarm a day on normal hours."""
    s = sorted((score(r) for r in rows if r["leak"] is None), reverse=True)
    return s[max(0, len(s) // 24 - 1)]


def main(path):
    rows = hours(path)
    print(f"{len(rows)} hours from {rows[0]['hour']:%d %b} to {rows[-1]['hour']:%d %b %Y}, "
          f"leak hours {sum(r['leak'] is not None for r in rows)}\n")
    raw = [f"{k}_mean" for k in ANALOG]
    stats = normal_stats(rows, list(rows[0]["x"]))
    ai_rule = json.loads(AI_RULE.read_text(encoding="utf-8"))["rule"] if AI_RULE.exists() else None
    load_normal = stats["load_share"][0]

    results = {b: [] for b in ("rule", "ai_rule", "ai_rule_fixed", "net_raw_thirds", "net_eng_thirds",
                               "net_raw", "net_eng", "mix")}
    cuts = normal_cuts(rows, raw + ENG)
    for i in range(len(SPANS)):
        test = block(i, rows)
        if not any(r["leak"] == i for r in test):
            print(f"leak {i + 1}: no logged hours, left out")
            continue
        ids = {id(r) for r in test}
        train = [r for r in rows if id(r) not in ids]
        nb_raw, nb_eng = naive_bayes(train, raw, cuts), naive_bayes(train, ENG, cuts)
        builds = {"rule": lambda r: r["x"]["load_share"],
                  "net_raw_thirds": naive_bayes(train, raw), "net_eng_thirds": naive_bayes(train, ENG),
                  "net_raw": nb_raw, "net_eng": nb_eng,
                  "mix": lambda r: nb_eng(r) if r["x"]["load_share"] > load_normal else 0.0}
        if ai_rule:
            builds["ai_rule"] = ai_score(ai_rule, stats)
            # the same rule once a person tells it what 0 and 1 mean: in this data MPG and
            # COMP read 1 when the compressor rests, so "active" is 0 (the page does not say)
            fixed = {k: (-d if k in FLIPPED else d) for k, d in ai_rule.items()}
            builds["ai_rule_fixed"] = ai_score(fixed, stats)
        for name, s in builds.items():
            lim = limit_for(s, train)
            caught = any(s(r) > lim for r in test if r["leak"] == i)
            results[name].append((auc(s, test), caught))
    print(f"{'build':15} {'rank (AUC)':>11}   leaks caught   per leak")
    for name, got in results.items():
        if not got:
            continue
        mean = sum(a for a, _ in got) / len(got)
        print(f"  {name:15} {mean:9.0%}   {sum(c for _, c in got)} of {len(got)}        "
              + "  ".join(f"{a:.0%}{'*' if c else ''}" for a, c in got))
    print("\n* = caught. Rank 50% is a coin toss, 100% means every leak hour scores above every normal hour.")


AI_SYSTEM = """You are a maintenance engineer. Using only the sensor notes, say which hourly readings of the compressor move during an air leak in the train's pneumatic system.
Pick 2 to 6 readings from the menu, each with +1 if it rises in a leak or -1 if it falls. Pick only readings the notes give a reason for.
Return only JSON: {"rule": {"reading": 1}, "why": {"reading": "one short reason"}}"""


def menu():
    m = [f"{k}_{s}" for k in ANALOG for s in ("mean", "min", "max")] + [f"{k}_share" for k in DIGITAL]
    return m + ["load_share", "starts", "tp3_min", "lps_share"]


MENU_NOTES = {"_mean": "hourly mean", "_min": "hourly lowest", "_max": "hourly highest",
              "_share": "share of the hour the signal is active", "load_share": "share of the hour the motor is under load (over 5.5 A)",
              "starts": "times the motor goes under load in the hour", "tp3_min": "lowest TP3 in the hour",
              "lps_share": "share of the hour under 7 bar"}


def draft_ai():
    """One Gemini call (run through dotenvx). Saves the rule; the test then needs no model."""
    from app import llm_client
    notes = (Path(__file__).parent / "data" / "metropt_description.txt").read_text(encoding="utf-8")
    items = {k: next((v for s, v in MENU_NOTES.items() if k == s or k.endswith(s)), k) for k in menu()}
    used = llm_client.track_models()
    reply = llm_client._generate(AI_SYSTEM, json.dumps({"NOTES": notes, "MENU": items}), max_tokens=1500, json_mode=True)
    data = llm_client._parse_json(reply) or {}
    rule = {k: (1 if v > 0 else -1) for k, v in (data.get("rule") or {}).items() if k in items and v}
    AI_RULE.write_text(json.dumps({"rule": rule, "why": data.get("why"), "models": used, "reply": reply}, indent=1), encoding="utf-8")
    print(rule, used)


if __name__ == "__main__":
    draft_ai() if sys.argv[1] == "--draft" else main(sys.argv[1])
