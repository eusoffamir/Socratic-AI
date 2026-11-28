"""Diagnosis demo on open machine data (Meeting 3, tasks 5, 7 and 8).

A small working version of the industrial use case. A milling machine from
the AI4I 2020 dataset has failed. The learner (or an engineer) picks checks
one at a time, and the system:
1. ranks the possible faults by walking "causes" edges backward (abductive),
   using the Bayesian network learned from 7,000 past runs (inductive),
2. says which check is worth most next (value of information, Koller and
   Friedman 2009, Chapter 23),
3. once one fault is clear, gives the published rule and the fix (deductive).

The maths is plain code (eval/pgm_ai4i.py). Only the last step uses a model:
the Diagnosis agent writes a short plain explanation of the chain, with a
hand-written one when there is no model or the reply fails a check
("agents decide, rules guard"; agents only where an algorithm cannot do it).

The edges use the standard relation classes drafted for task 5
(docs/supervisor/relation-classes.md). DRAFT by Claude, 27 November 2026.
"""
import json
import math
import threading
from functools import lru_cache

from eval import pgm_ai4i as net

from . import limits, llm_client

CHECKS = ["gap", "speed", "torque", "wear", "power", "strain"]
CONFIDENT = 0.9  # stop when one fault reaches this chance
TRAIN_RECORDS = 7000
# Every failed test machine, following the best check until 90 percent sure
# (python -m eval.diagnose_fleet, 27 November 2026): 112 of 114 right, 2.2 readings on average.
FLEET = {"machines": 114, "right": 112, "right_pct": 98, "avg_checks": 2.2}

CHECK_NAMES = {"gap": "Temperature gap", "speed": "Spindle speed", "torque": "Torque",
               "wear": "Tool wear", "power": "Power", "strain": "Strain on the tool"}
UNITS = {"gap": ("K", 2), "speed": ("rpm", 0), "torque": ("Nm", 1), "wear": ("min", 0),
         "power": ("W", 0), "strain": ("min Nm", 0)}
FAULTS = {"TWF": "tool wear failure", "HDF": "heat dissipation failure", "PWF": "power failure",
          "OSF": "overstrain failure", "RNF": "random failure"}
# The published rule behind each failure (dataset page, Matzka 2020), used as the
# deductive step, and the fix. The fixes are plain engineering sense, DRAFT.
RULES = {
    "TWF": "the tool is replaced or fails once its wear reaches 200 to 240 minutes",
    "HDF": "heat cannot escape when the gap between process and air temperature is under 8.6 K and the speed is under 1,380 rpm",
    "PWF": "the process fails when the power is under 3,500 W or over 9,000 W",
    "OSF": "the tool overstrains when wear times torque passes 11,000 min Nm for type L, 12,000 for type M and 13,000 for type H",
    "RNF": "about 1 run in 1,000 fails at random, with no cause in the readings",
}
FIXES = {
    "TWF": "Replace the tool, and plan the next change before 200 minutes of wear.",
    "HDF": "Improve the cooling, or avoid running the spindle slowly when the air is warm.",
    "PWF": "Keep the power between 3,500 W and 9,000 W by changing the speed or the load.",
    "OSF": "Lower the load, or change the tool sooner, since a worn tool under high torque overstrains.",
    "RNF": "No reading explains this, so log it and inspect the machine by hand.",
}
# What each reading tests, as "tests" edges (the true causes from the dataset page).
FIX_SHORT = {"TWF": "Replace the tool", "HDF": "Improve the cooling", "PWF": "Keep power in range",
             "OSF": "Lower the load", "RNF": "Inspect by hand"}
TESTS = {"wear": ["TWF"], "gap": ["HDF"], "speed": ["HDF"], "power": ["PWF"], "strain": ["OSF"], "torque": []}
MAX_PER_FAULT = 2
NEEDS = {"TWF": ["wear"], "HDF": ["gap", "speed"], "PWF": ["power"], "OSF": ["strain"]}  # readings each rule needs
OSF_LIMIT = {"L": 11000, "M": 12000, "H": 13000}  # wear times torque, min Nm, from the dataset page


