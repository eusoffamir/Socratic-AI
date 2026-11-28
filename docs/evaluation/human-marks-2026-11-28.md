# Human marker check, first results (28 November 2026)

Eusoff marked all 61 test answers (`eval/marks_eusoff.csv`) on the "Assessor Marking Sheet" artifact, with no view of the AI marks. The Assessor (prompt version 2026-10-21, Gemini free tier) was run again on the same day (`eval/ai_marks_2026-10-21_rerun-2026-11-28.csv`, 60 of 61 answers, C22 got no reply). Compared with `python eval/compare_marks.py eval/marks_eusoff.csv <AI file>`.

One human marker only, so this checks the Assessor against one person, not against an agreed standard. A second marker is still needed for human against human agreement.

| Mark | Agree | Kappa | Human 1s | AI 1s |
|---|---|---|---|---|
| clarity | 93% | 0.57 | 54 | 56 |
| accuracy | 83% | 0.66 | 23 | 29 |
| precision | 92% | 0.71 | 12 | 9 |
| relevance | 92% | 0.66 | 50 | 53 |
| depth | 92% | 0.81 | 21 | 20 |
| breadth | 83% | 0.28 | 8 | 8 |
| logic | 82% | 0.61 | 20 | 25 |
| significance | 82% | 0.60 | 20 | 23 |
| fairness | 90% | 0.65 | 13 | 7 |
| level (main move) | 65% | 0.48 | | |
| inductive | 92% | -0.03 | 4 | 1 |
| deductive | 82% | 0.25 | 10 | 7 |
| abductive | 75% | 0.33 | 11 | 18 |
| k_factual | 100% | 1.00 | 7 | 7 |
| k_conceptual | 87% | 0.43 | 10 | 6 |
| k_procedural | 98% | 0.92 | 8 | 7 |
| k_causal | 83% | 0.58 | 14 | 18 |
| k_relational | 85% | 0.23 | 5 | 8 |
| k_strategic | 90% | 0.53 | 4 | 10 |
| k_metacognitive | 100% | n/a | 0 | 0 |
| k_epistemic | 65% | 0.29 | 29 | 12 |

Graph reading (Goal 3 step 5, `--graph`). Only 11 of 60 answers had a step that landed on a real link of the case graph, so only those are scored. On them, abductive agrees (91%, kappa 0.62) but deductive does not (27%, the code reads 10 forward walks where the human saw 4).

What it means.

1. **The 9 standards mostly hold.** 7 of 9 have kappa 0.57 or more. Breadth (0.28) is the weak one. The AI is stricter than the human on fairness (7 against 13).
2. **The reasoning types are the weak spot.** Inductive is no better than chance (the AI almost never marks it), and the AI marks abductive too often (18 against 11). This is the main thing to fix in the Reasoning agent prompt.
3. **Epistemic is under-marked.** The human saw it in 29 answers and the AI in 12, so the rule for "judges how strong the evidence is" needs sharper wording in the prompt or in the guide.
4. **The graph reading rarely applies.** Most answers' steps do not land on a real link, and a forward walk is not the same as deductive reasoning as a person reads it.
5. **The run is stable.** Against the first run of the same prompt (21 October), the numbers moved only a little (for example level 62% then 65%).
