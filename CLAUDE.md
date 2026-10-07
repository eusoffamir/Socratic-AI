# CLAUDE.md: Socratic AI (FYP project 26S005)

Read this first. It holds everything decided so far in earlier chat sessions.

## About the student and how to write for them

- Final year student (UTP). Project: "Agentic AI for Fostering Critical Thinking Education", code 26S005, supervisor Dr Ho Tatt Wei. Difficulty level 4, RTG project. The student's draft title page said 26S004, so confirm the code.
- **Writing style for anything student-facing or thesis text: easy English, short and straightforward sentences. Do not use the double dash sign ("--") or em dashes.**
- The student has **no money for APIs**. Default to free options (Gemini free tier, mock mode, local tools). Do not suggest paid services as the main path.
- The student feels lost easily when many things change at once. Work one step at a time, explain what you did in plain words, and do not add large new features without asking.
- Be honest about uncertainty. Mark anything unverified clearly. Never invent citations.

## What the project is, in simple words

An app that makes students think for themselves instead of handing them answers, and then tests whether it works.

1. **Tutor agent:** asks Socratic questions in order, using Paul and Elder's 6 levels: clarify, assumptions, evidence, viewpoints, implications, question the question.
2. **Assessor agent:** reads each learner answer and scores the quality of reasoning with Paul and Elder's 9 intellectual standards (clarity, accuracy, precision, relevance, depth, breadth, logic, significance, fairness), plus which of the 6 moves the learner showed.
3. **App:** clear mission at the start, fixed number of rounds, feedback every turn, varied question formats, and a stats view for the learner. Working name: "Socratic AI". It is NOT an answer machine like ChatGPT, Gemini or Claude.

Prototype topic (one only, to keep scope small): *how quants find predictable patterns using data, for beginners, avoiding complex machine learning.* Three concepts are in `app/content.py`.

Target learners: **university students new to quant. Early testers are Dr Ho's students (decided 7 October 2026).** Topic stays quant only (Dr Ho's instruction). Tutor tone: calm, helpful assistant, like Jarvis in films. No slang, no emoji, no exclamation marks, no fake "cool" talk (the student dislikes AI that mimics human lingo). **Keep every piece of text in the app short and simple**: UI labels, buttons, errors and Tutor replies (word limits in `prompts.WORD_LIMITS`). The student is a visual person: in app text use numbers and symbols, not long words (`5 ups in a row = 1/32 chance`, `200 rules → 1 looks great by luck`). The notes in `content.py`, tool summaries and the Tutor prompt follow this.

Possible later use: teaching beginners (even high school students) to build AI agents, without the AI doing the thinking for them. This is the original project brief topic.

## Parent project

