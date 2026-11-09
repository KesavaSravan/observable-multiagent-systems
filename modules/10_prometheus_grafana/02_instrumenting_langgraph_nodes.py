"""
Module 10 - Script 02: Node Execution Timer & Error Tracking Decorator

Demonstrates:
1. Using @instrument_node to wrap LangGraph nodes
2. Automatically timing node execution into NODE_LATENCY_HISTOGRAM
3. Automatically recording exceptions into NODE_ERRORS_COUNTER
"""

import sys
import time
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
from shared.metrics import instrument_node, generate_latest, REGISTRY


class InstrumentedState(TypedDict):
    input_alert: str
    result: str


# 1. Wrapped Nodes with Instrumentation Decorator
@instrument_node(node_name="triage_node")
def triage_node(state: InstrumentedState) -> dict:
    time.sleep(0.12)  # Simulate latency
    return {"result": "Triaged as P2"}


@instrument_node(node_name="diagnostic_node")
def diagnostic_node(state: InstrumentedState) -> dict:
    time.sleep(0.25)  # Simulate latency
    if "fail" in state["input_alert"].lower():
        raise RuntimeError("Simulated cluster connection timeout")
    return {"result": state["result"] + " -> Diagnostics complete"}


def main():
    print("=" * 70)
    print("  MODULE 10: NODE EXECUTION TIMER & ERROR TRACKING DECORATOR")
    print("=" * 70)

    builder = StateGraph(InstrumentedState)
    builder.add_node("triage", triage_node)
    builder.add_node("diagnostic", diagnostic_node)

    builder.add_edge(START, "triage")
    builder.add_edge("triage", "diagnostic")
    builder.add_edge("diagnostic", END)

    graph = builder.compile()

    print("\n▶️ 1. Running Successful Graph Execution...")
    graph.invoke({"input_alert": "High CPU alert", "result": ""})

    print("\n▶️ 2. Running Failing Graph Execution (to trigger error metrics)...")
    try:
        graph.invoke({"input_alert": "Simulate FAIL cluster", "result": ""})
    except Exception:
        print("   🛡️ Expected exception trapped by runtime.")

    # Inspect recorded Prometheus metrics
    output = generate_latest(REGISTRY).decode("utf-8")
    print("\n" + "-" * 70)
    print("📊 Active Recorded Node Metrics in Prometheus Registry:")
    for line in output.split("\n"):
        if "langgraph_node_" in line and not line.startswith("#"):
            print(f"  {line}")
    print("-" * 70)
    print("✅ Completed Script 02 successfully!\n")


if __name__ == "__main__":
    main()