def _down(v, places):
    """Round down for display, so 8.595 K shows as 8.59 K and never looks like it meets an 8.6 K limit."""
    f = 10 ** places
    return math.floor(v * f) / f


def rule_check(r, mode):
    """The expert rule for a fault, tested on the machine's real numbers (task 7, the
    rules of thumb joined to the data network and the graph). This is the deductive
    check: if the rule's conditions hold, the fault must follow."""
    x = r["raw"]
    num = lambda v, unit, p=0: f"{_down(v, p):,.{p}f} {unit}"
    missing = [c for c in NEEDS.get(mode, []) if x.get(c) is None]
    if missing:
        return {"holds": None, "text": f"The rule cannot be checked, since {_join([CHECK_NAMES[c].lower() for c in missing])} was not given."}
    if mode == "TWF":
        holds = x["wear"] >= 200
        why = f"tool wear is {num(x['wear'], 'min')}, and the rule needs 200 minutes or more"
    elif mode == "HDF":
        holds = x["gap"] < 8.6 and x["speed"] < 1380
        why = f"the gap is {num(x['gap'], 'K', 2)} and the speed is {num(x['speed'], 'rpm')}, and the rule needs under 8.6 K and under 1,380 rpm"
    elif mode == "PWF":
        holds = x["power"] < 3500 or x["power"] > 9000
        why = f"power is {num(x['power'], 'W')}, and the rule needs under 3,500 W or over 9,000 W"
    elif mode == "OSF":
        limit = OSF_LIMIT[r["type"]]
        holds = x["strain"] > limit
        why = f"wear times torque is {num(x['strain'], 'min Nm')}, and the rule for type {r['type']} needs over {limit:,}"
    else:  # random failure: the rule is that no other rule explains it
        tried = {m: rule_check(r, m)["holds"] for m in ("TWF", "HDF", "PWF", "OSF")}
        others = [m for m, h in tried.items() if h]
        if not others and None in tried.values():
            return {"holds": None, "text": "The rule cannot be checked, since not every reading was given."}
        holds = not others
        why = ("no other rule fits these readings" if holds
               else f"the rule for {FAULTS[others[0]]} fits these readings")
    return {"holds": holds, "text": f"{'The rule holds' if holds else 'The rule does not hold'}, since {why}."}
WORDS = 70


@lru_cache(maxsize=1)
def model():
    """The engineer network, learned once per server start (a few seconds)."""
    rows = net.load()
    train, test = net.split(rows)
    parents = net.learn_structure(train, net.ENGINEER)
    tables = net.learn_tables(parents, train)
    failed = [r for r in test if any(r[m] for m in net.MODES)]
    right = sum(r[net.diagnose(parents, tables, r)] == 1 for r in failed)
    return {"parents": parents, "tables": tables, "test": test,
            "accuracy": round(100 * right / len(failed)), "tested": len(failed)}


def _faults_of(r):
    return [m for m in net.MODES if r[m]]


@lru_cache(maxsize=1)
def machines():
    """A few failed test machines: up to 2 for each fault with one cause, and
    one with two faults at once, so the hard cases are shown too."""
    picked, count = [], {m: 0 for m in net.MODES}
    two = None
    for r in model()["test"]:
        faults = _faults_of(r)
        if len(faults) == 1 and count[faults[0]] < MAX_PER_FAULT:
            count[faults[0]] += 1
            picked.append(r)
        elif len(faults) > 1 and two is None:
            two = r
    picked.sort(key=lambda r: r["udi"])
    if two:
        picked.append(two)
    return {r["udi"]: r for r in picked}


def reading(r, check):
    """'2,912 W, which is low' for one check on one machine."""
    unit, places = UNITS[check]
    value = f"{_down(r['raw'][check], places):,.{places}f}"
    return {"check": check, "name": CHECK_NAMES[check], "value": f"{value} {unit}", "band": r[check]}


