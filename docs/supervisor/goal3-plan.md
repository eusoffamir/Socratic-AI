# Goal 3: one way to represent knowledge (plan for Dr Ho)

Written by Claude on 22 October 2026 for Eusoff to share with Dr Ho. This is a DRAFT plan. In Meeting 2, Dr Ho put Goal 3 in the next semester, so it is built in new files and does not change Goal 1.

## 1. The idea, from Meeting 2

Knowledge comes from three places, and each place has its own natural form.

| Where it comes from | Form | A node is | A link is | File |
|---|---|---|---|---|
| Books and readings | Knowledge graph | one piece of knowledge with its type (factual, causal and so on) | causes, then, defines, supports, weakens, tests, leads to | `app/knowledge.py` (built in Goal 1) |
| Human heuristics (rules of thumb) | Decision tree | a question an expert asks, or the decision at the end | the answer, such as yes or no | `app/heuristics.py` (step 2) |
| Data | Probabilistic graph model (a small Bayesian network) | something that can be true or false, such as "the pattern is real" | "makes more likely", with a chance learned from the data | `app/pgm.py` (step 3) |

All three use the same shape, a list of nodes and a list of links, so one set of graph moves works on all of them. Each tree question and each network node also points to the knowledge graph node it rests on, so the three forms join into one map of the topic.

## 2. Reasoning as moves on the graph

Dr Ho's aim is to write reasoning as an operation on the graph (a graph traversal), so it can become an algorithm. The first definitions are below.

| Reasoning | Move on the graph | Quant example |
|---|---|---|
| Deductive | Start from known facts and follow the rules forward to a conclusion. In a decision tree, this is the walk from the top question down to a decision. | "More stocks streaked than luck gives, and the streak repeats on new days, so it may be a real pattern." |
| Inductive | Count over many examples in the data to make a link, or to learn how strong the link is. | "Out of 500 coin-flip stocks, about 15 went up 5 days in a row, so luck alone gives a streak about 3% of the time." |
| Abductive | Start from what was seen and walk the links backwards to the cause that best explains it. In the Bayesian network, this is the chance of each cause given what was seen. | "The stock streaked, and luck explains this better than a real pattern, because luck is far more common." |

A decision tree can also be read as a list of IF-THEN rules, one per path from the top to a decision. So a deductive step is "IF these answers, THEN this decision".

The Reasoning agent (Goal 1) already labels each answer as inductive, deductive or abductive. Later (step 5), the app can also find which nodes and links an answer used, and check whether the direction of the walk fits the label.

## 3. Steps

| Step | What | Status |
|---|---|---|
| 1 | This plan | Done 22 October 2026 |
| 2 | Decision trees: one rule-of-thumb tree per quant case, with a walk function (the deductive move) | Done 22 October 2026 |
| 3 | A Bayesian network per case, learned by counting over simulated data (the inductive move) and asked backwards (the abductive move) | Done 22 October 2026 |
| 4 | Knowledge graph from books: every node keeps its source and an exact quote, and code checks the quote is really in the reading | Done 22 October 2026 |
| 5 | Reasoning as traversal: map an answer onto the graph and check the reasoning label | Done 22 October 2026 |
| 6 | A Knowledge page that shows the three forms | Done 22 October 2026 |
| 7 | The Topic Builder agent drafts all three forms for any topic (links to Goal 2) | Next |

### What the networks learned (step 3, `app/pgm.py`)

Each network has 3 true or false nodes and learns its chances by counting over simulated data (20,000 stocks, 20,000 rules, 3,650 days of weather). The numbers below are what the networks give.

| Case | Question asked of the network | Move | Answer |
|---|---|---|---|
| Pattern or luck | How often does a stock with no pattern go up 5 days in a row? | Inductive | 3% |
| Pattern or luck | Chance the pattern is real, before seeing anything | Abductive | 2% |
| Pattern or luck | Chance it is real, after a 5-day streak | Abductive | 18% |
| Pattern or luck | Chance it is real, after the streak and a repeat in the next week | Abductive | 46% |
| Will it work again? | Chance a rule with no edge makes more than 15% on old data | Inductive | 7% |
| Will it work again? | Chance the rule is real, after a great old result | Abductive | 30% |
| Will it work again? | Chance it is real, after a great old result and a win on new data | Abductive | 45% |
| Will it work again? | Chance it is real, after a great old result and a loss on new data | Abductive | 4% |
| Moving together | Chance of many sunburns on any day | Inductive | 27% |
| Moving together | Chance of many sunburns when ice cream sales are high | Inductive | 47% |
| Moving together | Chance of many sunburns on a hot day, with or without high ice cream sales | Deductive | 69% |
| Moving together | Chance the day is hot, given high ice cream sales and many sunburns | Abductive | 93% |

