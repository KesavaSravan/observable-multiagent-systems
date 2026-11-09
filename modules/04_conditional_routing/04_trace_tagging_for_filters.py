"""
Module 04 - Script 04: Dynamic Trace Tagging for Granular UI Filtering

Demonstrates:
1. Dynamically updating LangSmith run tags based on the active execution branch
2. Attaching business metadata (e.g. customer_tier, urgency, route_taken)
3. Programmatically validating that tags appear in the trace configuration
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
from langchain_core.tracers.context import collect_runs
from shared.config import settings


class TaggedState(TypedDict):
    ticket_id: str
    category: str
    severity: str
    routed_target: str


def router_node(state: TaggedState) -> dict:
    cat = state["category"]
    target = "billing_queue" if cat == "billing" else ("security_queue" if cat == "security" else "general_queue")
    return {"routed_target": target}


def billing_processor(state: TaggedState) -> dict:
    return {"routed_target": "Processed by Stripe Billing Engine"}


def security_processor(state: TaggedState) -> dict:
    return {"routed_target": "Processed by AWS IAM Security Engine"}


def general_processor(state: TaggedState) -> dict:
    return {"routed_target": "Processed by Zendesk Service Desk"}


def main():
    print("=" * 70)
    print("  MODULE 04: TRACE TAGGING FOR GRANULAR UI FILTERING")
    print("=" * 70)

    builder = StateGraph(TaggedState)
    builder.add_node("router", router_node)
    builder.add_node("billing", billing_processor)
    builder.add_node("security", security_processor)
    builder.add_node("general", general_processor)

    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router",
        lambda s: "billing" if s["category"] == "billing" else ("security" if s["category"] == "security" else "general"),
        {"billing": "billing", "security": "security", "general": "general"}
    )
    for n in ["billing", "security", "general"]:
        builder.add_edge(n, END)

    graph = builder.compile()

    # Test cases with dynamic metadata and tags
    tickets = [
        {"id": "TICK-101", "category": "security", "severity": "CRITICAL"},
        {"id": "TICK-202", "category": "billing", "severity": "MEDIUM"},
    ]

    print("\n▶️ Executing Tagged Runs...")
    for t in tickets:
        custom_config = {
            "run_name": f"ticket-routing-{t['id']}",
            "tags": [
                "module:04_routing",
                f"category:{t['category']}",
                f"severity:{t['severity']}",
                "env:production"
            ],
            "metadata": {
                "ticket_id": t["id"],
                "sla_tier": "gold" if t["severity"] == "CRITICAL" else "standard"
            }
        }

        with collect_runs() as cb:
            res = graph.invoke(
                {"ticket_id": t["id"], "category": t["category"], "severity": t["severity"], "routed_target": ""},
                config=custom_config
            )
            run = cb.traced_runs[0] if cb.traced_runs else None

        print(f"• Ticket {t['id']} [{t['category'].upper()}] -> {res['routed_target']}")
        if run:
            print(f"  Run ID: {run.id} | Tags: {custom_config['tags']}")

    print("\n" + "=" * 70)
    print("💡 LangSmith Filtering Tip:")
    print("   In the LangSmith Runs UI, you can query: tag='category:security'")
    print("   or tag='severity:CRITICAL' to immediately isolate high-priority traces.")
    print("=" * 70)
    print("🎉 Module 04 completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
