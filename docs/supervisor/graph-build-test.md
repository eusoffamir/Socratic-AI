# Which way of building the graph works best (28 November 2026)

A test of the methods from the knowledge graph review (`docs/thesis/kg-generation-review.md`) on one machine. Code `eval/graph_build_test.py`, run with `python -m eval.graph_build_test` (about 6 minutes, plain Python, no model tokens).

## Set up

The AI4I 2020 milling machine data (UCI, CC BY 4.0, https://doi.org/10.24432/C5HS5C). We learn on 7,000 runs and test on the 114 failed machines in the other 3,000. A build is right when the fault it names really happened.

| Build | How the knowledge was made | Review family |
|---|---|---|
| rules_draft | The published rules, in the order Claude first drafted (tool wear first) | 2.1, 2.12 |
| rules | The same rules, in the order that does best on the training runs | 2.1, 2.12, order from data |
| nb | Naive Bayes on raw readings, no graph | baseline |
| net_raw | Network learned from data, nodes are the raw readings | 2.11 |
| net_eng | Network learned from data, nodes are the readings an engineer would compute (temperature gap, power, strain) | 2.11 |
| net_blind | The engineer nodes, but bands cut at the data's own thirds, so no number from the book | 2.11, data only |
| mix | net_eng ranks the faults, and a rule may only rule a fault out | 2.11 with 2.12 |
| ai_rules | Rules an AI model drafted from the dataset page text alone (it chose its own nodes too), in the order best on the training runs | 2.9 |
| ai_mix | net_eng ranks the faults, the AI-drafted rules may only rule one out | 2.9 with 2.11 |

## Results

| Build | All readings | No torque sensor | Limits 10% too strict | Limits 10% too loose |
|---|---|---|---|---|
| rules_draft | 82% | 45% | | |
| rules | 100% | 48% | 26% | 85% |
| nb | 75% | | | |
| net_raw | 82% | 77% | | |
| net_eng | 100% | 82% | | |
| net_blind | 76% | 69% | | |
| mix | **100%** | **83%** | **97%** | **99%** |

Records needed (all readings).

| Past runs (failures) | 250 (5) | 500 (13) | 1,000 (32) | 2,000 (66) | 4,000 (122) | 7,000 (234) |
|---|---|---|---|---|---|---|
| net_raw | 18% | 34% | 43% | 57% | 82% | 82% |
| net_eng | 75% | 91% | 100% | 100% | 100% | 100% |

Same every run. On 5 different random splits, each network learned the same arrows every time. net_eng found all 6 true cause arrows with no extra, net_raw found 2 of 6 with 4 extra, and net_blind (one split) found 4 of 6 with 2 extra.

## The AI-drafted graph

Code `eval/graph_build_ai.py`. Gemini (gemini-3.5-flash-lite, free tier) read only the facts from the dataset page (`eval/data/ai4i2020_description.txt`) and the six raw column names. It had to define its own new readings, draw the cause arrows and write each rule with its limits. 5 runs, about 1,200 tokens each, saved in `eval/data/ai_graphs.json`, then scored with no more model calls.

| Run | Arrows right | ai_rules, all | ai_rules, no torque | ai_mix, all | ai_mix, no torque |
|---|---|---|---|---|---|
| 1, 3, 4, 5 (the same reply) | 6 of 6, 0 extra | 100% | 47% | 100% | 83% |
| 2 | 5 of 6, 0 extra | 97% | 47% | 100% | 83% |

The model chose the same three new readings an engineer would (temperature gap, power with the right rad/s factor, strain) in every run. Run 2 forgot that the overstrain limit depends on the product type and used 11,000 for all, so its rules lost 3 machines. In the mix the network covered that mistake, so every run reached 100%.

This is the easy case for the model, since the source states every rule in one clear sentence. A real manual or standard is longer and vaguer, so this result is a best case, not proof that AI drafting is safe without a check.

## What it means

1. **Choosing the nodes matters most.** The same learning method goes from 82% to 100%, and needs about 1,000 past runs instead of 4,000 or more, when the nodes are the readings an engineer would compute. Choosing nodes is expert knowledge, not something the data gives.
2. **The order of the rules matters as much as the rules.** The rules were right, but checking tool wear first gave 82%, since many worn tools failed from overstrain. The order learned from the training runs (strain, power, heat, wear) gives 100%. The Knowledge page checklist now uses this order (`app/diagnose.TREE`).
3. **Rules alone break easily.** With one sensor missing they fall to 48%, and with limits 10% too strict to 26%. A real engineer's limits are rarely exact.
4. **Data alone is weaker too.** Without the book's limits to cut the readings (net_blind), the network falls to 76%.
5. **An AI model can draft the graph well from a clear text, but not reliably.** 4 of 5 drafts were perfect and 1 had a hidden mistake, so an AI draft needs a guard (an engineer's check, or the data network as here).
6. **The mix is best or tied on every test.** The network ranks, the rule guards. So the best way to build the graph is not one method. Experts choose the nodes and write the rules, the data sets the chances and the order, and the rules may only rule a fault out.

## Limits

- AI4I is synthetic, and its failures were made by exactly the published rules, so the rules are right by design here. Test 3 imitates fuzzier real rules by moving every limit 10%.
- One machine, one dataset. The same test should be run on real inspection records when the partner shares them.
- The AI model read a short, clear text. Next, give it a real manual or standard.
- Real data with known causes is rare. MetroPT-3 (UCI, CC BY 4.0) is real metro train compressor data with failures from the operator's maintenance reports, so it is the next dataset to try, but it has no published cause rules to check against.
