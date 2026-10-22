"""Data as probabilistic graph models, for Goal 3 (Meeting 2 with Dr Ho, 19 October 2026).

Each case has a small Bayesian network. A node is something that is true or
false on one example, such as "the pattern is real", and an edge [a, "causes", b]
means a changes the chance of b. Every node points to the knowledge graph node
it rests on ("why").

The network's chances are not written by hand. They are learned by counting
over seeded simulated data, which is the inductive move. Asking the network
for the chance of a cause given what was seen is the abductive move, and the
chance of an effect given its cause is a forward, deductive-style prediction.
Plain Python, exact answers by adding up every case (fine for 3 or 4 nodes).
See docs/supervisor/goal3-plan.md.

DRAFT: drafted by Claude on 22 October 2026, to be checked by Dr Ho. The
simulated numbers (how often a pattern is real, how strong it is) are made up
to show the method, not taken from real markets.
"""

import itertools
import random
from functools import lru_cache

from .content import CONCEPTS
from .tools import SEED


def _streak_data(rows=20000, real_share=0.02, real_up=0.8):
    """Stocks over 2 weeks. A few have a real pattern and go up most days, the
    rest are coin flips. "repeats" means 4 or more up days in the new week."""
    rng = random.Random(SEED)
    data = []
    for _ in range(rows):
        real = rng.random() < real_share
        up = real_up if real else 0.5
        week1 = [rng.random() < up for _ in range(5)]
        week2 = [rng.random() < up for _ in range(5)]
        data.append({"real": real, "streak": all(week1), "repeats": sum(week2) >= 4})
    return data


def _rule_data(rows=20000, real_share=0.05, edge=0.15, days=100):
    """Trading rules over old and new data. A few have a real edge (a small
    daily gain), the rest are noise. "great_old" means more than +15% on old data."""
    rng = random.Random(SEED)
    data = []
    for _ in range(rows):
        real = rng.random() < real_share
        mean = edge if real else 0.0
        # The sum of 100 daily results, drawn in one go: average 100 x mean, spread 10.
        old = rng.gauss(days * mean, days ** 0.5)
        new = rng.gauss(days * mean, days ** 0.5)
        data.append({"edge": real, "great_old": old > 15, "wins_new": new > 0})
    return data


def _weather_data(rows=3650, hot_share=0.3):
    """Days in a town. Hot weather raises both ice cream sales and sunburns,
    and the two have no link of their own."""
    rng = random.Random(SEED)
    data = []
    for _ in range(rows):
        hot = rng.random() < hot_share
        data.append({"hot": hot,
                     "ice_cream": rng.random() < (0.8 if hot else 0.2),
                     "sunburn": rng.random() < (0.7 if hot else 0.1)})
    return data


# "asks" are the questions worth putting to each network, with the move they show
# and a label for the page, read as "the chance that <label>". "lesson" sums them up.
NETWORKS = {
    "pattern_or_luck": {
        "data": _streak_data,
        "nodes": [
            {"id": "real", "why": "real_pattern", "text": "The stock has a real pattern."},
            {"id": "streak", "why": "streak_chance", "text": "It went up 5 days in a row."},
            {"id": "repeats", "why": "check_repeat", "text": "It went up on at least 4 of the next 5 days."},
        ],
        "edges": [["real", "causes", "streak"], ["real", "causes", "repeats"]],
        "counted": "20,000 simulated stocks",
        "asks": [
            {"move": "inductive", "target": "streak", "given": {"real": False},
             "label": "a stock with no pattern goes up 5 days in a row"},
            {"move": "abductive", "target": "real", "given": {}, "label": "the pattern is real, before seeing anything"},
            {"move": "abductive", "target": "real", "given": {"streak": True},
             "label": "the pattern is real, after a 5-day streak"},
            {"move": "abductive", "target": "real", "given": {"streak": True, "repeats": True},
             "label": "the pattern is real, after the streak and a good next week"},
        ],
        "lesson": "A streak alone is weak evidence, but a good next week makes a real pattern much more likely.",
    },
    "holds_on_new_data": {
        "data": _rule_data,
        "nodes": [
            {"id": "edge", "why": "rule", "text": "The rule has a real edge."},
            {"id": "great_old", "why": "best_10", "text": "It made more than 15% on old data."},
            {"id": "wins_new", "why": "new_data_proof", "text": "It made money on new data."},
        ],
        "edges": [["edge", "causes", "great_old"], ["edge", "causes", "wins_new"]],
        "counted": "20,000 simulated trading rules",
        "asks": [
            {"move": "inductive", "target": "great_old", "given": {"edge": False},
             "label": "a rule with no edge makes more than 15% on old data"},
            {"move": "abductive", "target": "edge", "given": {"great_old": True},
             "label": "the rule is real, after more than 15% on old data"},
            {"move": "abductive", "target": "edge", "given": {"great_old": True, "wins_new": True},
             "label": "the rule is real, after that and a win on new data"},
            {"move": "abductive", "target": "edge", "given": {"great_old": True, "wins_new": False},
             "label": "the rule is real, after that and a loss on new data"},
        ],
        "lesson": "A great result on old data says little, but new data says much more.",
    },
    "together_not_cause": {
        "data": _weather_data,
        "nodes": [
            {"id": "hot", "why": "luck_or_hidden", "text": "The day is hot."},
            {"id": "ice_cream", "why": "ice_cream", "text": "Ice cream sales are high."},
            {"id": "sunburn", "why": "ice_cream", "text": "Many people get sunburnt."},
        ],
        "edges": [["hot", "causes", "ice_cream"], ["hot", "causes", "sunburn"]],
        "counted": "3,650 simulated days",
        "asks": [
            {"move": "inductive", "target": "sunburn", "given": {}, "label": "many people get sunburnt, on any day"},
            {"move": "inductive", "target": "sunburn", "given": {"ice_cream": True},
             "label": "many people get sunburnt, when ice cream sales are high"},
            {"move": "deductive", "target": "sunburn", "given": {"ice_cream": True, "hot": True},
             "label": "many people get sunburnt, on a hot day with high ice cream sales"},
            {"move": "deductive", "target": "sunburn", "given": {"hot": True},
             "label": "many people get sunburnt, on a hot day"},
            {"move": "abductive", "target": "hot", "given": {"ice_cream": True, "sunburn": True},
             "label": "the day is hot, given high ice cream sales and many sunburns"},
        ],
        "lesson": "Ice cream and sunburns move together, but once you know the day is hot, ice cream adds nothing, so the heat is the hidden cause.",
    },
}


