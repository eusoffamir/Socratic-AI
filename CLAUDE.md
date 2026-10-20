# CLAUDE.md: Socratic AI (FYP project 26S005)

Read this first. It is the short version. The full history of what was built, fixed and found (dated notes, audits, real session findings, evaluation runs) is in `docs/project-history.md`. Open the matching section there only when a task needs that detail.

## About the student and how to write for them

- Student: **Muhammad Eusoff Amir bin Hazri, student ID 22010491**, goes by Eusoff. Course **EFB4042** (Final Year Project I), UTP. Use the full name, ID and course code on the title page, slides and forms.
- Project: "Agentic AI for Fostering Critical Thinking Education", code **26S005**, supervisor Dr Ho Tatt Wei. Difficulty level 4, RTG project.
- **Writing style for anything student-facing or thesis text: easy English, short and straightforward sentences. Do not use the double dash sign ("--") or em dashes.**
- The student has **no money for APIs**. Default to free options (Gemini free tier, mock mode, local tools). Do not suggest paid services as the main path.
- The student feels lost easily when many things change at once. Work one step at a time, explain what you did in plain words, and do not add large new features without asking.
- Be honest about uncertainty. Mark anything unverified clearly. Never invent citations.

## Two laptops: keep everything in sync (IMPORTANT)

The student works on **two laptops**, each with its own copy of this folder and its own VS Code and Claude chats. GitHub (`eusoffamir/Socratic-AI`) is the only link between them, so nothing may be left only on one laptop.