The FYP sits under a SoTL grant project led by the supervisor: "Elevating Critical Reasoning in AI-empowered Learners: A Novel Assessment Tool and Intervention to Enhance Analytical and Inductive Reasoning through Adaptive Socratic Dialogue with AI Chatbots". It plans an adaptive Socratic chatbot, an LLM transcript assessor (target: Cohen's kappa of at least 0.8 against human raters), Bloom levels 2-3 up to 4 (analytical) and 5 (inductive), and a rubric from Paul-Elder plus Richard Paul's 6 levels. Confirm with the supervisor which parts the FYP must cover.

## Supervisor feedback (from the student's messages)

- Gemini Gems as a Socratic tutor partly does what the project wants. Use it as literature review and compare with similar tools from other AI providers.
- Gaps: no principled way to move the learner up a critical thinking ladder (questions only lead toward an answer, and do not push the learner to ask "is this the right question?"), and no evaluation of the learner's critical thinking against a framework.
- The potential innovation is in the prompts that guide the AI.
- Student's plan: multi-agent design (questioning agent plus checking agent, more if needed). Prototype topic should be one quant topic.

## Findings from the student's own testing (Gemini Gem, September 2026)

- Test #1, online "Socratic Tutor" gem: refused answers, but asked the learner to invent the tracking method with no teaching first (learner said "i dont know" twice), lost context, no purpose or end.
- Test #2, our own Prompt v1 (`docs/tutor-prompt-v1-OLD.md`): asked "what do you mean" about 4 times in a row, forgot what the learner had said, ignored "you are asking way too much follow up questions", never gave feedback or showed progress. Cause: v1 forced exactly one question every turn with no memory, no end and no frustration handling.

## Architecture (already built in this folder)

Agentic version built 7 October 2026. Design idea for the thesis: **agents decide, rules guard.** Each turn (`app/graph.py`): assess, plan, guard, tutor (may run tools), check, rewrite once if needed, finish.

- Four AI agents: **Assessor** (scores the answer), **Planner** (proposes level change, format, hint, tool), **Tutor** (may run tools, then replies), **Checker** (reviews the reply; free code checks in `app/checker.py` run first).
- Each agent can be switched off in `.env`: `AGENT_PLANNER`, `AGENT_TOOLS`, `AGENT_CHECKER` (default 1). Useful for a "with vs without" comparison in the thesis.
- About 4 to 6 model calls per turn, 25 to 30 per 5-round session. Free-tier limits for this are **not verified yet**.
- `app/orchestrator.py`: plain code, no LLM. `apply_plan()` is the guard: a frustrated learner always gets A/B + hint (Planner cannot override), no moving up after a weak answer, level moves max 1 step, no format twice in a row, rounds and end always decided by code. If the plan is broken, `decide()` (the old fixed rules) takes over. Formats now rotate through all 4 (before 7 October 2026 only 2 were ever used, a bug).
- Found in a real Gemini session (7 October 2026): the Checker said an A/B question "does not match the level", and the Tutor's rewrite then dropped the A/B options, so no buttons showed. Fixed: (1) if a rewrite breaks a free code check that the first draft passed, `graph._check_node` sends the first draft (logged as `reverted_to_first_draft`); (2) the Checker prompt says A/B choices fit every level; (3) the Tutor payload has `options_required` for A/B and the rewrite rule says keep the options.
- `app/tools.py`: 3 seeded quant simulations (`simulate_streaks`, `test_many_rules`, `random_pairs_correlation`), one per case. The Tutor calls them with `{"tool": ..., "args": ...}`, max 2 per turn. Results show as a chart in the case file panel.
- `app/prompts.py`: Tutor, Assessor, Planner and Checker system prompts and the JSON payloads sent each turn. The Tutor replies in JSON: `feedback`, `key_idea`, `question`, `options` (2 options only for the A/B format).
- `app/llm_client.py`: providers: `mock` (no key), `gemini` (free tier, `GOOGLE_API_KEY`), `anthropic` (paid). Auto-detected from env vars. `.env` is loaded in `main.py`. Each model call gives up after 45 seconds and shows an error, so the page never spins forever. Gemini thinking is set to "low" to make replies faster.
- Model in `.env`: `gemini-3.5-flash-lite`. It replies in a few seconds. `gemini-3.8-flash` took 20 to 55 seconds per call (October 2026), which made the start screen look stuck.
- `app/graph.py`: LangGraph, one run per turn (flow above). Saves the full agent trace in `session["turns"]`.
- `app/main.py`: FastAPI. Endpoints: `POST /api/session`, `POST /api/session/{id}/answer`, `GET /api/session/{id}/stats`, `GET /api/concepts`. Every turn is saved to `transcripts/<session_id>.jsonl` (no names or personal data).
- `static/index.html` (redesigned 7 October 2026, every page fills the screen): calm paper + teal theme, light/dark toggle (saved per browser). **Home** follows a dashboard reference: teal icon rail, top bar, hero card with the rounds picker (3/5/8) and a "Mode" button that reads "Normal" (gray, default) or "A or B?" (vibrant blue-to-orange gradient) for A/B-only mode (every question is A or B: stored as `session["ab_only"]`, enforced in `orchestrator._finish` over rules and Planner alike, saved in each transcript line as `ab_only`), cases as list rows (picture, tag, title, mission, play button). **Session** is laid out like Claude: left sidebar with the case info and chart (closed by default, opens when the learner clicks the open button; a drawer on phones), thin top bar (`ROUND 3/5 · LEVEL`, ticks, Profile), chat in the middle, rounded answer box at the bottom. "Profile" opens a panel that slides in from the right (Esc or × closes it, it refreshes after each answer). The full profile at the end of a session shows inline in the chat with "New case". "Level reached" is a 6-point radar (one point per Socratic level, sized by how often the learner made that move, scaled to their own most-used move; the reached level's label is orange, unreached levels faded). "Moves you made" chips were removed (moves are still saved in transcripts). The "Strongest" and "Next" cards were removed (7 October 2026). Below the charts, the final profile shows "Comments": ONE paragraph (50 to 80 words) on HOW the learner answered (length, reasons, numbers or examples, focus, other views, giving up) and how to improve. Written once at the end by a **Coach** AI call (`COACH_SYSTEM` and `coach_user` in `prompts.py`, `llm_client.call_coach`), so +1 model call per session. Saved in `sessions/<id>.json` as `comment`. If the call fails or in mock mode, `orchestrator.fallback_comment` writes a plain-code paragraph (tips in `content.STANDARD_TIPS`). Not shown mid-session. Tutor message layout: format chip + feedback in one row above the card; inside the card the question with a round lightbulb "Hint" icon on its right; the key idea opens below the question only when clicked (learner thinks first, opens it only if needed). The last turn shows only the "Session complete" chip and the feedback line, no card and no question (7 October 2026); the profile follows. Whether a hint was opened is NOT recorded yet.
- Saved progress (7 October 2026): every session is written to `sessions/<id>.json` after each turn (about 5 to 20 KB each), so it survives leaving the page and server restarts. `GET /api/session/{id}` returns the turns to rebuild the chat. The browser remembers one unfinished session per case (localStorage `saved-sessions`); the case row shows "Round 3/5 · Continue", and the reading pop-up offers "Continue" or "Start over". Finished sessions lose the badge. Home no longer asks "progress will be lost". Session ids are checked as UUIDs before touching disk.
- Reading pop-up (7 October 2026): clicking a case opens a short visual reading (The idea, Example + chart, Key words, Think about) with "Start this case" at the bottom; learners can read or start straight away. "Read again" in the session sidebar reopens it. Text lives in `content.py` under `reading` and is a **DRAFT written by Claude, to be checked by Dr Ho**; the Tutor still uses only `notes`. Seconds the pop-up was open are saved per session as `reading_seconds` in every transcript line (capped at 3600), for a "read first vs skipped" comparison.
- First-time tour (Claude-style pop-ups, `TOURS` in `static/index.html`): home tour (Welcome on the first case row, Rounds, Mode) on first visit, session tour (Your case, Progress, Level, Question, Hint, Answer box, My stats) on the first session. Seen-state is saved per browser in localStorage (`tour-home`, `tour-session`); the "?" buttons (home icon rail, session sidebar footer) replay it. Steps whose target is not on screen are skipped; phones get their own target/text for the case step. 3-part tutor cards, A/B buttons. The "Notes so far" list and the 01/02/03 steps were removed at the student's request.
- Tests: `tests/test_orchestrator.py`, `tests/test_agents.py`, `tests/test_tools.py`. 28 passing (7 October 2026).

How to describe the design in the thesis: two AI agents (Tutor and Assessor) plus a rule-based orchestrator. The rules in plain code, not the AI, decide what happens next. This is on purpose, so the steps are fair and testable. Confirm the wording "agentic" with the supervisor.

Run: `uvicorn app.main:app --reload`, open http://127.0.0.1:8000. Tests: `pytest`.

## Design requirements R1 to R9 (from thesis Chapter 3, Table 3)

R1 clear mission at start. R2 fixed rounds and visible progress. R3 remember what the learner said and never re-ask it. R4 feedback plus a small teaching bit each turn, then ask. R5 notice frustration, acknowledge, change approach. R6 vary question formats. R7 separate assessor, scored against the framework. R8 learner stats view. R9 stable topic and context.

## Honest status

- **Real Gemini calls now work (6 October 2026).** A few short sessions were run with the student's free key. The Tutor gave short, simple replies with one question each. The Assessor's JSON was read without errors. These test transcripts were not saved.
- Not checked yet: whether `gemini-3.5-flash-lite` stays inside the free-tier limits, and a full session from start to the stats screen.
- Knowledge base is hand-written notes in `content.py`, not real RAG yet.
- Sessions are saved to `sessions/` and can be continued. No per-user history across sessions yet (no logins).
- Assessor reliability against human scoring is untested.

## Next steps, in order

1. Partly done. Real Gemini runs worked for the old 2-agent version. Transcript saving is now built. Still to do: run full sessions with the new agents on Gemini. Check that the Tutor returns valid JSON, uses a tool, stays short, and that the Planner and Checker give sensible output. Check the free-tier limits with about 25 to 30 calls per session.
2. Improve the Tutor and Assessor prompts based on real transcripts. Keep every transcript, since they become thesis Results.
3. Replace the hand-written notes with real quant reading material chosen with the supervisor, then add simple RAG.
4. Add saving of sessions to a file or SQLite so the stats page can show progress over time.
5. Evaluation (FYP2): requirement check R1 to R9 against the two baseline gems, assessor vs human scoring (percent agreement and Cohen's kappa, small sample), and a small learner questionnaire if ethics allows.
6. Keep `docs/` thesis files in sync with what is really built.

## FYP1 and FYP2 split (my assumption, confirm with the supervisor)

- FYP1: understand and plan. Thesis Chapters 1 to 3 (problem, literature review, methodology), early tests, first working demo.
- FYP2: build and prove. Finish prototype with a real model and notes, test it, write Results, Discussion and Conclusion.

## Thesis files in `docs/`

- `thesis-draft-v1-chapters1-2.md`: first draft of Chapters 1 and 2 (older).
- `thesis-update-v2.md`: the newer text for Chapters 1 to 3, test results and references. This is the current one. Items marked **[VERIFY]** or **[CHECK WITH SUPERVISOR]** are still open.
- `tutor-prompt-v1-OLD.md`: the first prompt that failed in Test #2. Keep for the thesis appendix, do not reuse.
- `sources.md`: source log with what is verified and what is not.

## Open items (do not forget)

- Confirm project code (26S004 vs 26S005).
- Confirm with the supervisor: the "agents decide, rules guard" wording for "agentic", quant topic instead of agent-building, which SoTL parts the FYP covers, how analytical and inductive reasoning map to Bloom levels, whether objective 4 (compare with baselines) fits scope, and who picks the quant notes.
- Verify the ChatGPT learning mode and Khanmigo cells in the comparison table. The Khanmigo claims came from general knowledge, not checked.
- Read every source from the SoTL proposal before citing it.
