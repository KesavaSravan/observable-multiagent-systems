"""
E-Commerce Cart Recovery Multi-Agent Graph Architecture
"""

from typing import Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.sqlite import SqliteSaver

from ecommerce_agent.core.state import CartRecoveryState
from ecommerce_agent.agents.intent_analyzer import intent_analyzer_agent
from ecommerce_agent.agents.overstock_matcher import overstock_matcher_agent
from ecommerce_agent.agents.margin_simulator import margin_simulator_agent
from ecommerce_agent.agents.merchandiser_gatekeeper import merchandiser_gatekeeper_agent
from ecommerce_agent.agents.copywriter import copywriter_agent
from ecommerce_agent.agents.copy_linter import copy_linter_agent
from ecommerce_agent.agents.dispatcher import dispatcher_agent


def route_after_gatekeeper(state: CartRecoveryState) -> str:
    """If merchandiser rejected, skip copy generation and go directly to cancel in dispatcher."""
    status = state.get("execution_status")
    if status == "rejected":
        return "dispatcher"
    return "copywriter"


def route_after_linter(state: CartRecoveryState) -> str:
    """If copy linter fails and attempts < 2, loop back to copywriter for self-correction."""
    linter_pass = state.get("linter_pass", True)
    attempts = state.get("linter_attempts", 1)
    if not linter_pass and attempts < 2:
        return "copywriter"
    return "dispatcher"


def build_cart_recovery_graph(
    checkpointer: Optional[BaseCheckpointSaver] = None,
    enable_hitl: bool = True
):
    """
    Builds the LangGraph multi-agent state graph for autonomous cart recovery.
    Includes the self-correction linter loop and the Merchandiser HITL breakpoint.
    """
    builder = StateGraph(CartRecoveryState)

    # 1. Register Nodes
    builder.add_node("intent_analyzer", intent_analyzer_agent)
    builder.add_node("overstock_matcher", overstock_matcher_agent)
    builder.add_node("margin_simulator", margin_simulator_agent)
    builder.add_node("gatekeeper", merchandiser_gatekeeper_agent)
    builder.add_node("copywriter", copywriter_agent)
    builder.add_node("copy_linter", copy_linter_agent)
    builder.add_node("dispatcher", dispatcher_agent)

    # 2. Add Linear Edges
    builder.add_edge(START, "intent_analyzer")
    builder.add_edge("intent_analyzer", "overstock_matcher")
    builder.add_edge("overstock_matcher", "margin_simulator")
    builder.add_edge("margin_simulator", "gatekeeper")

    # 3. Add Conditional Gatekeeper Edge
    builder.add_conditional_edges(
        "gatekeeper",
        route_after_gatekeeper,
        {
            "copywriter": "copywriter",
            "dispatcher": "dispatcher"
        }
    )

    # 4. Copywriter to Linter
    builder.add_edge("copywriter", "copy_linter")

    # 5. Add Self-Correction Loop Edge
    builder.add_conditional_edges(
        "copy_linter",
        route_after_linter,
        {
            "copywriter": "copywriter",
            "dispatcher": "dispatcher"
        }
    )

    builder.add_edge("dispatcher", END)

    # 6. HITL Breakpoint on Gatekeeper Node
    interrupt_nodes = ["gatekeeper"] if enable_hitl else []

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupt_nodes
    )
