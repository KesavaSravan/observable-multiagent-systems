"""
Module 04 - Script 03: Parallel Fan-Out & Fan-In Reduction

Demonstrates:
1. Dispatching execution from START to multiple parallel diagnostic nodes
2. Running log analyzer, metric analyzer, and security scanner concurrently
3. Fan-in aggregation node combining findings into a unified incident report
"""

import sys
import operator
from typing import TypedDict, Annotated, List
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langgraph.graph import StateGraph, START, END


class ParallelIncidentState(TypedDict):
    service_id: str
    findings: Annotated[List[str], operator.add]
    final_postmortem: str


# Parallel Node 1: Log Scanner
def scan_logs_node(state: ParallelIncidentState) -> dict:
    print(f" ⚙️ [Parallel Node: scan_logs] Scanning logs for service '{state['service_id']}'...")
    return {"findings": ["[LOGS] Found 45 instances of NullPointerException in AuthService.java:112"]}


# Parallel Node 2: Metric Scanner
def scan_metrics_node(state: ParallelIncidentState) -> dict:
    print(f" ⚙️ [Parallel Node: scan_metrics] Querying Prometheus timeseries for '{state['service_id']}'...")
    return {"findings": ["[METRICS] CPU throttle percentage jumped from 2% to 78% at 10:14 UTC."]}


# Parallel Node 3: Network Scanner
def scan_network_node(state: ParallelIncidentState) -> dict:
    print(f" ⚙️ [Parallel Node: scan_network] Checking Istio service mesh latency for '{state['service_id']}'...")
    return {"findings": ["[NETWORK] TCP retransmissions normal (0.01%), TLS handshake latency 4ms."]}


# Fan-In Aggregation Node
def synthesize_postmortem_node(state: ParallelIncidentState) -> dict:
    print("\n 🔄 [Fan-In Node: synthesize] Merging parallel findings into final summary...")
    summary = (
        f"Incident Postmortem for {state['service_id']}:\n" +
        "\n".join(f" - {f}" for f in state["findings"])
    )
    return {"final_postmortem": summary}


def main():
    print("=" * 70)
    print("  MODULE 04: PARALLEL FAN-OUT & FAN-IN REDUCTION")
    print("=" * 70)

    # Build Graph with Fan-Out / Fan-In
    builder = StateGraph(ParallelIncidentState)
    builder.add_node("scan_logs", scan_logs_node)
    builder.add_node("scan_metrics", scan_metrics_node)
    builder.add_node("scan_network", scan_network_node)
    builder.add_node("synthesizer", synthesize_postmortem_node)

    # Fan-out: START connects to all 3 parallel nodes
    builder.add_edge(START, "scan_logs")
    builder.add_edge(START, "scan_metrics")
    builder.add_edge(START, "scan_network")

    # Fan-in: All 3 nodes connect to the synthesizer
    builder.add_edge("scan_logs", "synthesizer")
    builder.add_edge("scan_metrics", "synthesizer")
    builder.add_edge("scan_network", "synthesizer")
    builder.add_edge("synthesizer", END)

    graph = builder.compile()

    print("\n▶️ Executing Parallel Graph...")
    result = graph.invoke(
        {"service_id": "auth-microservice-v2", "findings": [], "final_postmortem": ""},
        config={"run_name": "parallel-fanout-fanin-run", "tags": ["module:04_routing", "topology:fanout_fanin"]}
    )

    print("\n" + "-" * 70)
    print("📋 Consolidated Postmortem Result:")
    print(result["final_postmortem"])
    print("-" * 70)
    print("✅ Completed Script 03 successfully!\n")


if __name__ == "__main__":
    main()
