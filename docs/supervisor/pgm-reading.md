# Reading Koller and Friedman, Probabilistic Graphical Models (2009)

Meeting 3 task 6. The aim, in Dr Ho's words, is not to copy the book but to find the best way to present relationships in data to a reasoning machine. The book is in `docs/supervisor/materials/` (private, not in git). It has 1270 pages, so we read only the parts the project needs. Book page numbers are given; the PDF page is the book page plus 37.

These notes are our own summaries, in easy English. Started 25 November 2026.

## 1. Reading plan

The plan follows the authors' own reader's guide (Figure 1.2, "Core" first), then adds the parts the Ex inspection use case needs: many causes of one fault, learning chances from records, and choosing what to inspect first.

| Step | Sections | Book pages | Why we need it | Status |
|---|---|---|---|---|
| 1 | Ch 1 Introduction | 1 to 14 | The big picture and the words used | Done 25 Nov |
| 2 | 2.1 Probability, 2.2 Graphs | 15 to 44 | Conditional probability, Bayes rule, independence, graph words | Done 25 Nov |
| 3 | 3.1 to 3.4 Bayesian networks | 45 to 92 | What a node and an arrow mean, which questions the graph can answer (d-separation) | Done 25 Nov |
| 4 | 5.1 to 5.4 Local models | 157 to 185 | How to give chances to a node with many causes. Noisy-OR (5.4) fits "many things can cause a spark" | Done 25 Nov |
| 5 | 9.1 to 9.4 Variable elimination | 288 to 310 | Exact answers without adding up every case, so the network can grow past a few nodes | Done 25 Nov |
| 6 | 16, 17.1 to 17.4 Learning chances | 697 to 750 | Counting chances from data, which is what `app/pgm.py` does now, and adding prior knowledge | Done 25 Nov |
| 7 | 18.1 to 18.4 Structure learning | 783 to 820 | Learning the arrows from data. Links to section 2.8.5 of the thesis | Done 25 Nov |
| 8 | 21.1 to 21.2 Causality | 1009 to 1017 | The difference between seeing X and changing X | Done 25 Nov |
| 9 | 22.1, 22.3, 23.1, 23.2, 23.7 Decisions | 1059 to 1126 | Influence diagrams, which add actions and costs to a network, and the value of information. This could rank which equipment to inspect first | Done 25 Nov |
| Skim | 4.1 to 4.2 Markov networks | 103 to 115 | Only to know when an undirected graph fits better | |

All 9 steps were read on 25 November 2026. Next is task 8, a small network on an open dataset, as a proof of concept.

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

## 4. Notes on Chapter 3 (sections 3.1 to 3.4, Bayesian networks)

We read 3.1 to 3.4 and the four boxes, and only skimmed 3.4.3 (finding perfect maps, marked as advanced), which is the basis of the PC method in thesis section 2.8.5.

### 4.1 From one big table to small tables (3.1)

- **Write the chances in the order things happen.** Instead of one table for Intelligence and SAT together, give the chance of Intelligence, then the chance of each SAT score given Intelligence. The small table for one node given its parents is called a **CPD** (conditional probability distribution).
- **Naive Bayes** (3.1.3, Box 3.A) is one hidden class with many signs that are independent given the class. With n yes or no signs it needs only 2n + 1 numbers. Its known weakness is **double counting**. High blood pressure and obesity both point to heart disease, but they are linked to each other, so naive Bayes counts the same evidence twice, and diagnosis got worse as more signs were added. This is the weakness of our Builder's cause and signs model (section 3.4 of these notes).
- **Modularity.** Adding a new variable only needs one new small table. The old tables stay the same. This suits a graph that grows as engineers add knowledge.

### 4.2 What a Bayesian network is (3.2)

A Bayesian network is a DAG plus one CPD per node. The chance of a full case is the product of each node's chance given its parents (the **chain rule for Bayesian networks**). In the Student example (Difficulty, Intelligence, Grade, SAT, Letter) this needs 15 numbers instead of 47. With n yes or no nodes and at most k parents each, it needs fewer than n times 2 to the power k, so the size grows with the number of parents, not the number of nodes.

**What the graph promises (local independencies).** Each node is independent of everything that is not its descendant, once its parents are known. Parents shield a node from its causes further back, but its descendants (its effects) can still change our belief about it.

**The two views are the same thing.** If the graph's independencies hold, the chances can be split into the small tables, and if the chances are split that way, the independencies hold (Theorems 3.1 and 3.2).

### 4.3 Four reasoning patterns (3.2.1.2)

These match the reasoning types in our tool.

| Book's name | Direction | Student example | Our tool |
|---|---|---|---|
| Causal reasoning (prediction) | From cause to effect | Not so smart, so a strong letter is less likely (50 percent down to 39 percent) | The deductive-style forward move in `pgm.py` |
| Evidential reasoning (explanation) | From effect to cause | A grade of C, so a smart student is less likely (30 percent down to 8 percent) | The abductive move |
| Intercausal reasoning, explaining away | Between two causes of one effect | A grade of C, then learning the class is hard, so a smart student is a bit more likely again (8 percent up to 11 percent) | Not used yet |
| Combined | Mixed | A grade of C but a high SAT, so smart rises to 58 percent and a hard class rises to 76 percent | Not used yet |

**Explaining away** matters most for diagnosis. When two faults can cause the same sign, finding one fault lowers the chance of the other. In Ex inspection, finding a damaged gasket explains the water inside an enclosure, so a cracked housing becomes less likely.

We rebuilt the Student network in plain Python and got all 12 numbers the book gives in this section (for example 50.2 percent for a strong letter, 7.9 percent for smart given a C, 57.8 percent given a C and a high SAT). So adding up every case, the method `pgm.py` uses, matches the book. One thing `pgm.py` cannot do yet is a node with three values like Grade, because its nodes are only true or false.

### 4.4 Reading independence from the graph (3.3, d-separation)

For three nodes on a trail X, Z, Y, influence flows from X to Y in these cases.

| Shape | Name | Flows when |
|---|---|---|
| X to Z to Y | Causal chain | Z is not observed |
| X from Z from Y | Evidential chain | Z is not observed |
| X from Z to Y | Common cause | Z is not observed |
| X to Z from Y | Common effect (v-structure) | Z, **or one of its descendants**, is observed |

