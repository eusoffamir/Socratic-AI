"""Skill check (Goal 1, step 4): many short questions, each tagged with the skill it targets.

The Socratic cases are a free dialogue, so they cannot promise enough trials of
each skill. A skill check asks set questions instead. Each question targets one
reasoning type on one knowledge type, so every answer is a clean trial:
attained = 1 when the Reasoning agent marks BOTH the target reasoning type and
the target knowledge type, else 0. Over many checks these 1s and 0s feed the
statistics in step 5 (the tags are the Q-matrix).

One answer costs one model call (the Assessor with the Reasoning agent). There
is no tutor reply, so a check stays cheap and quick.

DRAFT: questions written by Claude on 21 October 2026, to be checked by Dr Ho.
Rewritten on 23 November 2026 to be more fun (people, posts, everyday life),
with the same tag, facts and numbers for each question.
"""
import random

from . import copycheck, llm_client, prompts
from .content import CONCEPTS
from .knowledge import KNOWLEDGE_TYPES
from .reasoning import CORE_KNOWLEDGE, REASONING_TYPES

QUESTIONS_PER_CHECK = 6
MAX_WORDS = 100  # "a few sentences"; a longer answer is sent back, which also stops most pasted AI replies

# (reasoning, knowledge, case, situation, question). Two per pair of reasoning
# type and core knowledge type, so 30 in all.
_BANK = [
    ("inductive", "factual", "pattern_or_luck",
     "Mei counts how many of 500 stocks go up 5 days in a row, every week for a month. She gets 14, 17, 15 and 16, even in boring weeks with no news.",
     "What general idea do her counts suggest about 5 day streaks?"),
    ("inductive", "factual", "together_not_cause",
     "A TikTok trader keeps posting secret twin stocks. You test 4 groups of 100 random pairs, and each time about 18 to 20 pairs move together strongly.",
     "What can you say in general about random pairs from your 4 tests?"),
    ("inductive", "conceptual", "holds_on_new_data",
     "Three YouTubers each showed a trading rule that made a fortune on old prices, and all 3 lost money once people used it on new prices.",
     "What do these 3 stories suggest a great backtest really means?"),
    ("inductive", "conceptual", "pattern_or_luck",
     "Your friend sends you 3 rocket stocks that each went up 5 days in a row, and the next week all 3 just wobbled up and down like normal.",
     "From these 3 cases, what would you say a streak usually means?"),
    ("inductive", "procedural", "holds_on_new_data",
     "Three students in a trading club each found a great rule. The 2 who tested it on new data first kept their gains, but the 1 who went straight to real money lost it.",
     "What step do these 3 stories suggest before trusting any rule?"),
    ("inductive", "procedural", "together_not_cause",
     "Hafiz found a stock that seemed to follow the rain, then football scores, then his cat's mood, and every link vanished on the next year of data.",
     "What habit would you build from his checks?"),
    ("inductive", "causal", "pattern_or_luck",
     "In 3 different years, streaks that started after good earnings news kept going more often than streaks that came out of nowhere.",
     "What general idea about the cause of lasting streaks do these years suggest?"),
    ("inductive", "causal", "together_not_cause",
     "Ice cream sales rise with sunburns, umbrella sales rise with Grab rides, and cold drink sales rise with air conditioning bills.",
     "What do these examples suggest is often behind 2 things moving together?"),
    ("inductive", "relational", "holds_on_new_data",
     "A bot tries random trading rules. With 10 rules the best one made 5%, with 100 rules the best made 12%, and with 1000 rules the best made 25%.",
     "What general link do you see between the number of rules and the best result?"),
    ("inductive", "relational", "pattern_or_luck",
     "With 50 stocks you see 1 streak, with 500 stocks you see 15, and with 5000 stocks a trading app shows about 150 hot streaks.",
     "What link between the number of stocks and the number of streaks do you notice?"),

    ("deductive", "factual", "pattern_or_luck",
     "A stock has about a 50% chance of going up on any day, much like a coin toss.",
     "Using this fact, what is the chance it goes up 3 days in a row, and how did you get it?"),
    ("deductive", "factual", "together_not_cause",
     "About 19 out of 100 random pairs move together strongly just by luck. A crypto group finds 1 perfect pair among the 100 coins it checked.",
     "Based on this fact, what can you conclude about their pair?"),
    ("deductive", "conceptual", "holds_on_new_data",
     "Overfitting means a rule learned the noise in old data instead of a real pattern, like memorising past exam answers instead of learning the subject.",
     "A rule made 40% on old data but lost 5% on new data, so using this meaning, what would you conclude?"),
    ("deductive", "conceptual", "pattern_or_luck",
     "A real pattern is one that keeps showing up again and again.",
     "Your uncle's favourite stock had 1 streak this year and none in any other year, so is it a real pattern by this meaning, and why?"),
    ("deductive", "procedural", "holds_on_new_data",
     "The fair way to test a rule is to find it on the first half of the data and test it on the second half, like a mock exam it has never seen.",
     "Your friend found and tested a rule on the same 2 years of data, so what follows about their test?"),
    ("deductive", "procedural", "pattern_or_luck",
     "To check a streak, you compare how many stocks had it with how many luck alone would give.",
     "Luck gives about 15 out of 500 and you counted 60, so what should you conclude, and why?"),
    ("deductive", "causal", "together_not_cause",
     "Hot weather causes both more ice cream sales and more sunburns.",
     "If next month is cool and rainy, what should happen to both, and why?"),
    ("deductive", "causal", "holds_on_new_data",
     "Trying many rules makes at least 1 of them look great just by luck.",
     "A trading app tried 500 rules and advertises only the best one, so what follows about its result?"),
    ("deductive", "relational", "pattern_or_luck",
     "The more stocks you watch, the more streaks you will see just by luck.",
     "A website watches 5000 stocks and brags about 150 streaks this week, so what does this link tell you about them?"),
    ("deductive", "relational", "together_not_cause",
     "If 2 things share a real reason, their link should still show up on new data.",
     "A link between rain and a stock vanished on new data, so what can you conclude about the reason behind it?"),

    ("abductive", "factual", "pattern_or_luck",
     "Your feed is suddenly full of streak posts. Last week 60 out of 500 stocks went up 5 days in a row, but luck alone gives about 15.",
     "What is the best explanation for so many streaks?"),
    ("abductive", "factual", "holds_on_new_data",
     "A trading course promised 30% a year from its rule's old results, but its students lost 4% in their first year of using it.",
     "What is the most likely explanation for this drop?"),
    ("abductive", "conceptual", "together_not_cause",
     "A viral post says a stock and the rain are strongly correlated, and it tells everyone to buy whenever it rains.",
     "What has the post most likely misunderstood about what correlation means?"),
    ("abductive", "conceptual", "pattern_or_luck",
     "Your friend calls every streak a pattern and buys it, but most of their patterns stop the very next week.",
     "What is the best explanation for why their patterns keep failing?"),
    ("abductive", "procedural", "holds_on_new_data",
     "Two friends tested the same rule, and one made 20% while the other lost 3%.",
     "What difference in how they tested it could best explain this?"),
    ("abductive", "procedural", "together_not_cause",
     "A student brags about a strong link between 2 stocks, but no one else in class can find the same link.",
     "What might the student have done in their method that best explains this?"),
    ("abductive", "causal", "together_not_cause",
     "A beach town's ice cream shop and its sunscreen shop both had record sales in the same month.",
     "What is the most likely cause behind both, and why?"),
    ("abductive", "causal", "pattern_or_luck",
     "Only 1 stock out of 500 went up 10 days in a row, and it started the day the company launched a viral new phone.",
     "What is the best explanation for this streak, and what would you check?"),
    ("abductive", "relational", "holds_on_new_data",
     "A fund's best rule looked better every time they tested more rules, but it never worked with real money.",
     "What link best explains this?"),
    ("abductive", "relational", "together_not_cause",
     "Two bank stocks have moved together almost every day for 5 years, like a pair of best friends.",
     "What connection between the 2 banks could best explain this?"),
]

