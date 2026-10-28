# What is our actual goal? (checked 20 October 2026)

Sources compared: Dr Ho's grant proposal, the official FYP project listing, Meeting 2 (19 October 2026) and Dr Ho's feedback on the slides (20 October 2026, 5:27 pm).

## 1. The official FYP project listing (26S005)

- **Title:** Agentic AI for Fostering Critical Thinking Education. Supervisor: Ts Dr Ho Tatt Wei. Cluster: Intelligent Signal and Imaging. Difficulty 4. Linked to the grant SoTL 015LF0-098.
- **Description:** explore prompt engineering and advanced retrieval augmented generation of agentic LLMs to engage and assess critical thinking in learners.
- **Problem:** critical thinking must be strengthened now that LLMs can do much of the analysis and software work, so students need an agentic AI tool to build their competency in complex decision making and design thinking.
- **Objectives:** (1) develop an agentic AI to interactively teach undergraduates (the listing says "about deployment of AI agents"; Dr Ho later set the topic to quant); (2) develop a methodology to guide agentic AI to **assess** critical thinking skills; (3) develop a methodology to guide agentic AI to **adapt** to the learner's gaps and customise the learning experience.
- **Deliverables:** (1) an agentic LLM, prompted and given a RAG knowledge graph; (2) an agentic workflow that interacts with the learner and customises the difficulty of the Socratic questions; (3) an agentic workflow that assesses the learner's critical thinking attainment.
- **Tools:** Claude AI, an agentic workflow with LangGraph.

## 2. The grant proposal (the parent project)

- **The grant's two objectives:** (1) build a valid instrument that measures reasoning from Socratic dialogue transcripts; (2) test whether an adaptive Socratic chatbot improves analytical and inductive reasoning.
- **The FYP's part:** the adaptive Socratic chatbot (grant Milestone 1) and the first automated assessor (Milestone 2). The psychometric validation, the factor analysis on 50 to 100 students and the pre/post study belong to the grant's later phases.

## 3. So the actual goal is

> **A Socratic AI tutor that develops a learner's critical thinking, measures it against a framework, and adapts to the learner's gaps.**

It has three parts: teach (the question ladder), assess (the framework scores) and adapt (support and difficulty). This matches the three objectives and three deliverables in the official listing, and Goal 1 from Meeting 2 (show attainment by reasoning type, knowledge type and quality). Quant is only the first topic, and the framework is meant to work for any topic.

## 4. Dr Ho's feedback on 20 October 2026

- "Problem statement is not clear enough."
- "Too many objectives, try to aim at 3, some can be combined."
- "For objectives try to focus on the desired end state or outcome, not descriptions of capability or tasks."
- "Evaluating the prototype is a task, not objective."

## 5. New problem statement (used in the slides, the script and the thesis)

Updated on 20 October 2026 (evening) so that it starts from the official listing in section 1, which the student set as the baseline.

> Generative AI can now do much of the analysis and software work that engineers used to do, so engineering undergraduates need strong critical thinking for complex decisions and design, and they must use AI well instead of handing their thinking to it. Socratic AI tutors such as Gemini Gems already refuse to give answers, but they have three gaps. Their questions do not climb a clear ladder toward deeper thinking, they do not measure the learner's critical thinking against any framework, and they do not adapt to what each learner is missing. So there is a need for an agentic AI tool that helps engineering undergraduates build their critical thinking.

Other alignments with the listing made at the same time: RAG with a knowledge graph is "planned for FYP2" (a listed deliverable), not "future work"; the tools say Claude AI is supported and the free Gemini tier is used for now; the quant topic is marked as set by the supervisor.

## 6. Objectives (rewritten 28 October 2026 after the defence)

Dr Ho's defence feedback: objectives in our own words (not anchored on the FYP listing), full and specific sentences, no "Teach, Assess, Adapt" verb labels, no methods inside, and each must be judged as achieved or not in this project.

1. Undergraduates who are new to a body of knowledge reach higher levels of Paul's six levels of Socratic questioning during a session with the tutor, without the tutor giving them the answer.
2. The tutor's marks of each learner's critical thinking, on Paul and Elder's nine intellectual standards and on the type of reasoning and knowledge the learner used, agree with the marks of human markers.
3. Each learner gets questions and hints that match the gaps in their critical thinking, and can see which reasoning and knowledge skills they have mastered and which still need work.

Scope (the limits of the claim, no methods). Learners are beginner undergraduates at UTP, in short English text chats. Knowledge is any body of knowledge given as text, tested on a few topics from different fields; quant, set by Dr Ho, is the first worked topic and the only one checked by hand. Critical thinking is as defined by Paul and Elder, measured only inside the sessions. Outside the scope are long-term change in thinking and a full class study (later grant phases). The free model and time limits go in Limitations.

Previous version (20 October 2026) had "Teach", "Assess" and "Adapt" labels. The old objective "evaluate the prototype against the baseline tutors" is now part of the methodology (the evaluation plan), because Dr Ho said it is a task, not an objective.

## 7. How each objective is checked (methodology, not objectives)

| Objective | Evidence of success |
|---|---|
| 1. Teach | Learners move up the levels during sessions; the tutor never gives the answer; design requirements R1 to R9 are met, compared with the baseline Gem tutors |
| 2. Assess | Agreement with human markers on the 61-answer test set (percent agreement and Cohen's kappa per standard; the grant's target is 0.8) |
| 3. Adapt | Frustrated or weak learners get easier questions and hints, strong learners move up; the dashboard shows each learner's attainment; a short learner questionnaire (after ethics approval) |