The common effect is the odd one. Two causes are independent until we see their shared effect, and then they become linked (this is explaining away). A longer trail is **active** if every three-node step on it lets influence through. X and Y are **d-separated** given what we have seen if no trail between them is active, and then they are truly independent in every network with that graph (sound, Theorem 3.3). The book also gives a fast algorithm that finds every node reachable by an active trail (3.3.3).

For our tool, d-separation tells the Ex system **which inspection results are worth asking for**. If a check is d-separated from the fault given what is already known, it cannot change the diagnosis, so it can be skipped.

### 4.5 Different graphs, same meaning (3.3.4)

Two graphs say the same thing (**I-equivalent**) exactly when they have the same skeleton (the edges with the arrows removed) and the same **immoralities** (v-structures X to Z from Y where X and Y are not joined). So data alone cannot tell "A causes B" from "B causes A". The direction must come from knowledge of the world (Chapter 21). This is why, in thesis section 2.8.5, learned arrows are "not always true causes".

### 4.6 From a distribution to a graph (3.4)

- **Minimal I-map.** Add the variables in some order, and give each one the smallest set of earlier variables that makes it independent of the rest. The result depends on the order. The causal order gives the clean Student graph, but a backwards order (Letter first) gives a graph that is almost fully joined and hides most independencies.
- **Perfect map.** A graph whose independencies are exactly those of the data. Not every distribution has one. Two examples are four students in a study circle, which needs an undirected graph (Chapter 4), and independencies that hold only for some values of a variable (Chapter 5).

### 4.7 Building a network by hand (Box 3.C) and a real case (Box 3.D)

Box 3.C is the most useful part of the chapter for the Ex use case.

- **Picking variables.** Each variable must pass the **clarity test**, which asks whether someone who saw everything could say its value. "Fever" is not clear until we say measured how, where and when. "Risk of heart attack" fails, because nobody can observe a risk, only whether the attack happened. For inspection, "seal damaged" must say what counts as damaged, and "spark risk" should not be a node.
- **Hidden variables help.** When many signs are linked by one unseen thing, add a hidden node for it. This answers our question 5. If rust and a loose cover both come from a wet location, add a "wet location" node as a parent of both, so they are independent given it, and naive Bayes no longer counts them twice.
- **Value ranges.** If the values are too coarse, the independencies can be false. For example, two cholesterol tests both fail more often when the level is borderline, so a "borderline" value is needed.
- **Picking structure.** Draw arrows from cause to effect, because causal graphs need fewer edges. Build backwards from the variable of interest. If the expert says its chance "depends on" something, add that as a parent (**extending the conversation**). Leave out weak links, because every extra edge makes the network harder to understand, to fill with numbers and to reason over. For fault diagnosis, the correct model has one variable per fault (several faults at once), but a **single fault** variable is a common simplification.
- **Picking chances.**
  - Experts dislike exact numbers, and the way a question is asked changes the answer.
  - A change from 70 to 75 percent rarely matters.
  - Three errors do matter. A **zero chance** for something that is only rare can never be undone by evidence (an early version of Pathfinder got 10 percent of its cases wrong this way). The order of size matters for rare events (1 in 10,000 against 1 in 100,000). The order between rows matters (a sign must be more likely under the right cause).
  - **Sensitivity analysis** shows which numbers change the answer, so the effort goes there.

For our tool, the Builder already asks for chances between 5 and 95 percent and the code keeps every chance between 1 and 99 percent (`builder._percent`), so it never gives a zero, and it checks the order between rows (`if_cause` higher than `if_not`). These are two of the three rules above.

**Pathfinder** (Box 3.D) diagnosed lymph node diseases with more than 60 diseases and about 100 findings. The full Bayesian network agreed with an expert pathologist in 50 of 53 cases, against 47 of 53 for naive Bayes. Its structure took about 35 hours to define and its numbers about 40 hours. The expert found it easier to give the chance of one finding across all diseases than all the findings for one disease. For the Ex use case, that suggests asking engineers "how often does each fault show this sign" one sign at a time, and planning for tens of hours of engineer time.

## 5. Notes on Chapter 5 (sections 5.1 to 5.4, local models)

Chapter 3 gave each node a full table of chances, one row for every mix of its parents' values. Chapter 5 is about smaller ways to fill that table. We skipped 5.5 (continuous variables) for now, and only skimmed the formal parts of 5.2.2 and 5.3.2 on the extra independencies these models create.

### 5.1 Why full tables break (5.1)

A full table for a yes or no node with k yes or no parents has 2 to the power k rows. Five parents need 32 rows and ten parents need 1,024. No expert will answer 1,024 questions such as "what is the chance of a fever with disease A but not B, and C but not D ...". The key idea of the chapter is that **a table is just one way to write a function** that takes the parents' values and gives a chance. Any rule that gives the right chances will do.

### 5.2 Fixed rules (5.2, deterministic CPDs)

Some nodes follow a rule with no chance at all, for example an OR gate, or blood type from two genes. They are common in machines and circuits, where the rule is part of the design.

A fixed node can also make a model simpler. The book's example is four tyres, any of which can go flat. Instead of making all four tyres parents of Steering and of Ride, add one node "a tyre is flat" that is the OR of the four, and make it the only parent of Steering and Ride.

For our tool, this is how a **fault tree fits into a Bayesian network** (thesis section 2.8.1). Each AND or OR gate becomes a fixed node, and the basic events keep their chances. So fault trees that engineers already have can be reused as part of the network.

### 5.3 When only some parents matter (5.3, context-specific CPDs)

Often a parent matters only in some situations. In the book's example, if the student did not apply for the job, the SAT score and the letter cannot affect the offer. If the SAT is high, the recruiter does not read the letter. So the 8 rows of the table collapse to 4 different cases.

- **Tree CPD.** A small yes or no tree over the parents, with a chance at each leaf (Figure 5.4). It has the same shape as the expert decision trees in `app/heuristics.py`, but here each leaf holds a chance instead of a decision. So an engineer's rule of thumb tree could become one node's table, with chances at the leaves counted from records.
- **Rule CPD.** A set of rules, each with a situation and a chance. This is finer than a tree.
- **Multinets and similarity networks** (Box 5.B). These use one small network per class, for example per disease group, holding only the signs that tell those classes apart. Pathfinder used similarity networks to cut its numbers from about 75,000 to under 14,000 (Box 3.D).
- **These models create extra independencies** that the graph alone does not show. If the student did not apply, getting the job tells us nothing about intelligence. The book shows that we can remove the arrows that do not matter in that situation and then use d-separation as before.

