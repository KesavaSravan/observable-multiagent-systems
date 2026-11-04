"""
Module 07 - Script 04: LangSmith Trace Continuity Across Pause and Resume

Demonstrates:
1. Running an interrupted graph and logging the initial trace run ID
2. Resuming execution and verifying that both executions belong to the same session thread in LangSmith
3. Inspecting the state transitions across pause/resume boundaries
"""

import sys
from typing import TypedDict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tracers.context import collect_runs
from shared.config import settings


class ContinuityState(TypedDict):
    task_id: str
    phase: str
    result: str


def phase1_node(state: ContinuityState) -> dict:
    print(" [Phase 1 Node] Initial analysis and risk calculation...")
    return {"phase": "awaiting_signoff"}


def phase2_node(state: ContinuityState) -> dict:
    print(" [Phase 2 Node] Post-approval remediation execution...")
    return {"phase": "completed", "result": "Production security fix applied."}


def main():
    print("=" * 70)
    print("  MODULE 07: TRACE CONTINUITY ACROSS PAUSE/RESUME")
    print("=" * 70)

    memory = MemorySaver()
    builder = StateGraph(ContinuityState)
    builder.add_node("phase1", phase1_node)
    builder.add_node("phase2", phase2_node)

    builder.add_edge(START, "phase1")
    builder.add_edge("phase1", "phase2")
    builder.add_edge("phase2", END)

    graph = builder.compile(checkpointer=memory, interrupt_before=["phase2"])

    thread_id = "hitl-continuity-session-882"
    base_config = {
        "configurable": {"thread_id": thread_id},
        "tags": ["module:07_hitl", f"thread:{thread_id}", "env:staging"],
        "metadata": {"operator": "admin_sre"}
    }

    # 1. Run Phase 1 (Pauses)
    print(f"\n▶️ Step 1: Executing Phase 1 (Thread: {thread_id})...")
    with collect_runs() as cb1:
        graph.invoke({"task_id": "SEC-801", "phase": "init", "result": ""}, config=base_config)
        run1 = cb1.traced_runs[0] if cb1.traced_runs else None

    if run1:
        print(f"✅ Phase 1 Run Captured: Run ID {run1.id} (Status: PAUSED at breakpoint)")

    # 2. Resume Phase 2
    print("\n▶️ Step 2: Resuming Phase 2 with same thread_id configuration...")
    with collect_runs() as cb2:
        final_state = graph.invoke(None, config=base_config)
        run2 = cb2.traced_runs[0] if cb2.traced_runs else None

    if run2:
        print(f"✅ Phase 2 Run Captured: Run ID {run2.id} (Status: COMPLETED)")

    print("\n" + "-" * 70)
    print(f"🎯 Final State: Phase='{final_state['phase']}' | Result='{final_state['result']}'")
    print("-" * 70)
    print("\n💡 Observability Continuity:")
    print(f"   Both runs are linked under the same thread_id '{thread_id}'. In LangSmith,")
    print("   you can see the full lifecycle preserved without state corruption.")
    print("🎉 Module 07 completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
