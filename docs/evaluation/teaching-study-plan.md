# Teaching study plan (backup paper, January 2027)

Draft 1, 27 November 2026, by Claude for Eusoff, to be agreed with Dr Ho. Based on Meeting 3 (`docs/supervisor/meetings/meeting3-notes.md`, section 2.2) and Dr Ho's grant proposal (history file, "Dr Ho's proposal vs the free tier").

## The question

Does one hour of practice with our tool improve students' reasoning (inductive, deductive and abductive) more than one hour of reading the same material?

## Design

A pretest and posttest study with a control group, which is what Dr Ho described.

1. **Pretest.** Every student takes the same short reasoning test.
2. **Split into two groups.** Sort students by pretest score, then pair them off and toss a coin within each pair (matched random assignment). This balances the groups' starting levels, as Dr Ho asked.
3. **One hour of learning on the same material.**
   - Control group reads the material (the same notes the tool uses).
   - Tool group works through the material with the tutor, in study mode.
4. **Posttest.** Both groups take a parallel form of the test right after.
5. **Optional delayed test** one week later, to see if the gain lasts.

Both groups get the same time and the same content, so the only difference is how they learn.

## Which cohort

Dr Ho listed four. The choice depends on the topic and on how many students we can get.

| Cohort | Likely size | Topic fit | Notes |
|---|---|---|---|
| Foundation students (January 2027) | Large | Foundation physics or a general topic | Big enough for the main study. Their lecturer must agree. |
| Foundation physics class | Medium to large | Physics material | Clear material to load, and the tool already builds a topic from a file. |
| Students going for internship | Small to medium | Workplace problem solving, close to diagnosis | Good fit with the industrial use case, but harder to gather at one time. |
| Dr Ho's master students, Intro to AI | Small | Dr Ho's own slides | Easiest to arrange, best as the pilot. |

**Suggestion.** Pilot with Dr Ho's master students (5 to 10), then run the main study with a foundation cohort. Eusoff and Dr Ho decide.

## How many students

These are standard power figures (Cohen, 1988), for a 5 percent significance level and an 80 percent chance of finding a real effect.

| Size of the real effect | Students per group | With the pretest used as a covariate (correlation about 0.5) |
|---|---|---|
| Medium (d = 0.5) | 64 | about 48 |
| Large (d = 0.8) | 26 | about 20 |

So a class of 40 can only show a large effect. The main study needs about 100 students in all to show a medium one. If we get fewer, we report the effect size and its confidence interval honestly, and call it a pilot.

## What we measure

1. **Main measure, the reasoning test (pre and post).** It must not favour the tool group, so both groups take it the same way, outside the tutor. Two options.
   - Use our skill check question bank (A or B choice with a reason, each question tagged inductive, deductive or abductive). It is ours, so it is free, but it needs a check that the questions are sound. The everyday skill check in the app is only 3 questions (one per reasoning type, since 27 November 2026), so the study test uses two longer forms from the same bank, 15 questions each (`docs/evaluation/study-test-forms.md`, made by `eval/study_forms.py`).
   - Use a published critical thinking test. Most known ones are paid or licensed, so check the cost and the licence first.
   Two parallel forms (A and B) are needed, and half the students get A first, half get B first.
2. **During the session, tool group only.** The Assessor's marks on the 9 standards and the reasoning types, the highest level reached, and the time spent. These describe how students used the tool but are not compared between groups.
3. **Short survey after.** How useful and how hard it was, for both groups.

## Analysis

- Main test. Posttest score by group, with the pretest score as a covariate (ANCOVA). Report the effect size.
- By reasoning type. The same for inductive, deductive and abductive scores, to see which one the tool helps most.
- Marker check. The Assessor's marks are only trusted once they agree with a human marker (Cohen's kappa), which is the human marker task in `docs/evaluation/assessor-evaluation-plan.md`.

## Ethics and data

- **Ethics approval is needed before any student is tested.** We do not know UTP's process yet, so ask Dr Ho now, because it takes time. Dr Ho's proposal named UPSI for the grant's ethics approval, so check whether that covers us.
- **Consent.** A draft information sheet and consent form are in `docs/evaluation/study-consent-draft.md`. Study mode is already built. It shows a consent screen and only accepts participant codes the lecturer hands out, so no names are stored (`STUDY_CODES`, history file "Study mode"). The consent text is marked DRAFT until the ethics wording is given.
- **Model access.** The free Gemini tier cannot serve a whole class at once. The Azure tokens from UTP would solve this, and a paid service also avoids the data being used for training, which matters for ethics.
- **AI_GUARD must be 1** during the study, so students cannot paste AI answers.

## Risks

| Risk | What we do |
|---|---|
| The tool group enjoys something new (novelty effect) | Use the delayed test, and keep the session the same length for both groups. |
| Students share between groups | Run both groups at the same time in separate rooms. |
| The test favours the tool | Both groups take it outside the tutor, in the same way. |
| Too few students | Report it as a pilot with effect sizes. |
| The server is slow with a full class | Test with 10 people first, on Azure. |

## Timeline

| When | What |
|---|---|
| Early December 2026 | Agree the cohort and topic with Dr Ho. Ask about ethics. |
| December 2026 (after exams) | Write the test (two forms), load the material into the tool, submit for ethics. |
| Early January 2027 | Pilot with 5 to 10 students. Fix problems. |
| Mid to late January 2027 | Main study. |
| February 2027 | Analysis and the paper draft. |

## To decide with Dr Ho

1. Which cohort, and which topic or material.
2. Our skill check or a published test for the pre and post measure.
3. The ethics route at UTP, or whether the grant's approval covers this.
4. Whether the Azure access will be ready by early January.
