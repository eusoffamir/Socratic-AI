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


# Goal 3, step 4: where each node comes from. Dr Ho has not named a quant
# textbook yet, so the "books" are fixed versions of Wikipedia articles (the
# oldid links never change). A "book" source quotes the article exactly, and
# eval/check_quotes.py checks every quote against the live article. "data" is a
# number counted by a simulation in tools.py, "heuristic" is a decision in
# heuristics.py, and "case" is a fact from the case story itself.
BOOKS = {
    "random_walk": ("Random walk hypothesis", 1378704873),
    "gamblers_fallacy": ("Gambler's fallacy", 1374294111),
    "clustering_illusion": ("Clustering illusion", 1373126978),
    "multiple_comparisons": ("Multiple comparisons problem", 1376255469),
    "data_dredging": ("Data dredging", 1377936004),
    "look_elsewhere": ("Look-elsewhere effect", 1375618893),
    "overfitting": ("Overfitting", 1374396766),
    "test_sets": ("Training, validation, and test data sets", 1379499860),
    "trading_strategy": ("Trading strategy", 1374935987),
    "correlation": ("Correlation", 1379810158),
    "spurious": ("Spurious relationship", 1374235767),
    "not_causation": ("Correlation does not imply causation", 1371652483),
    "confounding": ("Confounding", 1371518385),
}

SOURCES = {
    "pattern_or_luck": {
        "coin": ("random_walk", "Malkiel argued that this indicates that the market and stocks could be just as random as flipping a coin."),
        "streak_chance": ("gamblers_fallacy", "While a run of five heads has a probability of 1/32 = 0.03125 (a little over 3%)"),
        "many_tries": ("multiple_comparisons", "the overall probability of making at least one false positive increases as the number of tests grows"),
        "not_proof": ("clustering_illusion", "the tendency to erroneously consider the inevitable \"streaks\" or \"clusters\" arising in small samples from random distributions to be non-random"),
        "real_pattern": ("data_dredging", "If the hypothesis is not tested on a different data set from the same statistical population, it is impossible to assess the likelihood that chance alone would produce such patterns."),
        "multiply": ("gamblers_fallacy", "The outcomes in different tosses are statistically independent and the probability of getting heads on a single toss is 1/2 (one in two)."),
        "count_500": "simulate_streaks",
        "step_count": ("multiple_comparisons", "if 100 tests are each conducted at the 5% level and all corresponding null hypotheses are true, the expected number of incorrect rejections (also known as false positives or Type I errors) is 5."),
        "step_compare": ("data_dredging", "Conventional tests of statistical significance are based on the probability that a particular result would arise if chance alone were at work"),
        "check_repeat": ("data_dredging", "Once a hypothesis is formulated, it must be tested on subset B, which was not used to construct the hypothesis."),
    },
    "holds_on_new_data": {
        "rule": ("trading_strategy", "a trading strategy is a fixed plan that is designed to achieve a profitable return by going long or short in markets."),
        "split": ("test_sets", "A test data set is a data set that is independent of the training data set, but that follows the same probability distribution as the training data set."),
        "many_rules": ("data_dredging", "When enough hypotheses are tested, it is virtually certain that some will be reported to be statistically significant (even though this is misleading)"),
        "overfit": ("overfitting", "The essence of overfitting is to unknowingly extract some of the residual variation (i.e., noise) as if that variation represents the underlying model structure."),
        "new_data_proof": ("overfitting", "The optimal function usually needs verification on bigger or completely new datasets."),
        "best_10": "test_many_rules",
        "step_find": ("test_sets", "The model is initially fit on a training data set"),
        "step_test": ("test_sets", "The holdout method can also be employed, where the test set is used at the end, after training on the training set."),
        "more_tries_more_luck": ("multiple_comparisons", "The larger the number of inferences made in a series of tests, the more likely erroneous inferences become."),
        "ask_how_many": ("look_elsewhere", "an apparently statistically significant observation may have actually arisen by chance because of the sheer size of the parameter space to be searched."),
    },
    "together_not_cause": {
        "correlation": ("correlation", "In statistics, correlation is a type of statistical relationship between two random variables or bivariate data."),
        "luck_or_hidden": ("spurious", "two or more events or variables are associated but not causally related, due to either coincidence or the presence of a certain third, unseen factor"),
        "expert_questions": ("confounding", "careful study design and analytical methods (such as randomization, statistical adjustment, or causal diagrams) are required to distinguish causal effects from spurious associations."),
        "weak_reason": ("not_causation", "the inability to legitimately deduce a cause-and-effect relationship between two events or variables solely on the basis of an observed association or correlation between them."),
        "random_pairs": "random_pairs_correlation",
        "ice_cream": ("not_causation", "Ice cream is sold during the hot summer months at a much greater rate than during colder times, and it is during these hot summer months that people are more likely to engage in activities involving water, such as swimming."),
        "step_reason": ("not_causation", "a lurking variable, which is simply a hidden third variable that affects both of the variables observed to be correlated."),
        "step_repeat": ("data_dredging", "If the hypothesis is not tested on a different data set from the same statistical population, it is impossible to assess the likelihood that chance alone would produce such patterns."),
        "no_reason_rain": "case",
        "do_not_buy": "heuristic:d_do_not_buy",
    },
}


