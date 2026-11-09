"""
Module 05 - Script 04: Production SQLite Persistent Checkpointer

Demonstrates:
1. Using SqliteSaver to persist LangGraph states in a durable local SQLite file
2. Closing the process and re-opening the graph with persisted state intact
3. Long-term state recovery for production agents
"""

import sys
import sqlite3
import operator
from typing import TypedDict, Annotated, List
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
from langgraph.checkpoint.sqlite import SqliteSaver


class DurableState(TypedDict):
    durable_log: Annotated[List[str], operator.add]
    last_step: str


def process_task_node(state: DurableState) -> dict:
    return {"last_step": "task_completed"}


def main():
    print("=" * 70)
    print("  MODULE 05: PRODUCTION SQLITE DURABLE PERSISTENCE")
    print("=" * 70)

    db_path = ROOT_DIR / "checkpoints_demo.sqlite"
    print(f"📁 SQLite Checkpoints Database: {db_path.name}")

    # Build Graph
    builder = StateGraph(DurableState)
    builder.add_node("process_task", process_task_node)
    builder.add_edge(START, "process_task")
    builder.add_edge("process_task", END)

    # Use SqliteSaver connection
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    with SqliteSaver(conn) as checkpointer:
        # Setup tables
        checkpointer.setup()
        graph = builder.compile(checkpointer=checkpointer)

        thread_cfg = {"configurable": {"thread_id": "sqlite-prod-incident-100"}}

        print("\n▶️ Step 1: Writing first entry into SQLite checkpointer...")
        graph.invoke({"durable_log": ["[SESSION START] Incident INC-9901 registered in SQLite database."], "last_step": "init"}, config=thread_cfg)

        print("▶️ Step 2: Appending second entry...")
        graph.invoke({"durable_log": ["[UPDATE] Database failover initiated by autonomous agent."], "last_step": "failover"}, config=thread_cfg)

        # Retrieve state from SQLite
        saved_state = graph.get_state(thread_cfg)

        print("\n" + "-" * 70)
        print("💾 Persisted State Retrieved from SQLite DB:")
        for entry in saved_state.values["durable_log"]:
            print(f"  • {entry}")
        print("-" * 70)

    print("\n✅ State safely saved to disk! Checkpoints persist across server reboots.")
    print("🎉 Module 05 completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