SHIFT = 0.1  # a check "points to" or "makes unlikely" a fault when it moves its chance by 10 points or more


def found(r, done):
    """Each check in order, with what it found about the faults it can cause
    (its "causes" edges, learned from data). A big rise points to that fault
    (abductive), a big fall makes it unlikely, otherwise it tells little."""
    parents = model()["parents"]
    out, evidence = [], {"type": r["type"], "failed": 1}
    before = _chances(evidence)
    for c in done:
        evidence[c] = r[c]
        after = _chances(evidence)
        mine = [m for m in net.MODES if c in parents[m]]
        up = max(mine, key=lambda x: after[x] - before[x], default=None)
        down = min(mine, key=lambda x: after[x] - before[x], default=None)
        if up and after[up] - before[up] >= SHIFT:
            effect = {"kind": "up", "fault": FAULTS[up], "fault_id": up, "text": f"Points to {FAULTS[up]}"}
        elif down and before[down] - after[down] >= SHIFT:
            effect = {"kind": "down", "fault": FAULTS[down], "fault_id": down, "text": f"Makes {FAULTS[down]} unlikely"}
        else:
            effect = {"kind": "none", "fault": None, "fault_id": None, "text": "Tells little"}
        out.append({**reading(r, c), **effect})
        before = after
    return out


def _tells(gain, best):
    """How much a check would tell, compared with the best one now."""
    if best <= 0.01 or gain < best / 4:
        return "tells little"
    return "tells a lot" if gain >= best * 2 / 3 else "tells some"


def graph():
    """The demo's knowledge graph in the standard relation classes."""
    p = model()["parents"]
    nodes = [{"id": c, "kind": "check", "text": CHECK_NAMES[c]} for c in CHECKS]
    nodes += [{"id": m, "kind": "fault", "text": FAULTS[m].capitalize()} for m in net.MODES]
    nodes += [{"id": "type", "kind": "context", "text": "Product type (L, M or H)"}]
    nodes += [{"id": f"fix_{m}", "kind": "action", "text": FIXES[m], "short": FIX_SHORT[m]} for m in net.MODES]
    edges = [[c, "causes", m] for m in net.MODES for c in p[m]]  # learned from data
    edges += [[c, "tests", m] for c, ms in TESTS.items() for m in ms]
    edges += [[m, "fixed_by", f"fix_{m}"] for m in net.MODES]
    return {"nodes": nodes, "edges": edges}


def _chances(evidence):
    m = model()
    return net.mode_chances(m["parents"], m["tables"], evidence)


# The user's own machine: what can be typed in, with a sensible range for each
OWN = {"air": ("Air temperature", "K", 250, 350), "process": ("Process temperature", "K", 250, 400),
       "speed": ("Spindle speed", "rpm", 1, 5000), "torque": ("Torque", "Nm", 0.1, 200),
       "wear": ("Tool wear", "min", 0, 500)}


def own_machine(inp):
    """A machine row from the user's own numbers, banded like the training data.
    Gap, power and strain are worked out when the numbers they need are given.
    Raises ValueError on a bad type, a number out of range or no numbers at all."""
    t = inp.get("type")
    if t not in OSF_LIMIT:
        raise ValueError("Pick the product type, L, M or H.")
    x = {}
    for k, (name, unit, lo, hi) in OWN.items():
        v = inp.get(k)
        if v is None or v == "":
            continue
        try:
            v = float(v)
        except (TypeError, ValueError):
            raise ValueError(f"{name} must be a number.")
        if not (lo <= v <= hi) or v != v:
            raise ValueError(f"{name} should be between {lo:g} and {hi:g} {unit}.")
        x[k] = v
    raw = {"speed": x.get("speed"), "torque": x.get("torque"), "wear": x.get("wear"),
           "gap": x["process"] - x["air"] if "air" in x and "process" in x else None,
           "power": x["torque"] * x["speed"] * 2 * math.pi / 60 if "torque" in x and "speed" in x else None,
           "strain": x["wear"] * x["torque"] if "wear" in x and "torque" in x else None}
    if all(v is None for v in raw.values()):
        raise ValueError("Type at least one reading.")
    cuts = {"speed": ([1380, 1800], ["slow", "normal", "fast"]), "torque": ([30, 50], ["low", "mid", "high"]),
            "wear": ([200, 240], ["new", "worn", "old"]), "gap": ([8.6], ["small", "normal"]),
            "power": ([3500, 9000], ["low", "normal", "high"]), "strain": ([11000, 13000], ["low", "mid", "high"])}
    row = {"udi": 0, "pid": "Your machine", "type": t, "raw": raw, **{m: 0 for m in net.MODES}, "own": True}
    row.update({c: net._band(raw[c], *cuts[c]) for c in CHECKS if raw[c] is not None})
    return row