**Box 5.A (troubleshooting).** A printer network built for Windows 95 troubleshooting had a printer that could be joined to the computer by a local cable or by Ethernet. The Ethernet cable matters only when the printer is on the network. Writing this as a tree cut the numbers from 145 to 55. Ex equipment has the same kind of structure. For example, a check on the cable gland only matters for equipment fed by a cable, and the type of protection (flameproof, increased safety, intrinsic safety) decides which defects matter at all. That is a natural first split in a tree.

### 5.4 Many causes acting on their own (5.4, independence of causal influence)

When each cause acts on the effect through its own separate mechanism, the table can be built from one number per cause.

**Noisy-OR.**
- Each cause on its own makes the effect happen with its own chance (the noise parameter). In the book, a professor remembers a student's class questions 80 percent of the time and can read the final paper 90 percent of the time.
- The effect fails only if every present cause fails. With both causes, the letter is weak with a chance of 20 percent times 10 percent, which is 2 percent, so it is strong 98 percent of the time. We checked this number.
- A **leak** chance covers "it happens for no listed reason".
- With k causes, a noisy-OR needs k + 1 numbers instead of 2 to the power k.
- Proposition 5.3 says that when the effect is **absent**, its causes stay independent. This makes reasoning cheap in diagnosis, where most findings are absent (Box 5.C).

**Our own Ex example, with made-up numbers.** Take the node "the enclosure no longer contains a spark", with three possible defects. A damaged gasket breaks protection with a chance of 30 percent, missing bolts 20 percent and a wrong cable gland 10 percent, with a leak of 1 percent.

| Defects present | Chance protection is broken |
|---|---|
| None | 1 percent (the leak) |
| Gasket only | 30.7 percent |
| Bolts only | 20.8 percent |
| Gasket and bolts | 44.6 percent |
| All three | 50.1 percent |

That is 4 numbers instead of 8, and with ten possible defects it would be 11 numbers instead of 1,024. An engineer can answer "how often does a damaged gasket alone break protection", but not 1,024 questions about every mix of defects. An explosion still needs both a broken protection and gas in the air, which is a fixed AND (section 5.2 of these notes), not a noisy-OR.

**Logistic CPD (generalised linear model).** Each cause adds a weight to a total "burden", and an S-shaped curve (the sigmoid) turns the total into a chance. A small burden stays near 0 percent, a large one saturates near 100 percent, and in between it is close to a straight line. This is the same model as logistic regression, so its weights can be learned from records with standard tools. It also takes numeric parents, such as years in service or how many defects were found.

**The general idea (5.4.3).** Both models pass each cause through its own noise, then join the results with a simple rule (OR for noisy-OR, adding for the logistic model). **Noisy-MAX** (Box 5.D) does the same for an effect with levels of severity, which fits inspection grades such as minor, major and dangerous.

**Real size (Box 5.D).** QMR-DT, for internal medicine, has more than 500 diseases, about 4,000 findings and more than 40,000 links, all noisy-OR. CPCS has close to 500 variables. Full tables would need close to 134 million numbers, but with noisy-OR and noisy-MAX it needs 8,254, and only about 560 were asked of experts. The rest came from frequency weights already in the knowledge base. So **a large diagnosis network is possible with a few hundred expert answers**.

### 5.5 Which model for which node

This answers our question 2.

| The node looks like | Use | Numbers needed |
|---|---|---|
| Few parents, causes that interact in odd ways | Full table | 2 to the power k |
| A rule with no chance (a gate, a design rule) | Fixed (deterministic) node | None |
| Some parents matter only in some situations | Tree CPD or rules | One per leaf |
| Many causes, each able to cause the effect alone | Noisy-OR, with a leak | k + 1 |
| The effect has levels of severity | Noisy-MAX | Per cause and level |
| Causes add up, or parents are numbers, and there are records | Logistic CPD | k + 1 weights, learned from data |

## 6. Notes on Chapter 9 (sections 9.1 to 9.4, variable elimination)

We read 9.1 to 9.4 and Box 9.B, and skipped Box 9.A (the network polynomial) and the formal proofs in 9.1.

### 6.1 The bad news first (9.1)

Answering a question exactly from a Bayesian network is NP-hard in the worst case (Theorem 9.1). Even a rough answer is just as hard once there is evidence (Theorem 9.4). So no method is fast for every network. The good news is that real networks are rarely the worst case, and how hard a network is depends on its shape, which we can see and control.

### 6.2 The idea, push the sums inside (9.2)

To answer a question, `pgm.py` lists every full case, multiplies the small tables for each, and adds the ones that fit. In a chain A to B to C to D, most of those products repeat the same pieces. Variable elimination works from the inside out instead.

1. Multiply the chance of A by the chance of B given A, and add over A. This gives the chance of B, once.
2. Use that to get the chance of C, then the chance of D.

For a chain of n nodes with k values each, adding up every case costs about k to the power n steps, but this costs about n times k squared. So a chain of 20 yes or no nodes needs about 20 million multiplications by listing every case, and about 80 this way. The two ideas are that each piece of the sum depends on only a few variables, and that each piece is worked out once and kept (dynamic programming).

### 6.3 The method (9.3)

A **factor** is any small table over a few variables, for example one node's CPD. The method needs only two operations, multiplying factors and **summing out** a variable from a factor.

1. Start with one factor per node (its CPD).
2. Put the evidence in by keeping only the rows that agree with what was seen.
3. Pick an **elimination order** for the variables that are neither asked about nor seen.
4. For each variable in that order, multiply every factor that mentions it, sum it out, and put the new smaller factor back.
5. Multiply what is left and scale it to add up to 100 percent. The scale used is the chance of the evidence.

Two practical points from the worked example (9.3.1.2) follow.
- A variable below the question with no evidence on it adds nothing. It gives a factor that is always 1, so it can be dropped before starting.
- Evidence can make the work smaller. Seeing Intelligence meant that Grade and SAT never had to be joined in one factor, because they are independent once Intelligence is known.