def book_url(key):
    title, oldid = BOOKS[key]
    return f"https://en.wikipedia.org/w/index.php?title={title.replace(' ', '_')}&oldid={oldid}"


def source_of(case, node):
    """Where a node comes from, as {"kind": "book" | "data" | "heuristic" | "case", ...},
    or None when nothing backs it. A generated node carries the quote the
    Builder checked against its source text (builder.py)."""
    case = _case(case)
    if node.get("quote"):
        return {"kind": "book", "title": node.get("from") or "", "quote": node["quote"]}
    found = SOURCES.get(case.get("id"), {}).get(node["id"])
    if isinstance(found, tuple):
        return {"kind": "book", "title": BOOKS[found[0]][0], "url": book_url(found[0]), "quote": found[1]}
    if found == "case":
        return {"kind": "case"}
    if isinstance(found, str) and found.startswith("heuristic:"):
        return {"kind": "heuristic", "node": found.split(":", 1)[1]}
    if found:
        return {"kind": "data", "tool": found}
    return None


def grounded(case):
    """How many of a case's nodes have a source, out of how many, for the page and Dr Ho."""
    nodes = case_graph(case)["nodes"]
    return {"sourced": sum(source_of(case, n) is not None for n in nodes), "nodes": len(nodes)}


def _case(case):
    """A case dict, from a built-in case id or a generated case itself."""
    return CONCEPTS[case] if isinstance(case, str) else case


def case_graph(case):
    """The raw graph of a case. A generated case carries its own."""
    case = _case(case)
    return case.get("knowledge") or KNOWLEDGE[case["id"]]


def node_text(case, node):
    """The text of a node. Note nodes read the case note, so the two never drift apart."""
    if "note" in node:
        return _case(case)["notes"][node["note"]]
    return node["text"]


def graph(case):
    """The case graph with every node's text filled in, ready for an agent or the page."""
    g = case_graph(case)
    nodes = [{"id": n["id"], "type": n["type"], "text": node_text(case, n), **({"label": n["label"]} if n.get("label") else {}),
              **({"source": s} if (s := source_of(case, n)) else {})}
             for n in g["nodes"]]
    return {"nodes": nodes, "edges": [list(e) for e in g["edges"]]}


def types_in(case):
    """Which knowledge types a case covers, in Dr Ho's order."""
    used = {n["type"] for n in case_graph(case)["nodes"]}
    return [t for t in KNOWLEDGE_TYPES if t in used]
