"""
Agent 3: Unit Economics & Margin Simulation Sub-Agent
"""

from shared.metrics import instrument_node, track_ecommerce_margin, track_ecommerce_recovery
from ecommerce_agent.core.state import CartRecoveryState
from ecommerce_agent.tools.margin_sandbox_tool import simulate_bundle_economics
from ecommerce_agent.tools.coupon_tools import generate_dynamic_coupon


@instrument_node(node_name="margin_simulator_node")
def margin_simulator_agent(state: CartRecoveryState) -> dict:
    """
    Executes Python math sandbox to model the bundle economics and determine
    whether the offer preserves the store's minimum 30% gross margin target.
    """
    cart_items = state.get("cart_items", [])
    primary = cart_items[0] if cart_items else {}
    base_price = primary.get("price", 0.0)
    base_cogs = primary.get("cogs", 0.0)

    matched = state.get("matched_overstock_item") or {}
    acc_price = matched.get("price", 0.0)
    acc_cogs = matched.get("cogs", 0.0)

    hesitation = state.get("hesitation_reason", "price_hesitation")
    shipping_quote = state.get("shipping_quote_usd", 0.0)

    # Strategy formulation
    if hesitation == "shipping_sticker_shock":
        discount_pct = 5.0
        waive_shipping = True
    elif hesitation == "price_hesitation":
        discount_pct = 15.0
        waive_shipping = False
    else: # missing accessory
        discount_pct = 10.0
        waive_shipping = False

    # Execute math sandbox tool
    sim = simulate_bundle_economics.invoke({
        "base_price": base_price,
        "base_cogs": base_cogs,
        "accessory_price": acc_price,
        "accessory_cogs": acc_cogs,
        "discount_pct": discount_pct,
        "waive_shipping": waive_shipping,
        "shipping_cost": shipping_quote,
        "minimum_margin_threshold": 30.0
    })

    # Generate dynamic one-time coupon
    coupon_info = generate_dynamic_coupon.invoke({
        "cart_id": state.get("cart_id"),
        "discount_type": "PERCENTAGE" if not waive_shipping else "FREE_SHIPPING",
        "discount_value": discount_pct
    })

    margin_pct = sim["gross_margin_pct"]
    passed_guardrail = sim["passed_margin_guardrail"]
    total_val = sim["total_retail_value"]

    # HITL policy: trigger human review if margin < 30% OR cart value > $500
    requires_hitl = (not passed_guardrail) or (total_val > 500.0)

    # Track metrics
    track_ecommerce_margin(margin_pct)
    track_ecommerce_recovery(
        recovered_usd=sim["customer_pay_price"],
        discount_burned_usd=sim["discount_amount_usd"],
        strategy="dynamic_bundle"
    )

    audit_msg = (
        f"[MARGIN SIMULATOR] Simulated Bundle: Retail ${sim['total_retail_value']:.2f} -> "
        f"Customer Pays ${sim['customer_pay_price']:.2f} (Profit: ${sim['net_gross_profit_usd']:.2f}, "
        f"{margin_pct:.1f}% Margin). HITL Required: {requires_hitl}"
    )

    return {
        "bundle_retail_value": sim["total_retail_value"],
        "customer_pay_price": sim["customer_pay_price"],
        "discount_amount_usd": sim["discount_amount_usd"],
        "discount_code": coupon_info["coupon_code"],
        "projected_gross_margin_pct": margin_pct,
        "passed_guardrail": passed_guardrail,
        "requires_hitl": requires_hitl,
        "human_approved": None if requires_hitl else True,
        "human_notes": "Auto-approved by policy" if not requires_hitl else "",
        "audit_log": [audit_msg]
    }
