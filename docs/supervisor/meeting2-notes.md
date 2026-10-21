# Meeting 2 with Dr Ho (19 October 2026)

Sources: the meeting recording (`docs/supervisor/Meeting2.txt`, made by Whisper, so some words and names are misheard), Dr Ho's handwritten page (`docs/supervisor/Critical Thinking.pdf`) and his written message after the meeting. Written by Claude on 20 October 2026. Anything marked **[unclear]** could not be read or heard well, so check it with Dr Ho.

## 1. The big picture: three goals

| Goal | What it means | When |
|---|---|---|
| **Goal 1: the product** | A finished tool that shows learners their attainment in critical reasoning in three dimensions: the **type of reasoning** (inductive, deductive, abductive), the **type of knowledge** they reasoned with (procedural, causal, relational and so on), and the **quality** of their reasoning (the Paul-Elder standards such as clarity and depth). This is the FYP, and Dr Ho will declare it to the Innovation Office for an exhibition. | Now. Dr Ho expects it around **mid November 2026**. |
| **Goal 2: it works on any topic** | Show the same tool works on another body of knowledge, so the topic must be easy to swap (an "insertion point"). | After Goal 1. |
| **Goal 3: the theory** | Represent knowledge properly: textbooks become knowledge graphs, human heuristics become decision trees, and data becomes probabilistic graph models. Reasoning is then an operation on the graph (a graph traversal), so it can be written as an algorithm. | Next semester. |

Dr Ho's plan for outputs: Goal 1 alone is the product for the exhibition. Goals 1 and 2 together become a paper. He will also use the tool in his classes with future UTP students.

## 2. The framework (Dr Ho's working model, not complete yet)

Dr Ho said this is his current thinking and it is not final. Where a link is not clear yet, he said to "put dots" (mark it as unknown) rather than force it.

### Layer A: Prerequisites, from Paul's 8 elements of thought

Purpose, question at issue (the problem) and information come **before** reasoning (a priori). Without them the learner cannot reason at all, so the tool should check them first. The other five elements are where reasoning starts.

| Element of thought | Role | Dr Ho's first guess at a link |
|---|---|---|
| Purpose | Prerequisite | Factual or declarative knowledge |
| Question at issue / problem | Prerequisite | Factual or declarative knowledge |
| Information | Prerequisite | |
| Interpretation and inference | Start of reasoning | Deductive (rule driven, factual and procedural knowledge) |
| Concepts | Reasoning | Inductive (patterns that carry meaning) |
| Assumptions | Reasoning | Counterfactual |
| Implications and consequences | Reasoning | [unclear], "put dots" |
| Point of view | Reasoning | [unclear], "put dots" |

### Layer B: Types of knowledge (what the learner reasons with)

From Dr Ho's message:

| Type | Core question | Example |
|---|---|---|
| Factual / declarative | What is true? | "The voltage is 5 V." |
| Conceptual | What does it mean? | Understanding what "voltage" represents |
| Procedural | How do I do it? | How to measure voltage with a multimeter |
| Causal | Why does it happen? | Increasing resistance reduces current |
| Relational / propositional | How are things connected? | Voltage, current and resistance obey Ohm's law |
| Strategic (derived) | What should I do, given the situation? | Which measurement should I make next? |
| Metacognitive (derived) | How do I know, and how reliable is my knowing? | "My conclusion depends on assuming the sensor is calibrated." |
| Epistemic | What is justified for me to believe? | "The evidence supports X, but doesn't establish X conclusively." |

- The first five are "knowing". Strategic, metacognitive and epistemic are "knowing that leads to doing", and they end in a decision or choice.
- Most types can be drawn as a graph. Procedural knowledge is a sequence (step 1, step 2, step 3), causal knowledge is arrows that mean "causes", and relational knowledge is arrows with different meanings ("creates", "heats up").
- The handwritten page also lists **dialectical** knowledge (an adversarial frame with thesis, antithesis and synthesis) and **experiential** knowledge. Where these fit is not decided.

### Layer C: Modes of reasoning (the operation on knowledge)