def case_network(case):
    """The network of a case, from a built-in case id or a case dict."""
    case = CONCEPTS[case] if isinstance(case, str) else case
    return NETWORKS[case["id"]]


def parents(net, node_id):
    return [a for a, _, b in net["edges"] if b == node_id]


def order(net):
    """Node ids with every parent before its children."""
    done = []
    while len(done) < len(net["nodes"]):
        for n in net["nodes"]:
            if n["id"] not in done and all(p in done for p in parents(net, n["id"])):
                done.append(n["id"])
    return done


def learn(net, data):
    """The inductive move. For each node and each mix of its parents' values,
    count how often the node is true. One extra true and one extra false are
    added, so a mix never seen gives 50% and not a divide by zero.
    Returns {node id: {parent values as a tuple: chance of true}}."""
    table = {}
    for n in net["nodes"]:
        ps = parents(net, n["id"])
        table[n["id"]] = {}
        for values in itertools.product([True, False], repeat=len(ps)):
            rows = [r for r in data if all(r[p] == v for p, v in zip(ps, values))]
            table[n["id"]][values] = (sum(r[n["id"]] for r in rows) + 1) / (len(rows) + 2)
    return table


@lru_cache(maxsize=None)
def model(case_id):
    """The network of a built-in case with its chances learned from its data.
    Cached, so the simulation runs once per server start."""
    net = NETWORKS[case_id]
    return learn(net, net["data"]())


def _joint(net, table, world):
    chance = 1.0
    for n in net["nodes"]:
        p = table[n["id"]][tuple(world[x] for x in parents(net, n["id"]))]
        chance *= p if world[n["id"]] else 1 - p
    return chance


def chance(net, table, target, given=None):
    """The chance that target is true, given the values in "given", by adding up
    every possible world that fits. Works in any direction along the edges."""
    given = given or {}
    ids = [n["id"] for n in net["nodes"]]
    top = bottom = 0.0
    for values in itertools.product([True, False], repeat=len(ids)):
        world = dict(zip(ids, values))
        if any(world[k] != v for k, v in given.items()):
            continue
        p = _joint(net, table, world)
        bottom += p
        top += p if world[target] else 0.0
    return top / bottom


def findings(case_id):
    """Each "ask" of the case answered as a whole percentage, for the page and the Tutor."""
    net, table = NETWORKS[case_id], model(case_id)
    return [{**ask, "percent": round(100 * chance(net, table, ask["target"], ask["given"]))}
            for ask in net["asks"]]


def view(case_id):
    """Everything the Knowledge page shows for one network."""
    net = NETWORKS[case_id]
    return {**graph(case_id), "counted": net["counted"], "lesson": net["lesson"], "findings": findings(case_id)}


def graph(case_id):
    """The network in the shared shape, nodes and edges, with each node's learned
    chances in percent, ready for an agent or the page."""
    net, table = NETWORKS[case_id], model(case_id)
    nodes = [{"id": n["id"], "why": n["why"], "text": n["text"], "parents": parents(net, n["id"]),
              "chances": [{"given": dict(zip(parents(net, n["id"]), values)), "percent": round(100 * p)}
                          for values, p in table[n["id"]].items()]}
             for n in net["nodes"]]
    return {"nodes": nodes, "edges": [list(e) for e in net["edges"]]}
