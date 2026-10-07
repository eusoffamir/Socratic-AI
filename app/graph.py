"""One LangGraph run = one turn of the conversation.

    assess -> plan -> guard -> tutor (may run tools) -> check -> [rewrite once] -> finish

- assess: Assessor agent scores the learner's last answer.
- plan:   Planner agent proposes the next move (level, format, hint, tool).
- guard:  plain-code rules in orchestrator.py check the plan and fix it if
          needed. Rounds and the end are always decided here, never by an LLM.
- tutor:  Tutor agent writes the reply. It may run quant tools first.
- check:  free code checks, then the Checker agent. If either finds a
          problem, the Tutor rewrites once.

Each agent can be switched off in .env (AGENT_PLANNER, AGENT_TOOLS,
AGENT_CHECKER = 0), so the thesis can compare the app with and without it.
"""
import os
from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph

from . import checker, llm_client, orchestrator

MAX_REWRITES = 1


def agent_on(name):
    """Read at call time so tests can switch agents on and off."""
    return os.getenv(name, "1") != "0"


class TurnState(TypedDict, total=False):
    session: dict
    answer: Optional[str]
    assessment: Optional[dict]
    plan: Optional[dict]
    planned: bool
    overrides: list
    instruction: dict
    parts: dict
    first_parts: dict
    first_code_ok: bool
    tool_runs: list
    problems: list
    check: dict
    rewrites: int
    reply: str


def _assess_node(state: TurnState) -> TurnState:
    if state.get("answer") is not None:
        state["assessment"] = llm_client.call_assessor(state["session"], state["answer"])
    else:
        state["assessment"] = None  # first turn of the session, nothing to assess yet
    return state


def _plan_node(state: TurnState) -> TurnState:
    s = state["session"]
    ending = s["round"] >= s["total_rounds"]
    state["planned"] = state["assessment"] is not None and not ending and agent_on("AGENT_PLANNER")
    state["plan"] = llm_client.call_planner(s, state["assessment"]) if state["planned"] else None
    return state


def _guard_node(state: TurnState) -> TurnState:
    if state["planned"]:
        state["instruction"], state["overrides"] = orchestrator.apply_plan(
            state["session"], state["plan"], state["assessment"])
    else:
        state["instruction"] = orchestrator.decide(state["session"], state["assessment"])
        state["overrides"] = []
    return state


def _tutor_node(state: TurnState) -> TurnState:
    rewriting = bool(state.get("problems"))
    state["parts"], state["tool_runs"] = llm_client.call_tutor(
        state["session"], state["instruction"], state.get("answer"), state["assessment"],
        use_tools=agent_on("AGENT_TOOLS"), tool_runs=state.get("tool_runs"),
        draft=state.get("parts") if rewriting else None,
        problems=state.get("problems") if rewriting else None,
    )
    if not rewriting:
        state["first_parts"] = state["parts"]
    return state


def _check_node(state: TurnState) -> TurnState:
    ins = state["instruction"]
    if ins["action"] == "end" or not agent_on("AGENT_CHECKER"):
        state["problems"] = []
        state["check"] = {"ran": False}
        return state
    rewritten = state.get("rewrites", 0) > 0
    code_problems = checker.code_check(state["parts"], ins, state["session"]["questions"])
    prev = state.get("check", {}).get("history", [])
    if rewritten and code_problems and state.get("first_code_ok"):
        # The rewrite broke a free check the first draft passed (seen with
        # Gemini: fixing the wording, it dropped the A/B options). A draft
        # that works beats a rewrite that is broken, so send the first draft.
        state["parts"] = state["first_parts"]
        state["problems"] = prev[0] if prev else []
        state["check"] = {"ran": True, "history": prev + [code_problems], "reverted_to_first_draft": True}
        return state
    if not rewritten:
        state["first_code_ok"] = not code_problems
    problems = code_problems
    if not problems:  # only spend a model call when the free checks pass
        problems = llm_client.call_checker(ins, state.get("answer"), state["parts"])
    state["problems"] = problems
    state["check"] = {"ran": True, "history": prev + [problems]}
    return state


def _after_check(state: TurnState) -> str:
    if state["problems"] and state.get("rewrites", 0) < MAX_REWRITES:
        return "rewrite"
    return "finish"


def _rewrite_node(state: TurnState) -> TurnState:
    state["rewrites"] = state.get("rewrites", 0) + 1
    return state


def _finish_node(state: TurnState) -> TurnState:
    s, parts = state["session"], state["parts"]
    state["reply"] = llm_client.parts_text(parts)
    s["last_tutor"] = state["reply"]
    if parts["question"]:
        s["questions"].append(parts["question"])
    ins = state["instruction"]
    s["turns"].append({
        "round": ins["round"],
        "answer": state.get("answer"),
        "assessment": state["assessment"],
        "plan": state.get("plan"),
        "guard_overrides": state["overrides"],
        "instruction": ins,
        "tool_runs": state["tool_runs"],
        "check": state["check"],
        "rewrites": state.get("rewrites", 0),
        "shipped_with_problems": state["problems"],
        "parts": parts,
    })
    return state


def build_graph():
    g = StateGraph(TurnState)
    for name, fn in [("assess", _assess_node), ("plan", _plan_node), ("guard", _guard_node),
                     ("tutor", _tutor_node), ("check", _check_node), ("rewrite", _rewrite_node),
                     ("finish", _finish_node)]:
        g.add_node(name, fn)
    g.set_entry_point("assess")
    g.add_edge("assess", "plan")
    g.add_edge("plan", "guard")
    g.add_edge("guard", "tutor")
    g.add_edge("tutor", "check")
    g.add_conditional_edges("check", _after_check, {"rewrite": "rewrite", "finish": "finish"})
    g.add_edge("rewrite", "tutor")
    g.add_edge("finish", END)
    return g.compile()


_graph = build_graph()


def run_turn(session: dict, answer: Optional[str]) -> dict:
    """Run one turn. `answer` is None to open a brand new session."""
    result = _graph.invoke({"session": session, "answer": answer})
    return {
        "reply": result["reply"],
        "parts": result["parts"],
        "instruction": result["instruction"],
        "assessment": result["assessment"],
        "tool_runs": result["tool_runs"],
        "trace": result["session"]["turns"][-1],
        "session": result["session"],
    }
