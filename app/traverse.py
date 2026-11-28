"""Reasoning as moves on the knowledge graph, for Goal 3, step 5.

The Reasoning agent (sharing the Assessor's call) names the steps of the
learner's answer as moves between knowledge graph nodes, [from id, to id].
Plain code then reads each step against the graph's links and says which type
of reasoning the moves show, so the agent's own label can be checked by an
algorithm (Dr Ho, Meeting 2, "reasoning is an operation on the graph").

First definitions (docs/supervisor/goals/goal3-plan.md, question 4 for Dr Ho):
- A step WITH a link (a causes b, learner goes a to b) is forward. A step
  AGAINST a link (learner goes from b back to a) is backward.
- Inductive: a forward step out of a counted result (a "data" node), or two or
  more nodes leading forward into the same node, which is many cases to one idea.
- Deductive: any other forward step, a rule or fact applied to reach a conclusion.
- Abductive: a backward step, from what was seen back to what explains it.
Steps between nodes with no link are kept as "jump" but show no type.

28 November 2026, after the human marker check (only 11 of 60 answers had a
step on a real link, and forward walks were read as deductive far too often):
- A step may follow a short chain of links in one direction (at most
  MAX_HOPS), because learners skip ideas the graph spells out.
- Only reasoning links count toward a type (REASONING_RELATIONS). "then" is
  the order of steps and "defines" and "leads_to" are teaching links, so a
  step along only those is kept as "order" and shows no type.

DRAFT: drafted by Claude on 22 October 2026, to be checked by Dr Ho.
"""

from .knowledge import case_graph, source_of
from .reasoning import REASONING_TYPES

MAX_STEPS = 4
MAX_HOPS = 3  # links a single step may follow
# Links that carry reasoning. The others (then, defines, leads_to) are order or teaching.
REASONING_RELATIONS = {"causes", "supports", "weakens", "tests", "rules_out", "prevents"}


def clean_steps(raw, case):
    """The agent's steps, keeping only [from, to] pairs of real, different node ids."""
    ids = {n["id"] for n in case_graph(case)["nodes"]}
    steps = []
    for s in raw if isinstance(raw, list) else []:
        if isinstance(s, (list, tuple)) and len(s) == 2:
            a, b = (str(x).strip().lower() for x in s)
            if a in ids and b in ids and a != b and [a, b] not in steps:
                steps.append([a, b])
    return steps[:MAX_STEPS]


def _path(links, a, b):
    """The shortest chain of links from a to b, as a list of relations, or None."""
    frontier, seen = [(a, [])], {a}
    for _ in range(MAX_HOPS):
        nxt = []
        for node, rels in frontier:
            for (x, y), rel in links.items():
                if x == node and y not in seen:
                    if y == b:
                        return rels + [rel]
                    seen.add(y)
                    nxt.append((y, rels + [rel]))
        frontier = nxt
    return None


def read(case, raw_steps):
    """Each step with its direction and links, and the reasoning types the moves show (1 or 0)."""
    g = case_graph(case)
    data_nodes = {n["id"] for n in g["nodes"] if (source_of(case, n) or {}).get("kind") == "data"}
    links = {(a, b): rel for a, rel, b in g["edges"]}
    steps = []
    for a, b in clean_steps(raw_steps, case):
        fwd, back = _path(links, a, b), _path(links, b, a)
        rels, d = (fwd, "forward") if fwd else (back, "backward") if back else (None, "jump")
        if rels and not REASONING_RELATIONS & set(rels):
            d = "order"  # only then, defines or leads_to links, so no reasoning type
        steps.append({"from": a, "to": b, "dir": d, "rel": rels[0] if rels and len(rels) == 1 else rels, "hops": len(rels or [])})
    forward = [s for s in steps if s["dir"] == "forward"]
    into = {}
    for s in forward:
        into.setdefault(s["to"], set()).add(s["from"])
    many_to_one = {b for b, sources in into.items() if len(sources) >= 2}
    inductive = [s for s in forward if s["from"] in data_nodes or s["to"] in many_to_one]
    types = {"inductive": int(bool(inductive)),
             "deductive": int(len(forward) > len(inductive)),
             "abductive": int(any(s["dir"] == "backward" for s in steps))}
    return {"steps": steps, "types": types}


def landed(reading):
    """True when at least 1 step followed reasoning links, so the reading says something."""
    return any(s["dir"] in ("forward", "backward") for s in reading["steps"])


def agreement(assessments):
    """For each reasoning type, how often the graph reading and the agent's label
    agree, over answers whose steps landed on at least 1 link. For Dr Ho and the thesis."""
    marked = [a["reasoning"] for a in assessments
              if (a.get("reasoning") or {}).get("graph")
              and landed(a["reasoning"]["graph"])]
    return {"answers": len(marked),
            "agree": {k: sum(r["graph"]["types"][k] == r["types"][k] for r in marked) for k in REASONING_TYPES}}