- **Start of every chat:** run `git pull` before changing anything. If it fails or shows a conflict, stop and explain it in plain words before doing anything else.
- **After every finished, tested change:** commit and `git push` straight away, without asking. Say in the reply that it was pushed, because a push also redeploys the live app on Render. Plain push only, never force push.
- **Project knowledge goes in this file or `docs/project-history.md`**, not only in Claude's memory folder, because the memory folder stays on one laptop.
- **Not synced by Git, so set up by hand on each laptop:** `.env` (keys, never upload it), `.claude/settings.local.json` (the rules `PowerShell(git push)` and `Bash(git push)`), `docs/supervisor/2026_EdEx SoTL Grant Proposal (1).docx` (Dr Ho's private file), and Dr Ho's Module 7 and 8 PDFs (copyright, blocked by `.gitignore`). Learner data is in Supabase, so it is shared by both laptops and the live app.
- If `git` is not found, VS Code needs a full restart. Until then use `& "C:\Program Files\Git\cmd\git.exe"`.

## What the project is

An app that makes students think for themselves instead of handing them answers, and then tests whether it works. It is NOT an answer machine like ChatGPT, Gemini or Claude.

- The Tutor asks Socratic questions up Paul's 6 levels: clarify, assumptions, evidence, viewpoints, implications, question the question.
- The Assessor scores each answer on Paul and Elder's 9 intellectual standards (clarity, accuracy, precision, relevance, depth, breadth, logic, significance, fairness), plus which of the 6 moves the learner showed.
- The app has a clear mission, fixed rounds, feedback every turn, varied question formats and a stats view.
- **Our actual goal** (see `docs/supervisor/actual-goal.md`): a Socratic AI tutor that develops a learner's critical thinking, measures it against a framework, and adapts to the learner's gaps (teach, assess, adapt). It has 3 objectives written as end states.

Topic (quant only, Dr Ho's instruction): *how quants find predictable patterns using data, for beginners, avoiding complex machine learning.* There are 3 cases in `app/content.py`. Target learners are university students new to quant, and the early testers are Dr Ho's students.

### How text in the app must read

- Tutor tone: calm and helpful, like Jarvis in films. No slang, no emoji, no exclamation marks (one exception, "Congratulations! You reached ..."), and no fake "cool" talk.
- Keep every piece of text short: UI labels, buttons, errors and Tutor replies (word limits in `prompts.WORD_LIMITS`).
- Write smooth sentences joined with "because", "so", "and" or "but". Never the clipped "A car. It is red." style, and never join sentence parts with a colon. Example: "Each flip is still 50%, because a coin has no memory." not "Each flip = 50%. No memory."
- Keep the numbers (the student is visual), but inside sentences, not with symbols like →, = or ≠ (chart titles may use them). **Chances are always percentages, never fractions.**

## Parent project and supervisor

- The FYP sits under Dr Ho's SoTL grant: "Elevating Critical Reasoning in AI-empowered Learners...". It plans an adaptive Socratic chatbot, an LLM transcript assessor (Cohen's kappa of at least 0.8 against human raters), Bloom levels up to 4 (analytical) and 5 (inductive), and a rubric from Paul-Elder plus Paul's 6 levels. Its study plan: a pilot with 5 to 10 MSc students, 50 undergraduates for rubric validation, then 50 to 100 undergraduates, with UPSI ethics approval. The free tier cannot run a whole class, so the real study needs a paid key from the grant.
- Dr Ho's messages: `docs/supervisor/dr-ho-messages.md`. Key points: Gemini Gems partly do this already, so use them in the literature review; the gaps are no principled way up a critical thinking ladder and no evaluation against a framework; the innovation is in the prompts. Literature sources are six DeepLearning.AI courses plus his CAPE Modules 7 and 8 (thesis sections 2.2 to 2.4 follow Module 8).
- **Meeting 2 (19 October 2026), the new direction.** Read `docs/supervisor/meeting2-notes.md` before any Goal 1 work. Goal 1 (by mid November 2026) is a tool that shows attainment in three dimensions: type of reasoning (inductive, deductive, abductive first), type of knowledge (factual, conceptual, procedural, causal, relational and more), and quality (the 9 standards, already built). Build **new agents** (a Reasoning agent marking reasoning type and knowledge as 1/0 with evidence, and an Explainer agent), several questions per skill, statistics and a dashboard. Goal 2 is another topic, and Goal 3 (next semester) is knowledge graphs. **Ask the student before building, because the step order in section 8 is not decided.** Each new agent costs free Gemini calls.
- Early testing in September 2026 (Test #1 an online gem, Test #2 our own Prompt v1) showed lost context, repeated "what do you mean", no feedback and no end. The app fixes these.

## Architecture (built)

Design idea for the thesis: **agents decide, rules guard.** Each turn in `app/graph.py` (LangGraph) runs assess, plan, guard, tutor (may run a tool), check, rewrite once if needed, finish.

- **Agents** (prompts in `app/prompts.py`, calls in `app/llm_client.py`): Assessor, Planner, Tutor, Checker (free code checks in `app/checker.py` run first), and a Coach call at the end that writes one comment paragraph. Planner, tools and Checker can be switched off with `AGENT_PLANNER`, `AGENT_TOOLS`, `AGENT_CHECKER` in `.env`.
- **Rules** in `app/orchestrator.py` (plain code, no LLM). `apply_plan()` is the guard: a frustrated learner always gets A/B plus a hint, the level moves at most 1 step, it moves up only after 2 good answers in a row or 1 strong answer (5 standards plus a move, a guessed threshold), no format twice in a row, only the case's own tool, and code decides rounds and the end. If the plan is broken, `decide()` takes over. "You reached" shows the best level ever reached.
- **Copy check** (`app/copycheck.py`): an answer copied in runs of 6 or more words from hints, notes, reading or tool results skips the Assessor, scores 0 and gets the fixed call out "You copied the hint, please answer in your own words."
- **Tools** (`app/tools.py`): 3 seeded quant simulations, one per case, shown as charts.
- **Providers:** `mock` (no key), `gemini` (free, `GOOGLE_API_KEY`), `anthropic` (paid). Model `gemini-3.5-flash-lite`. Calls time out after 45 seconds. Assessor prompt v2 (`prompts.ASSESSOR_VERSION`) gets the case notes and strict rules and uses a fixed seed.
- **Server** `app/main.py` (FastAPI): session, answer, end, stats, overview, tutorial score, config, participant check and `GET /api/health` (open it before a testing day; it never calls the AI). Blank answers are refused and answers are cut at 2000 characters.
- **Limits** (`app/limits.py`): new sessions are refused after `DAILY_CALL_BUDGET` calls a day (default 400). Free tier is 15 requests a minute and 500 a day, and a 6-round session is about 30 to 35 calls, so about 14 sessions fit in a day.
- **Saving** (`app/storage.py`): Supabase online, files (`sessions/`, `transcripts/`) locally. This laptop's `.env` has the Supabase keys, so local runs save to the live database. For test servers set `SUPABASE_URL=" "`.
- **Page** `static/index.html`: Home (tutorial card plus 3 cases, rounds 3, 6 or ∞, Normal or A/B-only mode, tips strip, overall status panel), reading pop-up, "read the case first" spotlight, Claude-style session screen with sidebar, hint bulb, Status panel, end profile (level blocks, 9-point standards graph, Coach comment), first-time tours, scripted tutorial (`content.TUTORIAL`, `app/tutorial.py`), phone layout at 700 px or less. Reading texts and the tutorial script are **DRAFTs for Dr Ho to check**.
- **Study mode** is off unless `STUDY_CODES` is set. It shows a consent screen (DRAFT wording) and asks for a participant code, which is saved with every answer.
- **Evaluation tools:** `eval/test_set.csv` (61 answers), `eval/run_assessor.py`, `eval/compare_marks.py`, `eval/export_answers.py` (writes real learner data to the gitignored `eval/exports/`). Plan and marking guide in `docs/evaluation/`.
- **Deployment:** https://socratic-ai-qlk6.onrender.com (free Render, deploys from `main`, sleeps after 15 minutes; a cron-job.org ping keeps it awake). Tell testers not to type personal details, because Google may read free-tier data.

How to describe it in the thesis: AI agents plus a rule-based orchestrator, where plain code, not the AI, decides what happens next, so the steps are fair and testable. Confirm the word "agentic" with Dr Ho.

Run: `uvicorn app.main:app --reload`, open http://127.0.0.1:8000. Tests: `pytest` (94 passing on 15 October 2026).

## Design requirements R1 to R9 (thesis Table 3)

R1 clear mission at start. R2 fixed rounds and visible progress. R3 remember what the learner said and never re-ask it. R4 feedback plus a small teaching bit each turn, then ask. R5 notice frustration, acknowledge, change approach. R6 vary question formats. R7 separate assessor, scored against the framework. R8 learner stats view. R9 stable topic and context.

## Honest status

- Two full real sessions on the live site (15 October 2026) worked, and the problems they showed were fixed (details in the history file).
- The knowledge base is hand-written notes in `content.py`, not real RAG yet.
- There are no logins, so the overall status only combines sessions played in the same browser.
- The Assessor has only been compared with AI marks, never with human markers, so it is not validated.

## Next steps

0. **Defence first** (21 October 2026): finish the handoff below.
1. **Goal 1 from Meeting 2** (target mid November 2026): `docs/supervisor/meeting2-notes.md` section 8, one step at a time, with the student's OK before each step. In parallel, the interim report gaps in section 6 of those notes.
2. Improve the prompts from real transcripts, and keep every transcript for the thesis Results.
3. Real quant reading chosen with Dr Ho, then simple RAG.
4. Evaluation (FYP2): R1 to R9 against the two baseline gems, Assessor against human markers (agreement and Cohen's kappa), and a learner questionnaire if ethics allows.
5. Keep the thesis in sync with what is really built.

FYP1 is understand and plan (Chapters 1 to 3, first demo). FYP2 is build and prove (Results, Discussion, Conclusion). This split is an assumption to confirm with Dr Ho.

## Thesis files in `docs/`

Folders (see `docs/README.md`): `thesis/` (FYP1.docx, its PDF, `figures/`), `defence/` (slides, `build/`, `screenshots/`, `senior-example/` on this laptop only), `supervisor/` (messages, Meeting 2 notes and transcript, actual goal, handwritten framework, private proposal), `evaluation/`, `utp-rules/`. New files go in the matching folder, with a PDF copy next to its original for viewing in VS Code.

- `docs/thesis/FYP1.docx` is **the current thesis text**. Claude edits it as **tracked changes by "Claude"** that the student accepts in Word. It follows the UTP format (Times New Roman 12, 1.5 spacing, left margin 4 cm, APA references) and every figure has a source.
- UTP rules: the interim report is at most **20 pages without appendices**, but the main text is about 50 pages, so it must be cut (ask the student and Dr Ho first). FYP 1 marks are 50% supervisor and 50% examiners, and the literature review weighs the most in the interim form.

## Open items (do not forget)

- **Defence handoff done (20 October 2026 evening):** slides rebuilt (26S005, new problem statement on slide 4, 3 objectives on slide 5, Evaluation Plan items tagged Objective 1, 2, 3 or all, week-by-week Gantt, speaker notes on every slide loaded from `script.json`, conclusion names the three gaps), PDF re-exported, every changed slide checked as an image. `defence-script.md` matches `script.json`. Thesis `FYP1.docx` has new tracked changes by "Claude" for the student to accept: title page 26S005, a new closing paragraph in 1.2 with the new problem statement, 3 objectives in 1.3 plus a sentence that evaluation is part of the methodology, the week-by-week Gantt as Figure 18 with a sentence on the weeks; contents and list of figures refreshed. Later the same evening the three 1.2 bullets were rewritten as tracked changes to match (no ladder, no measurement, no adaptation; the third keeps the evidence from the Gem test).
- **Remind Dr Ho about the Claude and Render subscription requests** (he asked at Meeting 2). Until approved, stay on free tiers.
- Ask Dr Ho: the interim report layout (4 chapters or the template's 5), how to measure per-learner mastery before there are enough learners for factor analysis, the pedagogy expert's correct name (heard as "Dr Chong Suli"), permission to reuse figures from his Module 7 and 8 slides, the rubric to use, a paid API key from the grant, and ethics for Gemini free-tier data.
- Confirm with Dr Ho: the "agents decide, rules guard" wording for "agentic", which SoTL parts the FYP covers, and how analytical and inductive reasoning map to Bloom levels.
- For the student: confirm the Paul and Elder editions (2006 and 2019 used), verify the ChatGPT learning mode and Khanmigo cells in the comparison table (Khanmigo is unchecked), and read every source from the proposal before citing it.
