# Marking guide: the 9 standards, the 6 levels, and the reasoning and knowledge types

This guide is for the **human markers** who check the Socratic AI Assessor. You do not need to be an expert in critical thinking. You only need to apply the rules below the same way every time.

**Status: DRAFT (8 October 2026), to be checked by Dr Ho before marking starts.** The rules are based on Paul and Elder's 9 intellectual standards, as they are defined in the app (`app/content.py`). Where a definition was vague, this guide makes it sharper, and the Assessor's prompt will later be updated to match.

## How to mark

1. Open `eval/marks_template.csv` in Excel and save a copy as `eval/marks_<your name>.csv`.
2. For each row, read the **question first**, then the **answer**.
3. For each of the 9 standards, write **1** if the answer clearly shows it, or **0** if it does not.
4. In the `level` column, write the one move the answer mainly makes (see the end of this guide).
5. In the 3 reasoning columns (`inductive`, `deductive`, `abductive`) and the 8 knowledge columns (`k_factual` to `k_epistemic`), write **1** if the answer clearly uses it, or **0** if not. More than one can be 1, and all can be 0. See "The reasoning types" and "The knowledge types" below. (Added 23 October 2026 for Goal 1 and Goal 3.)
6. If you are unsure, write **0** and add a short note in the `note` column. Notes are useful, because they show where the rules are unclear.

Rules that apply to every standard:

- **Judge only what is written.** Do not guess what the learner meant.
- **Do not reward length or keywords.** A long answer is not better by being long, and an answer is not deep just because it contains "because" or "but".
- **Spelling and grammar do not matter.** "very low chace only 3%" is fine.
- **For an A/B question,** the answer is the pick plus the "Why". Judge them together.
- **"I'm stuck" or "idk"** scores 0 on every standard, and the level is `none`.
- **Mark on your own.** Do not look at the other marker's file or at `eval/old_ai_marks.csv` until you have finished.

## The 9 standards

Each standard has one yes/no question. Mark 1 only if the answer is clearly "yes".

### 1. Clarity
**Can you tell, on the first read, what the learner thinks?**
- Yes: "He means the price will keep going up because it went up before."
- No: "Because 3% but maybe, so therefore however 500 stocks." (the words do not form a clear point)
- A very short answer can still be clear, for example "low chance".

### 2. Accuracy
**Does the answer state at least one fact or claim, and is everything it states true and in line with the case notes?**
- Yes: "5 ups in a row is about a 3% chance."
- No: "It is 50%, because each day is 50% so five days is also 50%." (wrong)
- No: an answer that makes no factual claim at all, such as "i think so".
- Use the case notes at the end of this guide to check facts.

### 3. Precision
**Does the answer give a specific detail: a number, a count, or a concrete example?**
- Yes: "for example the next 20 days", "about 19 of 100 pairs", "like the company selling umbrellas".
- No: vague words only, such as "low chance", "a lot", "it depends".

### 4. Relevance
**Does the answer respond to the exact question that was asked?**
- Yes: the question asks what the friend is assuming, and the answer names an assumption.
- No: the question asks what 3% means, and the answer talks about crypto and an uncle's shares.

### 5. Depth
**Does the answer give a real reason or explain how something works, beyond repeating the claim?**
- Yes: "stock prices do not remember yesterday, so that assumption may be wrong."
- No: "because it just is", "because in a row", "because overfitting" (a word, not a reason).

### 6. Breadth
**Does the answer consider more than one possibility, cause or angle?**
- Yes: "it might go up... but it also might go down since the price is too high now."
- Yes: "Maybe a hidden third thing, like the season."
- No: only one side is considered.

### 7. Logic
**Does the conclusion actually follow from the reasons given, with no jump or contradiction?**
- Yes: "one will fit the old prices by luck, but that luck does not repeat, so on new data it drops."
- No: "Yes, because they moved together for a whole year." (moving together does not prove cause)
- No: there is no reason at all, so there is nothing for a conclusion to follow from.

### 8. Significance
**Does the answer focus on the point that matters most for this question, rather than a side detail?**
- For these cases the main points are usually: luck versus a real pattern, testing on new data, and whether there is a real reason.
- Yes: "I would check whether the same stock keeps rising on new days."
- No: "he wont lie to me" (trust in the friend is a side issue).

### 9. Fairness
**Does the answer honestly admit it could be wrong, name a limit of its own claim, or state an opposing view fairly?**
- Yes: "I could be wrong if there was real news."
- Yes: "That is a fair point, but with many pairs some will still line up by chance."
- No: giving another possible cause on its own. That is **Breadth**, not Fairness. For example, "there might be real news behind it" alone is Breadth.

