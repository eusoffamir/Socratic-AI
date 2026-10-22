"""Heuristics as decision trees, for Goal 3 (Meeting 2 with Dr Ho, 19 October 2026).

A heuristic is a rule of thumb an expert uses. Each case has one small decision
tree. A "question" node is what the expert asks, a "decision" node is what they
do in the end, and an edge is the answer that leads from one node to the next.
Every node points to the knowledge graph node it rests on ("why"), so the tree
and the book knowledge in knowledge.py stay joined.

Walking the tree from the top question to a decision is deductive reasoning,
because known facts (the answers) and fixed rules (the branches) give the
conclusion. See docs/supervisor/goal3-plan.md.

DRAFT: drafted by Claude on 22 October 2026, to be checked by Dr Ho.
"""

from .content import CONCEPTS

KINDS = ("question", "decision")

TREES = {
    "pattern_or_luck": {
        "root": "q_beats_luck",
        "nodes": [
            {"id": "q_beats_luck", "kind": "question", "why": "step_compare",
             "text": "Did more stocks make this streak than luck alone would give, which is about 3%?"},
            {"id": "q_repeats", "kind": "question", "why": "real_pattern",
             "text": "Does the streak keep showing up on new days?"},
            {"id": "d_luck", "kind": "decision", "why": "not_proof",
             "text": "Treat the streak as luck, so do not buy because of it."},
            {"id": "d_faded", "kind": "decision", "why": "not_proof",
             "text": "The streak did not repeat, so it was likely luck and is no reason to buy."},
            {"id": "d_maybe_real", "kind": "decision", "why": "check_repeat",
             "text": "It may be a real pattern, so it is worth a closer look before buying."},
        ],
        "edges": [
            ["q_beats_luck", "no", "d_luck"],
            ["q_beats_luck", "yes", "q_repeats"],
            ["q_repeats", "no", "d_faded"],
            ["q_repeats", "yes", "d_maybe_real"],
        ],
    },
    "holds_on_new_data": {
        "root": "q_tested",
        "nodes": [
            {"id": "q_tested", "kind": "question", "why": "step_test",
             "text": "Was the rule tested on new data it had never seen?"},
            {"id": "q_how_many", "kind": "question", "why": "ask_how_many",
             "text": "Were many rules tried to find it?"},
            {"id": "q_still_works", "kind": "question", "why": "new_data_proof",
             "text": "Did it still make money on the new data?"},
            {"id": "d_luck", "kind": "decision", "why": "many_rules",
             "text": "Its great result is likely luck, so test it on new data before using it."},
            {"id": "d_test_first", "kind": "decision", "why": "split",
             "text": "It might be real, but test it on new data before using it."},
            {"id": "d_overfit", "kind": "decision", "why": "overfit",
             "text": "It was overfitting, so do not use the rule."},
            {"id": "d_use_with_care", "kind": "decision", "why": "new_data_proof",
             "text": "That is much better proof, so the rule is worth using with care."},
        ],
        "edges": [
            ["q_tested", "no", "q_how_many"],
            ["q_tested", "yes", "q_still_works"],
            ["q_how_many", "yes", "d_luck"],
            ["q_how_many", "no", "d_test_first"],
            ["q_still_works", "no", "d_overfit"],
            ["q_still_works", "yes", "d_use_with_care"],
        ],
    },
    "together_not_cause": {
        "root": "q_reason",
        "nodes": [
            {"id": "q_reason", "kind": "question", "why": "step_reason",
             "text": "Is there a real reason that links the two things?"},
            {"id": "q_hidden", "kind": "question", "why": "luck_or_hidden",
             "text": "Could a hidden 3rd thing be causing both?"},
            {"id": "q_repeats_with_reason", "kind": "question", "why": "step_repeat",
             "text": "Does the link repeat on new data?"},
            {"id": "q_repeats_no_reason", "kind": "question", "why": "step_repeat",
             "text": "Does the link repeat on new data?"},
            {"id": "d_hidden", "kind": "decision", "why": "ice_cream",
             "text": "The link may come from the hidden thing, so study that thing instead."},
            {"id": "d_worth_using", "kind": "decision", "why": "step_repeat",
             "text": "It has a reason and it repeats, so the link is worth using with care."},
            {"id": "d_faded", "kind": "decision", "why": "random_pairs",
             "text": "It did not repeat, so treat the link as luck."},
            {"id": "d_find_reason", "kind": "decision", "why": "luck_or_hidden",
             "text": "It repeats but has no reason yet, so look for a reason or a hidden 3rd thing before buying."},
            {"id": "d_do_not_buy", "kind": "decision", "why": "do_not_buy",
             "text": "With no reason and no repeat, do not buy because of the link."},
        ],
        "edges": [
            ["q_reason", "yes", "q_hidden"],
            ["q_reason", "no", "q_repeats_no_reason"],
            ["q_hidden", "yes", "d_hidden"],
            ["q_hidden", "no", "q_repeats_with_reason"],
            ["q_repeats_with_reason", "yes", "d_worth_using"],
            ["q_repeats_with_reason", "no", "d_faded"],
            ["q_repeats_no_reason", "yes", "d_find_reason"],
            ["q_repeats_no_reason", "no", "d_do_not_buy"],
        ],
    },
}


