# Which way of building the graph works best (28 November 2026)

A test of the methods from the knowledge graph review (`docs/thesis/drafts/kg-generation-review.md`) on one machine. Code `eval/graph_build_test.py`, run with `python -m eval.graph_build_test` (about 6 minutes, plain Python, no model tokens).

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

## Real data, MetroPT-3 (28 November 2026)

Code `eval/metropt_test.py` (the 208 MB CSV stays outside the repo; download it from https://doi.org/10.24432/C5VW3R and pass its path). Real readings from the compressor of a Porto metro train, February to August 2020, about one every 10 seconds (Davari et al., 2021, UCI, CC BY 4.0). The only labels are the operator's 4 failure reports, all air leaks. So this test asks "is this hour a leak?", not "which fault is it?". 4,278 logged hours, 86 of them inside a leak.

Each network is trained with one leak left out, then tested on that leak and the 3 days either side. Rank is the chance a leak hour scores above a normal hour (50% is a coin toss). Caught means an alarm inside the leak, at a limit that allows about 1 false alarm a day.

| Build | Rank | Leaks caught |
|---|---|---|
| Rule from the sensor notes (a leak makes the compressor load more), no training | 90% | 4 of 4 |
| AI rule, as drafted by Gemini | 13% | 0 of 4 |
| AI rule, after a person says what 0 and 1 mean | 92% | 2 of 4 |
| Network, raw readings, bands at the data's thirds | 94% | 4 of 4 |
| Network, engineer readings, bands at the data's thirds | 85% | 0 of 4 |
| Network, raw readings, bands like alarm limits from the normal first month | 95% | 3 of 4 |
| Network, engineer readings, alarm limit bands | 90% | 3 of 4 |
| Mix (engineer network, the rule may rule a leak out) | 90% | 3 of 4 |

What a leak looks like here. The compressor works almost all the time. It is under load 67% of the hour against 12% normally, and it starts about 64 times an hour against 5.

What it means.

1. **A simple rule from how the machine works caught every leak with no failure data at all.** That matters on a real plant, where failures are rare and records are few.
2. **Choosing engineer nodes did not help here, unlike AI4I.** A leak is a large fault that moves many sensors at once, so even the raw averages show it. Engineer nodes matter most when the cause hides in a combination of readings, as overstrain does in AI4I.
3. **How readings are cut into bands matters.** Cutting at the data's thirds hid the leak inside the top third (0 of 4 caught for the engineer network). Bands set like alarm limits from normal running fixed it (3 of 4).
4. **An AI model reasoned well but misread the data.** Gemini rightly said the low pressure signals should change in a leak, but the dataset page never says what 0 and 1 mean, and in this data the signal reads 0 when "active". Its rule scored 13%, worse than a coin toss, until a person fixed the meaning (92%). So an AI draft needs a person to check what the data means, not only the logic.
5. **The mix did not beat the best single build here.** On AI4I it won every test. With one kind of fault and only 4 cases, there was little for it to add.

The AI rules are scored by where each picked reading ranks among all hours (no leak labels used), averaged over the picks, so a reading that hardly moves in normal running cannot swamp the others.

Limits. Only 4 leaks, all of one kind, so a difference of one leak caught is not meaningful. The page's failure table has a few odd details (two rows numbered 1, and report dates that do not match the table dates), and we used the table's start and end times as printed.

## A real manual (28 November 2026)

Code `eval/manual_test.py`. The AI read the troubleshooting tables of two real rotary screw compressor manuals, the Champion D5 manual (D5-MANS, March 2019, Troubleshooting Guide pages 30 to 32) and the SSR UP6 40 / 50PE / 50PEI operation manual, as `pdftotext` gives them (table columns run into each other, as in a real scan). It also read the MetroPT-3 sensor notes, this time with what 0 and 1 mean, so only the manual differs between the two kinds of run. It picked which hourly readings move in an air leak and had to quote the manual for each pick. The manuals are copyrighted, so their text is not in the repo. 5 runs with the manual and 5 without, on Gemini (gemini-3.5-flash-lite, free tier).

| Runs | Rule picked | Rank | Leaks caught | Quotes found in the manual |
|---|---|---|---|---|
| With manual, run 1 | load share up, starts up, compressor pressure down, reservoir pressure down | 88% | 4 of 4 | 4 of 4 |
| With manual, run 2 | load share up, starts up | 93% | 4 of 4 | 2 of 2 |
| With manual, runs 3 to 5 | load share up, starts up, lowest compressor pressure down | 75% | 0 of 4 | 9 of 9 |
| Without manual, 5 runs | panel or compressor pressure down, reservoir down, motor current up, starts up | 90% to 94% | 4 of 4 every run | |

Averages, 81% with the manual and 92% without.

What it means.

1. **The AI never made up the manual.** All 15 quotes were really in the manual (the check allows words split across lines by the table layout, and a made-up phrase fails it).
2. **A real quote is not a right rule.** The manual lists "Air system leaks" as a cause of "Low system air pressure". In 3 of 5 runs the AI turned that into "the lowest compressor pressure falls". On this train the opposite happens. The compressor hardly rests during a leak, so its pressure stays up. The quote was real, but the sensor it was mapped to was wrong, and those rules caught no leak.
3. **The manual did not help here.** Without it the AI did better and gave nearly the same rule every time. With it, the AI anchored on the manual's symptom words. A manual is written for a person who sees symptoms ("low pressure", "noise"), not for sensors, so the hard step is linking the manual's words to the right sensor.
4. **So check AI rules against data, not only against the text.** The quote check proves the source is real. Only the data showed the mapping was wrong.

Limits. The manuals are for factory screw compressors, not this train's air production unit, so they fit only roughly. Only 4 leaks of one kind.

## A data guard for AI-drafted rules (28 November 2026)

Code `eval/rule_guard.py` (`python -m eval.rule_guard`, no model calls). Before a rule the AI drafted is used, it is checked against past records. Three questions.

1. **Caught.** Of the past runs with this fault, how many does the rule fire on? The app lets a rule rule a fault out, so it must almost never miss. At 95% or more it may **rule out**.
2. **False alarms.** Of the runs without this fault, how many does it fire on? Under 2% and with no loose limit, it may also **name** the fault on its own.
3. **Loose limits.** For each product type, does each limit sit close to where the faults really start in the data? More than 5% looser is reported.

A rule that catches under 95% is **flagged** for a person to fix. The limits were set so the published rules pass (they are the right answer here), not tuned on the AI drafts. The guard judges on the 7,000 training runs, since the 3,000 test runs alone have too few faults of each type.

| Rule | Published | AI drafts 1, 3, 4, 5 | AI draft 2 |
|---|---|---|---|
| Tool wear | rule out (97%, 7.6% false alarms) | flag (93%) | flag (93%) |
| Heat | name | name | name |
| Power | name | name | name |
| Overstrain | name | name | rule out, "for type M the limit 11,000 is loose, since its faults start at 12,337" |

So the guard finds the hidden mistake in draft 2 that a person reading the rule could miss, and says what the data suggests instead. It also flags every AI tool wear rule. The AI copied "200 to 240 minutes" from the text as an upper limit too, but in the data some tools fail after 240 minutes, so that rule would wrongly rule tool wear out for 2 of 29 runs. The published rule has no upper limit.

Limits. False alarms alone could not see draft 2's mistake (0.2% overall, under 1% for type M), so the loose limit check is what catches it. On real records the limits will be fuzzier, and a fault seen fewer than 10 times cannot be judged at all. The guard is not in the app yet, because the app's rules are the published ones; it is ready for the partner's records, where AI-drafted rules would be used.
