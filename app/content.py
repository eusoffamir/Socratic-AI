"""Fixed content: the six Socratic levels, the nine standards, question formats, and the quant topic."""

LEVELS = [
    ("clarify", "Clarify", "Ask what the learner means, or ask them to say an idea in their own words."),
    ("assumption", "Assumptions", "Ask what the learner is assuming, and what changes if that assumption is wrong."),
    ("evidence", "Evidence", "Ask how they know, what data would support the claim, and how much data is enough."),
    ("viewpoint", "Viewpoints", "Ask how a sceptic, or someone who disagrees, would see it."),
    ("implication", "Implications", "Ask what follows if the learner is right, and where the idea could fail."),
    ("question_the_question", "Question the question",
     "Ask whether this is the right question at all, and what better question is hiding underneath."),
]
MOVES = [k for k, _, _ in LEVELS] + ["none"]

STANDARDS = {
    "clarity": "the answer is easy to understand and says what it means",
    "accuracy": "what is said is true and consistent with the notes",
    "precision": "it gives specific detail, such as numbers, counts or examples, not vague words",
    "relevance": "it stays on the question that was asked",
    "depth": "it goes beneath the surface, for example by giving a reason or a mechanism",
    "breadth": "it considers more than one angle or possibility",
    "logic": "the steps follow, and the conclusion follows from the reasons given",
    "significance": "it focuses on what matters most for the question",
    "fairness": "it treats other views, or the chance of being wrong, honestly",
}

# One short tip per standard, shown in the learner's profile when it is the weakest.
STANDARD_TIPS = {
    "clarity": "Say your idea in one plain sentence.",
    "accuracy": "Check your claim against the notes.",
    "precision": "Use a number or an example.",
    "relevance": "Answer the exact question asked.",
    "depth": "Give a reason. Say why.",
    "breadth": "Look at one more angle.",
    "logic": "Make each step follow from the last.",
    "significance": "Focus on what matters most.",
    "fairness": "Say how you could be wrong.",
}

FORMATS = [
    "open question",
    "predict what happens next",
    "spot the flaw in a claim",
    "choose A or B and defend the choice",  # the easiest format, used when the learner is stuck
]

# The prototype knowledge base. Later this can be replaced by RAG over real reading material.
CONCEPTS = {
    "pattern_or_luck": {
        "title": "Pattern or luck?",
        "mission": "Tell a real pattern from luck.",
        "tag": "Luck",
        "tool": "simulate_streaks",
        "scenario": "A stock went up 5 days in a row. Your friend says: \"It's a pattern! Buy it now!\"",
        # Notes use numbers and symbols, not long sentences: the learners read them fast.
        "notes": [
            "Each day = coin flip: up or down.",
            "5 ups in a row = 1/32 chance.",
            "Many stocks × many days → streaks happen often, by luck.",
            "A streak alone ≠ proof of a pattern.",
            "Real pattern = shows up again and again.",
        ],
        # Short reading shown in a pop-up before the case starts. DRAFT: written for
        # the prototype, to be checked by the supervisor. Numbers match tools.py.
        "reading": {
            "idea": [
                "Each day = coin flip: up or down.",
                "5 ups in a row = 1/2 × 1/2 × 1/2 × 1/2 × 1/2 = 1/32.",
                "500 stocks → about 500 ÷ 32 ≈ 15 do it, by luck.",
                "1 streak ≠ proof. Proof = it repeats on new days.",
            ],
            "example": "NVDA went up 5 days in a row. Out of 500 stocks, about 15 do this every week, just by luck.",
            "key_words": [
                ["Streak", "the same move, many days in a row"],
                ["Luck", "no reason behind it, like a coin flip"],
                ["Pattern", "a move that repeats, for a real reason"],
            ],
            "think": "If 15 of 500 stocks do this by luck, how could you tell if NVDA is different?",
        },
    },
    "holds_on_new_data": {
        "title": "Will it work again?",
        "mission": "See why a rule that worked can fail.",
        "tag": "Testing",
        "tool": "test_many_rules",
        "scenario": "Someone tried 200 buying rules on old prices. 1 rule would have made a lot of money.",
        "notes": [
            "Trading rule = a simple plan. Example: buy after 3 down days.",
            "Experts split old data: part 1 finds the rule, part 2 tests it.",
            "Try 200 rules → 1 looks great, by luck.",
            "Fits the past too well = overfitting. It learned noise, not a pattern.",
            "Still works on new data → much better proof.",
        ],
        "reading": {
            "idea": [
                "Trading rule = a simple plan. Example: buy after 3 down days.",
                "Try 200 rules on old prices → 1 will look great, by luck.",
                "Fix: split the data. Part 1 finds the rule. Part 2 tests it.",
                "Still works on part 2 → much better proof.",
            ],
            "example": "Best of 200 random rules: +32% on old data → only +8% on new data.",
            "key_words": [
                ["Backtest", "testing a rule on old prices"],
                ["Overfitting", "a rule that fits past noise, not a real pattern"],
                ["New data", "prices the rule has never seen"],
            ],
            "think": "Why would a big winner on old data do worse on new data?",
        },
    },
    "together_not_cause": {
        "title": "Moving together, but why?",
        "mission": "See why moving together is not proof.",
        "tag": "Links",
        "tool": "random_pairs_correlation",
        "scenario": "For 1 year, a stock's price and the rain in 1 city went up and down together.",
        "notes": [
            "2 things moving together = correlation.",
            "Could be luck. Or a 3rd thing causes both: heat → ice cream ↑ and sunburn ↑.",
            "Experts ask: Is there a reason? Does it repeat on new data?",
            "No reason + no repeat = weak reason to buy.",
        ],
        "reading": {
            "idea": [
                "2 things moving together = correlation.",
                "It can be luck: 100 random pairs → about 19 move together strongly.",
                "Or a 3rd thing causes both: heat → ice cream ↑ and sunburn ↑.",
                "Ask 2 things: Is there a reason? Does it repeat on new data?",
            ],
            "example": "A stock's price and the rain moved together for 1 year. There is no clear reason rain moves a stock.",
            "key_words": [
                ["Correlation", "2 things moving up and down together"],
                ["Cause", "one thing makes the other happen"],
                ["Hidden 3rd factor", "something else behind both"],
            ],
            "think": "What 3rd thing could make both the stock and the rain move?",
        },
    },
}
