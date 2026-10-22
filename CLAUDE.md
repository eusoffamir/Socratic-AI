# CLAUDE.md: Socratic AI (FYP project 26S005)

Short version. Full history, details, audits and dated findings are in `docs/project-history.md` (same section names as here). Open only the section a task needs.

## Student and writing style

- **Muhammad Eusoff Amir bin Hazri**, ID **22010491**, goes by Eusoff. Course **EFB4042** (FYP I), UTP. Project "Agentic AI for Fostering Critical Thinking Education", code **26S005**, supervisor Dr Ho Tatt Wei.
- **Student-facing and thesis text: easy English, short sentences. Never use "--" or em dashes.**
- No money for APIs. Default to free options (Gemini free tier, mock mode, local tools).
- Work one step at a time, explain in plain words, ask before large new features.
- Be honest about uncertainty. Never invent citations.

## Two laptops: keep in sync (IMPORTANT)

- **Start of every chat:** `git pull`. If it fails or conflicts, stop and explain.
- **After every finished, tested change:** commit and `git push` without asking, and say so (a push redeploys Render). Never force push.
- A commit that only changes docs or the thesis gets `[skip render]` in its message, so Render does not rebuild and restart the app.
- Render free plan sleeps after 15 minutes idle. A cron-job.org job ("Socratic AI wake", Eusoff's account) pings `/api/health` every 10 minutes to keep it awake. A "Service waking up" page right after a push is the redeploy, not a broken ping.
- Project knowledge goes in this file or `docs/project-history.md`, not only in Claude's memory.
- Not synced, set up by hand per laptop: `.env`, `.claude/settings.local.json`, Dr Ho's private proposal docx, his Module 7 and 8 PDFs.
- If `git` is not found, use `& "C:\Program Files\Git\cmd\git.exe"`.

## Saving tokens (rules for Claude)

- Do not read `.docx`, `.pptx` or `.pdf` files whole. Extract or grep only the part needed.
- Use Grep or `sed -n` for line ranges instead of reading whole large files (`app/prompts.py`, `static/index.html`, `docs/project-history.md`).
- Do not re-read a file just to check an edit. Do not run the full `pytest` after every small change; run the matching test file, then the full suite once before pushing.
- Do not spawn subagents unless the student asks.
- Keep replies short. No long recaps of what was already said.

## What the project is

A Socratic tutor that develops critical thinking, measures it against a framework, and adapts to the learner's gaps (teach, assess, adapt). Not an answer machine. Goal details: `docs/supervisor/actual-goal.md`.

- Tutor asks questions up Paul's 6 levels (clarify, assumptions, evidence, viewpoints, implications, question the question).
- Assessor scores on Paul and Elder's 9 standards plus which of the 6 moves were shown.
- Topic: **any topic** (Goal 2). The built-in, checked topic is quant (how quants find predictable patterns in data, for beginners, no complex ML; 3 cases in `app/content.py`). Any other topic is drafted by the Topic Builder agent `app/builder.py`.

### App text rules

- Tutor tone calm and helpful, like Jarvis. No slang, emoji or exclamation marks (only exception "Congratulations! You reached ...").
- Keep all text short (limits in `prompts.WORD_LIMITS`). Smooth sentences joined with "because", "so", "and", "but". No clipped style, no colons joining parts.
- Numbers inside sentences, not →, = or ≠ (chart titles may). **Chances always as percentages, never fractions.**

## Supervisor

- Messages: `docs/supervisor/dr-ho-messages.md`. Parent SoTL grant details in the history file.
- **Meeting 2 (19 October 2026):** read `docs/supervisor/meeting2-notes.md` before any Goal 1 work. Goal 1 (mid November 2026): attainment in reasoning type, knowledge type and quality, with new Reasoning and Explainer agents. All 6 steps of section 8 are done.

## Architecture

"Agents decide, rules guard." `app/graph.py` (LangGraph): assess, plan, guard, tutor (may run a tool), check, rewrite once, finish.

- Agents: prompts `app/prompts.py`, calls `app/llm_client.py`. Assessor, Planner, Tutor, Checker (`app/checker.py` runs first), Coach. Reasoning agent `app/reasoning.py` (Goal 1, shares the Assessor call), knowledge graphs `app/knowledge.py`. Skill check (tagged question bank, 1 call per answer) `app/skillcheck.py`. Mastery stats `app/stats.py`, class model `eval/dina.py`, Explainer agent `app/explainer.py`. Topic Builder agent `app/builder.py` with Wikipedia grounding `app/sources.py` (Goal 2: 3 cases plus skill check questions for any topic, kept inside the session; look cases up with `content.case_of(session)`, never `CONCEPTS[...]`). Goal 1 summary for Dr Ho: `docs/supervisor/goal1-summary.md`. Goal 3 (knowledge from books, heuristics and data, reasoning as graph moves): plan `docs/supervisor/goal3-plan.md`, decision trees `app/heuristics.py`, Bayesian networks `app/pgm.py`, node sources and quotes in `app/knowledge.py` (check with `python -m eval.check_quotes`), reasoning read as graph moves `app/traverse.py` (shares the Assessor call). Toggles `AGENT_PLANNER`, `AGENT_PLANNER_SHARED` (Planner rides on the Assessor's call, default 1), `AGENT_TOOLS`, `AGENT_CHECKER`, `AGENT_REASONING`, and `AI_GUARD` (AI-style answer check plus paste off in the skill check, default 1).
- Rules: `app/orchestrator.py` (`apply_plan()` guard, `decide()` fallback). Copy check `app/copycheck.py`. Tools `app/tools.py`. Limits `app/limits.py`. Saving `app/storage.py` (Supabase; local `.env` writes to the live DB, so set `SUPABASE_URL=" "` for test servers).
- Providers: `mock`, `gemini` (free, model `gemini-3.5-flash-lite`), `anthropic`.
- Server `app/main.py` (FastAPI, `GET /api/health`). Page `static/index.html`. Eval tools in `eval/`, plans in `docs/evaluation/`.
- Live: https://socratic-ai-qlk6.onrender.com (deploys from `main`).
- Run: `uvicorn app.main:app --reload`. Tests: `pytest`. For a no-cost test server use `PROVIDER=mock` (`MOCK=1` is ignored when `.env` sets `PROVIDER`).

Design requirements R1 to R9 and honest status: see history file.

## Thesis and docs

- `docs/thesis/FYP1.docx` is the current thesis. Edit as **tracked changes by "Claude"**. UTP format (Times New Roman 12, 1.5 spacing, left margin 4 cm, APA).
- Interim report must be at most 20 pages without appendices; main text is about 50, cut only after asking.
- Folder guide: `docs/README.md`.

## Next steps

1. Goal 1 is built (21 October 2026). Next, Dr Ho checks the drafts (see `docs/supervisor/goal1-summary.md`), then check the Reasoning agent against a human marker.
1. Goal 2 (any topic) is built (21 October 2026, see history file "Goal 2"). Next, try many topics on Gemini, tighten the Builder prompts from what goes wrong, and show Dr Ho.
1. Goal 3 started 22 October 2026 (Dr Ho planned it for next semester). Steps 1 to 5 are done (plan, decision trees, Bayesian networks, sources and quotes, reasoning as graph moves; all plain Python; Wikipedia stands in for a quant book, since Dr Ho could not name one). Steps 6 and 7 are done too (a full-width Knowledge page from the sidebar; the Builder drafts a tree and a model with AI-guessed chances for any topic). All 7 steps of the plan are built. Next, show Dr Ho `docs/supervisor/goal3-plan.md` and the Knowledge page, and check the step 5 graph reading against a human marker. Steps in `docs/supervisor/goal3-plan.md`.
2. Improve prompts from real transcripts, keep every transcript.
3. Real quant reading with Dr Ho, then simple RAG.
4. Evaluation in FYP2 (R1 to R9, Assessor against human markers).

## Open items

- **BEFORE THE PILOT: `AI_GUARD=1`** in `.env` and on Render (it turns the AI-style answer check on and paste off). Eusoff sets it to 0 for testing. Remind Eusoff whenever the pilot, the study or study mode comes up.

- Remind Dr Ho about the Claude and Render subscription requests.
- Full list of questions for Dr Ho and things to verify: history file, "Open items".
