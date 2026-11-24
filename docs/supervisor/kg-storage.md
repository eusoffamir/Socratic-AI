# How the knowledge graph is stored and passed to the agents (Meeting 3, task 4)

Checked against the code on 25 November 2026. Dr Ho asked that the graph be "a hard artifact passed in at retrieval time, not something that only stays in the chat context". The short answer is **yes for the Reasoning agent, only partly for the Tutor**, and the graph is copied into each chat instead of being kept once per topic.

## 1. The data structure

Each case has one small graph, as plain JSON (a Python dictionary). There is no graph database.

```json
{
  "nodes": [
    {"id": "n1", "type": "causal", "note": 0, "label": "Many tries", "quote": "...", "from": "..."},
    {"id": "e1", "type": "procedural", "text": "Count the tries first.", "label": "Count tries"}
  ],
  "edges": [["n1", "causes", "e1"]]
}
```

- **Nodes.** Each has an id and one of Dr Ho's eight knowledge types (factual, conceptual, procedural, causal, relational, strategic, metacognitive, epistemic). A node either points to one of the case's 5 teaching notes (`"note": 0` to `4`, so the note and the node can never drift apart) or holds its own text. It can also carry a short label for the diagram and a quote from its source.
- **Edges.** Each is a list of three items, `[from id, relation, to id]`. The relation must be one of seven names in `app/knowledge.py` (`RELATIONS`): causes, then, defines, supports, weakens, tests, leads_to.
- **Size.** A built-in quant case has about 10 nodes. A generated case has 8 to 11 nodes and 6 to 12 edges.
- **Linked parts.** A generated case can also carry an expert rule tree (`"heuristics"`, used by `app/heuristics.py`) and a small cause and signs model (`"model"`, used by `app/pgm.py`). Each of their nodes points back to a graph node through a `"why"` id, so the three kinds of knowledge stay joined.

## 2. Where it is stored

| Case | Where the graph lives | Code |
|---|---|---|
| Built-in quant case (3 cases) | In the code, `KNOWLEDGE[case_id]` | `app/knowledge.py` |
| Generated case (any topic) | Inside the case, under `"knowledge"` | `app/builder.py`, `clean_case()` |

A generated case moves like this.

1. **Built.** The Topic Builder asks the model for the graph as JSON. Plain code then cleans it. Unknown relations, links to missing nodes, nodes beyond the limit, and quotes that are not really in the source are all dropped (`clean_case()`).
2. **Kept in the browser.** The server does not keep a list of topics. The page keeps the last 12 built topics in the browser (`my-topics` in local storage), and, for a learner signed in with Google, in their profile (`profiles` table in Supabase).
3. **Checked again.** When a chat starts, the page sends the case back, and the server cleans it again with the same rules (`builder.recheck()`). So the page cannot slip in a graph the Builder could not have made.
4. **Saved with the chat.** The clean case, graph included, is stored inside the session (`session["case"]`). It is saved after every turn to the `sessions` table in Supabase, or to `sessions/<id>.json` when there is no database (`app/storage.py`). So the graph survives a server restart.

`content.case_of(session)` is the one way the code finds a session's case: the stored generated case, or the built-in case by id. `knowledge.case_graph(case)` returns the raw graph either way, and `knowledge.graph(case)` returns it with every node's text filled in.

## 3. Which agents get it

| Agent or part | What it gets | How |
|---|---|---|
| Assessor, with the Reasoning agent on (one shared call) | **The whole graph** (node texts and links), plus each note's knowledge type, read fresh from the stored session on every turn | `prompts.assessor_user()` adds `GRAPH` from `_graph_for_agent()` |
| Graph reading of the answer (plain code) | The agent's `graph_steps` are checked against the stored graph's real nodes and links | `llm_client._add_graph_reading()` calls `traverse.read()` |
| Tutor | **Only the 5 note texts**, the story and the mission. **Not the links or the extra nodes** | `prompts.tutor_user()` sends `NOTES` |
| Checker, Planner, Coach | No graph | |
| Explainer | The built-in quant graphs' texts as background. Nothing for a learner's own topic | `explainer.user_payload()` |
| Knowledge page and the chat's diagram | The whole graph, for drawing | `main.py` returns `knowledge.graph()` |
| Rule trees and the cause and signs model | Node texts, through each `"why"` id | `heuristics.py`, `pgm.py` |

## 4. What this means against Dr Ho's requirement

**What already meets it**

- The graph is a hard artifact. It is structured JSON with checked node ids, types and relations, stored in the database, and read fresh on every turn.
- It is passed in at question time to the agent that reasons over it (the Reasoning agent), and plain code checks the agent's graph steps against it.
- It survives restarts, and it cannot be changed by the page without passing the same checks.

**What does not yet**

1. **The Tutor does not use the graph's links.** It asks questions from the 5 note texts, so its questions are not chosen by walking the graph. For diagnosis as "a walk on the graph", the agent that leads the walk needs the links too.
2. **One copy per chat, not one graph per topic.** Each session holds its own copy of its case's graph. The server keeps no single graph for a topic, and nothing joins the same idea across cases or topics. A built topic exists on the server only once a chat on it starts.
3. **Small and separate graphs.** Each case's graph has about 10 nodes and is never merged with the others, so there is no larger graph to retrieve a part of.
4. **No version.** If a graph is improved later, old sessions keep their old copy, and nothing records which version a chat used.

## 5. Suggestion for the Ex use case (for discussion, not built)

For the inspection use case, the graph should be kept once per domain, as its own record, and not inside chats.

- A `graphs` table (or JSON files in the repo for a start) with one versioned graph per domain, for example "Ex equipment", with stable node ids.
- Chats and agents refer to the graph by id and version, and each agent call gets only the part it needs, for example the nodes within two links of the current finding.
- The relation classes are standardised first (task 5), so graphs built at different times can be merged.
- The three linked parts (concept graph, rule trees, probability model) stay joined by node ids, as they already are through `"why"`.

None of this is needed for the tutor as it stands, so it should wait until the Ex data arrives.
