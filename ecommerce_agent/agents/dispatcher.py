"""
Dispatcher Node: Omnichannel SendGrid/Twilio Transmission & Real-Time Stock Depletion
"""

from shared.metrics import instrument_node, track_ecommerce_overstock_cleared
from ecommerce_agent.core.state import CartRecoveryState
from ecommerce_agent.tools.coupon_tools import dispatch_omnichannel_offer
from ecommerce_agent.tools.inventory_tools import deplete_item_stock


@instrument_node(node_name="dispatcher_node")
def dispatcher_agent(state: CartRecoveryState) -> dict:
    """
    Final node that dispatches the approved coupon and personalized recovery
    assets via simulated SendGrid (Email) and Twilio (SMS), then decrements
    real-time stock in SQLite and updates Prometheus inventory metrics.
    """
    status = state.get("execution_status", "approved")
    c_email = state.get("customer_email", "customer@example.com")
    subject = state.get("generated_email_subject", "Special Offer")
    html = state.get("generated_email_html", "")
    sms = state.get("generated_sms_text", "")
    matched = state.get("matched_overstock_item")
    cart_id = state.get("cart_id", "")

    if status == "approved":
        res = dispatch_omnichannel_offer.invoke({
            "customer_email": c_email,
            "subject": subject,
            "html_preview": html[:100],
            "sms_text": sms
        })

        depletion_info = ""
        if matched and matched.get("sku"):
            matched_sku = matched.get("sku")
            dep_res = deplete_item_stock(sku=matched_sku, quantity=1, cart_id=cart_id)
            remaining = dep_res.get("remaining_stock", "N/A")
            track_ecommerce_overstock_cleared(
                sku=matched_sku,
                category=matched.get("category", "general"),
                units=1
            )
            depletion_info = f" | Cleared 1 unit of {matched_sku} (Warehouse stock: {remaining})"

        audit_msg = f"[DISPATCHER] 🚀 Transmitted personalized recovery offer to {c_email} via Email & SMS{depletion_info}."
        final_status = "dispatched"
    else:
        audit_msg = f"[DISPATCHER] 🚫 Offer delivery cancelled because operator rejected the discount."
        final_status = "cancelled"

    return {
        "execution_status": final_status,
        "audit_log": [audit_msg]
    }
