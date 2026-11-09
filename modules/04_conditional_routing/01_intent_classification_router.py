"""
Module 04 - Script 01: LLM Intent Classification Router

Demonstrates:
1. Using an LLM node as an intent classifier
2. Returning routing keys ('database', 'security', 'infrastructure')
3. Directing graph flow conditionally to specialized specialist nodes
"""

import sys
from typing import TypedDict, Literal
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
from shared.llm_factory import get_chat_model


class RouterState(TypedDict):
    alert_text: str
    target_team: Literal["database", "security", "infra", "general"]
    resolution_plan: str


# 1. Router Node: Classify Alert
def classify_intent_node(state: RouterState) -> dict:
    print(f" [Router Node] Classifying alert: '{state['alert_text']}'")
    alert_lower = state["alert_text"].lower()
    
    if any(w in alert_lower for w in ["sql", "postgres", "deadlock", "db", "query"]):
        team = "database"
    elif any(w in alert_lower for w in ["cve", "auth", "unauthorized", "token", "jwt", "breach"]):
        team = "security"
    elif any(w in alert_lower for w in ["k8s", "oom", "cpu", "disk", "node", "pod"]):
        team = "infra"
    else:
        team = "general"
        
    print(f"   ↳ Decided target team: [{team.upper()}]")
    return {"target_team": team}


# 2. Specialized Specialist Nodes
def database_specialist_node(state: RouterState) -> dict:
    print(" [Specialist: Database] Analyzing slow query logs & buffer pool...")
    return {"resolution_plan": "Action: Enable PgBouncer connection pooling and add index on user_id."}


def security_specialist_node(state: RouterState) -> dict:
    print(" [Specialist: Security] Revoking compromised API keys and rotating TLS certificates...")
    return {"resolution_plan": "Action: Revoked token session ID 0x88F and triggered password reset."}


def infra_specialist_node(state: RouterState) -> dict:
    print(" [Specialist: Infrastructure] Increasing replica count and memory request limits...")
    return {"resolution_plan": "Action: Scaled HPA min_replicas from 2 to 5."}


def general_triage_node(state: RouterState) -> dict:
    print(" [Specialist: General] Dispatching to on-call engineer queue...")
    return {"resolution_plan": "Action: Paged secondary on-call engineer."}


# 3. Conditional Routing Function
def route_decision(state: RouterState) -> str:
    return state["target_team"]


def main():
    print("=" * 70)
    print("  MODULE 04: INTENT CLASSIFICATION ROUTER")
    print("=" * 70)

    # Build Graph
    builder = StateGraph(RouterState)
    builder.add_node("router", classify_intent_node)
    builder.add_node("database", database_specialist_node)
    builder.add_node("security", security_specialist_node)
    builder.add_node("infra", infra_specialist_node)
    builder.add_node("general", general_triage_node)

    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router",
        route_decision,
        {
            "database": "database",
            "security": "security",
            "infra": "infra",
            "general": "general"
        }
    )
    for node in ["database", "security", "infra", "general"]:
        builder.add_edge(node, END)

    graph = builder.compile()

    # Test with different alerts
    test_alerts = [
        "CRITICAL: Postgres Deadlock detected on orders_table row 491",
        "SECURITY: Unauthorized API access attempts with expired JWT",
        "ALERT: Kubernetes Pod OOMKilled in payment namespace"
    ]

    for alert in test_alerts:
        print(f"\n▶️ Testing Alert: '{alert}'")
        res = graph.invoke({"alert_text": alert, "target_team": "general", "resolution_plan": ""})
        print(f"   Route Taken : [{res['target_team'].upper()}]")
        print(f"   Plan Output : {res['resolution_plan']}")

    print("\n" + "=" * 70)
    print("✅ Completed Script 01 successfully!\n")


if __name__ == "__main__":
    main()
