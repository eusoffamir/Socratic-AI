# Goal 1: what is built (for Dr Ho)

Written by Claude on 21 October 2026 for Eusoff to share with Dr Ho. Everything below is live on https://socratic-ai-qlk6.onrender.com. All question text and knowledge tags are DRAFTS for Dr Ho to check.

## 1. What the learner sees

- **Skill check** on Home ("What kind of thinker are you?"). It asks 6 short set questions, and each one targets one reasoning type on one knowledge type. At the end the learner sees a grid of "attained out of asked" and a **Mastery so far** chart.
- **Mastery so far**: for each of 8 skills (inductive, deductive, abductive, and factual, conceptual, procedural, causal, relational knowledge), it shows a bar for the likely range of the learner's true score, a verdict (mastered, not mastered yet, not sure yet, not enough answers) and a message such as "You have mastered 2 of 8 skills, so 6 are left."
- **Reasoning × Knowledge grid** in the Status panel of every Socratic case, the end profile and the overall status. It counts which reasoning type the learner used on which knowledge type in their free answers, with the average Paul-Elder standards met per reasoning type.
- **Why this matters** pop-up. Clicking any grid cell opens the Explainer agent, which gives why it matters, a short quant example, 2 or 3 steps and a practice question. The learner can pick 1 or 2 knowledge types to see how they combine.

## 2. The agents

| Agent | Job | Model calls |
|---|---|---|
| Assessor (existing) | 9 Paul-Elder standards, 1 or 0 with evidence | 1 per answer |
| **Reasoning agent** (new, `app/reasoning.py`) | inductive, deductive or abductive, plus which of 8 knowledge types were used, 1 or 0 with evidence | 0 extra, because it shares the Assessor's call |
| **Explainer agent** (new, `app/explainer.py`) | "why this matters" with a scenario | 1 per new pair, then cached |
| Planner, Tutor, Checker, Coach (existing) | the Socratic dialogue | unchanged |

The knowledge of each case is now a small **knowledge graph** (`app/knowledge.py`). Each node is one piece of knowledge tagged with its type, and the edges are "causes", "then" (procedural steps), "defines", "supports", "weakens", "tests" and "leads to". The Reasoning agent and the Explainer both read these tags.

## 3. Trials and statistics

**Trials.** The question bank (`app/skillcheck.py`) has 30 questions, 2 for each pair of reasoning type (3) and core knowledge type (5). An answer is **attained = 1** only when the Reasoning agent marks both the target reasoning type and the target knowledge type. Each skill check costs 6 model calls.

**Per learner (in the app): a Beta-Binomial mastery estimate, plus Hamming distance.**
- Start from a flat prior and add the learner's 1s and 0s for each skill. This gives the most likely share, a 90% range, and the chance that the true share is at least 60%.
- It works with few trials and is honest about how unsure it is, which factor analysis cannot do for one learner.
- The **Hamming distance** between the learner's pattern of mastered skills and the all-mastered pattern is the "skills left" number. The same distance before the last check shows progress.

**Across the class (offline, `eval/dina.py`): a DINA model instead of plain factor analysis.**
- Our data is 1s and 0s, and every question is already tagged with the 2 skills it needs, so we have a Q-matrix.
- DINA uses that Q-matrix directly. It estimates each question's slip and guess, and each learner's chance of mastering each skill.
- Factor analysis would have to discover the skills from scratch and is built for continuous scores. It can still be run later on tetrachoric correlations, as a check that the 8 skills really separate in the data.
- DINA is usually credited to Junker and Sijtsma (2001). Please check this source before citing it.

**Simulation check (fake learners with known skills, true slip 10% and guess 20%):**

| Fake learners | Questions each | Skill calls right (50% = chance) |
|---|---|---|
| 50 | 18 (3 checks) | 70% |
| 100 | 18 | 74% |
| 200 | 18 | 77% |
| 100 | 30 (all) | 87% |

So more questions per learner matter more than more learners. With about 50 students who each do 3 to 5 checks, the class model should be usable.

## 4. Questions for Dr Ho

1. Are the knowledge type tags in the 3 case graphs right?
2. Do the 30 skill check questions really call for their tagged reasoning type? Each question is tagged with one reasoning type and one knowledge type.
3. Are the mastery thresholds right? A skill counts as mastered at 60% or more, with at least 80% certainty, and only after at least 3 answers. These are placeholders.
4. Is the Bayesian estimate per learner and DINA for the class acceptable in place of factor analysis, with factor analysis kept as a later check?
5. Should the skill check be part of the study? It is switched off in study mode for now.

## 5. Honest limits

- The Reasoning agent has only been checked on a few answers. It still needs a comparison with a human marker, like the Assessor plan in `docs/evaluation/`.
- There is no login, so mastery is per browser. In study mode the participant code would link a student's checks.
- The question bank is small (30). More questions per skill would make the estimates tighter.
