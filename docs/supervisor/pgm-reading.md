# Reading Koller and Friedman, Probabilistic Graphical Models (2009)

Meeting 3 task 6. The aim, in Dr Ho's words, is not to copy the book but to find the best way to present relationships in data to a reasoning machine. The book is in `docs/supervisor/materials/` (private, not in git). It has 1270 pages, so we read only the parts the project needs. Book page numbers are given; the PDF page is the book page plus 37.

These notes are our own summaries, in easy English. Started 25 November 2026.

## 1. Reading plan

The plan follows the authors' own reader's guide (Figure 1.2, "Core" first), then adds the parts the Ex inspection use case needs: many causes of one fault, learning chances from records, and choosing what to inspect first.

| Step | Sections | Book pages | Why we need it | Status |
|---|---|---|---|---|
| 1 | Ch 1 Introduction | 1 to 14 | The big picture and the words used | Done 25 Nov |
| 2 | 2.1 Probability, 2.2 Graphs | 15 to 44 | Conditional probability, Bayes rule, independence, graph words | Done 25 Nov |
| 3 | 3.1 to 3.4 Bayesian networks | 45 to 92 | What a node and an arrow mean, which questions the graph can answer (d-separation) | Next |
| 4 | 5.1 to 5.4 Local models | 157 to 185 | How to give chances to a node with many causes. Noisy-OR (5.4) fits "many things can cause a spark" | |
| 5 | 9.1 to 9.4 Variable elimination | 288 to 310 | Exact answers without adding up every case, so the network can grow past a few nodes | |
| 6 | 16, 17.1 to 17.2 Learning chances | 697 to 732 | Counting chances from data, which is what `app/pgm.py` does now | |
| 7 | 18.1 to 18.4 Structure learning | 783 to 820 | Learning the arrows from data. Links to section 2.8.5 of the thesis | |
| 8 | 21.1 to 21.2 Causality | 1009 to 1017 | The difference between seeing X and changing X | |
| 9 | 22.1, 23.1 to 23.2 Decisions | 1059 to 1095 | Influence diagrams, which add actions and costs to a network. This could rank which equipment to inspect first | |
| Skim | 4.1 to 4.2 Markov networks | 103 to 115 | Only to know when an undirected graph fits better | |

Then task 8, a small network on an open dataset, as a proof of concept.

## 2. Notes on Chapter 1 (Introduction)

**Keep the knowledge apart from the reasoning.** The book builds a model of the world inside the computer (a declarative representation), and general algorithms answer questions from it. The same algorithms then work for any domain, and the model can be improved without touching the algorithms. This matches two points from Meeting 3. The graph should be a stored artifact that the diagnosis walks on, and agents should be used only where a fixed algorithm cannot do the job.

**Why chances and not just rules.** We rarely know the true state of the world, because we see only part of it, what we see has noise, and most links are not certain. Listing every possible cause is useless ("it could be any of 573 diseases"), so we need what is probable, not just what is possible. For Ex inspection, many faults could lead to a spark, and the point is to rank them.

**Choosing the variables is a design decision.** Each node is a random variable, such as Flu (yes or no) or Season (four values). The book says the choice of variables and their values depends on the questions we want to answer. This is the same question as "which things become nodes" in our knowledge graph review (thesis section 2.8).

**A question is a conditional chance.** With a joint distribution over all variables, we can ask for the chance of one thing given what we have seen, for example the chance of flu given that it is autumn, the nose is blocked and there is no muscle pain. This is the abductive move in our tool (cause given signs).

**The graph makes this small.** Five variables already have 64 combinations. The graph says each variable depends directly on only a few others, so the full table breaks into small pieces that multiply together. In the flu example this needs 17 numbers instead of 63. The graph can be read two ways that turn out to be the same: as a list of independencies (once flu and hay fever are known, the season tells us nothing more about a blocked nose), or as a recipe for which small tables to multiply.

**Two kinds of graph.** Bayesian networks use arrows (directed). Markov networks use plain lines (undirected). They can express different sets of independencies.

**Three jobs.** Every model needs a representation (the graph and its numbers), inference (answering questions from it) and learning (building it from data). The book says the usual way to learn is that an expert names the variables and the main links, and the numbers are filled in from data. That is the mix suggested at the end of thesis section 2.8.

