"""
Module 02 - Script 02: Custom State Reducers & Channel Merging

Demonstrates:
1. Using Annotated with operator.add for append-only state channels (e.g. audit logs, messages)
2. Using custom reducer functions to merge complex dictionaries
3. Multi-node sequential execution with state accumulation
"""

import sys
import operator
from typing import TypedDict, Annotated, List, Dict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langgraph.graph import StateGraph, START, END


# Custom reducer function to merge metric dicts
def merge_metrics(left: Dict[str, float], right: Dict[str, float]) -> Dict[str, float]:
    """Combines metric dictionaries, keeping the latest timestamp/value."""
    merged = left.copy() if left else {}
    if right:
        merged.update(right)
    return merged


# 1. State Schema with Reducers
class IncidentInvestigationState(TypedDict):
    incident_id: str
    # 'audit_trail' appends new string entries using operator.add
    audit_trail: Annotated[List[str], operator.add]
    # 'telemetry' updates keys using custom reducer
    telemetry: Annotated[Dict[str, float], merge_metrics]
    severity: str


# 2. Node 1: Ingest Alert
def ingest_node(state: IncidentInvestigationState) -> dict:
    print(" [Node: ingest_alert] Parsing incoming webhook payload...")
    return {
        "audit_trail": [f"[{state['incident_id']}] Alert ingested: Ingress 5xx spike detected."],
        "telemetry": {"ingress_5xx_rate": 0.14, "cpu_usage": 0.85},
        "severity": "HIGH"
    }


# 3. Node 2: Analyze Metrics
def metric_node(state: IncidentInvestigationState) -> dict:
    print(" [Node: analyze_metrics] Correlating telemetry data...")
    return {
        "audit_trail": ["[METRICS] Correlated with database connection pool exhaustion."],
        "telemetry": {"db_connection_pool_active": 98.0, "db_wait_queue_ms": 420.0}
    }


# 4. Node 3: Synthesize Findings
def synthesize_node(state: IncidentInvestigationState) -> dict:
    print(" [Node: synthesize] Assembling preliminary incident report...")
    return {
        "audit_trail": ["[SYNTHESIS] Root cause identified as DB connection pool saturation."]
    }


def main():
    print("=" * 70)
    print("  MODULE 02: CUSTOM STATE REDUCERS & CHANNEL MERGING")
    print("=" * 70)

    # Build 3-node graph
    builder = StateGraph(IncidentInvestigationState)
    builder.add_node("ingest", ingest_node)
    builder.add_node("metric_analyzer", metric_node)
    builder.add_node("synthesize", synthesize_node)

    builder.add_edge(START, "ingest")
    builder.add_edge("ingest", "metric_analyzer")
    builder.add_edge("metric_analyzer", "synthesize")
    builder.add_edge("synthesize", END)

    graph = builder.compile()

    initial_state: IncidentInvestigationState = {
        "incident_id": "INC-8921",
        "audit_trail": ["Initialization started."],
        "telemetry": {},
        "severity": "UNKNOWN"
    }

    config = {
        "run_name": "custom-reducers-run",
        "tags": ["module:02_state", "reducer:operator.add"]
    }

    print("\n▶️ Invoking Graph with Multi-Node Reducers...")
    result = graph.invoke(initial_state, config=config)

    print("\n" + "-" * 70)
    print(f"🎯 Incident ID: {result['incident_id']} (Severity: {result['severity']})")
    print("\n📜 Consolidated Audit Trail (Appended via operator.add):")
    for step in result["audit_trail"]:
        print(f"  • {step}")

    print("\n📊 Consolidated Telemetry Map (Merged via custom reducer):")
    for k, v in result["telemetry"].items():
        print(f"  • {k.ljust(30)}: {v}")
    print("-" * 70)
    print("✅ Completed Script 02 successfully!\n")


if __name__ == "__main__":
    main()