def case_tree(case):
    """The tree of a case, from a built-in case id or a case dict. A generated
    case will carry its own tree (Goal 3, step 7)."""
    case = CONCEPTS[case] if isinstance(case, str) else case
    return case.get("heuristics") or TREES[case["id"]]


def branches(tree, node_id):
    """The answers out of a node, as {answer: next node id}."""
    return {answer: b for a, answer, b in tree["edges"] if a == node_id}


def problems(tree, graph=None):
    """What is wrong with a tree, as short messages. An empty list means it is a
    proper tree, so a drafted tree can be checked the same way as the built-in ones.
    With the case's knowledge graph, every "why" must name one of its nodes."""
    nodes = {n["id"]: n for n in tree["nodes"]}
    out = []
    if len(nodes) != len(tree["nodes"]):
        out.append("node ids repeat")
    if tree.get("root") not in nodes:
        return out + ["the root is missing"]
    parents = {}
    for a, answer, b in tree["edges"]:
        if a not in nodes or b not in nodes:
            out.append(f"the {answer} branch from {a} joins a missing node")
            continue
        parents.setdefault(b, []).append(a)
    known = {n["id"] for n in graph["nodes"]} if graph else None
    for n in tree["nodes"]:
        out_answers = [answer for a, answer, _ in tree["edges"] if a == n["id"]]
        if n.get("kind") not in KINDS:
            out.append(f"{n['id']} has an unknown kind")
        elif n["kind"] == "question" and len(out_answers) < 2:
            out.append(f"{n['id']} needs at least 2 answers")
        elif n["kind"] == "decision" and out_answers:
            out.append(f"{n['id']} is a decision, so it cannot branch")
        if len(out_answers) != len(set(out_answers)):
            out.append(f"{n['id']} has the same answer twice")
        if len(parents.get(n["id"], [])) != (0 if n["id"] == tree["root"] else 1):
            out.append(f"{n['id']} needs {'no parent' if n['id'] == tree['root'] else 'exactly 1 parent'}")
        if known is not None and n.get("why") not in known:
            out.append(f"{n['id']} rests on an unknown knowledge node")
    # One parent each still allows a loop cut off from the root, so walk from the top.
    seen, todo = set(), [tree["root"]]
    while todo:
        at = todo.pop()
        if at not in seen:
            seen.add(at)
            todo.extend(branches(tree, at).values())
    out += [f"{i} cannot be reached from the root" for i in nodes if i not in seen]
    return out


def walk(case, answers):
    """The deductive move. Start at the top question and take the branch each
    answer gives, such as {"q_beats_luck": "yes"}, until a decision is reached.

    The walk stops early at the first question with no usable answer, so the
    result also says what to ask next. Returns the path as [question id, answer]
    steps, the node reached, its text, and whether it is a decision."""
    tree = case_tree(case)
    nodes = {n["id"]: n for n in tree["nodes"]}
    path, at = [], tree["root"]
    while nodes[at]["kind"] == "question":
        answer = str(answers.get(at, "")).strip().lower()
        nxt = branches(tree, at).get(answer)
        if nxt is None:
            break
        path.append([at, answer])
        at = nxt
    return {"path": path, "at": at, "text": nodes[at]["text"], "done": nodes[at]["kind"] == "decision"}


def rules(case):
    """The tree read as IF-THEN rules, one per path from the top to a decision,
    as {"if": [[question id, answer], ...], "then": decision id}."""
    tree = case_tree(case)
    out = []

    def down(at, conditions):
        if not branches(tree, at):
            out.append({"if": conditions, "then": at})
        for answer, nxt in branches(tree, at).items():
            down(nxt, conditions + [[at, answer]])

    down(tree["root"], [])
    return out