# Everyday questions (23 November 2026). Eusoff wanted the default skill check
# fun, simple and not about quant, so these need no case notes. Each situation
# holds every fact the learner needs. Same layout, but the case is None.
_EVERYDAY = [
    ("inductive", "factual", None,
     "Your bus came 10 minutes late on Monday, Wednesday and Friday.",
     "What general idea do you get about this bus?"),
    ("inductive", "factual", None,
     "Three bubble tea shops near campus each have a queue of 20 people at 5 pm, but almost nobody at 10 am.",
     "What do these 3 shops suggest about when people buy bubble tea?"),
    ("inductive", "conceptual", None,
     "A mango, a tomato and a cucumber all grow from a flower and hold seeds inside.",
     "From these 3, what do you think makes something a fruit?"),
    ("inductive", "conceptual", None,
     "Aina, Ben and Chong each said they were too busy to study, and each spent over 4 hours on their phone that day.",
     "What do these 3 stories suggest being too busy often means?"),
    ("inductive", "procedural", None,
     "You burned your rice 3 times this month, and each time you had left the kitchen to check your phone.",
     "What cooking habit would you build from these 3 times?"),
    ("inductive", "procedural", None,
     "Three friends bought the same new phone. The 2 who read reviews first were happy, but the 1 who bought it on launch day was not.",
     "What step do these 3 stories suggest before buying a gadget?"),
    ("inductive", "causal", None,
     "On 3 nights you slept after 2 am, and each next morning you did badly in the quiz.",
     "What do these 3 nights suggest about why the quizzes went badly?"),
    ("inductive", "causal", None,
     "Your plant drooped in the week you forgot to water it, in the week it sat in the dark, and in the week it got too hot.",
     "What do these 3 weeks suggest makes a plant droop?"),
    ("inductive", "relational", None,
     "A cafe sold 20 iced drinks on a 25 degree day, 50 on a 30 degree day, and 90 on a 35 degree day.",
     "What link between the heat and iced drink sales do you notice?"),
    ("inductive", "relational", None,
     "Your group project took 4 hours with 2 people, 3 hours with 4 people, and 5 hours with 8 people.",
     "What link do you see between group size and the time taken?"),

    ("deductive", "factual", None,
     "A fair coin has a 50% chance of landing heads each time you flip it.",
     "What is the chance of getting 2 heads in a row, and how did you get it?"),
    ("deductive", "factual", None,
     "Your phone loses about 10% battery every hour while you watch videos, and it has 40% left.",
     "How long can you keep watching before it dies, and why?"),
    ("deductive", "conceptual", None,
     "A mammal is an animal that feeds its babies with milk.",
     "A whale feeds its baby with milk, so is a whale a mammal, and why?"),
    ("deductive", "conceptual", None,
     "A fair game gives every player the same chance to win.",
     "In a board game the host always moves first and wins most games, so is it fair by this meaning, and why?"),
    ("deductive", "procedural", None,
     "In a fair taste test, every drink must be tasted without seeing its label.",
     "Your friend compared 2 colas while looking at the cans, so what follows about the test?"),
    ("deductive", "procedural", None,
     "To get a free coffee, you must buy 9 coffees and show your full stamp card.",
     "Mei bought 9 coffees but lost the stamp card, so does Mei get a free coffee, and why?"),
    ("deductive", "causal", None,
     "Rain makes the roads wet and also makes more people book a Grab.",
     "If tomorrow is dry and sunny, what should happen to both, and why?"),
    ("deductive", "causal", None,
     "Caffeine keeps you awake for about 6 hours after you drink it.",
     "You drink a big coffee at 9 pm, so what should happen at midnight, and why?"),
    ("deductive", "relational", None,
     "The more people share a pizza, the fewer slices each person gets.",
     "A pizza has 12 slices and 6 friends share it equally, so what follows for each friend?"),
    ("deductive", "relational", None,
     "The earlier you book a flight, the cheaper the ticket usually is.",
     "Sara books 1 day before the trip and Ken books 2 months before, so who should pay less, and why?"),

    ("abductive", "factual", None,
     "A quiet cafe near campus was packed last Tuesday, but on every other Tuesday it is almost empty.",
     "What is the best explanation, and what would you check?"),
    ("abductive", "factual", None,
     "A new online shop has 200 reviews, all with 5 stars, and all written in the same week.",
     "What is the most likely explanation for these reviews?"),
    ("abductive", "conceptual", None,
     "A post says organic food is always healthy, and shows an organic chocolate cake as proof.",
     "What has the post most likely misunderstood about what organic means?"),
    ("abductive", "conceptual", None,
     "Someone says the cheetah must be the strongest animal because it is the fastest.",
     "What has this person most likely mixed up?"),
    ("abductive", "procedural", None,
     "You and a friend baked the same cake recipe, and yours came out flat while theirs rose well.",
     "What difference in how you baked could best explain this?"),
    ("abductive", "procedural", None,
     "Two classes took the same quiz, and one class scored much higher than the other.",
     "What might have been different in how each class took the quiz?"),
    ("abductive", "causal", None,
     "Everyone in one hostel block got a stomach ache on the same night, but nobody in the other blocks did.",
     "What is the most likely cause, and why?"),
    ("abductive", "causal", None,
     "Your phone suddenly loses battery twice as fast as it did last week.",
     "What is the best explanation, and what would you check?"),
    ("abductive", "relational", None,
     "Your football team has won every match this season when it wore its blue kit.",
     "What could best explain this link?"),
    ("abductive", "relational", None,
     "Ice cream sales and the number of drownings rise and fall together every year.",
     "What connection could best explain this?"),
]


