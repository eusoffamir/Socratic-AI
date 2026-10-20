# Socratic AI

A tutor app that helps university students new to quant think for themselves
instead of being handed answers. It asks Socratic questions, marks each answer
for the quality of the reasoning, and shows the learner how they did.

Final year project 26S004 at UTP, "Agentic AI for Fostering Critical Thinking
Education", supervised by Dr Ho Tatt Wei.

Live prototype: https://socratic-ai-qlk6.onrender.com (free hosting, so the
first visit after a quiet spell can take up to a minute).

## How it works

The learner picks one of 3 short quant cases (pattern or luck, will a rule work
again, moving together vs causing) and plays 3, 6 or unlimited rounds. Each
round has 4 AI agents and a set of plain-code rules. The design idea is
**agents decide, rules guard**.

1. **Assessor** marks the answer against Paul and Elder's 9 intellectual
   standards (clarity, accuracy, precision, relevance, depth, breadth, logic,
   significance, fairness) and names the reasoning move the learner made.
2. **Planner** proposes the next step: move up, stay or move down a level,
   the question format, a hint, and maybe a simulation.
3. **Rules** (plain Python, no AI) check the plan and fix it if needed. For
   example, a frustrated learner always gets an easier A or B question, a
   level only goes up after 2 good answers in a row or 1 strong answer, and the
   number of rounds is never decided by the AI.
4. **Tutor** writes the reply: short feedback, a key idea (hidden behind a hint
   button) and one question. It may use a small simulation of the case.
5. **Checker** reviews the reply (no giving away the answer, no repeated
   question) after free code checks. If something is wrong, the Tutor rewrites
   once.

The questions climb Richard Paul's 6 levels: Clarify, Assumptions, Evidence,
Viewpoints, Implications and Question the question. At the end, a **Coach** AI
writes one paragraph on how the learner answered.

Other parts: a reading pop-up before each case, a tutorial that shows how
answers are marked, an A or B only mode, a status panel (level reached and the
9 standards), an overall status across cases, saved progress, and a copy check
that scores 0 when a learner pastes a hint instead of thinking.

## Folders

```
app/          the server: agents, prompts, rules, simulations, saving
  main.py         FastAPI app and all endpoints
  graph.py        one turn: assess, plan, guard, tutor, check, rewrite once
  orchestrator.py the plain-code rules ("rules guard")
  prompts.py      the prompts for all 5 AI roles
  llm_client.py   calls Gemini (free) or returns mock replies (no key)
  content.py      the 6 levels, 9 standards, 3 cases and the tutorial script
  tools.py        3 small seeded quant simulations, one per case
  checker.py      free code checks on a Tutor reply
  copycheck.py    catches answers pasted from a hint
  limits.py       daily limit of AI calls, to stay inside the free quota
  storage.py      saves to files locally, or to Supabase online
  tutorial.py     scoring for the tutorial
static/       the web page (index.html) and images
tests/        automatic tests (run with pytest)
deploy/       supabase.sql, the database tables for the online version
docs/         thesis, defence slides, supervisor notes, evaluation plan, UTP rules (see docs/README.md)
eval/         the test set of answers for checking the Assessor against humans
render.yaml   settings for the free Render hosting
```

## Run it on your own computer

You need Python 3.11 or newer.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1         # Windows PowerShell (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env             # then open .env and fill it in
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000.

### Settings in `.env`

| Setting | What it does |
| --- | --- |
| `GOOGLE_API_KEY` | Free Gemini key from https://aistudio.google.com/apikey. Leave it blank to run in mock mode with fake replies and no AI. |
| `GEMINI_MODEL` | Default `gemini-3.5-flash-lite`, which is fast and has 500 free calls a day. |
| `PROVIDER` | Force `gemini` or `mock`. Blank means it is picked from the keys. |
| `AGENT_PLANNER`, `AGENT_TOOLS`, `AGENT_CHECKER` | `0` switches that agent off, for "with vs without" tests or to save calls. |
| `DAILY_CALL_BUDGET` | New sessions stop after this many AI calls a day (default 400, `0` = no limit). |
| `SUPABASE_URL`, `SUPABASE_SECRET_KEY` | Save to a free Supabase database instead of local files. Needed online. |

The settings are read when the server starts, so restart it after editing
`.env`. Never upload `.env`, because it holds your keys.

One 6-round session uses about 25 AI calls, so the free tier fits roughly 15
to 20 sessions a day, with about 3 learners answering at the same moment.

## The online version

The live app runs on Render's free plan (`render.yaml`) and saves sessions to a
free Supabase database (`deploy/supabase.sql`), because Render wipes its files
on every restart. Render installs every new version pushed to the `main`
branch on GitHub.

Before a testing day, open `/api/health`. It says in plain words whether saving
works, which AI is in use, and how many AI calls were used today. It never
calls the AI itself.

Gemini's free tier lets Google use what learners type to improve its products,
so testers should not type personal details.

## Endpoints

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/` | The web page |
| GET | `/api/health` | Whether saving and the AI work, and today's call count |
| GET | `/api/concepts` | The 3 cases with their readings |
| POST | `/api/session` | Starts a case. Body: `concept_id`, `total_rounds` (3, 6, or 0 for no limit), `ab_only`, `reading_seconds` |
| GET | `/api/session/{id}` | A saved session, to continue it |
| POST | `/api/session/{id}/answer` | Sends an answer. Body: `{"answer": "..."}` |
| POST | `/api/session/{id}/end` | Ends an unlimited session |
| GET | `/api/session/{id}/stats` | The status panel: level, standards and the Coach comment |
| POST | `/api/overview` | Overall status across the sessions played in this browser |
| GET | `/api/tutorial` | The tutorial script |
| POST | `/api/tutorial/score` | Marks the tutorial's round 3 answer |

Interactive docs are at `/docs` while the server runs.

## Tests

```bash
pytest
```

The tests check everything that should behave the same every time: the rules,
the guard, the simulations, the code checks, saving, the daily limit and whole
sessions in mock mode. They never call the real AI or the real database. How
good the AI agents are is judged from real transcripts and from the Assessor
evaluation (see `docs/evaluation/assessor-evaluation-plan.md`).

## Known gaps

- The case notes are hand-written, not taken from real reading material (no
  RAG yet).
- There are no logins, so "my progress" only covers sessions played in the
  same browser. The parent research project needs an anonymous participant
  code to link a student's sessions.
- The Assessor has not yet been checked against human markers.
- Whether a learner opened the hint is not recorded.
