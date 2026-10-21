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

# One tip per standard, used in the end-of-session comments. Written as smooth,
# easy sentences (the student found clipped "It is red." style hard to read).
STANDARD_TIPS = {
    "clarity": "Try to say your main idea in one clear sentence.",
    "accuracy": "Check that what you say matches the facts in the case.",
    "precision": "Add a number or a real example to back up your point.",
    "relevance": "Make sure you answer the exact question that was asked.",
    "depth": "Explain why, not just what, by giving a reason.",
    "breadth": "Look at the problem from one more angle.",
    "logic": "Make sure each step leads clearly to the next one.",
    "significance": "Focus on the point that matters most.",
    "fairness": "Say how you might be wrong, or what someone else might think.",
}

# "Learn with Socrates": a fixed 3-round tutorial. Socrates answers round 1,
# the learner picks in round 2 and Socrates adds the why, the learner answers
# round 3 (checked by the real Assessor, or by plain code if it fails).
# Each example sentence lists the standards it meets, so all 9 light up.
# The level goes up 1 step per round, like a real case after a good answer.
# DRAFT text, to be checked by the supervisor. Numbers match the case notes.
TUTORIAL = {
    "id": "tutorial",
    "title": "Tutorial",
    "tag": "Start here",
    "mission": "Learn how to answer critically.",
    "scenario": "A coin has landed on heads 4 times in a row, and your friend says tails is now \"due\".",
    # shown in the reading pop-up before the tutorial starts, same as a case
    "reading": {
        "idea": [
            "Every flip has a 50% chance of heads and a 50% chance of tails.",
            "A coin has no memory, so the last 4 flips do not change the next one.",
            "Getting 4 heads in a row happens about 6% of the time (50% × 50% × 50% × 50%), so luck can easily do it.",
            "In this app, every answer is checked against 9 standards, and each standard you meet earns 1 point.",
        ],
        "example": "Your friend saw 4 heads and now bets on tails, but the coin has no idea what came before.",
        "key_words": [
            ["Due", "expected to happen soon"],
            ["Assumption", "something you believe without checking it"],
            ["Standard", "a sign of good thinking, such as clarity or logic"],
        ],
        "think": "If a coin has no memory, can tails ever really be \"due\"?",
    },
    "rounds": [
        {
            "level": "clarify",
            "feedback": "Watch me type my answer, then press Enter to send it.",
            "format": "open question",
            "question": "What does \"due\" mean here, in your own words?",
            "key_idea": "Each flip is still 50%, because a coin has no memory.",
            "answer": [
                ["\"Due\" means my friend thinks tails is more likely now,", ["clarity", "relevance"]],
                ["but a coin has no memory,", ["accuracy", "logic"]],
                ["so each flip is still 50%, even after 4 heads.", ["precision", "depth"]],
                ["The past flips do not change the next one.", ["significance"]],
                ["I could be wrong if the coin is bent, so I would test that first.", ["fairness", "breadth"]],
            ],
        },
        {
            "level": "assumption",
            "feedback": "Now pick A or B, and I will type the why.",
            "format": "choose A or B and defend the choice",
            "question": "What is your friend assuming?",
            "key_idea": "Ask yourself whether the coin can know what came before.",
            "options": ["The coin remembers past flips", "The coin is bent"],
            "best": 0,
            "pick_standards": ["accuracy"],  # earned only by the right pick
            "right": "Good pick. Watch how I explain why.",
            "wrong": "A is the stronger choice. Watch how I explain why.",
            "answer": [
                ["\"Due\" only makes sense if the coin keeps score of past flips,", ["clarity", "relevance", "logic"]],
                ["but it does not, so each flip stays at 50% and the 4 heads change nothing.", ["precision", "depth"]],
                ["That hidden belief is the main mistake in the claim.", ["significance"]],
                ["I could be wrong if the coin is bent, but a bent coin would favour heads, not tails.", ["breadth", "fairness"]],
            ],
        },
        {
            "level": "evidence",
            "feedback": "Now you try, and aim to meet all 9 standards.",
            "format": "open question",
            "question": "A stock rose 5 days in a row. How would you check whether this is a real pattern or just luck?",
            "key_idea": "One streak is not proof, but a pattern that repeats on new days is.",
            # shown after the learner answers, to compare
            "answer": [
                ["I would test it on new days instead of the same 5 days,", ["clarity", "relevance", "depth"]],
                ["because 5 ups in a row happens about 3% of the time, so out of 500 stocks about 15 do it by luck.",
                 ["precision", "accuracy", "logic"]],
                ["If the rise keeps repeating on new days, that would be real proof.", ["significance"]],
                ["But I could be wrong, since real news might be pushing it up, so I would check that too.", ["fairness", "breadth"]],
            ],
        },
    ],
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
        "scenario": "A stock went up 5 days in a row. Your friend says, \"It is a pattern, so buy it now.\"",
        # Notes keep the numbers but read as smooth, easy sentences.
        "notes": [
            "Each day, a stock going up or down is a bit like a coin flip.",
            "Going up 5 days in a row happens about 3% of the time.",
            "With many stocks and many days, streaks like this happen often, just by luck.",
            "A streak on its own does not prove there is a pattern.",
            "A real pattern is one that keeps showing up again and again.",
        ],
        # Short reading shown in a pop-up before the case starts. DRAFT: written for
        # the prototype, to be checked by the supervisor. Numbers match tools.py.
        "reading": {
            "idea": [
                "Each day, a stock going up or down is a bit like a coin flip.",
                "Going up 5 days in a row happens about 3% of the time (50% × 50% × 50% × 50% × 50%).",
                "Out of 500 stocks, that means about 15 will do it, just by luck.",
                "So one streak is not proof, but a streak that repeats on new days is.",
            ],
            "example": "NVDA went up 5 days in a row, but out of 500 stocks about 15 do this every week just by luck.",
            "key_words": [
                ["Streak", "the same move, many days in a row"],
                ["Luck", "no real reason behind it, like a coin flip"],
                ["Pattern", "a move that repeats for a real reason"],
            ],
            "think": "If 15 out of 500 stocks do this by luck, how could you tell whether NVDA is different?",
        },
    },
    "holds_on_new_data": {
        "title": "Will it work again?",
        "mission": "See why a rule that worked can fail.",
        "tag": "Testing",
        "tool": "test_many_rules",
        "scenario": "Someone tried 200 buying rules on old prices, and 1 of them would have made a lot of money.",
        "notes": [
            "A trading rule is a simple plan, such as buying after 3 down days.",
            "Experts split old data in two, so they find the rule with the first part and then test it on the second.",
            "If you try 200 rules, at least 1 will look great just by luck.",
            "A rule that fits the past too well is overfitting, which means it learned noise instead of a real pattern.",
            "A rule that still works on new data gives much better proof.",
        ],
        "reading": {
            "idea": [
                "A trading rule is a simple plan, such as buying after 3 down days.",
                "If you try 200 rules on old prices, 1 of them will look great just by luck.",
                "The fix is to split the data, using the first part to find the rule and the second part to test it.",
                "If the rule still works on the second part, that is much better proof.",
            ],
            "example": "The 10 best of 200 random rules made +21% on old data on average, but -2% on new data.",
            "key_words": [
                ["Backtest", "testing a rule on old prices"],
                ["Overfitting", "a rule that fits past noise instead of a real pattern"],
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
            "When 2 things move up and down together, this is called correlation.",
            "It could be luck, or a hidden 3rd thing could cause both, like hot weather raising both ice cream sales and sunburns.",
            "Experts ask whether there is a real reason, and whether it repeats on new data.",
            "With no reason and no repeat, it is a weak reason to buy.",
        ],
        "reading": {
            "idea": [
                "When 2 things move up and down together, this is called correlation.",
                "It can happen by luck, since about 19 out of 100 random pairs move together strongly.",
                "Or a hidden 3rd thing can cause both, like hot weather raising both ice cream sales and sunburns.",
                "So ask yourself whether there is a real reason, and whether it repeats on new data.",
            ],
            "example": "A stock's price and the rain moved together for 1 year, but there is no clear reason why rain would move a stock.",
            "key_words": [
                ["Correlation", "2 things moving up and down together"],
                ["Cause", "when one thing makes the other happen"],
                ["Hidden 3rd factor", "something else that drives both"],
            ],
            "think": "What 3rd thing could make both the stock and the rain move?",
        },
    },
}

# Goal 2: the engine works on any topic. The quant cases above are the built-in
# topic, checked by the supervisor. A case made for a learner's own topic (see
# builder.py) has the same shape plus its own "knowledge" graph and no tool.
QUANT_TOPIC = "How quants find real patterns in data"
for _id, _case in CONCEPTS.items():
    _case.update(id=_id, topic=QUANT_TOPIC)


def case_of(session):
    """The case a session is about. A generated case is kept inside the
    session, so it survives a server restart. A built-in case is found by id."""
    return session.get("case") or CONCEPTS[session["concept_id"]]