**Our check.** We wrote a small plain Python version (about 50 lines, in the scratchpad, not in the app) and ran it on the Student network.
- It gave the same answers as adding up every case for the four questions we tried, for example 50.2 percent for a strong letter and 57.8 percent for smart given a C and a high SAT.
- It used 62 to 80 multiplications against 192 for listing all 48 cases.
- With a poor order (Grade first), the largest factor grew from 3 to 4 variables and the work rose from 80 to 118 multiplications.

The network is small, so the saving is small, but it grows quickly with size, as in the chain example.

### 6.4 What makes a network hard (9.4)

- The cost is set by the **largest factor made along the way**. A factor over m variables with v values each has v to the power m rows.
- Eliminating a variable joins all of its neighbours, which can add new links (**fill edges**). The graph with all of these links is the **induced graph**, and each factor made is a clique in it.
- The **width** of an order is the size of the largest clique minus 1. The smallest width over all orders is the **tree-width** of the network. **The work grows exponentially in the tree-width, not in the number of nodes.**
- Finding the best order is itself NP-hard (Theorem 9.7). Simple greedy rules work well in practice, such as eliminating next the variable that adds the fewest fill edges (min-fill).
- **Polytrees** (Box 9.B), networks with at most one trail between any two nodes, are always easy, and the cost grows only with the size of their tables. But there is no sharp line between easy and hard. The difficulty rises smoothly with the tree-width.

### 6.5 What this means for the Ex use case

- **Size is not the problem, shape is.** A network with hundreds of nodes is fine if it is close to a tree. A two-layer fault network (faults on top, findings below, as in Box 5.C) can have a large tree-width when many faults share many findings. The noisy-OR trick from section 5.4 of these notes (an absent finding can be removed) is what keeps such networks fast.
- **Keep the graph close to a tree.** This matches Box 3.C's advice to leave out weak links. Every extra link can raise the tree-width.
- **Question 6 is partly answered.** If the model has a single fault variable, "the most likely fault" is just one probability query (the chance of each fault given the evidence) followed by picking the largest. Variable elimination answers it, and the cost depends on the tree-width. With one variable per fault, finding the most likely set of faults is a marginal MAP question (Chapter 13), which is harder.
- **For `pgm.py`.** Adding up every case is fine for its 3 or 4 nodes. When the Ex network passes about 20 yes or no nodes (about 1 million cases), the app needs variable elimination. Our scratch version shows it fits in plain Python with no new libraries, in the same spirit as `pgm.py`. A library such as pgmpy could check its answers.

## 7. Notes on Chapter 16 and sections 17.1 to 17.4 (learning chances from data)

We read Chapter 16 (skipping the formal parts of 16.2 and Box 16.B) and sections 17.1 to 17.4 (skipping 17.2.4 and 17.2.5, which are marked as advanced, and the proofs). We read 17.3 and 17.4 as well as the planned 17.1 and 17.2, because they answer our question 3.

### 7.1 Why learn from data at all (16.1)

Building a network by hand needs a skilled person and experts for hours, and for large networks weeks or months. Sometimes the experts' time is too costly, sometimes no expert understands the whole domain, and sometimes the domain changes from site to site or over time. Records are often easier to get than expert time. The usual mix is still prior knowledge from a person plus numbers from data.

### 7.2 Three goals, three ways to judge (16.2)

1. **A good overall model** of the whole distribution, judged by how likely it finds new records.
2. **A good answer to one task**, such as classifying a fault, judged by how often that answer is right.
3. **Knowledge discovery**, finding which links are real, judged by whether the learned graph is the true one. This is the hardest to get. Equivalent graphs cannot be told apart (section 4.5 of these notes), weak links get lost in noise, and with many variables and few records some links appear strong by pure chance.

For the Ex use case, goal 2 (rank the faults) is what the product needs, and goal 3 (which defects really lead to which failures) is what the paper might claim. Goal 3 needs much more care about how sure we are.

### 7.3 Overfitting (16.3)

The chances that fit the training records best are just the shares seen in those records. With 1,000 records over 100 yes or no variables, almost every possible case gets a chance of zero. More generally, the amount of data needed grows with the number of numbers to learn, so it grows exponentially with the number of parents.

This is the **bias and variance trade-off**.
- A simple model may be wrong even with endless data (bias).
- A rich model fits the few records we have, including their noise, and changes a lot from one sample to another (variance).
- With little data, a model that is known to be too simple can give better answers than the true one.

There are two fixes, used together. One is to limit the kind of model (for example, few parents or noisy-OR). The other is to add a preference for simple models (**regularisation**).

**How to check (Box 16.A).** Test on records that were not used for learning (a **holdout test set**). With few records, use **k-fold cross-validation**, which splits the data into k parts and tests on each part in turn. A large gap between training and test results means overfitting.

### 7.4 What kind of learning (16.4)

Learning problems differ along three lines.
- **What is given.** The graph may be given with only the numbers to learn (the easy case), only the variables may be given, or even the variables may not all be known.
- **What is seen.** The data may be complete, have gaps, or have **hidden variables** that are never seen.
- **Bayesian or Markov network.**

For Bayesian networks with complete data and a known graph, the answer has a simple closed form. Gaps and hidden variables make it much harder. The methods guess the missing values, re-estimate, and repeat, which needs inference at every step (Chapter 19).

Hidden variables can still be worth it. In Figure 16.1, one hidden node with 17 numbers stands for a model that would need 59 numbers without it, which is the "wet location" idea from section 4.7 of these notes. For Ex inspection, the real state of the protection is never seen directly, only through inspection findings, so it is a hidden variable by nature.

### 7.5 Counting (17.1 and 17.2, maximum likelihood)

- **One variable.** For a thumbtack that lands heads 35 times in 100, the best fitting chance is 35 percent. This is the **maximum likelihood estimate (MLE)**, the chance that makes the seen data most likely.
- **A whole network.** The likelihood splits into one part per node, and each node's table can be learned on its own (17.2.2). For a full table, each entry is the count of that value with that parent mix, divided by the count of that parent mix (17.2.3). This is exactly what `pgm.learn()` does, apart from the extra counts described in 7.6 below.
- **Data fragmentation.** Each entry uses only the records that match its parent mix. With more parents there are many more mixes, so each gets fewer records. That gives noisy estimates and many zeros. The book calls this one of the main limits of learning Bayesian networks from data.
- **Naive Bayes as a classifier (Box 17.A).** It is easy to learn because each sign needs only its own small table. Its chances are often badly off, but it often still ranks the classes in the right order. So it is a good first baseline for "which fault is most likely".