def step(udi, done, own=None):
    """Where the diagnosis stands after the checks in `done`, in order, for a demo
    machine (udi) or the user's own readings (own)."""
    r = own_machine(own) if own is not None else machines().get(udi)
    if r is None:
        raise KeyError(udi)
    have = [c for c in CHECKS if c in r]
    done = [c for i, c in enumerate(done) if c in have and c not in done[:i]]
    evidence = {"type": r["type"], "failed": 1, **{c: r[c] for c in done}}
    m = model()
    left = [c for c in have if c not in done]
    now, values = net.value_of_information(m["parents"], m["tables"], evidence, left) if left else (
        max(_chances(evidence).values()), {})
    chances = _chances(evidence)  # each fault on its own, since a machine can have two at once
    ranked = sorted(net.MODES, key=lambda x: -chances[x])
    top = ranked[0]
    finished = now >= CONFIDENT or not left
    out = {
        "machine": {"udi": r["udi"], "pid": r["pid"], "type": r["type"], "own": bool(r.get("own"))},
        "given": have,
        "done": found(r, done),
        "faults": [{"id": x, "name": FAULTS[x], "percent": _pct(chances[x])} for x in ranked],
        "sure": _pct(now),
        "checks": [{"check": c, "name": CHECK_NAMES[c], "gain": round(100 * max(values.get(c, 0), 0)),
                    "tells": _tells(values.get(c, 0), max(values.values(), default=0))} for c in left],
        "best": max(left, key=lambda c: values.get(c, 0)) if left else None,
        "finished": finished,
    }
    out["checks"].sort(key=lambda c: -c["gain"])
    if finished:
        truth = [] if r.get("own") else _faults_of(r)  # nobody knows the real cause of the user's own machine
        out.update({"named": top, "named_name": FAULTS[top], "rule": RULES[top], "fix": FIXES[top],
                    "rule_check": rule_check(r, top), "truth": [FAULTS[x] for x in truth],
                    "right": (top in truth) if truth else None})
        out["explanation"] = explain(out)
    return out


def _pct(p):
    """A chance as a whole percent, never 100, since the data can always surprise us."""
    return min(99, round(100 * p))


def _join(parts):
    return ", ".join(parts[:-1]) + (" and " if len(parts) > 1 else "") + (parts[-1] if parts else "")


def machine_list():
    m = model()
    # the short names the graph card shows for each reading
    names = {**CHECK_NAMES, "type": "Product type"}
    return {"machines": [{"udi": r["udi"], "pid": r["pid"], "type": r["type"]} for r in machines().values()],
            "accuracy": m["accuracy"], "tested": m["tested"], "records": TRAIN_RECORDS,
            "confident": round(100 * CONFIDENT), "graph": graph(), "names": names,
            "fleet": FLEET, "checks": len(CHECKS),
            "own": [{"id": k, "name": n, "unit": u, "min": lo, "max": hi} for k, (n, u, lo, hi) in OWN.items()]}


# ---------- the Diagnosis agent: a plain explanation of the chain ----------

