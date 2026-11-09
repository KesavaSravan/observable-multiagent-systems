"""
Module 07 - Script 02: State Inspection and Human Mutation via update_state()

Demonstrates:
1. Pausing graph before a mutation node
2. Inspecting in-flight variables
3. Modifying state programmatically via graph.update_state()
4. Resuming with the human-edited parameters
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


class ScaleState(TypedDict):
    service: str
    replicas: int
    executed_command: str


def propose_scaling_node(state: ScaleState) -> dict:
    print(f" [Agent] Proposing to scale {state['service']} to 10 replicas...")
    return {"replicas": 10}


def execute_scale_node(state: ScaleState) -> dict:
    cmd = f"kubectl scale deployment {state['service']} --replicas={state['replicas']}"
    print(f" 🚀 [Cluster Manager] Executing command: '{cmd}'")
    return {"executed_command": cmd}


def main():
    print("=" * 70)
    print("  MODULE 07: STATE INSPECTION & HUMAN MUTATION")
    print("=" * 70)

    memory = MemorySaver()
    builder = StateGraph(ScaleState)
    builder.add_node("propose_scaling", propose_scaling_node)
    builder.add_node("execute_scale", execute_scale_node)

    builder.add_edge(START, "propose_scaling")
    builder.add_edge("propose_scaling", "execute_scale")
    builder.add_edge("execute_scale", END)

    graph = builder.compile(checkpointer=memory, interrupt_before=["execute_scale"])
    config = {"configurable": {"thread_id": "scaling-thread-400"}}

    # 1. Run until breakpoint
    print("\n▶️ Step 1: Agent proposes scale...")
    graph.invoke({"service": "order-service", "replicas": 1, "executed_command": ""}, config=config)

    # 2. Inspect state
    current_state = graph.get_state(config)
    print(f"\n⏸️ Breakpoint hit! Current agent proposal: {current_state.values['replicas']} replicas.")

    # 3. Human overrides replicas from 10 to 4 (cost optimization)
    print("✍️ Human intervention: Overriding replica count from 10 to 4 (prevent over-provisioning)...")
    graph.update_state(config, {"replicas": 4})

    # 4. Resume execution
    print("\n▶️ Step 2: Resuming graph with updated human-approved state...")
    final_res = graph.invoke(None, config=config)

    print("\n" + "-" * 70)
    print(f"🎯 Final Executed Command: {final_res['executed_command']}")
    print("-" * 70)
    print("✅ Completed Script 02 successfully!\n")


if __name__ == "__main__":
    main()