### 7.6 Adding prior knowledge (17.3 and 17.4, Bayesian estimation)

Counting alone cannot tell 3 heads in 10 tosses from 300,000 in 1,000,000, and cannot tell a thumbtack (we know little) from a coin (we are sure it is about 50 percent). Bayesian estimation fixes both.

- **Laplace's correction.** With no prior knowledge, add 1 imaginary heads and 1 imaginary tails, so the estimate is (heads + 1) divided by (tosses + 2). **This is exactly what `pgm.learn()` does now**, so a parent mix with no records gives 50 percent and never zero.
- **A prior as imaginary records (the Beta prior).** A prior belief of p with strength a is like having already seen a times p true cases and a times (1 minus p) false cases. Real records are then added on top. In the book's example, 3 heads in 10 gives 33 percent with a weak prior (1 and 1) and 43 percent with a strong prior (10 and 10). After 300 heads in 1,000, both give about 30 percent. So the prior matters when data is scarce and fades as data grows.
- **For a whole network (17.4.3).** The usual way is to imagine a prior data set of a chosen size, described by a rough network, and to use its counts as the imaginary records for every table (the **BDe prior**).
- **The evidence (Box 17.C).** The ICU-Alarm network has 37 nodes and 504 numbers. Learning its numbers back from simulated records, plain counting (MLE) did worst, because it follows each sample too closely. A **weak prior** (an imaginary sample of about 5) did best. Strong priors added bias at first, but their effect faded as records grew.

**Our own example, with made-up numbers.** Suppose the Builder or an engineer guesses that a damaged gasket breaks protection 30 percent of the time, and we give that guess the weight of 10 imaginary inspections (3 broken, 7 not).

| Real records | Broken | Counting alone | Guess plus records |
|---|---|---|---|
| 0 | 0 | No answer | 30 percent (the guess) |
| 5 | 2 | 40 percent | 33 percent |
| 50 | 10 | 20 percent | 22 percent |
| 1,000 | 200 | 20 percent | 20.1 percent |

This is the fix for the problem we found in Chapter 1. **The AI-guessed chances should not be thrown away or trusted blindly. They should be a prior with a small weight, which real records then correct.** The weight says how much we trust the guess (an engineer's estimate might get more weight than a language model's). This also answers question 3. There is no fixed number of records. The answer for each table entry depends on how many records match its parent mix, and the prior covers the gap until there are enough.

## 8. Notes on Chapter 18 (sections 18.1 to 18.4, learning the arrows)

We read 18.1 to 18.4, skipping the formulas in 18.2.2 and 18.3.3 to 18.3.4, and the advanced parts (18.3.7 and 18.4.4). Section 18.4.4 is where the GES method cited in thesis section 2.8.5 is explained, so it is worth a later look for the thesis.

### 8.1 The problem (18.1)

The data is noisy, so the shares in it never show an exact independence. 100 tosses of two fair coins almost never give exactly 25 of each pair. So every method must decide **how sure it must be before it adds an arrow**. Adding more arrows gives false links, and adding fewer misses real ones. Which mistake is worse depends on the use.

- **For knowledge discovery**, the best possible answer is the true graph's equivalence class (section 4.5 of these notes), never more. Data cannot fix the direction of every arrow.
- **For good answers on new cases**, fewer arrows are often better, even if some of them are real. Each extra parent splits the records into smaller groups, so the numbers get noisier (data fragmentation, section 7.5 of these notes). In the book's example, a chance estimated from 9 records instead of 20 has a spread of about 17 points instead of 11.

### 8.2 Three families of methods (18.1.2)

| Family | Idea | Strength | Weakness |
|---|---|---|---|
| Constraint-based (18.2), such as PC | Test which pairs are independent given small sets of others, then build the graph that fits the tests | Clear and close to the meaning of a Bayesian network. Uses few, small tests | One wrong test can lead to several wrong arrows |
| Score-based (18.3, 18.4), such as hill climbing and GES | Give each whole graph a score for fit and simplicity, then search for a high score | Looks at the whole graph at once, so it can weigh weak links better | The search space is huge, and finding the best graph is NP-hard |
| Model averaging | Keep many likely graphs and average their answers | Shows how sure we are about each arrow | Costly. Not in our reading plan |

### 8.3 Testing independence (18.2)

The usual test for yes or no and category data is the **chi-squared test** (or mutual information). It asks how far the counts are from what independence would predict, and how likely so large a gap is by chance (the **p-value**). An arrow is kept when that chance is below 5 percent. With many tests, about 1 in 20 rejections will be wrong (the **multiple testing** problem). Stricter levels cut false arrows but miss more real ones. The book says this works well with few variables, many records and strong links, and struggles when the links are weak.

### 8.4 Scoring a graph (18.3)

- **Fit alone always prefers more arrows.** Adding an arrow can never lower the plain likelihood score, so learning by fit alone ends with an almost fully joined graph. That is overfitting.
- **The Bayesian score**, and its simple form the **BIC score**, add a cost for each number in the model. BIC is the fit minus half the log of the number of records times the number of free numbers. The fit grows with the number of records, but the cost only grows with its log. So with little data, simpler graphs win, and with more data the true graph wins. The book shows this on ICU-Alarm data, where simpler graphs (359 and 214 numbers) beat the true one (509 numbers) until there are enough records (Figure 18.4).
- **Consistency (Theorem 18.2).** With enough data, BIC picks the true graph or an equivalent one.
- **Priors on the graph** matter little once there is data, unless they rule a graph out. A small cost per arrow is a common choice. This is also where expert knowledge can enter, for example by fixing arrows the engineers are sure of, or forbidding arrows that point back in time.

### 8.5 Searching (18.4)

