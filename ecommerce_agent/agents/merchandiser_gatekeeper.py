"""
Agent 6: Merchandiser Risk Gatekeeper & Human-in-the-Loop Node
"""

from shared.metrics import instrument_node, track_ecommerce_merchandiser_hitl
from ecommerce_agent.core.state import CartRecoveryState


@instrument_node(node_name="merchandiser_gatekeeper_node")
def merchandiser_gatekeeper_agent(state: CartRecoveryState) -> dict:
    """
    Evaluates policy constraints (e.g. margin < 30% or cart > $500).
    Acts as a Human-in-the-Loop breakpoint where an e-commerce merchandiser
    signs off on custom high-value discounts before customer transmission.
    """
    requires_hitl = state.get("requires_hitl", False)
    approved = state.get("human_approved")

    if not requires_hitl:
        track_ecommerce_merchandiser_hitl("auto_approved")
        status = "approved"
        audit = "[MERCHANDISER GATEKEEPER] ✅ Auto-approved by policy (Margin >= 30% & Value <= $500)."
    elif approved is True:
        track_ecommerce_merchandiser_hitl("human_approved")
        status = "approved"
        audit = f"[MERCHANDISER GATEKEEPER] 👤 Merchandiser human operator APPROVED offer. Notes: {state.get('human_notes', 'None')}"
    else:
        track_ecommerce_merchandiser_hitl("human_rejected")
        status = "rejected"
        audit = f"[MERCHANDISER GATEKEEPER] 🛑 Merchandiser human operator REJECTED offer. Notes: {state.get('human_notes', 'None')}"

    return {
        "execution_status": status,
        "audit_log": [audit]
    }
