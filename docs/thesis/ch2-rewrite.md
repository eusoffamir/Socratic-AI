# Chapter 2 rewrite in Eusoff's own words

Eusoff explains each point casually, Claude only fixes grammar and adds citations. When all 14 paragraphs are done, they replace Chapter 2 in `Interim-Report.docx` as tracked changes.

## 2.1, paragraph 1 (done)

To get good answers from an AI, it has to be guided with information, references and examples, because it does not fully know what we want and will otherwise guess (Ho, 2025a, 2025b). It is like guiding a new staff member, where we tell them exactly what we want and how to do it. With Chain of Thought prompting, the AI does not solve a complex task right away. It breaks the task down into steps and solves them one by one, so that each step is done properly before it reaches a conclusion (Wei et al., 2022). ReAct goes further, because the AI can call a tool to do a task, get back the result and compare it with what it already has before it answers (Yao et al., 2023).

## 2.1, paragraph 2 (done)

To stop the AI from making up facts, it can first look up verified information, such as proper websites, articles and surveys, and compare its answer with that evidence instead of guessing. This is called Retrieval Augmented Generation (RAG) (Lewis et al., 2020; Gao et al., 2023). The Model Context Protocol (MCP) works like a standard plug, so the same tools and data can be used by many different AI models (Anthropic, 2024). Multi-agent systems such as MetaGPT and AgileCoder split a big job between several AI workers (Hong et al., 2024; Nguyen et al., 2024). Each worker can focus on its own task, and the work is put together at the end, so each part is done in more detail than if one worker did everything. However, these systems were tested on writing code, where the output is either right or wrong, like a maths answer. The output of a tutor is more subjective, like an essay, which a teacher has to read and judge. So it is still not proven that teams of agents make better tutors.

## 2.1, paragraph 3 (done)

Brand (2026) warns that not every task needs an AI agent, because fixed and predictable jobs may be better done by plain automation. This project follows that advice. An AI does not give the same answer twice, so it should not decide fixed things. The learner chooses how long the session runs, and plain code makes sure that choice is kept, because it is the learner's decision and not the AI's. AI is used where judgement is needed, such as writing the questions, while simple rules handle fixed checks, such as the copy check. Figure 1 shows each idea and the part of this project where it is used.
