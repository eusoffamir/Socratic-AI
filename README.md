# Socratic AI, prototype v2 (agentic)

A multi-agent Socratic tutor: four AI agents (Assessor, Planner, Tutor,
Checker) plus plain-code guard rules, wired with LangGraph, served by FastAPI,
with a small browser front end. The design idea: **agents decide, rules guard.**

A session works like this: the learner picks a quant case, and a fixed number
of rounds (5 by default) runs. Each round:

1. **Assess.** The Assessor agent scores the learner's last answer against the
   9 intellectual standards and returns structured JSON.
2. **Plan.** The Planner agent proposes the next move: level up, stay or down,
   the question format, a hint, and maybe a tool to run.
3. **Guard.** Plain Python (`orchestrator.apply_plan`) checks the plan against
   the fixed rules and fixes it if needed. A frustrated learner always gets an
   easier A/B question. No moving up after a weak answer. No format twice in a
   row. The round count is never decided by an AI. If the plan is missing or
   broken, the old fixed rules (`decide()`) take over.
4. **Tutor.** The Tutor agent may first run a small quant simulation
   (`app/tools.py`), then replies in 3 parts: feedback, key idea, one question
   (plus 2 options for A/B questions).
5. **Check.** Free code checks (length, one question, no repeat), then the
   Checker agent (does it give the answer away?). If either fails, the Tutor
   rewrites once.

Every turn, with the full agent trace, is saved to
`transcripts/<session_id>.jsonl`. Each agent can be switched off in `.env`
(`AGENT_PLANNER`, `AGENT_TOOLS`, `AGENT_CHECKER`).

At the end, the stats panel shows which standards and reasoning moves the
learner showed.

## What's in here

```
app/
  content.py       the 6 Socratic levels, 9 intellectual standards, 4 question
                   formats, and the 3 quant "concepts" (the prototype's
                   knowledge base, standing in for RAG for now)
  prompts.py       the Tutor, Assessor, Planner and Checker system prompts,
                   and the JSON payloads sent to each on every turn
  tools.py         3 small seeded quant simulations the Tutor can run
  checker.py       free code checks on a Tutor reply
  llm_client.py    picks the provider (Gemini / Claude / mock) and makes the
                   calls; mock mode fakes both agents so you can run and demo
                   the app with no API key
  orchestrator.py  the fixed rules (R1-R9 from Table 3) and the guard that
                   checks the Planner's proposal
  graph.py         LangGraph wiring: assess -> plan -> guard -> tutor -> check
                   (-> rewrite once), one run per turn
  main.py          FastAPI app, its endpoints, and transcript saving
static/
  index.html       the browser UI: case cards, a status line (round and
                   level), a case file panel (scenario, chart, notes that
                   grow), 3-part tutor cards, A/B buttons, "I'm stuck" (R5),
                   and the end-of-session thinking profile
tests/
  test_orchestrator.py   unit tests for the fixed rules
  test_agents.py         guard, JSON parsing, code checks, and full mock
                         sessions with each agent switched off
  test_tools.py          the quant simulations
transcripts/       one .jsonl per session (created on first run)
sessions/          one .json per session, for continuing later (created on first run)
data/              empty for now; meant for the reading material RAG will use
.env.example       template for your .env (API keys and provider settings)
```

## Setup

You need Python 3.11 or newer (the existing `.venv` was built with 3.13).

```bash
cd socratic-ai
python -m venv .venv
```

Activate the venv:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (Git Bash)
source .venv/Scripts/activate
# macOS / Linux
source .venv/bin/activate
```

Then install the dependencies and create your `.env`:

```bash
pip install -r requirements.txt
cp .env.example .env        # PowerShell: Copy-Item .env.example .env
```

### Choosing a model

There are three ways to run this. Pick one and set it in `.env`.

**Free, real model (recommended if you have no API budget).** Get a free key
at https://aistudio.google.com/apikey (just a Google account, no card):
```
GOOGLE_API_KEY=your-key-here
```
The free tier has a requests-per-minute limit. That's fine for testing by
hand, but it will throttle you if you send requests in a tight loop (e.g. an
automated evaluation script). If that happens, slow down the requests or set
`GEMINI_MODEL` to a smaller/cheaper model.

**Paid, real model.** If you have Anthropic API credits, set
`ANTHROPIC_API_KEY` and leave `GOOGLE_API_KEY` blank.

**No key at all.** Leave both keys blank, or set `MOCK=1`. The Tutor and
Assessor replies will be fake/templated, but every rule, the whole request
flow, and the stats screen run exactly as they would live. That's good for
demoing the architecture, not for judging how good the tutoring is.

The provider is picked in this order (first match wins):

1. `PROVIDER` is set (`gemini`, `anthropic` or `mock`): use that.
2. `MOCK=1`: mock.
3. `GOOGLE_API_KEY` is set: Gemini.
4. `ANTHROPIC_API_KEY` is set: Claude.
5. Otherwise: mock.

| Variable            | Default            | Purpose                                 |
| ------------------- | ------------------ | --------------------------------------- |
| `GOOGLE_API_KEY`    | (none)             | Key for Gemini                          |
| `GEMINI_MODEL`      | `gemini-3.8-flash` | Gemini model to call                    |
| `ANTHROPIC_API_KEY` | (none)             | Key for Claude                          |
| `ANTHROPIC_MODEL`   | `claude-sonnet-5`  | Claude model to call                    |
| `PROVIDER`          | auto               | Force `gemini` / `anthropic` / `mock`   |
| `MOCK`              | `0`                | `1` forces mock unless `PROVIDER` is set |
| `AGENT_PLANNER`     | `1`                | `0` uses the fixed rules only           |
| `AGENT_TOOLS`       | `1`                | `0` stops the Tutor running simulations |
| `AGENT_CHECKER`     | `1`                | `0` skips the review and rewrite step   |

The provider is chosen once, when the server starts. `--reload` only watches
`.py` files, so after you edit `.env`, stop the server and start it again.

Don't commit `.env`, since it holds your API key. Commit `.env.example`
instead.

## Run it

```bash
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000 in a browser, pick a topic, and start.

