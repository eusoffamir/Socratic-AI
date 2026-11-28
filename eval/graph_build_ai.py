"""The AI-drafted build for the graph build test (review family 2.9, 28 November 2026).

A language model reads only the dataset page's text (eval/data/ai4i2020_description.txt)
and the names of the raw columns. It must choose the nodes itself (it may define new
readings from two columns), draw the "causes" arrows and write each fault's rule
with its limits. We run it several times, save every reply, and score the drafts in
eval/graph_build_test.py with no further model calls.

Draft (uses the free model through dotenvx, about 5 calls):
    npx.cmd dotenvx run -- python -m eval.graph_build_ai 5
Saved drafts: eval/data/ai_graphs.json
"""
import json
import math
import sys
import time
from datetime import date
from pathlib import Path

from app import llm_client

SOURCE = Path(__file__).parent / "data" / "ai4i2020_description.txt"
SAVED = Path(__file__).parent / "data" / "ai_graphs.json"
COLUMNS = ["type", "air", "process", "speed", "torque", "wear"]
FAULTS = ["TWF", "HDF", "PWF", "OSF", "RNF"]

SYSTEM = """You build a small knowledge graph for diagnosing a failed milling machine, using only the source text.
The raw readings are: type (L, M or H), air (air temperature, K), process (process temperature, K), speed (rotational speed, rpm), torque (Nm), wear (tool wear, min).
You may define new readings from two raw readings when the text needs them. Each new reading is a, an op ("minus" or "times") and b, times an optional factor (default 1).
For each failure mode give the readings that cause it, and a rule that is true when the failure happens. A rule is a list of alternatives; it holds when every condition in any one alternative holds. A condition is a reading, an op ("<", "<=", ">", ">=") and a value, or for a limit that depends on type, value_by_type with L, M and H.
Use the failure mode ids TWF, HDF, PWF, OSF, RNF. A failure with no cause in the readings has no causes and an empty rule.
Return only JSON in this shape:
{"derived": [{"name": "...", "a": "...", "op": "minus", "b": "...", "factor": 1}],
 "faults": [{"id": "TWF", "causes": ["..."], "rule": [[{"reading": "...", "op": ">=", "value": 0}]]}]}"""


def draft(n):
    text = SOURCE.read_text(encoding="utf-8")
    user = json.dumps({"SOURCE": text}, ensure_ascii=False)
    out = json.loads(SAVED.read_text(encoding="utf-8")) if SAVED.exists() else []
    for i in range(n):
        used = llm_client.track_models()
        t = time.time()
        try:
            reply = llm_client._generate(SYSTEM, user, max_tokens=2000, json_mode=True)
        except Exception as e:  # keep going, a failed call is part of the result
            reply = None
            print(f"run {i + 1} failed: {e}")
        out.append({"date": str(date.today()), "models": used, "seconds": round(time.time() - t, 1),
                    "chars_in": len(SYSTEM) + len(user), "chars_out": len(reply or ""), "reply": reply})
        print(f"run {i + 1}: {used} {out[-1]['seconds']} s, {len(reply or '')} chars")
        time.sleep(5)  # stay inside the free plan's calls a minute
    SAVED.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")


# ---------- reading a saved draft (no model calls) ----------

def parse(reply):
    """The draft as {derived, faults}, or None when the reply is not usable JSON."""
    data = llm_client._parse_json(reply or "")
    if not data or not isinstance(data.get("faults"), list):
        return None
    return data


def values(raw_row, derived):
    """All readings of one run as numbers, raw first, then the draft's own new readings."""
    v = dict(raw_row)
    for d in derived or []:
        try:
            a, b = v[d["a"]], v[d["b"]]
            x = a - b if d["op"] == "minus" else a * b
            v[d["name"]] = x * float(d.get("factor", 1) or 1)
        except (KeyError, TypeError, ValueError):
            continue
    return v


OPS = {"<": lambda a, b: a < b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}


def holds(rule, v):
    """True, False, or None when a reading the rule needs is missing."""
    if not rule:
        return False
    missing = False
    for alt in rule:
        ok = True
        for c in alt:
            limit = c.get("value_by_type") or c.get("value")
            if isinstance(limit, dict):  # a limit for each type, under either key
                limit = limit.get(v["type"])
            x = v.get(c.get("reading"))
            if x is None or limit is None or c.get("op") not in OPS:
                missing, ok = True, False
                break
            if not OPS[c["op"]](x, float(limit)):
                ok = False
                break
        if ok:
            return True
    return None if missing else False


# Our names for a new reading, found from what it is made of (so arrows can be compared).
KNOWN = {("minus", frozenset({"process", "air"})): "gap", ("times", frozenset({"torque", "speed"})): "power",
         ("times", frozenset({"wear", "torque"})): "strain"}


def canonical(draft_):
    """Each fault's causes in our node names."""
    names = {d.get("name"): KNOWN.get((d.get("op"), frozenset({d.get("a"), d.get("b")})), d.get("name"))
             for d in draft_.get("derived") or []}
    return {f.get("id"): {names.get(c, c) for c in f.get("causes") or []} for f in draft_["faults"]}


def check_power_factor(draft_):
    """The text gives power with speed in rad/s, so the factor should be 2 pi / 60."""
    for d in draft_.get("derived") or []:
        if KNOWN.get((d.get("op"), frozenset({d.get("a"), d.get("b")}))) == "power":
            return abs(float(d.get("factor", 1) or 1) - 2 * math.pi / 60) < 0.001
    return None


if __name__ == "__main__":
    draft(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
