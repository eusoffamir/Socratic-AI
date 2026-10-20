# Plan: checking and improving the Assessor

Written 8 October 2026. The Assessor is the part the rest of the app depends on: the level moves, My stats, the comments and the tutorial score all come from its marks. It is also what the SoTL project measures (target: Cohen's kappa of 0.8 or more against human raters). So this plan answers two questions: **is it a good marker, and how do we make it better?**

## What we know so far

From the 46 answers marked by Gemini in `transcripts/` (8 October 2026):
- Most answers are short (the middle one is 9 words), and many were early tests.
- Some standards were almost never given: Fairness 0 of 46, Breadth 1, Precision 2. Clarity was given 44 times and Relevance 40.
- The Assessor is asked to judge Accuracy "against the notes" but is **not sent the case notes**, only the question and the answer (`prompts.assessor_user`). This is a known gap to fix.
- In the tutorial, the Assessor gave Fairness 0 to an answer that only offered another cause. That is a fair call under a strict reading, and it shows why a written marking guide is needed.

## What "good" means

1. **Agrees with careful human markers** (the main test): percent agreement and Cohen's kappa, per standard.
2. **Consistent:** the same answer gets the same marks when run 3 times.
3. **Not fooled:** trick answers (keyword stuffing, long off-topic text, confident but wrong) get low marks.
4. **Explains itself:** its evidence quote points to the part of the answer that earned the mark.

## Files

| File | What it is |
|---|---|
| `docs/evaluation/assessor-marking-guide.md` | Yes/no rules and examples for each standard and level. For the human markers. |
| `eval/test_set.csv` | 61 answers: 37 real (from transcripts, 11 repeats of the "I'm stuck" button removed) and 24 constructed on purpose. Each row is `tune` (may be used as prompt examples) or `test` (never shown to the prompt). The `purpose` column says why a constructed answer was written. |
| `eval/marks_template.csv` | The same 61 answers in a mixed order, with empty columns to mark. Each marker saves a copy as `marks_<name>.csv`. |
| `eval/old_ai_marks.csv` | The marks Gemini gave the real answers at the time (prompt v1). Markers must not look at it until they finish. |

The constructed answers were written by Claude to cover every standard with clear passes and fails. The thesis should say so honestly.

## Steps, one at a time

1. **Check the marking guide** with Dr Ho, ideally before anyone marks.
2. **Practice round:** two markers (the student and Dr Ho or someone he names; a coursemate as a second marker if possible) each mark the first 10 rows, compare, and fix unclear rules.
3. **Mark all 61 rows** separately. Work out human to human agreement first. A standard the humans cannot agree on is unclear, and the Assessor should not be judged harshly on it.
4. **Run the Assessor (v1, the current prompt)** on all 61 rows, 3 times each, with a small script (`eval/run_assessor.py`, not written yet). About 180 free-tier Gemini calls, spread over a few days if needed. Compare with the human marks: agreement, kappa, and whether it is too strict or too generous on each standard.
5. **Improve the prompt (v2),** one change at a time, checking on the `tune` rows only:
   - send the case notes, so Accuracy can be judged;
   - put the marking guide's yes/no rules into the prompt;
   - ask for a quote for each standard before the mark;
   - lower the randomness (temperature 0), and try more thinking time for the Assessor only;
   - add 3 or 4 marked examples from the `tune` rows;
   - save a prompt version number in every transcript line.
6. **Final check on the `test` rows** with v1 and v2. These rows were never used to tune the prompt, so the result is fair.
7. **Write it up** for the Results chapter: v1 versus v2, per standard, with the human to human agreement next to it.

## Things to be honest about in the thesis

- The sample is small (61 answers, mostly from one topic and one person's test sessions), so kappa will have wide uncertainty.
- A standard with very few passes makes kappa unstable. The constructed answers are there to reduce this.
- Kappa targets: the SoTL project aims for 0.8. Common reading guides (for example Landis and Koch, 1977) describe 0.61 to 0.80 as "substantial". **[VERIFY before citing]**
- The human markers are trained with this guide, not experts in critical thinking. The practice round with the supervisor is what makes their marks trustworthy.
