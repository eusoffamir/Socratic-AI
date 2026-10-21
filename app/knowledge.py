"""Knowledge layer for Goal 1 (Meeting 2 with Dr Ho, 19 October 2026).

Each case is a small knowledge graph. A node is one piece of knowledge with its
type (Dr Ho's list), and an edge is a link such as "causes" or "then".
Nodes with a "note" number are the case notes in content.CONCEPTS, so the graph
and the notes the Tutor reads stay the same text.

DRAFT: drafted by Claude on 21 October 2026, to be checked by Dr Ho.
"""

from app.content import CONCEPTS

# Dr Ho's types of knowledge. The first five are "knowing", the last three are
# "knowing that leads to doing" and end in a decision or choice.
KNOWLEDGE_TYPES = {
    "factual": "What is true?",
    "conceptual": "What does it mean?",
    "procedural": "How do I do it?",
    "causal": "Why does it happen?",
    "relational": "How are things connected?",
    "strategic": "What should I do, given the situation?",
    "metacognitive": "How do I know, and how reliable is my knowing?",
    "epistemic": "What is justified for me to believe?",
}

# Edge meanings. "then" joins the steps of procedural knowledge, "causes" is
# causal knowledge, and the rest are the different arrows of relational knowledge.
RELATIONS = {
    "causes": "makes the other happen",
    "then": "is the next step after",
    "defines": "gives the meaning of",
    "supports": "is a reason to believe",
    "weakens": "is a reason to doubt",
    "tests": "is a way to check",
    "leads_to": "points to the choice",
}

KNOWLEDGE = {
    "pattern_or_luck": {
        "nodes": [
            {"id": "coin", "type": "conceptual", "note": 0},
            {"id": "streak_chance", "type": "factual", "note": 1},
            {"id": "many_tries", "type": "causal", "note": 2},
            {"id": "not_proof", "type": "epistemic", "note": 3},
            {"id": "real_pattern", "type": "conceptual", "note": 4},
            {"id": "multiply", "type": "relational",
             "text": "The chance of 5 up days is 50% multiplied by itself 5 times, which is about 3%."},
            {"id": "count_500", "type": "factual",
             "text": "Out of 500 stocks, about 15 go up 5 days in a row just by luck."},
            {"id": "step_count", "type": "procedural",
             "text": "First count how many stocks did the same streak."},
            {"id": "step_compare", "type": "procedural",
             "text": "Then compare that count with the number luck alone would give."},
            {"id": "check_repeat", "type": "strategic",
             "text": "Before buying, check whether the streak repeats on new days."},
        ],
        "edges": [
            ["coin", "supports", "multiply"],
            ["multiply", "supports", "streak_chance"],
            ["streak_chance", "supports", "count_500"],
            ["many_tries", "causes", "count_500"],
            ["count_500", "weakens", "real_pattern"],
            ["count_500", "supports", "not_proof"],
            ["step_count", "then", "step_compare"],
            ["step_compare", "tests", "real_pattern"],
            ["real_pattern", "defines", "check_repeat"],
            ["not_proof", "leads_to", "check_repeat"],
        ],
    },
    "holds_on_new_data": {
        "nodes": [
            {"id": "rule", "type": "conceptual", "note": 0},
            {"id": "split", "type": "procedural", "note": 1},
            {"id": "many_rules", "type": "causal", "note": 2},
            {"id": "overfit", "type": "conceptual", "note": 3},
            {"id": "new_data_proof", "type": "epistemic", "note": 4},
            {"id": "best_10", "type": "factual",
             "text": "The 10 best of 200 random rules made +21% on old data on average, but -2% on new data."},
            {"id": "step_find", "type": "procedural",
             "text": "First find the rule using only the first part of the data."},
            {"id": "step_test", "type": "procedural",
             "text": "Then test the same rule on the second part, without changing it."},
            {"id": "more_tries_more_luck", "type": "relational",
             "text": "The more rules you try, the better the best one looks by luck alone."},
            {"id": "ask_how_many", "type": "strategic",
             "text": "Before trusting a rule, ask how many rules were tried to find it."},
        ],
        "edges": [
            ["many_rules", "causes", "best_10"],
            ["more_tries_more_luck", "supports", "many_rules"],
            ["overfit", "defines", "best_10"],
            ["split", "defines", "step_find"],
            ["step_find", "then", "step_test"],
            ["step_test", "tests", "overfit"],
            ["step_test", "supports", "new_data_proof"],
            ["best_10", "weakens", "rule"],
            ["more_tries_more_luck", "leads_to", "ask_how_many"],
        ],
    },
    "together_not_cause": {
        "nodes": [
            {"id": "correlation", "type": "conceptual", "note": 0},
            {"id": "luck_or_hidden", "type": "causal", "note": 1},
            {"id": "expert_questions", "type": "procedural", "note": 2},
            {"id": "weak_reason", "type": "epistemic", "note": 3},
            {"id": "random_pairs", "type": "factual",
             "text": "About 19 out of 100 random pairs move together strongly, just by luck."},
            {"id": "ice_cream", "type": "relational",
             "text": "Hot weather raises both ice cream sales and sunburns, so the two move together."},
            {"id": "step_reason", "type": "procedural",
             "text": "First look for a real reason that links the two things."},
            {"id": "step_repeat", "type": "procedural",
             "text": "Then check whether the link repeats on new data."},
            {"id": "no_reason_rain", "type": "factual",
             "text": "There is no clear reason why rain in 1 city would move a stock."},
            {"id": "do_not_buy", "type": "strategic",
             "text": "Without a reason and a repeat, do not buy because of the link."},
        ],
        "edges": [
            ["random_pairs", "supports", "luck_or_hidden"],
            ["ice_cream", "supports", "luck_or_hidden"],
            ["luck_or_hidden", "weakens", "correlation"],
            ["expert_questions", "defines", "step_reason"],
            ["step_reason", "then", "step_repeat"],
            ["step_repeat", "tests", "correlation"],
            ["no_reason_rain", "supports", "weak_reason"],
            ["weak_reason", "leads_to", "do_not_buy"],
        ],
    },
}


def node_text(case_id, node):
    """The text of a node. Note nodes read the case note, so the two never drift apart."""
    if "note" in node:
        return CONCEPTS[case_id]["notes"][node["note"]]
    return node["text"]


def graph(case_id):
    """The case graph with every node's text filled in, ready for an agent or the page."""
    g = KNOWLEDGE[case_id]
    nodes = [{"id": n["id"], "type": n["type"], "text": node_text(case_id, n)} for n in g["nodes"]]
    return {"nodes": nodes, "edges": [list(e) for e in g["edges"]]}


def types_in(case_id):
    """Which knowledge types a case covers, in Dr Ho's order."""
    used = {n["type"] for n in KNOWLEDGE[case_id]["nodes"]}
    return [t for t in KNOWLEDGE_TYPES if t in used]