SYSTEM = """You are the Diagnosis agent for RootAI. A milling machine has failed, and plain code has already found the most likely fault with a Bayesian network. You only explain the reasoning to an engineer in training, in at most """ + str(WORDS) + """ words. Use only the facts given and change no number.

Write 3 or 4 sentences in this order.
1. Abductive. Which reading in CHECKS points to FAULT, so FAULT is the best explanation at CHANCE. Name the reading and its number.
2. If other checks were done, say in one sentence that they made the other faults unlikely.
3. Deductive. What RULE says, so the FIX follows. Give the fix.
4. Inductive. The chances were learned from RECORDS past runs of the machine.
Easy English, short smooth sentences joined with "because", "so" and "but". Calm tone, no slang, no emoji, no exclamation marks, no colons and no dashes. Chances as percentages.

Return ONLY this JSON: {"explanation": ""}"""

_cache, _lock = {}, threading.Lock()


def facts(d):
    return {"type": d["machine"]["type"], "checks": [f"{x['name']} {x['value']} ({x['band']})" for x in d["done"]],
            "fault": d["named_name"], "chance": f"{d['faults'][0]['percent']}%", "rule": d["rule"],
            "rule_check": d["rule_check"]["text"],
            "fix": d["fix"], "records": TRAIN_RECORDS}


def fallback(d):
    """The hand-written explanation: the reading that points to the fault
    (abductive), what the others ruled out, the rule and fix (deductive), and
    where the chances came from (inductive)."""
    top, named = d["faults"][0], d["named"]
    said = lambda x: f"the {x['name'].lower()} was {x['band']} at {x['value']}"
    key = [x for x in d["done"] if named in TESTS[x["check"]]]
    rest = [x for x in d["done"] if named not in TESTS[x["check"]]]
    if key:
        first = (f"The machine failed, and {_join([said(x) for x in key])}, which is a known cause of {d['named_name']}, "
                 f"so it is the best explanation at {top['percent']}%.")
    elif rest:
        first = (f"The machine failed, but no reading points to a known cause, so {d['named_name']} "
                 f"is the best explanation left at {top['percent']}%.")
    else:
        first = (f"The machine failed, and for a type {d['machine']['type']} product {d['named_name']} "
                 f"is the most likely cause at {top['percent']}%.")
    if key and rest:
        first += f" The other checks made the other faults unlikely, since {_join([said(x) for x in rest])}."
    return (f"{first} The rule says {d['rule']}, so the fix follows. {d['fix']} "
            f"These chances were learned from {TRAIN_RECORDS:,} past runs.")


def clean(text, d):
    """A safe agent reply, or None. Rules guard: short, names the same fault, no colons or dashes."""
    if not isinstance(text, str):
        return None
    text = " ".join(text.split())
    if not text or len(text.split()) > WORDS + 15 or ":" in text or " - " in text or "—" in text:
        return None
    if d["named_name"].split()[0].lower() not in text.lower():
        return None
    return text


def explain(d):
    key = (d["machine"]["udi"], tuple((x["check"], x["value"]) for x in d["done"]))
    with _lock:
        if key in _cache:
            return _cache[key]
    text = None
    if llm_client.PROVIDER != "mock" and limits.budget_left():
        try:
            raw = llm_client._generate(SYSTEM, json.dumps(facts(d)), max_tokens=300, json_mode=True)
            text = clean((llm_client._parse_json(raw) or {}).get("explanation"), d)
        except Exception:  # any model problem: the hand-written one is used
            text = None
    if text is None:
        return {"text": fallback(d), "source": "fallback"}  # not cached, so a later call can still use the agent
    out = {"text": text, "source": "agent"}
    with _lock:
        _cache[key] = out
    return out


# ---------- the Knowledge page for engineers: the same machine, three kinds of knowledge ----------

