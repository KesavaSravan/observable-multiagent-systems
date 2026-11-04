"""
Module 07 - Script 03: Interactive Human Approval vs Rejection Workflows

Demonstrates:
1. Dynamic conditional branching based on human decision (APPROVED vs REJECTED)
2. Handling operator rejection by routing to a safe fallback node
3. Full lifecycle simulation
"""

import sys
from typing import TypedDict, Literal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


class ApprovalWorkflowState(TypedDict):
    database: str
    proposed_sql: str
    approval_status: Literal["pending", "approved", "rejected"]
    execution_result: str


def draft_migration_node(state: ApprovalWorkflowState) -> dict:
    print(f" [Agent] Drafting DB migration for '{state['database']}'...")
    return {
        "proposed_sql": "ALTER TABLE users ADD COLUMN last_login_ts TIMESTAMP DEFAULT NOW();",
        "approval_status": "pending"
    }


def human_gatekeeper_node(state: ApprovalWorkflowState) -> dict:
    # This node acts as the pause barrier
    print(" 🛡️ [Gatekeeper] Gatekeeper node reached.")
    return {}


def apply_migration_node(state: ApprovalWorkflowState) -> dict:
    print(f" ✅ [DB Engine] Applying SQL: '{state['proposed_sql']}'")
    return {"execution_result": "Migration completed in 12ms. Schema updated."}


def abort_migration_node(state: ApprovalWorkflowState) -> dict:
    print(" ❌ [DB Engine] Migration rejected by human. Operation safely aborted.")
    return {"execution_result": "Aborted by operator. No changes made."}


def check_human_decision(state: ApprovalWorkflowState) -> str:
    if state["approval_status"] == "approved":
        return "apply_migration"
    return "abort_migration"


def main():
    print("=" * 70)
    print("  MODULE 07: APPROVAL VS REJECTION WORKFLOW")
    print("=" * 70)

    memory = MemorySaver()
    builder = StateGraph(ApprovalWorkflowState)
    builder.add_node("drafter", draft_migration_node)
    builder.add_node("gatekeeper", human_gatekeeper_node)
    builder.add_node("apply_migration", apply_migration_node)
    builder.add_node("abort_migration", abort_migration_node)

    builder.add_edge(START, "drafter")
    builder.add_edge("drafter", "gatekeeper")
    builder.add_conditional_edges(
        "gatekeeper",
        check_human_decision,
        {"apply_migration": "apply_migration", "abort_migration": "abort_migration"}
    )
    builder.add_edge("apply_migration", END)
    builder.add_edge("abort_migration", END)

    graph = builder.compile(checkpointer=memory, interrupt_before=["gatekeeper"])

    # Scenario: Operator rejects unsafe schema change
    config = {"configurable": {"thread_id": "db-migration-rejection-demo"}}
    
    print("\n▶️ Step 1: Agent creates proposal and pauses at gatekeeper...")
    graph.invoke({"database": "users_production", "proposed_sql": "", "approval_status": "pending", "execution_result": ""}, config=config)

    print("\n⏸️ Paused for human decision.")
    print("🧑‍💼 Operator decides: REJECT")
    graph.update_state(config, {"approval_status": "rejected"})

    print("\n▶️ Step 2: Resuming graph...")
    res = graph.invoke(None, config=config)

    print("\n" + "-" * 70)
    print(f"🎯 Final Result: {res['execution_result']}")
    print("-" * 70)
    print("✅ Completed Script 03 successfully!\n")


if __name__ == "__main__":
    main()