**Beyond seeing.** Part IV adds causality (what happens if I change X, not only what I learn if I see X) and decisions (influence diagrams, which add actions and how much each outcome matters). This is the part closest to "prioritise by safety impact".

**History worth citing.**
- Early expert systems used naive Bayes, where all symptoms are independent given the disease. The book reports that one such system for acute abdominal pain was right in over 90 percent of cases, against about 65 percent for doctors (section 1.4; check the original paper before citing it).
- Rule systems with "confidence factors", such as Mycin and Prospector, replaced them, but their numbers had no clear meaning and gave odd results in some reasoning patterns.
- Pearl (1988) and Lauritzen and Spiegelhalter (1988) made Bayesian networks practical. Pathfinder, for pathology diagnosis, was an early large success.
- The book lists fault diagnosis as a common use.

## 3. Notes on Chapter 2 (sections 2.1 Probability and 2.2 Graphs)

We skipped the parts on continuous variables, expectation and variance (2.1.6 and 2.1.7) for now. They matter later if the inspection data has measurements such as temperature or resistance.

### 3.1 What a chance means

There are two readings of a chance, and both follow the same rules.

- **Frequency.** A chance of 30 percent means that if we repeat the same thing many times, it happens about 30 percent of the time. This fits dice and fits records of many inspections. It does not fit one-off events, such as "this plant will have a fire next year".
- **Degree of belief.** A chance of 30 percent is how strongly a person believes it. The book's betting argument says a rational person's beliefs must still obey the rules of probability, or someone could set up bets that make them lose for sure.

For our tool, the chances in `app/pgm.py` are frequencies (counted from data). The chances the Topic Builder guesses for a new topic, and an engineer's estimates, are degrees of belief. Both are allowed, but a belief must at least be consistent. For example, the chances of all the values of one variable must add up to 100 percent, and a sign must be more likely when its cause is there (the Builder already checks that `if_cause` is higher than `if_not`).

### 3.2 Conditional chance, the chain rule and Bayes rule

- **Conditional chance.** The chance of B given A is the share of the A cases in which B is also true. Learning A gives a new set of chances.
- **Chain rule.** The chance that several things are all true is the chance of the first, times the chance of the second given the first, and so on. Any order gives the same answer. This is the rule that a Bayesian network later uses to multiply small tables.
- **Bayes rule.** It turns "chance of the sign given the cause" into "chance of the cause given the sign". This is the abductive move in our tool.

**The base rate trap (Example 2.2).** A test that is right 95 percent of the time, for something only 1 in 1000 people has, gives a positive result that is right less than 2 percent of the time, because almost all positives come from the many healthy people. The same thing will happen in Ex inspection. Here is our own example with made-up numbers. A camera check flags a damaged seal 95 percent of the time and gives a false alarm 5 percent of the time. If only 1 enclosure in 100 really has a damaged seal, then a flagged enclosure is truly damaged only about 16 percent of the time. So the diagnosis must always use how common the fault is, not only how good the check is.

### 3.3 Variables, joint and marginal tables

- A **random variable** is one property of each case, with a set of values, such as Grade (A, B or C) or a seal's condition (good, worn or damaged). A yes or no variable is called Bernoulli.
- The **joint table** gives the chance of every combination of values. The **marginal** chance of one variable comes from adding the joint table along a row or column (Figure 2.1).
- A **conditional table** is a set of chances for X, one for each value of Y. In the book's example, a student is smart with a chance of 30 percent, but 72 percent once we know the grade is A.

### 3.4 Independence and conditional independence

- Two things are **independent** if learning one does not change the chance of the other.
- Real things are rarely independent, but often they become independent **once a third thing is known**. Admission to Stanford and to MIT are linked, but if both depend only on the grade and we know the grade, learning one admission tells us nothing more about the other.
- The book lists rules for working out new independencies from known ones (symmetry, decomposition, weak union, contraction, and intersection for distributions with no zero chances). They are the tools behind d-separation in Chapter 3.

