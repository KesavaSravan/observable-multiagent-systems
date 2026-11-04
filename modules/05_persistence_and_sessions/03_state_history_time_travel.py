"""
Module 05 - Script 03: State History Inspection & Time-Travel Debugging

Demonstrates:
1. Querying graph.get_state_history() to inspect past checkpoint snapshots
2. Inspecting the state values at each discrete checkpoint
3. Branching execution from a prior historical checkpoint
"""

import sys
import operator
from typing import TypedDict, Annotated, List
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


class HistoryState(TypedDict):
    step_history: Annotated[List[str], operator.add]
    current_action: str


def step_a_node(state: HistoryState) -> dict:
    return {"step_history": ["Executed Step A: Verified DNS resolution"]}


def step_b_node(state: HistoryState) -> dict:
    return {"step_history": ["Executed Step B: Checked Load Balancer targets"]}


def step_c_node(state: HistoryState) -> dict:
    return {"step_history": ["Executed Step C: Issued TLS Certificate refresh"]}


def main():
    print("=" * 70)
    print("  MODULE 05: STATE HISTORY INSPECTION & TIME TRAVEL")
    print("=" * 70)

    memory = MemorySaver()
    builder = StateGraph(HistoryState)
    builder.add_node("step_a", step_a_node)
    builder.add_node("step_b", step_b_node)
    builder.add_node("step_c", step_c_node)

    builder.add_edge(START, "step_a")
    builder.add_edge("step_a", "step_b")
    builder.add_edge("step_b", "step_c")
    builder.add_edge("step_c", END)

    graph = builder.compile(checkpointer=memory)

    config = {"configurable": {"thread_id": "time-travel-demo-thread"}}

    print("\n▶️ Step 1: Executing full graph pipeline...")
    final_res = graph.invoke(
        {"step_history": ["Init pipeline"], "current_action": "start"},
        config=config
    )

    print("\n📜 Current Latest State:")
    for s in final_res["step_history"]:
        print(f"  • {s}")

    # Inspect Checkpoint History
    print("\n🕒 Step 2: Inspecting Checkpoint History via get_state_history():")
    history = list(graph.get_state_history(config))
    print(f"  Found {len(history)} recorded historical checkpoints:\n")

    for idx, snapshot in enumerate(history, 1):
        checkpoint_id = snapshot.config["configurable"].get("checkpoint_id", "N/A")
        next_node = snapshot.next
        step_items = snapshot.values.get("step_history", [])
        print(f"  [{idx}] Checkpoint ID : {checkpoint_id}")
        print(f"      Next Node     : {next_node}")
        print(f"      State Values  : {len(step_items)} items in step_history")
        print(f"      Latest Entry  : '{step_items[-1] if step_items else 'None'}'\n")

    print("=" * 70)
    print("💡 Time-Travel Capability:")
    print("   You can replay or branch from ANY prior checkpoint by passing its exact")
    print("   config={'configurable': {'thread_id': '...', 'checkpoint_id': '<ID>'}}")
    print("=" * 70)
    print("✅ Completed Script 03 successfully!\n")


if __name__ == "__main__":
    main()