The last case shows the hidden 3rd thing in numbers. Ice cream and sunburns move together, but once the weather is known, ice cream adds nothing.

### Where each piece of knowledge comes from (step 4)

Dr Ho has not named a quant textbook yet, so for now the "books" are 13 Wikipedia articles, fixed at one version each (for example Gambler's fallacy, Overfitting, Data dredging, Spurious relationship). Every node of the 3 quant graphs now has a source.

- **Book:** 25 nodes quote an article word for word. For example, the 3% streak node quotes Gambler's fallacy, "a run of five heads has a probability of 1/32 = 0.03125 (a little over 3%)". A script (`eval/check_quotes.py`) checks every quote against the live article, and all 25 were found on 22 October 2026.
- **Data:** 3 nodes are numbers counted by the simulations, such as "about 15 of 500 stocks streak by luck".
- **Heuristic:** 1 node (do not buy without a reason and a repeat) is a decision from the rain case's decision tree.
- **Case:** 1 node (no clear reason why rain would move a stock) comes from the case story itself.

For any other topic, the Topic Builder now gives a quote from its Wikipedia source (or the learner's reading or file) for each fact, and plain code keeps only quotes that are really in that text. In a first test on "Photosynthesis", 18 of 21 facts kept a checked quote, and the other 3 were shown as having no source.

### Reading an answer as moves on the graph (step 5, `app/traverse.py`)

The Reasoning agent, still in the same single AI call as the Assessor, now also names the steps of the learner's answer as moves between knowledge graph nodes, at most 4. Plain code then reads each step against the graph's links.

- A step that goes with a link is **forward**, and a step that goes against a link is **backward**. A step between two nodes with no link is a **jump**.
- **Inductive** is a forward step out of a counted result (a data node), or two or more nodes leading into the same node.
- **Deductive** is any other forward step.
- **Abductive** is a backward step, from what was seen back to what explains it.

So each answer now has two labels for its reasoning type: the agent's own judgement, and the one an algorithm reads from the graph. Where they differ is worth a look by a human marker.

A first test on Gemini (22 October 2026) used 6 sample answers. In 5 of them the steps landed on graph links, and there the two labels agreed 4 of 5 times for deductive, 4 of 5 for abductive and 3 of 5 for inductive. Two answers that reasoned from counted data ("15 of 500 stocks", "lots of random pairs") were read as inductive by the graph but only as deductive by the agent, and the graph reading looks arguably right. Jumps showed links the graphs are missing, such as from "many tries" to "a streak is not proof", so the reading also shows where a graph needs another link.

### The Knowledge page (step 6)

A new sidebar item, **Knowledge**, opens its own page, so the chat and its Status panel do not change. The learner picks a case (the 3 quant cases, plus any case on their own topic in the open chat) and sees three tabs.

- **From books:** the knowledge map. Tapping a box shows where it comes from, such as the exact Wikipedia quote with a link, a simulation, a rule of thumb or the case story.
- **Rules of thumb:** the expert's yes or no questions. The learner answers one at a time until a decision is reached, which also shows the idea it rests on.
- **From data:** the Bayesian network as a small picture, the chances it learned as bars, each marked inductive, deductive or abductive, and one sentence that sums them up.

For a learner's own topic, only "From books" has content until step 7. The graph moves from step 5 are not shown to learners yet, because they need checking against a human marker first.

## 4. Choices made

- **Plain Python, no new libraries.** The trees and networks are small (3 to 6 nodes), so exact counting and exact inference need little code. This keeps the free Render server light, and every step is easy to explain in the thesis. Libraries such as pgmpy and scikit-learn can check the results later.
- **Simulated data first.** The data for the Bayesian networks comes from seeded simulations like the ones the Tutor already runs (`app/tools.py`), so it matches the cases and gives the same result every time. Real market data or learner data can replace it later.
- **Drafts for Dr Ho.** Claude drafts the trees and networks, and Dr Ho checks them, the same as the Goal 1 knowledge graphs.

## 5. Questions for Dr Ho

1. Is a small Bayesian network the "probabilistic graph model" you meant, or did you have another model in mind, such as a Markov network?
2. Should the decision trees come from real experts, for example a short interview with a quant, or are drafted rules of thumb enough for now?
3. Which book should the quant knowledge graph come from, so each node can cite a page? Until then, Wikipedia is used (step 4).
4. Is "deductive is a forward walk, inductive is counting over data, abductive is a backward walk" a good first definition of reasoning as graph traversal?

## 6. Honest limits

- The trees and networks are drafts by Claude, and no expert has checked them yet.
- Simulated data shows the method, but it is not real market data.
- Mapping a free answer onto the graph (step 5) is the hardest part. It may need an AI call, so it may not be fully exact.