For our tool, the small cause and signs model that the Builder drafts assumes the two signs are independent once the cause is known. This is the naive Bayes assumption from Chapter 1. It keeps the model small, but it is wrong when two signs share another cause. In Ex inspection, for example, rust and a loose cover might both come from the same wet location, not only from a broken seal.

### 3.5 Three kinds of question

1. **Probability query.** The chance of some variables given the evidence. This is what `pgm.chance()` answers now.
2. **MAP query.** The single most likely full combination of all unknown variables.
3. **Marginal MAP query.** The most likely value of only the variables we care about, after adding over the rest.

**Picking each variable's best value one by one is not the same as picking the best combination** (Example 2.4). For diagnosis, the book's point is that we usually want marginal MAP over the fault only. Otherwise, a rare fault whose few signs are all very likely can beat a common fault whose many signs are each only fairly likely. So when the Ex tool says "the most likely fault", it should add over the signs it has not seen, not choose a full story of every variable.

### 3.6 Graph words (2.2)

- **Directed edge** X to Y (Y is the **child**, X the **parent**). **Undirected edge** X with Y (they are **neighbours**).
- A **path** follows the arrows. A **trail** ignores their direction. **Ancestors** and **descendants** come from directed paths.
- A **topological order** lists every parent before its children. `pgm.order()` uses one, so that each node's chance is worked out after its parents.
- A **cycle** is a directed path back to the start. Bayesian networks must be **acyclic (a DAG)**, because a model with directed cycles has no clear meaning.
- A **loop** is a trail back to the start, ignoring direction. Graphs with no loops (trees and **polytrees**) are cheap to reason over. Loops make reasoning cost more.
- A **clique** is a set of nodes that are all joined. A graph is **chordal** if every loop of 4 or more nodes has a shortcut edge. Both come back in Chapters 9 and 10 to measure how hard exact reasoning is.

For our tool, the knowledge graph allows "causes" arrows in any direction, and nothing stops them forming a cycle (A causes B, B causes A). That is fine for teaching, but **if we ever turn the causal part of the knowledge graph into a Bayesian network, we must first check that it is acyclic**. `app/heuristics.py` already walks its decision trees from the root to catch loops, so the same idea can be reused.

## 4. What this means for our tool

| In the book | In our tool now | Gap |
|---|---|---|
| Nodes are random variables chosen for the questions | Nodes are true or false statements, each linked to a knowledge graph node (`app/pgm.py`) | Only yes or no values. Real inspection data will have more values, such as a condition grade |
| Numbers learned from data | Chances counted from simulated data with a fixed seed | The data is made up to show the method |
| Inference by smart algorithms (Ch 9) | Exact answer by adding up every case | Fine for 3 or 4 nodes, too slow past about 20 |
| Structure from experts or data (Ch 18) | Arrows written by hand, or drafted by the Builder | No structure learning yet |
| Confidence numbers without meaning are a known failure (Mycin) | The Builder's chances for a new topic are AI guesses in round numbers | Our guessed chances have the same weakness. They should be marked as guesses or replaced by counted ones |

## 5. Questions to carry into the next chapters

1. How do we pick the values of a variable when the inspection data uses grades or free text?
2. When does a node with many causes need noisy-OR (5.4) instead of a full table?
3. How much data does counting need before the chances are trustworthy (Ch 17)?
4. Can an influence diagram (23.2) turn "chance of a spark" plus "cost of an explosion" into an inspection order?
5. When two signs share another cause (rust and a loose cover from a wet location), how does a Bayesian network show it without the table growing too big (Chapter 3)?
6. Is marginal MAP over the fault (2.1.5.3) cheap enough to answer for a network of 20 or more nodes (Chapter 9 and 13)?

## References

Koller, D., & Friedman, N. (2009). Probabilistic graphical models: Principles and techniques. MIT Press.

Lauritzen, S. L., & Spiegelhalter, D. J. (1988). Local computations with probabilities on graphical structures and their application to expert systems. Journal of the Royal Statistical Society, Series B, 50(2), 157-194. https://doi.org/10.1111/j.2517-6161.1988.tb01721.x

Pearl, J. (1988). Probabilistic reasoning in intelligent systems: Networks of plausible inference. Morgan Kaufmann. (Cited in Koller and Friedman; not yet checked.)