## Troubleshooting

If a model call fails, the page shows the reason and puts your answer back in
the box. Nothing is counted, so you can just press Send again.

- **"overloaded right now" (HTTP 503 from Gemini).** Google is busy. The app
  already retries twice; wait a moment and resend.
- **"quota used up" (HTTP 429).** Each round makes about 4 to 6 model calls
  (Assessor, Planner, Tutor, maybe a tool round, Checker, maybe a rewrite),
  so the free tier's per-minute limit runs out fast. Switching an agent off
  in `.env` cuts calls. Wait a
  minute, or switch `GEMINI_MODEL` to another model, since each model has its
  own quota. Run `python -c "from google import genai; import os; from dotenv
  import load_dotenv; load_dotenv(); print([m.name for m in
  genai.Client(api_key=os.environ['GOOGLE_API_KEY']).models.list()])"` to see
  which models your key can use.
- **Mock replies when you expected a real model, or the other way round.**
  Check the provider order above. `PROVIDER` overrides `MOCK`.

## API

The browser UI uses these endpoints. You can also call them directly; the
interactive docs are at http://127.0.0.1:8000/docs.

| Method | Path                       | What it does                                                        |
| ------ | -------------------------- | ------------------------------------------------------------------- |
| GET    | `/`                        | Serves the UI                                                       |
| GET    | `/api/concepts`            | Lists the topics (`id`, `title`, `mission`)                         |
| POST   | `/api/session`             | Starts a session. Body: `{"concept_id": "pattern_or_luck", "total_rounds": 5, "ab_only": false, "reading_seconds": 0}` (`ab_only: true` makes every question an A/B choice; `reading_seconds` is how long the reading pop-up was open, saved in the transcript). Returns the `session_id` and the Tutor's opening message |
| POST   | `/api/session/{id}/answer` | Sends the learner's answer. Body: `{"answer": "..."}`. Returns the Tutor's reply (`parts`: feedback, key_idea, question, options), the round, the level, any `tools` run, a short agent `trace` and the last assessment |
| GET    | `/api/session/{id}`        | Returns a saved session (round, level, and every turn) so the page can continue it |
| GET    | `/api/session/{id}/stats`  | Returns the per-session summary and full assessment history         |

The topic ids are `pattern_or_luck`, `holds_on_new_data` and
`together_not_cause`.

## Run the tests

```bash
pytest
```

These test the parts that should behave the same on every run: the rules,
the guard, the tools, the code checks, and whole sessions in mock mode. The
agents themselves call a live model, so judge them by reading transcripts,
which is what Chapter 4 (your requirement check, R1-R9) is for.

## Changing the content or the rules

- **Add a topic:** add an entry to `CONCEPTS` in `app/content.py` with a
  `title`, `mission`, `scenario` and a list of `notes`. It shows up in the UI
  automatically.
- **Change how fast learners move up or get hints:** edit the constants at
  the top of `app/orchestrator.py` (`GOOD_STANDARDS_THRESHOLD`,
  `STREAK_TO_ADVANCE`, `STREAK_TO_SCAFFOLD`), then run `pytest`.
- **Change what the agents say or how they score:** edit `TUTOR_SYSTEM` or
  `ASSESSOR_SYSTEM` in `app/prompts.py`.

## What maps to what in the thesis

- **R1, R2 (mission and fixed round count):** `orchestrator.new_session`,
  the `"open"`/`"end"` actions in `decide()`.
- **R3, R9 (memory, no re-asking):** `session["said"]` and `session["questions"]`,
  passed into the Tutor's prompt as `LEARNER_SAID` / `ASKED_QUESTIONS`, and
  checked again in `checker.code_check`.
- **R4, R6 (feedback each turn, varied formats):** `prompts.tutor_user`
  builds `what_was_strong` / `what_was_missing` from the Assessor's output;
  `_next_format` rotates through `FORMATS`.
- **R5 (frustration):** `assessment["confused_or_frustrated"]`, enforced in
  both `decide()` and the guard `apply_plan()`. The Planner cannot override it.
- **R7 (separate, structured assessment):** `Assessor` is its own prompt and
  its own call, never mixed into the Tutor's prompt.
- **R8 (stats):** `GET /api/session/{id}/stats`, rendered by the stats panel
  in `index.html`.

## Known gaps to close next

- The knowledge base in `content.py` is hand-written, not RAG. Swapping in
  real retrieval only touches `prompts.tutor_user` (the `NOTES` field), and
  `graph.py` has room for a retrieval node before `tutor`.
- Sessions are saved to `sessions/<id>.json` after every turn and can be
  continued after a reload or restart. There are no logins, so "your" saved
  cases are remembered per browser only.
- The Assessor's JSON parsing has a fallback for stray prose, but hasn't been
  stress-tested against a live model yet, only the mock.
- No login or per-user history across sessions, so the "look at my stats over
  time" part of your product vision isn't built yet, only per-session stats.
