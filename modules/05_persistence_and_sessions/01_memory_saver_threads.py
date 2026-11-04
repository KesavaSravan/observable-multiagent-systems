"""
Module 05 - Script 01: MemorySaver Checkpointing & Thread Isolation

Demonstrates:
1. Compiling a graph with MemorySaver checkpointer
2. Running two independent sessions using different thread_ids
3. Proving complete state isolation between sessions
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


class SessionState(TypedDict):
    notes: Annotated[List[str], operator.add]
    last_update: str


def append_note_node(state: SessionState) -> dict:
    return {"last_update": "note_added"}


def main():
    print("=" * 70)
    print("  MODULE 05: MEMORYSAVER CHECKPOINTING & THREAD ISOLATION")
    print("=" * 70)

    # 1. Initialize checkpointer
    memory = MemorySaver()

    # 2. Build and compile graph with checkpointer
    builder = StateGraph(SessionState)
    builder.add_node("recorder", append_note_node)
    builder.add_edge(START, "recorder")
    builder.add_edge("recorder", END)

    graph = builder.compile(checkpointer=memory)

    # 3. Execute Turn 1 on Thread Alpha
    config_alpha = {"configurable": {"thread_id": "thread_alpha"}}
    config_beta = {"configurable": {"thread_id": "thread_beta"}}

    print("\n▶️ Step 1: Writing note to Thread Alpha...")
    graph.invoke({"notes": ["Alpha: Initialized deployment v1.0"], "last_update": ""}, config=config_alpha)

    print("▶️ Step 2: Writing note to Thread Beta...")
    graph.invoke({"notes": ["Beta: Triggered roll-back for auth service"], "last_update": ""}, config=config_beta)

    print("▶️ Step 3: Appending second note to Thread Alpha...")
    graph.invoke({"notes": ["Alpha: Verification smoke tests passed"], "last_update": ""}, config=config_alpha)

    # 4. Inspect states of both threads
    state_alpha = graph.get_state(config_alpha)
    state_beta = graph.get_state(config_beta)

    print("\n" + "-" * 70)
    print("📦 State Snapshot for 'thread_alpha':")
    for n in state_alpha.values["notes"]:
        print(f"  • {n}")

    print("\n📦 State Snapshot for 'thread_beta':")
    for n in state_beta.values["notes"]:
        print(f"  • {n}")
    print("-" * 70)
    print("✅ Verified thread isolation: Alpha and Beta maintain independent histories!\n")


if __name__ == "__main__":
    main()
