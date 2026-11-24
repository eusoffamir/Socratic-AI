# Meeting 3 with Dr Ho (24 November 2026)

Source: the meeting recording (private, made by Whisper, so many words are misheard). Written by Claude on 25 November 2026. This is the public version; industry partners are described in general terms, and the full notes are kept private (`meeting3-notes-full.md`, git-ignored, with a copy in Eusoff's Drive). Anything marked **[unclear]** could not be heard well, so check it with Dr Ho.

## 1. In short

- Dr Ho was very happy with the tool. He did not know how much was built. He called the automatic knowledge graph "a third innovation" and said the tool is already a knowledge ingestion and reasoning system. It now needs an **application** (a real use case).
- Reasoning is narrowed to a subset of critical thinking, **inductive, deductive and abductive** reasoning.
- Two outputs, each a paper.
  1. **Main, the industrial use case** (paper plus product). Inspection of electrical equipment in hazardous areas for an oil and gas partner. Target **end of January 2027**.
  2. **Backup, the teaching study** (paper only). A class experiment with a control group. Target to have the tool ready **January 2027**.
- While Dr Ho sets up access, Eusoff writes a **review of knowledge graph generation algorithms** (it goes into the thesis) and studies **probabilistic graphical models** (the Koller and Friedman book).

## 2. Turning the project into a product and a paper

Dr Ho's worry is how to turn the prototype into two separate things, a product and a paper. The prototype is there. The work now is at the application level.

### 2.1 Industrial use cases Dr Ho listed

| # | Use case | Notes from the meeting |
|---|---|---|
| 1 | **Plasma system** (high voltage, about 10 kV **[unclear]**, ionised gas, pinch) | Dr Ho's personal interest. Very niche, hard physics. The knowledge graph would be anchored with differential equations plus data. |
| 2 | **Semiconductor equipment** | Dr Ho can give a data sheet. The "information of concern" must be found or created first. |
| 3 | **Manufacturing equipment** (vision inspection, PCB) | Slow, needs more discussion with the partner team. |
| 4 | **Ex equipment inspection (oil and gas)** | Electrical equipment on gas facilities must be isolated so it cannot spark and explode ("Ex" equipment). Engineers inspect it with many images. Dr Ho expects images from the partner within about 2 months. |
| 5 | **Another oil and gas agentic system** (asset readiness, many databases) | Problem comes only at the end of December. |
| 6 | **Robotics lab** | Mentioned only. |

**Decision.** Use case 4, **Ex equipment inspection**, because it is the fastest to start. Eusoff's FYP is about 6 months, so speed matters more than size. Dr Ho can ask the partner engineer directly. Image classification is not Eusoff's job; focus on the knowledge graph and reasoning (deductive, inductive, abductive).

What the diagnosis could look like, in Dr Ho's words. Not only "these items are missing", but **prioritising by safety impact**. For example, link the containers or tanks to the single line diagram, then rank which items are more or less hazardous by their chance of sparking. This needs one knowledge graph on what causes the damage, one on the actual infrastructure, and a link between them.

For the FYP, it is enough to state the problem and the impact clearly, so examiners understand the purpose. Beyond the FYP, aim for a pitch.

### 2.2 Teaching study (backup paper)

- Design. Test students first. One group reads the material for one hour, the other group uses the tool tuned to the same material. Both take a test after. Balance their background levels. Use a statistical test to show the tool group scores significantly higher. This is evidence for the grant and a pedagogy paper.
- Where to get students. Foundation students from January 2027, foundation physics, students going for internship, or Dr Ho's master students in Intro to AI. **Pick one.** The choice depends on the topic.
- Dr Ho has training slides for an "IML" course **[unclear]**. Think about how to load such slides into the tool so it surfaces deeper reasoning, not just summaries.

## 3. What Dr Ho saw in the tool

- The Topic Builder already asks Gemini to build a knowledge graph from the material, then uses that graph to make the cases. Dr Ho said this unblocks his next phase, because he was stuck on how to build the graph.
- Reasoning can proceed as a **walk on the graph**, so the graph is the artifact. Diagnosis should be based on the graph, not the PDF.
- There is no single right way to build a knowledge graph. It depends on which concepts you want to surface.
- **Token limit is the bottleneck.** A new topic runs four agents at once, about 6,000 tokens, mostly from the Wikipedia grounding. Eusoff explained the free fallback chain (Gemini models, then Groq models).

## 4. Technical tasks

1. **Azure tokens.** In the next few days Dr Ho expects Azure ML access through UTP (he is sending the costing). He will give Eusoff access. Test the agents on Azure. Do not redesign everything, just switch the model calls (the low hanging fruit).
2. **Review of knowledge graph generation algorithms** (the main task while waiting). For each algorithm give the name, the brief approach, pros and cons, and above all **how it decides the nodes and the edges** (which concepts become nodes, how many nodes, and how relations are chosen). Use AI to help. This goes into the thesis. Then discuss with Dr Ho.
3. **Refine the knowledge graph prompt** so it uses a chosen generation method and surfaces specific dimensions.
4. **Find out how the graph is stored** (its data structure). It must be a hard artifact passed in at retrieval time, not something that only stays in the chat context.
5. **Standardise the classes of relations**, and find which ones are useful for debugging. The inspection use case will show this.
6. **Probabilistic graphical models.** Read Koller and Friedman, *Probabilistic Graphical Models* (2009), with AI help. It is in `docs/supervisor/materials/`, and the library may have a copy. The idea is not to copy it, but to find the best way to present relationships in data to a reasoning machine.
7. **Fuse three kinds of graph** into one reasoning graph (this matches Goal 3).
   - a knowledge graph of concepts (from textbooks and standards),
   - decision trees from engineer heuristics ("gut feeling" is aggregated pattern matching),
   - a probabilistic graph from data (conditioning and joint distributions, counting frequencies).
8. **Try a small probabilistic graph on an open source dataset**, as a proof of concept. Dr Ho called this "another feather" for the system.
9. Later, edges could carry numbers, vectors or differential equations, so rates can be compared. A vector-database style compression of the graph can come after the use case is proven.

Eusoff's idea. Choose the graph-building algorithm adaptively from the input and justify the choice. Dr Ho said he does not know the answer. It is a hard problem (which concepts, which relations, which numbers), and only real problems with real data will show which method works. So the algorithm review comes first.

## 5. The value proposition (why go deep)

- **Not Obsidian-style lookup.** Tools that just walk a graph to fetch an answer that is already in it are too shallow.
- **The target is complex reasoning, such as root cause analysis.** The answer is not in any textbook or in the graph. The graph gives the factors that govern the decision (the five or ten things that could cause the problem and how they relate). The model then reasons over the data with those factors to find the cause.
- **Explainable and traceable.** The knowledge base is explicit and checkable by humans. The model can output a chain-of-thought graph showing which factors it used, and that graph is the evidence for the decision.
- **Use agents only where an algorithm cannot do the job.** Anything that can be written as a fixed algorithm should be. Language models are worth their slow inference only for reasoning that cannot be written as an algorithm.
- Dr Ho is not sure a knowledge graph is the best representation, but it is the most general one he knows. Vector databases are linear. Graphs allow branching, many graphs, fusion and loops.
- **Business case.** Diagnosis and troubleshooting are common in most industries, and the bottleneck is the few most talented engineers. Offer it as a service, or as one-time infrastructure plus a subscription to build the client's own graph (the "secret sauce"). Value comes from someone sitting with the engineers, formulating the problem, building the graph, and letting the system see the long chain. Example, a medical plate manufacturer with about 10 process steps and unexplained failures.

## 6. Action list

- [ ] Write the review of knowledge graph generation algorithms (how nodes and edges are chosen), then discuss with Dr Ho.
- [ ] Read Koller and Friedman on probabilistic graphical models; try a small model on an open source dataset.
- [ ] Find and document how the tool's knowledge graph is stored and passed to the agents.
- [ ] When Azure access arrives, switch the agents to Azure models and test.
- [ ] Wait for the Ex inspection images and problem details (about 2 months), then build the use case.
- [ ] Pick one cohort for the teaching study and plan the January 2027 experiment.

## 7. Claude's honest notes

- **Scope risk.** The FYP now has the Goal 1 product, Goal 2, Goal 3, an industrial use case, a teaching study and all before about April 2027. The industrial case depends on partner images that may take 2 months. Keep the teaching study ready as the safe path for the report.
- **The teaching study needs ethics approval** at most universities before testing students. Ask Dr Ho how UTP handles this, early.
- **The knowledge graph today is drafted by Gemini from Wikipedia.** It is good for a demo, but the algorithm review should say clearly what the current method is and where it falls short (no standard relation classes, size not controlled, no numbers on edges).
- Many names were misheard by Whisper. Confirm them with Dr Ho before writing them anywhere official.
