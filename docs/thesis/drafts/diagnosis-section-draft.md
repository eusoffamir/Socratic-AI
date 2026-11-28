# Thesis draft, diagnosis on open machine data (for FYP1.docx Chapter 3, or the FYP2 dissertation)

Draft 1, 27 November 2026, by Claude for Eusoff. Not yet in `FYP1.docx`. When it goes in, add it as tracked changes by "Claude", in UTP format, and check the section number. Every number below comes from `eval/pgm_ai4i.py`, `app/diagnose.py` and their tests, run on 27 November 2026. References are the two already checked for `docs/industrial/pgm-ai4i.md`.

## 3.x Diagnosis on open machine data

### 3.x.1 Why a first test on open data

Our main use case is the inspection of electrical equipment in hazardous areas, with an oil and gas partner. The partner's data will take about two months to arrive. So we first tested the whole diagnosis method on an open dataset, the AI4I 2020 Predictive Maintenance Dataset (Matzka, 2020). It has 10,000 runs of a milling machine, each with a product type, two temperatures, the rotation speed, the torque, the tool wear and five failure modes. The data is synthetic and the rule behind each failure mode is published, so we can check whether our method finds the true cause, which is not possible with real plant data.

### 3.x.2 How the diagnosis works

The method joins the three kinds of knowledge from our design (Section [x]), as Dr Ho asked in the third supervision meeting.

1. **Knowledge from data (inductive).** We cut each reading into two or three named values, such as low, normal or high power. We added three values an engineer would compute, the temperature gap, the power and the strain on the tool. A Bayesian network then learned which readings cause which failure, using the BIC score and greedy hill climbing, and learned the chances by counting 7,000 past runs (Koller & Friedman, 2009). One piece of knowledge was given as a rule, that a failure never causes a reading.
2. **Choosing the next check.** When a machine fails, the system works out, for each reading not yet checked, how much it would raise the chance of naming the right fault. It suggests the reading with the highest value. This is the value of information (Koller & Friedman, 2009).
3. **Finding the cause (abductive).** After each check, the network gives the new chance of each fault, walking from the failure back to its likely cause. Each check is shown as pointing to a fault or making one unlikely, so the user can follow the reasoning.
4. **Applying the expert rule (deductive).** When one fault reaches a 90 percent chance, the system tests the published rule for that fault on the machine's real numbers, and gives the fix.
5. **Explaining.** Only this last step uses a language model. The Diagnosis agent writes a short plain explanation of the three moves. Plain code checks the reply, and a fixed explanation is used if it fails. This follows the principle that agents are used only where a fixed algorithm cannot do the job.

The links between readings, faults, checks and fixes use the standard relation classes of Section [x] (causes, tests and fixed_by).

### 3.x.3 Results

| Test | Result |
|---|---|
| Learned causes match the published causes | All 5 failure modes, with the engineer's values |
| Right fault named, using all readings (114 failed test machines) | 100 percent with the engineer's values, 81.6 percent with raw readings only |
| Expert rule agrees with a real fault (114 failed test machines) | 114 of 114 |
| Demo machines found by following the suggested checks | 11 of 11, after 1 to 6 checks |

The biggest effect came from choosing the variables. The same method with the same data went from 81.6 percent to 100 percent when it used the values an engineer would compute instead of the raw readings. This supports the main point of our knowledge graph review (Section 2.8), that how the nodes are chosen matters most.

### 3.x.4 Limits

- The AI4I data is synthetic, so it is cleaner than real plant data, and the result of 100 percent should not be expected on the partner's data.
- The fixes shown are plain engineering sense, not taken from a standard.
- The method has not been tested with engineers yet.

### References

Koller, D., & Friedman, N. (2009). *Probabilistic graphical models: Principles and techniques*. MIT Press.

Matzka, S. (2020). Explainable artificial intelligence for predictive maintenance applications. In *2020 Third International Conference on Artificial Intelligence for Industries (AI4I)* (pp. 69-74). IEEE. https://doi.org/10.1109/AI4I49448.2020.00023
