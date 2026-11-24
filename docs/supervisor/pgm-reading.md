# Reading Koller and Friedman, Probabilistic Graphical Models (2009)

Meeting 3 task 6. The aim, in Dr Ho's words, is not to copy the book but to find the best way to present relationships in data to a reasoning machine. The book is in `docs/supervisor/materials/` (private, not in git). It has 1270 pages, so we read only the parts the project needs. Book page numbers are given; the PDF page is the book page plus 37.

These notes are our own summaries, in easy English. Started 25 November 2026.

## 1. Reading plan

The plan follows the authors' own reader's guide (Figure 1.2, "Core" first), then adds the parts the Ex inspection use case needs: many causes of one fault, learning chances from records, and choosing what to inspect first.

| Step | Sections | Book pages | Why we need it | Status |
|---|---|---|---|---|
| 1 | Ch 1 Introduction | 1 to 14 | The big picture and the words used | Done 25 Nov |
| 2 | 2.1 Probability, 2.2 Graphs | 15 to 44 | Conditional probability, Bayes rule, independence, graph words | Next |
| 3 | 3.1 to 3.4 Bayesian networks | 45 to 92 | What a node and an arrow mean, which questions the graph can answer (d-separation) | |
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

## 3. What this means for our tool

| In the book | In our tool now | Gap |
|---|---|---|
| Nodes are random variables chosen for the questions | Nodes are true or false statements, each linked to a knowledge graph node (`app/pgm.py`) | Only yes or no values. Real inspection data will have more values, such as a condition grade |
| Numbers learned from data | Chances counted from simulated data with a fixed seed | The data is made up to show the method |
| Inference by smart algorithms (Ch 9) | Exact answer by adding up every case | Fine for 3 or 4 nodes, too slow past about 20 |
| Structure from experts or data (Ch 18) | Arrows written by hand, or drafted by the Builder | No structure learning yet |
| Confidence numbers without meaning are a known failure (Mycin) | The Builder's chances for a new topic are AI guesses in round numbers | Our guessed chances have the same weakness. They should be marked as guesses or replaced by counted ones |

## 4. Questions to carry into the next chapters

1. How do we pick the values of a variable when the inspection data uses grades or free text?
2. When does a node with many causes need noisy-OR (5.4) instead of a full table?
3. How much data does counting need before the chances are trustworthy (Ch 17)?
4. Can an influence diagram (23.2) turn "chance of a spark" plus "cost of an explosion" into an inspection order?

## References

Koller, D., & Friedman, N. (2009). Probabilistic graphical models: Principles and techniques. MIT Press.

Lauritzen, S. L., & Spiegelhalter, D. J. (1988). Local computations with probabilities on graphical structures and their application to expert systems. Journal of the Royal Statistical Society, Series B, 50(2), 157-194. https://doi.org/10.1111/j.2517-6161.1988.tb01721.x

Pearl, J. (1988). Probabilistic reasoning in intelligent systems: Networks of plausible inference. Morgan Kaufmann. (Cited in Koller and Friedman; not yet checked.)