SOURCE = {"title": "AI4I 2020 Predictive Maintenance Dataset, Matzka (2020)", "url": "https://doi.org/10.24432/C5HS5C"}
# What each band of a reading means in real numbers (the cuts in eval/pgm_ai4i.load).
BANDS = {
    "type": [("L", "Low quality"), ("M", "Medium quality"), ("H", "High quality")],
    "wear": [("new", "under 200 min"), ("worn", "200 to 240 min"), ("old", "240 min or more")],
    "strain": [("low", "under 11,000 min Nm"), ("mid", "11,000 to 13,000"), ("high", "13,000 or more")],
    "power": [("low", "under 3,500 W"), ("normal", "3,500 to 9,000 W"), ("high", "9,000 W or more")],
    "gap": [("small", "under 8.6 K"), ("normal", "8.6 K or more")],
    "speed": [("slow", "under 1,380 rpm"), ("normal", "1,380 to 1,800 rpm"), ("fast", "1,800 rpm or more")],
    "torque": [("low", "under 30 Nm"), ("mid", "30 to 50 Nm"), ("high", "50 Nm or more")],
}
# The engineer's checklist, the published rules in the order that names the right fault
# most often on the 7,000 training runs (eval/graph_build_test.py, 28 November 2026).
# Tool wear goes last, since many worn tools fail from overstrain instead; checking it
# first gave 82%, this order gives 100% on the failed test machines. DRAFT by Claude,
# until a real expert checks it.
TREE = {
    "root": "q_strain",
    "nodes": [
        {"id": "q_strain", "kind": "question", "text": "Is wear times torque over the limit for its type?",
         "sub": "11,000 min Nm for L, 12,000 for M, 13,000 for H"},
        {"id": "q_power", "kind": "question", "text": "Is power under 3,500 W or over 9,000 W?"},
        {"id": "q_heat", "kind": "question", "text": "Is the temperature gap under 8.6 K and the speed under 1,380 rpm?"},
        {"id": "q_wear", "kind": "question", "text": "Is tool wear 200 minutes or more?"},
        *[{"id": f"d_{m}", "kind": "decision", "fault": m, "text": FAULTS[m].capitalize(), "fix": FIX_SHORT[m]}
          for m in ("OSF", "PWF", "HDF", "TWF", "RNF")],
    ],
    "edges": [["q_strain", "yes", "d_OSF"], ["q_strain", "no", "q_power"],
              ["q_power", "yes", "d_PWF"], ["q_power", "no", "q_heat"],
              ["q_heat", "yes", "d_HDF"], ["q_heat", "no", "q_wear"],
              ["q_wear", "yes", "d_TWF"], ["q_wear", "no", "d_RNF"]],
}


def knowledge():
    """The machine knowledge in three parts: what the published source says (books),
    the engineer's checklist (rules of thumb) and the network learned from data."""
    p = model()["parents"]
    names = {**CHECK_NAMES, "type": "Product type"}
    book = [{"id": m, "name": FAULTS[m].capitalize(), "rule": RULES[m][0].upper() + RULES[m][1:] + ".",
             "fix": FIXES[m], "short": FIX_SHORT[m], "causes": sorted(net.TRUE_PARENTS[m])} for m in net.MODES]
    learned = {m: sorted(p[m]) for m in net.MODES}
    return {"names": names, "source": SOURCE, "book": book, "tree": TREE, "records": TRAIN_RECORDS,
            "learned": learned,
            # readings that go together (the network's arrows between readings), drawn as arcs
            "links": [[a, c] for c in CHECKS for a in p[c] if a in CHECKS],
            "agree": all(set(learned[m]) == net.TRUE_PARENTS[m] for m in net.MODES),
            "bands": {k: [{"value": v, "text": t} for v, t in b] for k, b in BANDS.items()}}


def what_if(evidence):
    """The chance of each fault for a failed machine, given the readings set so far."""
    ok = {k: v for k, v in (evidence or {}).items() if k in BANDS and v in dict(BANDS[k])}
    chances = _chances({"failed": 1, **ok})
    return {"evidence": ok, "faults": [{"id": m, "name": FAULTS[m], "percent": _pct(chances[m])} for m in net.MODES]}