def _items(bank, prefix=""):
    out = {}
    for r, k, case, situation, question in bank:
        n = sum(1 for i in out.values() if i["reasoning"] == r and i["knowledge"] == k) + 1
        id_ = f"{prefix}{r[:3]}-{k[:4]}-{n}"
        out[id_] = {"id": id_, "reasoning": r, "knowledge": k, "case": case,
                    "situation": situation, "question": question}
    return out


ITEMS = _items(_EVERYDAY, "e-")  # the default skill check
QUANT_ITEMS = _items(_BANK)  # the quant questions used until 23 November 2026, kept so old checks still read
ALL_ITEMS = {**QUANT_ITEMS, **ITEMS}


def pick(seen=(), n=QUESTIONS_PER_CHECK, rng=random, items=None):
    """n questions, the same number per reasoning type, each with a different
    knowledge type where possible. Questions not answered before come first.
    items: a generated topic's bank (Goal 2), else the everyday bank."""
    seen = set(seen)
    items = items or ITEMS
    per_type = n // len(REASONING_TYPES)
    chosen = []
    for r in REASONING_TYPES:
        pool = [i for i in items.values() if i["reasoning"] == r]
        rng.shuffle(pool)
        pool.sort(key=lambda i: i["id"] in seen)  # stable, so unseen ones first, still shuffled
        kinds = set()
        for i in pool:
            if len([c for c in chosen if c["reasoning"] == r]) == per_type:
                break
            if i["knowledge"] not in kinds:
                chosen.append(i)
                kinds.add(i["knowledge"])
    rng.shuffle(chosen)
    return [i["id"] for i in chosen]


