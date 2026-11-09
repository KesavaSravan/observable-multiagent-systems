"""
Module 06 - Script 02: Supervisor Multi-Agent Orchestration Pattern

Demonstrates:
1. Supervisor Agent acting as the central orchestrator
2. Researcher Sub-Agent (investigates system logs and traces)
3. Coder Sub-Agent (generates code fix and terraform patch)
4. Dynamic routing loop until Supervisor emits FINISH
"""

import sys
import operator
from typing import TypedDict, Annotated, List, Literal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from langgraph.graph import StateGraph, START, END


class MultiAgentState(TypedDict):
    task: str
    next_worker: Literal["researcher", "coder", "FINISH"]
    research_notes: str
    code_patch: str
    iteration: int
    history: Annotated[List[str], operator.add]


# 1. Supervisor Node
def supervisor_node(state: MultiAgentState) -> dict:
    it = state.get("iteration", 0) + 1
    print(f"\n 👑 [Supervisor] Turn {it}: Evaluating system state...")
    
    # Simple state evaluation logic
    if not state.get("research_notes"):
        decision = "researcher"
        reason = "Delegating to Researcher to collect logs."
    elif not state.get("code_patch"):
        decision = "coder"
        reason = "Research complete. Delegating to Coder to draft fix."
    else:
        decision = "FINISH"
        reason = "Both research and code patch complete. Ending orchestration."

    print(f"    ↳ Decision: [{decision.upper()}] ({reason})")
    return {
        "next_worker": decision,
        "iteration": it,
        "history": [f"Supervisor -> {decision}"]
    }


# 2. Researcher Sub-Agent
def researcher_node(state: MultiAgentState) -> dict:
    print(" 🔬 [Sub-Agent: Researcher] Querying Elasticsearch logs and Prometheus metrics...")
    notes = "Root cause: Connection pool max_connections=20 exhausted under 200 QPS load."
    return {
        "research_notes": notes,
        "history": ["[Researcher] Identified connection pool bottleneck."]
    }


# 3. Coder Sub-Agent
def coder_node(state: MultiAgentState) -> dict:
    print(" 💻 [Sub-Agent: Coder] Writing Terraform config patch to scale DB pool...")
    patch = "resource 'aws_db_parameter_group' 'pg' { parameter { name = 'max_connections' value = '200' } }"
    return {
        "code_patch": patch,
        "history": ["[Coder] Generated Terraform parameter group patch."]
    }


def main():
    print("=" * 70)
    print("  MODULE 06: SUPERVISOR MULTI-AGENT ORCHESTRATION")
    print("=" * 70)

    # Build Multi-Agent Graph
    builder = StateGraph(MultiAgentState)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("coder", coder_node)

    builder.add_edge(START, "supervisor")

    # Supervisor conditional edge to delegate or finish
    builder.add_conditional_edges(
        "supervisor",
        lambda s: s["next_worker"],
        {
            "researcher": "researcher",
            "coder": "coder",
            "FINISH": END
        }
    )

    # Sub-agents always report back to the Supervisor
    builder.add_edge("researcher", "supervisor")
    builder.add_edge("coder", "supervisor")

    graph = builder.compile()

    initial_state: MultiAgentState = {
        "task": "Investigate and resolve 504 Gateway Timeouts on checkout API.",
        "next_worker": "supervisor",
        "research_notes": "",
        "code_patch": "",
        "iteration": 0,
        "history": []
    }

    print("\n▶️ Launching Supervisor Multi-Agent System...")
    final_state = graph.invoke(initial_state, config={"run_name": "supervisor-multiagent-run"})

    print("\n" + "=" * 70)
    print("📋 Final Supervisor Summary:")
    print(f"Task             : {final_state['task']}")
    print(f"Research Findings: {final_state['research_notes']}")
    print(f"Generated Patch  : {final_state['code_patch']}")
    print("\n👣 Execution Timeline:")
    for h in final_state["history"]:
        print(f"  • {h}")
    print("=" * 70)
    print("✅ Completed Script 02 successfully!\n")


if __name__ == "__main__":
    main()
