"""
Dynamic Coupon Code Generation & Dispatch Tools
"""

import time
import uuid
from typing import Dict, Any
from langchain_core.tools import tool
from shared.metrics import TOOL_INVOCATIONS_COUNTER


@tool
def generate_dynamic_coupon(cart_id: str, discount_type: str, discount_value: float) -> Dict[str, Any]:
    """
    Generate an authenticated, one-time promotional coupon code in Shopify / E-Commerce engine.

    Args:
        cart_id: The ID of the abandoned cart.
        discount_type: 'PERCENTAGE', 'FIXED_AMOUNT', or 'FREE_SHIPPING'.
        discount_value: The numerical value (e.g. 15 for 15% or 20.0 for $20).
    """
    TOOL_INVOCATIONS_COUNTER.labels(tool_name="generate_dynamic_coupon", status="success").inc()
    time.sleep(0.02)

    suffix = uuid.uuid4().hex[:4].upper()
    if discount_type == "FREE_SHIPPING":
        code = f"FREESHIP-{suffix}"
    elif discount_type == "PERCENTAGE":
        code = f"SAVE{int(discount_value)}-{suffix}"
    else:
        code = f"BUNDLE{int(discount_value)}-{suffix}"

    return {
        "coupon_code": code,
        "discount_type": discount_type,
        "discount_value": discount_value,
        "valid_hours": 24,
        "cart_id": cart_id,
        "status": "active"
    }


@tool
def dispatch_omnichannel_offer(customer_email: str, subject: str, html_preview: str, sms_text: str) -> Dict[str, Any]:
    """
    Simulates sending the generated personalized recovery offer via SendGrid (Email) and Twilio (SMS).
    """
    TOOL_INVOCATIONS_COUNTER.labels(tool_name="dispatch_omnichannel_offer", status="success").inc()
    time.sleep(0.05)
    return {
        "status": "delivered",
        "email_recipient": customer_email,
        "subject": subject,
        "sms_character_count": len(sms_text),
        "channels": ["email_sendgrid", "sms_twilio"],
        "delivered_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