def new_check(seen=(), cases=None, bank=None):
    """Saved in the same table as the cases, marked by its mode. For a
    generated topic (Goal 2), its cases and question bank are kept inside the
    check, like a generated case is kept inside a session."""
    items = pick(seen, items=bank)
    check = {"mode": "skill_check", "concept_id": None, "items": items, "round": 0,
             "total_rounds": len(items), "ended": False, "history": [], "turns": []}
    if bank:
        check.update(topic=cases[0]["topic"], bank=bank, cases={c["id"]: c for c in cases})
    return check


def _item(check):
    return (check.get("bank") or ALL_ITEMS)[check["items"][check["round"]]]


def _case(check, item):
    """The case behind a question, or None for an everyday question."""
    if not item["case"]:
        return None
    return (check.get("cases") or {}).get(item["case"]) or CONCEPTS[item["case"]]


def current(check):
    """The question to show now, or None when the check is finished."""
    if check["ended"]:
        return None
    i = _item(check)
    return {"id": i["id"], "number": check["round"] + 1, "total": check["total_rounds"],
            "case": (_case(check, i) or {}).get("title"), "situation": i["situation"], "question": i["question"]}


def answer(check, text, seconds=None):
    """Mark one answer (one model call) and move to the next question.
    Rules first: an answer copied from the notes, or one that looks like an AI
    chatbot wrote it, scores 0 with no model call."""
    item = _item(check)
    asked = f'{item["situation"]} {item["question"]}'
    case = _case(check, item)
    # An everyday question has no case, so the Assessor judges it from the question alone
    as_session = {"concept_id": item["case"], "case": case, "last_tutor": asked} if case else {"last_tutor": asked}
    ai_reason = copycheck.ai_reason(text)
    if ai_reason:
        a = copycheck.ai_assessment(ai_reason)
    elif case and copycheck.is_copied(text, copycheck.session_sources(as_session), item["situation"]):
        a = copycheck.copied_assessment()
    else:
        a = llm_client.call_assessor(as_session, text)
    rs = a.get("reasoning") or {}
    attained = int(bool(rs.get("types", {}).get(item["reasoning"]) and rs.get("knowledge", {}).get(item["knowledge"])))
    turn = {"item": item["id"], "reasoning": item["reasoning"], "knowledge": item["knowledge"],
            "answer": text, "assessment": a, "assessor_version": prompts.ASSESSOR_VERSION, "attained": attained,
            "ai_like": ai_reason, "seconds": seconds}  # seconds from showing the question to sending, for the research
    check["turns"].append(turn)
    check["history"].append({"assessment": a, "item": item["id"]})
    check["round"] += 1
    check["ended"] = check["round"] >= check["total_rounds"]
    return turn


