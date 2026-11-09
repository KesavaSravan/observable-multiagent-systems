"""
Module 06 - Script 01: Subgraph Composition as Graph Nodes

Demonstrates:
1. Building an independent Subgraph (Diagnostic Sub-Agent)
2. Compiling the Subgraph
3. Embedding the compiled Subgraph as a single node in a parent workflow
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


# Shared State
class IncidentState(TypedDict):
    ticket: str
    diagnostics: str
    remediation: str


# --- Subgraph: Diagnostic Agent ---
def fetch_k8s_node(state: IncidentState) -> dict:
    print("   [Sub-Agent: Diagnostics] Querying K8s cluster status...")
    return {"diagnostics": "Found CrashLoopBackOff on service-ingress."}


def subagent_graph():
    builder = StateGraph(IncidentState)
    builder.add_node("k8s_fetcher", fetch_k8s_node)
    builder.add_edge(START, "k8s_fetcher")
    builder.add_edge("k8s_fetcher", END)
    return builder.compile()


# --- Parent Graph ---
def root_planner_node(state: IncidentState) -> dict:
    print(" [Parent Graph: Planner] Ingesting ticket and preparing diagnostic sub-agent...")
    return {}


def remediation_node(state: IncidentState) -> dict:
    print(f" [Parent Graph: Remediation] Applying fix based on diagnostics: '{state['diagnostics']}'")
    return {"remediation": "Scaled deployment replicas to 3."}


def main():
    print("=" * 70)
    print("  MODULE 06: SUBGRAPH COMPOSITION AS GRAPH NODES")
    print("=" * 70)

    # Compile Sub-agent
    diagnostic_subagent = subagent_graph()

    # Build Parent Graph
    parent = StateGraph(IncidentState)
    parent.add_node("planner", root_planner_node)
    # Add compiled subagent as a regular node
    parent.add_node("diagnostics_subagent", diagnostic_subagent)
    parent.add_node("remediation", remediation_node)

    parent.add_edge(START, "planner")
    parent.add_edge("planner", "diagnostics_subagent")
    parent.add_edge("diagnostics_subagent", "remediation")
    parent.add_edge("remediation", END)

    master_graph = parent.compile()

    print("\n▶️ Invoking Parent Graph containing Subgraph Node...")
    res = master_graph.invoke({
        "ticket": "INC-771",
        "diagnostics": "",
        "remediation": ""
    })

    print("\n" + "-" * 70)
    print("🎯 Final Consolidated State:")
    print(f"  • Ticket     : {res['ticket']}")
    print(f"  • Diagnostics: {res['diagnostics']}")
    print(f"  • Remediation: {res['remediation']}")
    print("-" * 70)
    print("✅ Completed Script 01 successfully!\n")


if __name__ == "__main__":
    main()
