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
