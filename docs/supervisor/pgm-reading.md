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
| 6 | 16, 17.1 to 17.2 Learning chances | 697 to 732 | Counting chances from data, which is what `app/pgm.py` does now | Next |
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

## 7. What this means for our tool

| In the book | In our tool now | Gap |
|---|---|---|
| Nodes are random variables chosen for the questions | Nodes are true or false statements, each linked to a knowledge graph node (`app/pgm.py`) | Only yes or no values. Real inspection data will have more values, such as a condition grade. Grade in the Student example needs three values |
| Explaining away between two causes (3.2.1.2) | Each case has one cause | A fault model needs two or more causes of the same sign |
| Hidden nodes stop double counting (Box 3.C) | The Builder's model is naive Bayes, with one cause and two signs | Add a shared hidden cause when signs are linked |
| Smaller tables (noisy-OR, trees, fixed nodes, Ch 5) | Every node has a full table | Fine for 1 or 2 parents. A fault with many causes needs noisy-OR, and fault trees need fixed AND and OR nodes |
| Tree CPDs (5.3) | Expert decision trees in `app/heuristics.py` end in decisions, not chances | The same tree shape could hold chances at its leaves and become one node's table |
| Numbers learned from data | Chances counted from simulated data with a fixed seed | The data is made up to show the method |
| Variable elimination (Ch 9) | Exact answer by adding up every case | Fine for 3 or 4 nodes, too slow past about 20. Variable elimination works in plain Python (checked in a scratch version), and its cost depends on the tree-width, not the number of nodes |
| Structure from experts or data (Ch 18) | Arrows written by hand, or drafted by the Builder | No structure learning yet |
| Confidence numbers without meaning are a known failure (Mycin) | The Builder's chances for a new topic are AI guesses in round numbers | Our guessed chances have the same weakness. They should be marked as guesses or replaced by counted ones |

## 8. Questions to carry into the next chapters

Question 5 is answered in section 4.7 (add a hidden shared cause). Question 1 is partly answered there too (the clarity test, and values fine enough for the independencies to hold). Question 2 is answered in section 5.5 (the table of which model to use for which node). Question 6 is partly answered in section 6.5 (with one fault variable it is a single probability query, and the cost depends on the tree-width).

1. How do we pick the values of a variable when the inspection data uses grades or free text?
2. When does a node with many causes need noisy-OR (5.4) instead of a full table?
3. How much data does counting need before the chances are trustworthy (Ch 17)?
4. Can an influence diagram (23.2) turn "chance of a spark" plus "cost of an explosion" into an inspection order?
5. When two signs share another cause (rust and a loose cover from a wet location), how does a Bayesian network show it without the table growing too big (Chapter 3)?
6. Is marginal MAP over the fault (2.1.5.3) cheap enough to answer for a network of 20 or more nodes (Chapter 9 and 13)?
7. Can d-separation pick the next inspection check to ask for, by skipping checks that cannot change the diagnosis?
8. Should the Ex model use one variable per fault (several faults at once) or a single fault variable, given the cost of reasoning?
9. Do the partner's inspection records grade defects by severity (for noisy-MAX), and do they say the type of protection, so that it can be the first split of a tree?

## References

Koller, D., & Friedman, N. (2009). Probabilistic graphical models: Principles and techniques. MIT Press.

Lauritzen, S. L., & Spiegelhalter, D. J. (1988). Local computations with probabilities on graphical structures and their application to expert systems. Journal of the Royal Statistical Society, Series B, 50(2), 157-194. https://doi.org/10.1111/j.2517-6161.1988.tb01721.x

Pearl, J. (1988). Probabilistic reasoning in intelligent systems: Networks of plausible inference. Morgan Kaufmann. (Cited in Koller and Friedman; not yet checked.)
