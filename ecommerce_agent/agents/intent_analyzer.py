"""
Agent 1: Cart Abandonment Intent & Hesitation Analyzer
"""

from shared.metrics import instrument_node, track_ecommerce_hesitation
from shared.llm_factory import get_chat_model
from ecommerce_agent.core.state import CartRecoveryState


@instrument_node(node_name="intent_analyzer_node")
def intent_analyzer_agent(state: CartRecoveryState) -> dict:
    """
    Analyzes session clickstream, exit point, dwell time, and cart contents
    to diagnose the exact reason for abandonment.
    """
    cart_id = state.get("cart_id")
    exit_point = state.get("exit_point", "")
    dwell = state.get("dwell_seconds", 0)
    shipping_quote = state.get("shipping_quote_usd", 0.0)
    customer_tier = state.get("customer_tier", "FIRST_TIME")
    items = state.get("cart_items", [])
    item_names = ", ".join([i.get("name", "Product") for i in items])

    # Rule-assisted LLM Intent Diagnosis
    if exit_point == "shipping_calculator" and shipping_quote > 15.0:
        inferred_reason = "shipping_sticker_shock"
    elif exit_point == "payment_step" and dwell > 180:
        inferred_reason = "price_hesitation"
    elif exit_point == "cart_view":
        inferred_reason = "missing_accessory"
    else:
        inferred_reason = "price_hesitation"

    # LLM Synthesis for nuanced customer understanding
    model = get_chat_model(project_id="ecommerce_recovery", allow_mock_fallback=True)
    prompt = (
        f"You are a Senior E-Commerce Merchandiser.\n"
        f"Customer Tier: {customer_tier}\n"
        f"Items in Cart: {item_names} (Total: ${state.get('cart_total', 0):.2f})\n"
        f"Dwell Time: {dwell} seconds\n"
        f"Exit Screen: {exit_point} (Shipping Quote: ${shipping_quote:.2f})\n"
        f"Inferred Reason: {inferred_reason}\n\n"
        f"Provide a 1-sentence diagnostic explanation of what caused the customer to abandon."
    )
    resp = model.invoke(prompt)
    summary = resp.content if hasattr(resp, "content") else str(resp)

    track_ecommerce_hesitation(inferred_reason)

    audit_msg = (
        f"[INTENT ANALYZER] Diagnosed cart {cart_id}: {inferred_reason.upper()} "
        f"(Dwell: {dwell}s, Exit: {exit_point})"
    )

    return {
        "hesitation_reason": inferred_reason,
        "hesitation_summary": summary.strip(),
        "audit_log": [audit_msg]
    }
