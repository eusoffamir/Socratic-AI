# Messages from Dr Ho Tatt Wei (Ts Dr, FoE, UTP)

Kept so every session knows what the supervisor asked for. Newest at the bottom.

## 15 September 2026, 3:39 pm: literature for the review

Dr Ho gave these as the literature review material for the project.

**DeepLearning.AI short courses** (titles taken from the links, not checked on the site):

1. Agentic Knowledge Graph Construction: https://learn.deeplearning.ai/courses/agentic-knowledge-graph-construction/information
2. Long-Term Agentic Memory with LangGraph: https://learn.deeplearning.ai/courses/long-term-agentic-memory-with-langgraph/information
3. Retrieval Augmented Generation: https://learn.deeplearning.ai/courses/retrieval-augmented-generation/information
4. Building and Evaluating Advanced RAG: https://learn.deeplearning.ai/courses/building-evaluating-advanced-rag/information
5. Knowledge Graphs for RAG: https://learn.deeplearning.ai/courses/knowledge-graphs-rag/information
6. Building Agentic RAG with LlamaIndex: https://learn.deeplearning.ai/courses/building-agentic-rag-with-llamaindex/information

**Dr Ho's own course slides** (in this folder, never on GitHub because they are copyright "INSTITUTE OF TECHNOLOGY PETRONAS SDN BHD, all rights reserved"):

- `2025_FoundnModnDNN_Vitrox_CAPE_Module7 (1) (1).pdf`: *Foundations of Modern Deep Neural Networks*, Module 7, **Foundation Models and Generative AI** (73 slides). Generative models and GANs, cycle consistency, prompts as latent vectors, foundation models (CLIP, DINO, SAM), transfer learning versus prompting, hard and soft prompts, prompt tuning, PEFT, transformers and GPT-2, DeepSeek, developing and pretraining an LLM, reinforcement learning (as used in DeepSeek R1).
- `2025_FoundnModnDNN_Vitrox_CAPE_Module8 (1) (1).pdf`: same course, Module 8, **Towards Agentic AI** (32 slides). What an agentic system is, prompts (instruction plus context), Chain of Thought, self-consistency, XoT, context windows, RAG and improved RAG patterns, ReAct, vibe coding, the agentic AI stack, Model Context Protocol (MCP), multi-agent systems with A2A and MCP, MetaGPT, AgileCoder.

Notes for the thesis:
- Sections 2.2 to 2.4 of `docs/thesis/FYP1.docx` follow Module 8 (and the PEFT part of Module 7) closely. Cite the modules, for example: Ho, T. W. (2025). *Foundations of Modern Deep Neural Networks, Module 8: Towards Agentic AI* [Course slides]. Centre for Advanced and Professional Education, Universiti Teknologi PETRONAS. **[CHECK the exact title and year with Dr Ho.]**
- If any thesis figures were copied from these slides, they need a source line under the figure, and the FYP guidelines (section 6.2 h) ask for permission from the rights holder, so ask Dr Ho.

## 17 September 2026, 6:52 am: reply about the Gemini Gem video

