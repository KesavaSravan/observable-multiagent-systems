"""
Module 07 - Script 01: Breakpoint Interruption Before Risky Action

Demonstrates:
1. Configuring interrupt_before=["restart_production_cluster"]
2. Graph automatically pausing before executing the dangerous node
3. Resuming execution after operator approval
"""

import sys
from typing import TypedDict
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
from langgraph.checkpoint.memory import MemorySaver


class RemediationState(TypedDict):
    service: str
    action_plan: str
    status: str


def plan_remediation_node(state: RemediationState) -> dict:
    print(" [Step 1: Plan] Agent diagnosing issue and proposing pod restart...")
    return {
        "action_plan": f"Execute 'kubectl rollout restart deployment/{state['service']}'",
        "status": "pending_approval"
    }


def restart_production_cluster_node(state: RemediationState) -> dict:
    print(f" 🔥 [Step 2: DANGEROUS ACTION] Restarting deployment '{state['service']}' on production...")
    return {"status": "restarted_successfully"}


def main():
    print("=" * 70)
    print("  MODULE 07: BREAKPOINT INTERRUPTION BEFORE RISKY ACTION")
    print("=" * 70)

    memory = MemorySaver()
    builder = StateGraph(RemediationState)
    builder.add_node("plan_remediation", plan_remediation_node)
    builder.add_node("restart_production_cluster", restart_production_cluster_node)

    builder.add_edge(START, "plan_remediation")
    builder.add_edge("plan_remediation", "restart_production_cluster")
    builder.add_edge("restart_production_cluster", END)

    # 1. Compile with interrupt_before
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["restart_production_cluster"]
    )

    config = {"configurable": {"thread_id": "hitl-incident-001"}}

    # 2. First Invocation: Pauses automatically before restart
    print("\n▶️ Step 1: Starting Agent Graph Execution...")
    graph.invoke({"service": "payment-api", "action_plan": "", "status": "init"}, config=config)

    # 3. Check State at Breakpoint
    current_state = graph.get_state(config)
    print("\n⏸️ Graph Paused at Breakpoint!")
    print(f"   • Next Node Pending: {current_state.next}")
    print(f"   • Proposed Action  : {current_state.values['action_plan']}")
    print(f"   • Current Status   : {current_state.values['status']}")

    # 4. Operator Resumes Execution
    print("\n▶️ Step 2: Human Operator grants approval. Resuming graph...")
    final_res = graph.invoke(None, config=config)

    print("\n" + "-" * 70)
    print(f"🎯 Execution Completed! Final Status: {final_res['status']}")
    print("-" * 70)
    print("✅ Completed Script 01 successfully!\n")


if __name__ == "__main__":
    main()
