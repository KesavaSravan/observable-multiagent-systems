"""
Module 06 - Script 04: Nested Trace Trees with LangSmith @traceable

Demonstrates:
1. Using LangSmith @traceable decorator on helper functions and sub-agents
2. Generating deeply nested hierarchical span trees
3. Inspecting parent-child trace execution times in LangSmith
"""

import sys
import time
from typing import TypedDict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langsmith import traceable
from langchain_core.tracers.context import collect_runs
from langgraph.graph import StateGraph, START, END
from shared.config import settings


# 1. Traceable low-level tool/worker functions
@traceable(name="query_log_aggregator", run_type="tool")
def fetch_logs(service: str) -> str:
    time.sleep(0.05)
    return f"Logs for {service}: Heap memory exceeded limits."


@traceable(name="query_prometheus_timeseries", run_type="tool")
def fetch_metrics(service: str) -> dict:
    time.sleep(0.05)
    return {"cpu": "92%", "mem": "98%"}


@traceable(name="researcher_agent_subflow", run_type="chain")
def run_researcher_subflow(service: str) -> dict:
    logs = fetch_logs(service)
    metrics = fetch_metrics(service)
    return {"findings": f"{logs} | Metrics: {metrics}"}


# 2. LangGraph state & nodes
class RootState(TypedDict):
    service: str
    investigation_summary: str


def investigation_node(state: RootState) -> dict:
    print(f" [Root Node] Dispatching investigation subflow for '{state['service']}'...")
    sub_res = run_researcher_subflow(state["service"])
    return {"investigation_summary": sub_res["findings"]}


def main():
    print("=" * 70)
    print("  MODULE 06: NESTED TRACE TREES WITH @TRACEABLE")
    print("=" * 70)

    builder = StateGraph(RootState)
    builder.add_node("investigator", investigation_node)
    builder.add_edge(START, "investigator")
    builder.add_edge("investigator", END)

    graph = builder.compile()

    config = {
        "run_name": "nested-multiagent-trace-demo",
        "tags": ["module:06_multiagent", "traceable:nested_tree"],
        "metadata": {"system": "k8s-telemetry-agent"}
    }

    print("\n▶️ Invoking Graph with Nested @traceable Functions...")
    with collect_runs() as cb:
        result = graph.invoke({"service": "order-processor", "investigation_summary": ""}, config=config)
        root_run = cb.traced_runs[0] if cb.traced_runs else None

    print("\n" + "-" * 70)
    print(f"🎯 Output: {result['investigation_summary']}")
    print("-" * 70)

    if root_run:
        print("\n🔍 LangSmith Nested Span Hierarchy:")
        print(f"   • Root Span: {root_run.name} (ID: {root_run.id})")
        print(f"     └─ investigation_node")
        print(f"          └─ researcher_agent_subflow")
        print(f"               ├─ query_log_aggregator")
        print(f"               └─ query_prometheus_timeseries")
        if settings.LANGCHAIN_API_KEY and not settings.LANGCHAIN_API_KEY.startswith("lsv2_pt_your"):
            print(f"   🔗 Trace URL: https://smith.langchain.com/o/default/projects/p/{settings.LANGCHAIN_PROJECT}/r/{root_run.id}")

    print("\n" + "=" * 70)
    print("🎉 Module 06 completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