Eusoff sent Dr Ho a YouTube video about a Socratic tutor made with Gemini Gems (https://youtu.be/27UCLMBqWGo) and asked if it matched the project. Dr Ho replied (lightly cleaned up for typos):

> Hi Eusoff, good find! Gemini Gems as described does partially what the project aims for. You may review it as lit review and use the prompts as a starting point. Also look for other similar tools by other AI providers and contrast them.
>
> You may also try a Gemini Gem prompted as a starting point for teaching agentic quant, and evaluate how it does.
>
> It doesn't yet do a few things which we want to achieve. There needs to be a principled way to guide the questioning so the student moves up the critical thinking competency ladder. Right now the prompt for the Socratic tutor is a good start, but its questions just lead toward an answer and do not encourage the student to ask deeper, such as "is this the right question?"
>
> Also we want the Socratic tutor to evaluate the student's attainment in critical thinking based on a framework and the conversation.
>
> I hope this clarifies? The potential innovation is in the prompts designed to guide the AI.

What came from this: the two Gemini Gem tests (Test #1 and Test #2 in the thesis), the six-level question ladder ending in "question the question", the separate Assessor against the Paul-Elder framework, and the comparison table of other tools (Section 2.7).

## 28 October 2026: feedback on the proposal defence

Sent after the defence (slot 2.20 pm). Dr Ho's words, unchanged:

> Hi Eusoff, some feedback on your presentation. Good opening but maybe tone it down "no one is thinking critically"...for problem statement, consider giving some illustrative example that the audience can connect with... Objective is incorrect. you have to fully flesh out your project objectives - don't have to anchor on fyp project objectives... three verbs on objectives is not good, be more specific, full sentences
>
> scope of study is a bit scattered ... you have mixed methodology with scope.... objectives is the big picture, no methods inside, must be able to answer was it achieved or not. Scope is a limitation ( you claim you achieved obj 1 under specific limitations or constraints which is the scope).
>
> Literature review is not effective as a table. you need to think of a better way to visualize the literature. The agentic elements. Your narrative style of presenting for literature review is effective though
>
> The research gap is clear... the tool justification should be in methodology
>
> your success measures for the tool R1-R9 is good!
>
> the 6 socratic questions and 9 intellectual standards, types of reasoning and types of knowledge not clearly explained... hence a lot of questions raised because audience not able to understand what you are measuring, what is being achieved... you might need to spend more time during literature review talking/describing critical thinking
>
> lets chat a bit more about non engineering domain questions... i have more to share
>
> don't worry you did very well, but it is my practice to be more critical of good students so you get good feedback to improve
>
> marks wise you shouldn't worry, but take the feedback as points for further improvement during presentation

What to change (for the interim report, Chapter 1 to 3, and later talks):
1. Opening, softer claim. Not "no one is thinking critically".
2. Problem statement, add one example the audience can relate to.
3. Objectives, rewrite fully in our own words, not anchored on the FYP listing. Full, specific sentences, no "Teach, Assess, Adapt" verb labels, no methods inside, and each one must be checkable as achieved or not.
4. Scope, rewrite as the limits and conditions under which the objectives are claimed (topic, users, model, time). Move method content out.
5. Literature review, replace the tutor comparison table with a better picture, focused on the agentic elements. Keep the narrative style.
6. Tool justification (the "Justification" half of the research gap slide) moves to Methodology.
7. Keep R1 to R9 as the success measures (Dr Ho liked them).
8. Explain critical thinking much more in the literature review, meaning the 6 Socratic question types, the 9 standards, the reasoning types and the knowledge types, each with a plain example, so the audience knows what is measured.
9. Ask Dr Ho about the non-engineering domain questions (he has more to share).

### Talk with Dr Ho after the feedback (28 October 2026, from Eusoff's account)

- Critical thinking. Eusoff held back on explaining it because he did not fully understand it yet. Dr Ho said to push credibility and not be scared, because Paul and Elder is a framework with a very strong background.
- Say "we", not "I". This is a project of Eusoff and Dr Ho together, since Dr Ho is the supervisor. Dr Ho said Eusoff has integrity.
- The knowledge graph is "amazing". Next, the arrows must have clear meaning, showing how the pieces link. Dr Ho linked this to machines that make errors and go back along the links to fix them ("self heal"), and to knowledge that comes from a person with 25 years of experience, with the arrows showing the relationships. Eusoff did not fully follow this part yet, so ask Dr Ho to explain it again.
- Dr Ho said this could become a startup and set Eusoff up for a masters.
- He wants to see the knowledge graph together with inductive and deductive reasoning, and to see each knowledge type (conceptual, factual, causal, epistemic, relational, procedural, strategic) on its own graph.
- Self heal, made clear by Eusoff. Dr Ho meant self-healing machine lines in industry, where a production line finds the cause of a fault and fixes or works around it with little human help. An expert's knowledge graph with meaningful arrows is what lets a system walk back from a fault to its cause (abductive) and then forward to the fix (deductive).
- Note. `app/knowledge.py` already has all 7 of these types plus "metacognitive" (8 in all), and 7 arrow meanings (causes, then, defines, supports, weakens, tests, leads to). Metacognitive stays (Eusoff and Claude, 28 October 2026), because thinking about your own thinking is central to Paul and Elder, and the top level of the ladder, question the question, is a metacognitive move. Tell Dr Ho.