| Mode | Meaning | Quant example from the meeting |
|---|---|---|
| **Inductive** | Pattern driven. From observations to a general idea (new knowledge). | "It is not just CIMB. All Singapore banks and Malaysian banks fell, so it is the whole Southeast Asian financial sector." |
| **Deductive** | Rule driven. From known facts and rules to a specific conclusion. | "What causes this? Maybe the EPS numbers." |
| **Abductive** | Diagnostic. The best explanation from incomplete information. | "Something is happening that was not reported. What is the source?" |
| Analogic | Domain mapping. The same idea in a different field. | Electric current is like water flow and pressure. |
| Counterfactual | Boundary testing (elenchus). Finding a case where the general idea fails. | |
| Triangulation | Knowing 2, 3 or 4 facts that improve the knowledge of one. Dr Ho called it a Socratic tactic. | |

- **Causal is crossed out** on the page. Dr Ho said causal is a type of knowledge, not a type of reasoning, because you learn causes through induction.
- Focus first on the **top three: inductive, deductive and abductive.** The others are a bonus.
- Reasoning has two outputs: **new knowledge**, or **new choices and actions**.

### Layer D: Quality, from the Paul-Elder 9 intellectual standards

These are already built (clarity, accuracy, precision, relevance, depth, breadth, logic, significance, fairness). Each one is marked 1 or 0, with evidence. The new idea is to judge the quality **of each reasoning type**, for example "how clear and deep is this learner's inductive reasoning".

### Layer E: Complexity, from the SOLO taxonomy

This is the "structure of observed learning outcomes": prestructural, unistructural, multistructural, relational and extended abstract. Dr Ho suggested it could measure **how many types of knowledge the learner combines** in one piece of reasoning (the synthesis of knowledge). Combining more types means a more complex answer.

### Layer F: Statistics, from many trials

- Do not judge a skill from one question. Ask **5, 10 or 20 questions** per skill, and record a 1 or 0 for each element every time.
- Start with **Hamming distance**, a simple first measure. It counts how many places two strings of 1s and 0s differ.
- Then move to **factor analysis** (or another method Claude suggests) to show statistically that a learner has mastered a skill.

Paul's **6 levels of Socratic questioning** are also already built, and they stay as the question ladder.

Dr Ho's analogy from the meeting: the framework is a bit like a neural network. The prerequisites are the input layer, reasoning on knowledge is the hidden layer, and the quality is the output. The hard part is finding which connections are real, because not everything connects to everything.

## 3. What Dr Ho asked for in Goal 1

1. **Types of knowledge in the app.** Add a section where topic knowledge is entered with its type (factual, procedural, causal, relational and so on), ideally as a graph. Let an agent generate the body of knowledge and the knowledge graph for the quant topic ("agent does everything, you are the architect").
2. **Detect the reasoning type and the knowledge used.** For each answer, mark which reasoning type was shown and which knowledge types were used, as 1 or 0 with an evidence quote. Add **new agents** for this rather than rebuilding the current ones ("spin up additional agents", keep the system modular).
3. **An Explainer agent.** It explains in plain words, with a real scenario, why a reasoning type matters and where to use it with a given mix of knowledge types. Dr Ho suggested a pop-up with an example scenario, "why you need to know this".
4. **Many questions per skill.** Generate several questions for each reasoning type and knowledge type, so each learner gives enough 1s and 0s for the statistics.
5. **Statistics.** Hamming distance first, then factor analysis or a better method, run on the 1s and 0s.
6. **A dashboard.** Show attainment by reasoning type, knowledge type and quality. Dr Ho said even a message like "you have not mastered inductive reasoning on causal knowledge" is already very valuable, because it builds the learner's self-awareness.
7. **The rubric is a placeholder.** Copy the Paul-Elder descriptions and let the AI say "present or not, and what is the evidence". The AI agents stand in for human experts for now. Dr Ho plans to send the framework to a pedagogy expert, Dr Chong Suli **[name unclear in the recording]**, to improve it later.

## 4. Advice for the thesis and the proposal defence

- Add a **diagram of all the agents** and the flow between them (which agent runs after which), plus what information is passed between agents (the interfaces). Mentioning MCP is optional.
- Show **how each agent is prompted**, both to assess and to generate questions. Build prompts in a systematic way, from a template with context, instruction, background knowledge and rules.
- **Make the presentation easy to follow** for examiners outside the field. Test it on friends who do not know agentic AI. The take-home message is that this is a new way of building software (many prompted agents working together), and that the design took real thought.
- Prepare **1 or 2 slides** that pitch it as a product.
- **Mock presentation around mid November 2026.** Send the slides to Dr Ho early for feedback.

## 5. Reminders

