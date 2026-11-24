# A small Bayesian network on an open dataset (Meeting 3, task 8)

Proof of concept, 25 November 2026. Code `eval/pgm_ai4i.py`, tests `tests/test_pgm_ai4i.py`, reading notes `docs/supervisor/pgm-reading.md`. Plain Python with no new libraries. It runs in about 5 seconds with `python eval/pgm_ai4i.py`.

## Why this dataset

We used the AI4I 2020 Predictive Maintenance Dataset from the UCI repository (CC BY 4.0, so it can be shared with credit, and a copy is in `eval/data/`). It has 10,000 runs of a milling machine. Each run has a product type (L, M or H), air and process temperature, rotation speed, torque and tool wear, and five failure modes (tool wear, heat dissipation, power, overstrain and random failure).

It suits a first test for three reasons.

1. It is about **diagnosing machine faults**, which is close to the Ex inspection use case.
2. It is **synthetic, and the rule behind each failure mode is published**. For example, heat dissipation fails when the gap between process and air temperature is under 8.6 K and the speed is under 1,380 rpm. So we know the true causes and can check whether the network finds them, which is not possible with real data.
3. It is small enough for plain Python.

## What we built

Each step follows a part of Koller and Friedman (2009).

1. **Variables** (Box 3.C, the clarity test). Each reading is cut into two or three named values, for example speed is slow, normal or fast. We made two sets of variables.
   - **Raw.** Only the readings as given.
   - **Engineer.** This adds three things an engineer would compute, the temperature gap, the power (torque times speed) and the strain (tool wear times torque).
2. **Arrows** (Chapter 18). These were learned from 7,000 records with the BIC score and greedy hill climbing, with up to 3 parents per node. One piece of knowledge was given as a rule, that readings come first, so a failure mode may never point back to a reading.
3. **Chances** (Chapter 17). These are counts plus 1 imaginary record per value, so no chance is ever zero.
4. **Tests on 3,000 held-out records** (Box 16.A). We asked which failure mode happened and which machines should be looked at first.
5. **Choosing the next check** (Chapter 23.7). This uses exact inference by variable elimination (Chapter 9) and the value of information.

## Results

### Did it find the true causes?

| Failure mode | True causes | Learned, raw variables | Learned, engineer variables |
|---|---|---|---|
| Tool wear | wear | wear | wear |
| Heat dissipation | gap, speed | air temperature, speed | gap, speed |
| Power | power | torque | power |
| Overstrain | strain, type | torque, wear | strain, type |
| Random | none | none | none |

With the engineer variables, the network found **exactly the true causes of all five failure modes** and no extra ones. With raw readings only, it found the readings closest to the truth but not the real concepts. It picked torque instead of power, and torque and wear instead of strain and type.

### Which failure mode? (114 failed test records)

| Method | Right |
|---|---|
| Always say the most common mode | 29.8 percent |
| Naive Bayes on the raw readings | 75.4 percent |
| Network, raw variables | 81.6 percent |
| Network, engineer variables | 100 percent |

### Which machines first? (real failures among the 114 highest-ranked of 3,000)

| Method | Real failures found |
|---|---|
| Random order | about 4 |
| Network, raw variables | 43 |
| Network, engineer variables | 96 |

### Which check next?

A machine has failed and only its type is known. At that point the network names the right mode only about 34 percent of the time. The value of each check is how much it raises that chance.

| Type | Best check | Second | Third |
|---|---|---|---|
| L | strain, +25 points | gap, +24 | power, +23 |
| M | power, +29 | gap, +26 | speed, +17 |
| H | power, +29 | gap, +27 | speed, +17 |

Strain is the best first check for type L but the worst for type H. This is because the overstrain limit is lowest for L products, so strain tells more about them. The network worked this out from the data.

On five failed test machines, picking the best check each time and stopping at 90 percent confidence named the right mode after one to three checks every time. One machine had two faults (tool wear and overstrain), and the network named one of them, overstrain.

## What this shows

1. **The method works end to end in plain Python.** It covers learning the arrows, learning the chances, exact answers, and choosing the next check. Everything we read in Koller and Friedman runs on a real dataset in a few seconds.
2. **Which things become nodes matters most.** The same data and the same method gave 82 percent with raw readings and 100 percent with the engineer's variables. This is the main point of our knowledge graph review (thesis section 2.8) and of Box 3.C. Engineers' knowledge is most useful in choosing the variables, not only in drawing arrows.
3. **Knowledge as a rule helps learning.** Fixing the time order (readings before failures) stopped the search from drawing arrows from failures back to readings.
4. **Value of information gives a sensible order of checks,** and that order changes with what is already known, here the product type.

## Honest limits

- **The 100 percent is too good to expect on real data.** The engineer variables use the exact published limits (8.6 K, 1,380 rpm, 3,500 W and 9,000 W, and 11,000 to 13,000 min Nm), and the data was generated from those very rules with almost no noise. In real inspections the limits will not be known exactly, findings will be noisy, and some causes will be hidden.
- **The strain bands are not split by product type.** The real overstrain limit depends on the type, so the network had to learn type as a second parent. It did, but finer bands could matter on real data.
- **The data has small inconsistencies with its own description.** 9 records are marked failed with no failure mode, 18 have a failure mode but are not marked failed, and the random failure and tool wear counts differ from the page. We used the five failure mode columns and treated "failed" as any mode being present.
- **Only one split was tested** (seed 7). A fuller study would use cross-validation.
- **Synthetic data has no hidden common causes or selection bias,** which real inspection records will have (section 9 of the reading notes).

## Next steps (for discussion with Dr Ho)

1. Is this the kind of "small probabilistic graph on an open dataset" you had in mind?
2. Try a real (not synthetic) fault dataset with noise and missing values. This would test the prior from the Builder or an engineer (Chapter 17) and the cost of hidden variables.
3. Add utilities (the harm of each failure and the cost of each check) so the next check is chosen by value minus cost, as in the Ex plan.
4. Move the shared parts (variable elimination, learning with a prior) into `app/pgm.py` only when the Ex data arrives, so the app stays small until then.

## References

AI4I 2020 Predictive Maintenance Dataset [Dataset]. (2020). UCI Machine Learning Repository. https://doi.org/10.24432/C5HS5C

Koller, D., & Friedman, N. (2009). Probabilistic graphical models: Principles and techniques. MIT Press.

Matzka, S. (2020). Explainable artificial intelligence for predictive maintenance applications. In 2020 Third International Conference on Artificial Intelligence for Industries (AI4I) (pp. 69-74). IEEE. https://doi.org/10.1109/AI4I49448.2020.00023