- **Trees are easy (18.4.1).** If each node may have at most one parent, the best tree can be found exactly and quickly. Each pair of nodes gets a weight (how much one tells about the other), and the best tree is the maximum spanning tree (the Chow and Liu idea). A tree is a good first model, because it is sparse and cannot overfit much.
- **A known order is easier (18.4.2).** If we know which variables come first, for example by time, there can be no cycles, and each node's parents can be chosen on its own. A wrong order gives an overly complex graph, as in section 4.6 of these notes. For inspection data, a natural order exists: design and environment, then defects, then the state of the protection, then the findings.
- **General graphs are hard (18.4.3).** Finding the best graph with up to 2 parents per node is already NP-hard (Theorem 18.5). The usual method is **greedy hill climbing**. Start from an empty graph, a tree or an expert's graph. Try every single change (add, remove or reverse one arrow) that keeps the graph acyclic, apply the best one, and repeat until nothing helps. It can get stuck at a local best or on a flat stretch where equivalent graphs score the same. Fixes include tabu search (do not undo recent moves), random restarts, and slightly reweighting the data.
- **In practice (18.4.3.4)**, learning both the arrows and the numbers of ICU-Alarm was only a little worse than learning the numbers with the true arrows given. A network of about 100 variables took a few minutes. The learned graphs were usually simpler than the true one, but answered almost as well.

### 8.6 Our check

We sampled records from the book's Student network (5 nodes, 4 arrows, Figure 3.4) and learned the arrows back with the BIC score and greedy hill climbing (plain Python, in the scratchpad, about 60 lines).

| Records | Samples (out of 10) where the learned links were exactly right |
|---|---|
| 50 | 2 |
| 100 | 4 |
| 200 | 7 |
| 500 | 8 |

With one sample of 50 records, it missed the weak link from Difficulty to Grade and added two false links (from Letter and from SAT to Difficulty). From 200 records upward it usually found all four links with no extras. The arrows into Grade (from Difficulty and Intelligence) can be told apart from the data, because they form a v-structure, but the direction of the Intelligence and SAT link cannot (section 4.5 of these notes). So **even a 5-node network needs a few hundred clean records to learn its links reliably, and some arrow directions always need knowledge from outside the data.**

### 8.7 What this means for the Ex use case and the thesis

- **Start from the engineers' graph, not from nothing.** Use the expert or Builder graph as the starting point and as a prior, fix the arrows the engineers are sure of, forbid arrows against the time order, and let the data suggest additions and removals. This is the mix proposed at the end of thesis section 2.8.
- **Do not claim causes from learned arrows alone.** Directions inside an equivalence class come from knowledge, not data. This backs the warning in thesis section 2.8.5.
- **Expect to need hundreds of records** even for a small network, more for weak links. Until then, structure learning is best used to flag possible missing links for an engineer to check, not to build the graph.
- **A tree is a safe first step.** With few records, the best tree is quick to learn and hard to overfit.

## 9. Notes on Chapter 21 (sections 21.1 and 21.2, causality)

We read 21.1 and 21.2, the summary (21.8), and Box 21.C, which is about repair. We skipped the advanced parts (21.3 to 21.7: when a causal answer can be found from data, counterfactuals and learning causal models). Section 21.7 is worth a later look if the paper ever claims causes from data.

### 9.1 Seeing is not doing (21.1.1)

Up to now, the direction of the arrows did not matter for answers, as long as the network gave the right chances. Arrows that follow cause and effect just give sparser, more natural graphs. Direction starts to matter when we **act on the world** instead of only looking at it.

- **Seeing.** "Given that the grade is A, what is the chance the student is smart?" This is an ordinary conditional chance.
- **Doing (an intervention).** "If we **set** the grade to A, what is the chance the student is smart?" It is written with "do", as in the chance of smart given do(grade = A). An ideal intervention sets one variable and changes nothing else directly.
- **Counterfactual.** "Given what actually happened, what would have happened if we had changed one thing?" For example, a car does not start but its lights work, so would replacing the battery have fixed it? The evidence (the lights work) must be kept, and it already says the battery is probably fine.