Common mix-ups:
- **Breadth or Fairness?** Breadth = more than one possibility. Fairness = honesty about being wrong, or treating the other side fairly. One sentence can show both, but only if it does both.
- **Depth or Logic?** Depth = there is a real reason. Logic = the conclusion follows from that reason. An answer can have a reason that does not support its conclusion (Depth 1, Logic 0).

## The level (one choice per answer)

Write the **one** move the answer mainly makes:

| Level | The answer mainly... | Example |
|---|---|---|
| `clarify` | explains what a word or idea means | "Due means tails is more likely now." |
| `assumption` | names a hidden belief behind a claim | "He is assuming the streak will continue." |
| `evidence` | says how to check, or what data would prove it | "I would test it on new days." |
| `viewpoint` | looks at how someone else would see it | "A sceptic would say it is luck." |
| `implication` | says what follows if something is true | "Then buying is closer to a coin flip." |
| `question_the_question` | asks whether this is the right question | "The better question is whether it beats the market over months." |
| `none` | none of these, or no real answer | "idk", "i will buy" |

## The reasoning types (1 or 0 each)

**Status: DRAFT (23 October 2026).** These use the same meanings as the Reasoning agent (`app/reasoning.py`), so a human and the agent mark against the same rules.

| Column | Write 1 when the answer... | Example |
|---|---|---|
| `inductive` | goes from several cases or observations to a general idea or pattern | "Most of the 200 rules failed on new data, so rules found this way usually do not last." |
| `deductive` | goes from a rule or known fact to a conclusion for this case | "Each day is like a coin flip, so 5 ups in a row is about a 3% chance." |
| `abductive` | goes from what was seen to the best explanation of why it happened | "They moved together probably because a hidden third thing, like the season, drives both." |

- Mark what the answer **does**, not the words it uses. "I think" does not make an answer abductive.
- A bare claim with no step from one idea to another ("it is luck") is 0 on all three.

## The knowledge types (1 or 0 each)

Write 1 only when the answer **uses** that kind of knowledge, not just names it.

| Column | Write 1 when the answer... |
|---|---|
| `k_factual` | states a specific fact, number or observation ("only 3%", "15 of 500") |
| `k_conceptual` | uses or explains what an idea or term means ("overfitting is learning the noise") |
| `k_procedural` | describes steps or a method to do or check something ("split the data, then test") |
| `k_causal` | says why something happens, that one thing makes another happen |
| `k_relational` | links two or more things, such as how one changes when another changes |
| `k_strategic` | chooses what to do next, given the situation ("I would wait for new data before buying") |
| `k_metacognitive` | reflects on how they know, or on their own thinking ("I assumed too fast") |
| `k_epistemic` | judges how strong the evidence is, or what is justified to believe ("one streak is weak proof") |

**Checking the graph reading (Goal 3, step 5).** The AI also names the steps of each answer as moves between boxes of the map of the ideas, and plain code turns those moves into reasoning types (`graph_inductive` and so on in the AI file). Your 3 reasoning columns are the human check for that too, so there is nothing extra to mark. Run `python eval/compare_marks.py eval/marks_<your name>.csv eval/ai_marks_<version>.csv --graph` to compare.

## Case notes (for checking Accuracy)

**Pattern or luck?** A stock went up 5 days in a row.
- Each day, a stock going up or down is a bit like a coin flip.
- Going up 5 days in a row happens about 3% of the time (older questions call this 1/32).
- Out of 500 stocks, about 15 will do it just by luck.
- One streak is not proof, but a streak that repeats on new days is.

**Will it work again?** Someone tried 200 buying rules on old prices.
- If you try 200 rules, at least 1 will look great just by luck.
- The fix is to split the data: find the rule with the first part, test it on the second.
- Overfitting means a rule learned past noise instead of a real pattern.
- In the app's simulation, the best of 200 random rules made +32% on old data but only +8% on new data.

**Moving together, but why?** A stock's price and the rain moved together for 1 year.
- Moving together is called correlation, and it does not prove one causes the other.
- About 19 out of 100 random pairs move together strongly, just by luck.
- A hidden 3rd thing can cause both.
- Ask two questions: is there a real reason, and does it repeat on new data?

## Practice round first

Before marking everything, the two markers each mark the **first 10 rows**, compare, and talk through every disagreement. If a rule caused the disagreement, fix the rule in this guide, then mark the rest. Write down what changed, because the thesis should report it.