- **Remind Dr Ho to submit the requests for a Claude subscription and a Render subscription** (about USD 25 a month was mentioned for Render **[check the amount]**). He asked to be reminded and said approval may come late, so keep using the free tiers until then. Dr Ho said the move to a "real prototype" is planned for December onwards.
- Product declaration to the Innovation Office, for the next exhibition or competition.

## 6. FYP rules that matter now (from `docs/utp-rules/FYP Guidelines 2024.pdf` and the interim report template)

**Interim report structure (guidelines, section 6.1):** title page, abstract, Chapter 1 Introduction (background, problem statement, objectives and scope), Chapter 2 Literature Review, Chapter 3 Methodology, **Chapter 4 Conclusion and Future Work**, references and appendices. The template file shows 5 chapters, with Results and Discussion as Chapter 4, so ask Dr Ho which layout he wants.

**Format:** at most **20 pages**, not counting the appendices. Times New Roman 12 with 1.5 line spacing. The left margin is 4 cm and the other margins are 2.5 cm (the first page of each chapter has a 5 cm top margin). No more than 3 levels of numbered headings. APA or IEEE references, passive voice, and plain wording.

**FYP 1 marks:**

| Part | Supervisor | Examiners |
|---|---|---|
| Progress assessment 1 | 10% | |
| Proposal defence | 10% | 20% |
| Progress assessment 2 | 10% | |
| Interim report | 20% | 30% |

**Interim report marking (Form 08), with weights:** literature review and critical analysis **x4** (the biggest), background and problem statement x2, objectives x2, quality of references x2, methodology and project activities x2, abstract x1, scope x1, project milestones and timeline x1, plus the conclusion and future work. Part B covers the format, English and referencing.

**What `docs/thesis/FYP1.docx` is still missing (checked 20 October 2026):**
- an abstract
- Chapter 4, Conclusion and Future Work. "Testing and Results" is not a numbered chapter yet.
- a project timeline, such as a Gantt chart, for FYP 1 and FYP 2 (it carries marks)
- the agent flow diagram Dr Ho asked for
- the new framework (types of knowledge and modes of reasoning), in the objectives, scope, literature review and methodology
- a page check. The draft is about 7,800 words including the appendix prompts, so the main text may be close to the 20-page limit.

## 7. Claude's honest notes on the plan

- **Factor analysis needs many learners.** One learner's answers cannot give a factor analysis. It looks for patterns across many people (rules of thumb ask for at least 5 to 10 learners per item, and Dr Ho's grant plans 50 undergraduates). So a sensible split is: for **one learner**, show the share of 1s per skill with a simple confidence band (or a Bayesian estimate), and for **the whole class**, run factor analysis once enough sessions are collected. This needs Dr Ho's agreement.
- **Hamming distance** compares two strings of 1s and 0s, for example a learner's pattern against a "mastered" pattern, or two attempts by the same learner. It is easy to build and easy to explain.
- **Model calls.** More agents means more AI calls per turn, and the free Gemini quota is limited (the app's daily budget is 400 calls). A good design runs the new Reasoning agent in the same call as the Assessor, or only on some turns.

## 8. Suggested order for Goal 1 (the student decides before anything is built)

1. **Knowledge layer:** tag each case note with its knowledge type, and let an agent draft a small knowledge graph per case (a DRAFT for Dr Ho to check). **Done 21 October 2026** in `app/knowledge.py`, drafted by Claude: about 10 nodes per case (the 5 case notes plus extra nodes), 8 knowledge types and 7 link types. Dr Ho still needs to check it. An agent that writes the graph for any new topic is left for Goal 2.
2. **Reasoning agent:** for each answer, mark 1 or 0 for inductive, deductive and abductive reasoning and for the knowledge types used, with evidence. **Done 21 October 2026** in `app/reasoning.py`. It shares the Assessor's model call (no extra quota) and saves `assessment.reasoning` with `types`, `knowledge` and `evidence`. It can be switched off with `AGENT_REASONING=0`, and `ASSESSOR_VERSION` is now 2026-10-21. A first check on 3 answers with Gemini looked sensible ("idk" gave all 0, a counting answer gave deductive, and a hidden-news answer gave abductive), but it has not been checked against human markers yet.
3. **Dashboard:** a grid of reasoning type by knowledge type, plus the quality standards, in the Status panel.
4. **Question bank:** several questions per skill, so there are enough trials.
5. **Statistics:** Hamming distance first, then a per-learner mastery estimate, then factor analysis across learners.
6. **Explainer agent:** a "why this matters" pop-up with a scenario.