**Our check, on the Student network.** Seeing an A raises the chance that the student is smart from 30 percent to 61 percent. Faking the A (the book's student hacks the grade database) leaves it at 30 percent, because a set grade says nothing about where it came from. The chance of a strong letter is 90 percent either way, because the letter depends only on the grade.

### 9.2 Why links in data are not causes (21.1.2)

A link between X and Y in data can come from X causing Y, from Y causing X, or from both sharing a cause. The book's examples are useful as warnings for real inspection data.

- **Hidden common cause (confounding).** People who take an antacid get more ulcers, but the discomfort before an ulcer causes both. We can never list every hidden cause.
- **Selection bias.** A survey answered mostly by good students and by athletes shows a false negative link between sport and grades.
- **Mixed groups.** Across all children, height and verbal ability look negatively linked, only because boys and girls differ in both.
- **Shared trends over time.** Average height rose while polar ice shrank over the last century, so they look linked, but time is the hidden common cause.

### 9.3 A causal model (21.2)

A **causal model** is a Bayesian network in which each arrow is read as a direct cause, and each node's table is the **mechanism** that makes its value from its parents. To answer "what if we set Z to z", cut every arrow into Z and fix Z to z (the **mutilated network**), then ask the question as usual.

So X to Y and Y to X are the same for seeing but different for doing. This is why the direction of arrows, which data alone cannot always fix (section 8.6 of these notes), matters as soon as the system recommends actions.

**Simpson's paradox (Example 21.9).** We checked the book's numbers.
- **Seeing.** Overall, 57.5 percent of patients who took a drug were cured, against 50 percent of those who did not, so the drug looks good.
- **By group.** Among men it was 70 percent against 80 percent, and among women 20 percent against 40 percent, so it was worse in both groups. Men took the drug far more often (75 percent against 25 percent) and men recover more often anyway.
- **Doing.** Cutting the arrow from gender to drug gives 45 percent cured if everyone takes the drug and 60 percent if no one does. So the drug harms.

The causal graph tells us which numbers to trust, which the data alone cannot.

### 9.4 Repair is an action (Box 21.C)

In troubleshooting, a repair is an intervention. It sets a part to "not broken". But the question after a repair is a counterfactual one: given the faults we saw before, is the system fixed now? If the evidence already said the replaced part was probably fine, the system is probably still broken. With noisy-OR tables and a single fault, this is cheap to compute (the book points to Breese and Heckerman, 1996, which we have not checked).

### 9.5 What this means for the Ex use case

- **Diagnosis is seeing, but advice is doing.** "Which fault is most likely, given these findings?" is an ordinary question, so a non-causal network is fine. "Will replacing the gasket restore protection?" or "Which repair lowers the chance of ignition most?" are questions about doing, so the arrows must follow real cause and effect. They must come from engineers and physics, not from data alone.
- **Watch for these traps in inspection records.**
  - Selection bias. Equipment flagged before may be inspected more closely, so it shows more defects.
  - Hidden common causes. Older sites, or sites near the sea, may have both more corrosion and more of other defects.
  - Mixed groups. Each type of protection may behave differently, so pooling them can hide or reverse a link, as in Simpson's paradox.

  The fix is to put these factors in the model as nodes (site, age, type of protection), so the network can account for them.
- **For our tool.** The deductive move in `pgm.py` asks for the chance of an effect given its cause by seeing, not doing. For a cause with no parents, such as "the day is hot", seeing and doing give the same answer, so the current cases are fine. The difference appears once a cause has its own causes.

## 10. Notes on Chapters 22 and 23 (sections 22.1, 22.3, 23.1, 23.2 and 23.7, decisions)

We read 22.1.1, 22.3.1 and Box 22.B in Chapter 22, and 23.1, 23.2, 23.7 and Box 23.C in Chapter 23. We added 23.7 (value of information) and Box 23.C (troubleshooting) to the plan, because they answer our question 7 and match the Ex use case closely. We skipped the proofs, utility curves and attitudes to risk (22.2), complex outcomes (22.4), and the algorithms for solving influence diagrams (23.3 to 23.6).

### 10.1 Expected utility (22.1)

A chance alone does not say what to do. We also need how much each outcome matters, its **utility**. The rule is to **pick the action with the highest expected utility**, which is each outcome's utility times its chance, added up over the outcomes.

- In the book's example, a graduate deciding whether to start a company faces no demand (50 percent, utility minus 7), low demand (30 percent, utility 5) or high demand (20 percent, utility 20). Starting the company has an expected utility of 2, and not starting has 0, so he should start it.
- Utility is not the same as money. Most people take a sure 3 million over an 80 percent chance of 4 million, even though the second is worth 3.2 million on average. Fear of loss is part of the utility.

### 10.2 Where utilities come from (22.3, Box 22.B)

Utilities are harder to get than chances. Chances can be counted from data, but utilities are a person's or an organisation's own preferences, they are never seen directly, and different ways of asking give different answers. The classic way is the **standard gamble**, which asks at what chance of the best outcome (against the worst) a person is indifferent to a sure middle outcome.

**Pathfinder again (Box 22.B).**
- Its evaluation weighed each wrong diagnosis by how much harm it does. Mistaking a viral infection for a bacterial one costs a few days of antibiotics, but mistaking Hodgkin's disease for a viral infection can be deadly.
- It put all harms on one scale, the **micromort**, a one-in-a-million chance of death.
- Splitting the harm into parts (the disease itself, a delayed treatment, a needless treatment) cut the questions by 80 percent, to about 60 hours of work.
- The full Bayesian network lost on average 16 micromorts per case, against 340 for naive Bayes.
- The book adds a useful point. A **bad decision** is not the best choice given what was known, but a **bad outcome** can happen to a good decision by bad luck. So a system should be judged on its decisions, not on single outcomes.

### 10.3 Decision trees and influence diagrams (23.1 and 23.2)

- **Decision tree.** This has the agent's choices and nature's chances as branches and utilities at the leaves. It is solved from the leaves up (**backward induction**). At a chance point, take the chance-weighted average. At a choice point, take the best branch. It is clear but grows very fast and repeats the same numbers in many branches.
  - This is a different object from the expert decision trees in `app/heuristics.py`, which are yes or no rules with no chances or utilities.
- **Influence diagram** (decision network). This is a Bayesian network with two more kinds of node:
  - **chance nodes** (ovals), with their usual tables
  - **decision nodes** (rectangles), whose incoming arrows show what is known when the choice is made (**information edges**)
  - **utility nodes** (diamonds), each a fixed number for each mix of its parents, with no children. The total utility is the sum of the utility nodes.

  A decision is an action, so an influence diagram is causal by nature. Choosing a value for a decision node is a "do" (section 9 of these notes).

### 10.4 Value of information (23.7)

The **value of perfect information** of a check is how much the best expected utility rises if we see the check's result before deciding. It is never negative. It is **zero if no possible result would change the decision**.

- **Our check.** In the book's example, a market survey before deciding gives an expected utility of 3.25 with the book's tables, against 2 without it, so the survey is worth about 1.25. The book gives 3.22 and a value of 1.22. The small gap is probably rounding, or a survey cost set in Example 23.6, which we did not read.
- **Many checks.** Choosing the best plan of checks, where each next check depends on earlier results, is very hard. The usual shortcut is **myopic**: pick the single best next check, see its result, and repeat. It can miss a check that is worth little alone but shows which other check to do.

This answers question 7. d-separation can rule out checks that cannot change any chance that matters (their value is zero). Value of information goes further. It ranks the remaining checks by how much they can change the decision, and the cost of each check can be subtracted.

### 10.5 Troubleshooting (Box 23.C)

The Windows 95 troubleshooters were hundreds of Bayesian networks, each a few dozen to a few hundred variables, one per common fault such as printing.
- Actions were either **checks** (observe a part) or **repairs** (replace a part), each with a cost.
- Repairs were handled as counterfactuals (Box 21.C), because the evidence from before the repair still holds after it.
- With a single fault and noisy-OR tables, the expected cost of repair could be computed exactly, and the next check chosen by its value of information.
- On the printer network, this saved about 20 percent of repair time over the best fixed plan. It did as well or better even when there were several faults, which broke the model's own assumption.
- Users found the questions sensible and could skip one. Designers found it easier to update a few tables than to redraw a flowchart.

### 10.6 What this means for the Ex use case

This is the part of the book closest to Dr Ho's "prioritise by safety impact".

- **Rank by expected loss, not by chance alone.** A simple version is the chance that an item's protection is broken times the harm if it ignites.
  - In our own example with made-up numbers, a pump motor in a Zone 1 area with a 30 percent chance of broken protection and a harm of 100 gives an expected loss of 30. A light fitting in Zone 1 at 10 percent gives 10. A junction box in Zone 2 at 45 percent, with a harm of only 20 because gas is present less often there, gives 9.
  - So the junction box is the most likely to be broken but the least urgent.
  - The real harm should come from the partner's own risk ratings, not from us. Hazardous area zones are a real classification, but our numbers are not.
- **The influence diagram is the natural model of the product.**
  - Chance nodes: the hidden state of each item's protection, its defects, the gas present and the findings.
  - Decision nodes: which item to inspect next, and whether to repair or isolate it.
  - Utility nodes: the harm of an ignition and the cost of inspection, repair and downtime.
- **Value of information picks the next inspection.** Choose the check with the largest value minus its cost, see the result, update and repeat (myopic). This is the same loop as the Windows troubleshooters, which is evidence that it works in practice.
- **Judge the system on decisions, not outcomes** (Box 22.B). For the paper, compare its ranking with an expert's ranking on the same findings, not with whether a fault happened later.
- **Utilities belong to the partner.** The cost of an ignition against the cost of downtime is the partner's and the regulator's choice. Our job is to make that choice explicit and use it consistently.

## 11. What this means for our tool

| In the book | In our tool now | Gap |
|---|---|---|
| Nodes are random variables chosen for the questions | Nodes are true or false statements, each linked to a knowledge graph node (`app/pgm.py`) | Only yes or no values. Real inspection data will have more values, such as a condition grade. Grade in the Student example needs three values |
| Explaining away between two causes (3.2.1.2) | Each case has one cause | A fault model needs two or more causes of the same sign |
| Hidden nodes stop double counting (Box 3.C) | The Builder's model is naive Bayes, with one cause and two signs | Add a shared hidden cause when signs are linked |
| Smaller tables (noisy-OR, trees, fixed nodes, Ch 5) | Every node has a full table | Fine for 1 or 2 parents. A fault with many causes needs noisy-OR, and fault trees need fixed AND and OR nodes |
| Tree CPDs (5.3) | Expert decision trees in `app/heuristics.py` end in decisions, not chances | The same tree shape could hold chances at its leaves and become one node's table |
| Numbers learned from data, with a prior (Ch 17) | Chances counted from simulated data with a fixed seed, plus 1 imaginary true and 1 false (Laplace's correction, `pgm.learn()`) | The data is made up to show the method. The prior is the same weak one everywhere, and is not yet taken from an expert or the Builder's guess |
| Variable elimination (Ch 9) | Exact answer by adding up every case | Fine for 3 or 4 nodes, too slow past about 20. Variable elimination works in plain Python (checked in a scratch version), and its cost depends on the tree-width, not the number of nodes |
| Structure from experts or data (Ch 18) | Arrows written by hand, or drafted by the Builder | No structure learning yet. BIC with hill climbing works in plain Python (checked in a scratch version), but needs a few hundred records even for 5 nodes. Best used to start from the expert graph and suggest changes |
| Confidence numbers without meaning are a known failure (Mycin) | The Builder's chances for a new topic are AI guesses in round numbers | Our guessed chances have the same weakness. Chapter 17 gives the fix, use each guess as a weak prior (a few imaginary records) that real records then correct (section 7.6) |
| Holdout test or cross-validation (Box 16.A) | Not used, because the data is simulated | Needed as soon as real inspection records arrive |
| Seeing against doing (Ch 21) | Only seeing. The deductive move conditions on the cause | Same answer for causes with no parents, as in the current cases. Advice about repairs needs "do" (cut the arrows into the repaired part) and arrows that follow real causes |
| Influence diagrams and value of information (Ch 23) | No decisions or utilities. The tool reports chances only | The Ex product needs decision and utility nodes, a ranking by expected loss, and value of information to choose the next check |

## 12. Questions still open

Question 5 is answered in section 4.7 (add a hidden shared cause). Question 1 is partly answered there too (the clarity test, and values fine enough for the independencies to hold). Question 2 is answered in section 5.5 (the table of which model to use for which node). Question 6 is partly answered in section 6.5 (with one fault variable it is a single probability query, and the cost depends on the tree-width). Question 3 is answered in section 7.6 (it depends on the records per parent mix, and a weak prior covers the gap). Questions 4 and 7 are answered in sections 10.4 and 10.6 (yes, an influence diagram ranks by expected loss, and value of information chooses the next check).

1. How do we pick the values of a variable when the inspection data uses grades or free text?
2. When does a node with many causes need noisy-OR (5.4) instead of a full table?
3. How much data does counting need before the chances are trustworthy (Ch 17)?
4. Can an influence diagram (23.2) turn "chance of a spark" plus "cost of an explosion" into an inspection order?
5. When two signs share another cause (rust and a loose cover from a wet location), how does a Bayesian network show it without the table growing too big (Chapter 3)?
6. Is marginal MAP over the fault (2.1.5.3) cheap enough to answer for a network of 20 or more nodes (Chapter 9 and 13)?
7. Can d-separation pick the next inspection check to ask for, by skipping checks that cannot change the diagnosis?
8. Should the Ex model use one variable per fault (several faults at once) or a single fault variable, given the cost of reasoning?
9. Do the partner's inspection records grade defects by severity (for noisy-MAX), and do they say the type of protection, so that it can be the first split of a tree?
10. How many imaginary records should a guessed chance be worth, for a language model guess and for an engineer's estimate? Cross-validation on the first real records could choose it.
11. Will the partner have enough clean inspection records (a few hundred or more, with the same fields filled in) to suggest links, or only enough to correct the numbers of an engineer-built graph?
12. Do the inspection records say why each item was inspected (routine or flagged), and give site, age and type of protection, so that selection bias and hidden common causes can be modelled?
13. What harm or risk rating does the partner already use for each item and zone, so that the utilities come from them and not from us?

## References

Koller, D., & Friedman, N. (2009). Probabilistic graphical models: Principles and techniques. MIT Press.

Lauritzen, S. L., & Spiegelhalter, D. J. (1988). Local computations with probabilities on graphical structures and their application to expert systems. Journal of the Royal Statistical Society, Series B, 50(2), 157-194. https://doi.org/10.1111/j.2517-6161.1988.tb01721.x

Pearl, J. (1988). Probabilistic reasoning in intelligent systems: Networks of plausible inference. Morgan Kaufmann. (Cited in Koller and Friedman; not yet checked.)
