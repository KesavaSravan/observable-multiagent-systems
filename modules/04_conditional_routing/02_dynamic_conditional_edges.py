"""
Module 04 - Script 02: Dynamic Conditional Edges with Fallback Resilience

Demonstrates:
1. Routing logic with confidence scores
2. Routing to a fallback triage node when confidence is low
3. Safe error trapping inside routing functions
"""

import sys
from typing import TypedDict, Optional
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


class DiagnosticState(TypedDict):
    telemetry_input: str
    confidence_score: float
    selected_path: str
    diagnostic_summary: str


def evaluate_telemetry_node(state: DiagnosticState) -> dict:
    inp = state["telemetry_input"]
    print(f" [Node: evaluate_telemetry] Analyzing input: '{inp}'")
    
    # Simulate scoring
    if "p99 > 5000ms" in inp:
        return {"confidence_score": 0.95, "selected_path": "auto_mitigate"}
    elif "intermittent" in inp:
        return {"confidence_score": 0.40, "selected_path": "manual_review"}
    else:
        return {"confidence_score": 0.10, "selected_path": "fallback_triage"}


def auto_mitigate_node(state: DiagnosticState) -> dict:
    print(" [Path: auto_mitigate] High confidence anomaly -> Triggering automated auto-scaler.")
    return {"diagnostic_summary": "Auto-scaling policy triggered successfully."}


def manual_review_node(state: DiagnosticState) -> dict:
    print(" [Path: manual_review] Medium confidence -> Generating Slack alert for on-call.")
    return {"diagnostic_summary": "Notification dispatched to #sre-oncall Slack channel."}


def fallback_triage_node(state: DiagnosticState) -> dict:
    print(" [Path: fallback_triage] Low confidence -> Logging telemetry to cold storage for audit.")
    return {"diagnostic_summary": "Telemetry archived to S3 bucket /audit-logs/unclassified."}


def route_with_confidence(state: DiagnosticState) -> str:
    score = state.get("confidence_score", 0.0)
    if score >= 0.8:
        return "auto_mitigate"
    elif score >= 0.3:
        return "manual_review"
    return "fallback_triage"


def main():
    print("=" * 70)
    print("  MODULE 04: DYNAMIC CONDITIONAL EDGES WITH FALLBACK")
    print("=" * 70)

    builder = StateGraph(DiagnosticState)
    builder.add_node("evaluator", evaluate_telemetry_node)
    builder.add_node("auto_mitigate", auto_mitigate_node)
    builder.add_node("manual_review", manual_review_node)
    builder.add_node("fallback_triage", fallback_triage_node)

    builder.add_edge(START, "evaluator")
    builder.add_conditional_edges(
        "evaluator",
        route_with_confidence,
        {
            "auto_mitigate": "auto_mitigate",
            "manual_review": "manual_review",
            "fallback_triage": "fallback_triage"
        }
    )
    for n in ["auto_mitigate", "manual_review", "fallback_triage"]:
        builder.add_edge(n, END)

    graph = builder.compile()

    cases = [
        "CRITICAL ALERT: p99 > 5000ms on search-api",
        "WARN: intermittent jitter observed on gateway",
        "UNKNOWN: metric stream packet checksum glitch"
    ]

    for c in cases:
        print(f"\n▶️ Running Case: '{c}'")
        res = graph.invoke({"telemetry_input": c, "confidence_score": 0.0, "selected_path": "", "diagnostic_summary": ""})
        print(f"   Confidence: {res['confidence_score']:.2f} -> Path: [{res['diagnostic_summary']}]")

    print("\n" + "=" * 70)
    print("✅ Completed Script 02 successfully!\n")


if __name__ == "__main__":
    main()