def summarize(turns):
    """grid[knowledge][reasoning] = {"asked", "attained"} over all answered
    questions, plus totals per reasoning type and per knowledge type and up to 2
    plain messages. Unlike the case grid, this one knows what was asked."""
    grid = {k: {r: {"asked": 0, "attained": 0} for r in REASONING_TYPES} for k in CORE_KNOWLEDGE}
    for t in turns:
        cell = grid[t["knowledge"]][t["reasoning"]]
        cell["asked"] += 1
        cell["attained"] += t["attained"]

    def total(cells):
        return {"asked": sum(c["asked"] for c in cells), "attained": sum(c["attained"] for c in cells)}

    by_type = {r: total([grid[k][r] for k in CORE_KNOWLEDGE]) for r in REASONING_TYPES}
    by_kind = {k: total(grid[k].values()) for k in CORE_KNOWLEDGE}
    flagged = sum(1 for t in turns if t.get("ai_like"))
    note = ([f"{flagged} of your answers looked like {'they' if flagged > 1 else 'it'} came from an AI chatbot, "
             f"so {'they' if flagged > 1 else 'it'} scored 0. Answer in your own words."] if flagged else [])
    return {"answers": len(turns), "grid": grid, "reasoning": by_type, "knowledge": by_kind,
            "messages": note + _messages(by_type, grid), "ai_like": flagged,
            "reasoning_types": REASONING_TYPES,
            "knowledge_types": {k: KNOWLEDGE_TYPES[k] for k in CORE_KNOWLEDGE}}


def _messages(by_type, grid):
    asked = [(r, v) for r, v in by_type.items() if v["asked"]]
    if not asked:
        return []
    share = lambda v: v["attained"] / v["asked"]  # noqa: E731
    best = max(asked, key=lambda x: share(x[1]))
    out = []
    if best[1]["attained"]:
        out.append(f"Your strongest reasoning so far is {best[0]}, shown in {best[1]['attained']} of {best[1]['asked']} questions.")
    # The weakest pair that was asked at least once, so the learner knows what to practise.
    cells = [(c["attained"] / c["asked"], k, r) for k in CORE_KNOWLEDGE for r, c in grid[k].items() if c["asked"]]
    low = min(cells)
    if low[0] < 0.5:
        out.append(f"You have not shown {low[2]} reasoning on {low[1]} knowledge yet.")  # "mastered" needs the stats of step 5
    return out
