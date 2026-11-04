"""
Agent 4: Omnichannel Copywriter & Offer Personalizer
"""

from shared.metrics import instrument_node
from shared.llm_factory import get_chat_model
from ecommerce_agent.core.state import CartRecoveryState


@instrument_node(node_name="copywriter_node")
def copywriter_agent(state: CartRecoveryState) -> dict:
    """
    Generates tailored, persuasive recovery messaging (responsive HTML email + SMS)
    customized to the customer's specific hesitation and including the approved bundle offer.
    Supports self-correction loops when linter feedback is present.
    """
    c_name = state.get("customer_name", "Valued Customer")
    items = state.get("cart_items", [])
    primary_name = items[0].get("name") if items else "your selected item"
    matched = state.get("matched_overstock_item")
    acc_name = matched.get("name") if matched else ""
    code = state.get("discount_code", "SAVE10")
    pay_price = state.get("customer_pay_price", 0.0)
    discount_usd = state.get("discount_amount_usd", 0.0)
    hesitation = state.get("hesitation_reason", "")
    feedback = state.get("linter_feedback", "")
    attempts = state.get("linter_attempts", 0) + 1

    model = get_chat_model(project_id="ecommerce_recovery", allow_mock_fallback=True)

    feedback_instruction = ""
    if feedback:
        feedback_instruction = (
            f"\nATTENTION - PREVIOUS DRAFT FAILED QUALITY LINTING:\n"
            f"Fix this issue in this new draft: {feedback}\n"
        )

    prompt = (
        f"You are a World-Class Direct Response Copywriter for high-growth e-commerce brands.\n"
        f"Recipient: {c_name}\n"
        f"Primary Product: {primary_name}\n"
        f"Bundled Complimentary Item: {acc_name}\n"
        f"Customer Pay Price: ${pay_price:.2f} (Savings: ${discount_usd:.2f} off)\n"
        f"Unique Coupon Code: {code}\n"
        f"Diagnosed Hesitation: {hesitation}\n"
        f"{feedback_instruction}\n"
        f"Generate two assets in this EXACT format:\n"
        f"SUBJECT: <Catchy, high-open-rate subject line under 60 chars>\n"
        f"SMS: <Concise, personalized SMS under 160 chars including coupon code {code}>\n"
        f"HTML: <A clean, styled HTML email container highlighting the bundle savings and coupon code {code}>"
    )

    resp = model.invoke(prompt)
    content = resp.content if hasattr(resp, "content") else str(resp)

    # Parse sections
    subject = f"Your exclusive offer on {primary_name[:25]}"
    sms_text = f"Hi {c_name.split()[0]}! Complete your {primary_name[:20]} bundle & save ${discount_usd:.0f} with code {code}. Order today!"
    html_body = (
        f"<div style='font-family: sans-serif; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;'>"
        f"<h2 style='color: #2c3e50;'>We saved your {primary_name}!</h2>"
        f"<p>Hi {c_name}, we noticed you left your cart behind.</p>"
        f"<p>To make this an easy decision, we added a complimentary <strong>{acc_name}</strong> to your order!</p>"
        f"<div style='background: #f8f9fa; padding: 15px; border-radius: 6px; margin: 20px 0;'>"
        f"<p style='margin: 0; font-size: 18px;'>Bundle Total: <strong>${pay_price:.2f}</strong> "
        f"(<span style='color: #27ae60;'>Save ${discount_usd:.2f}</span>)</p>"
        f"<p style='margin: 8px 0 0 0;'>Use Code: <code style='font-size: 20px; color: #e74c3c;'>{code}</code></p>"
        f"</div>"
        f"<a href='#' style='background: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;'>Complete My Bundle ➔</a>"
        f"</div>"
    )

    lines = content.splitlines()
    for line in lines:
        if line.startswith("SUBJECT:"):
            subject = line.replace("SUBJECT:", "").strip()
        elif line.startswith("SMS:"):
            sms_text = line.replace("SMS:", "").strip()

    if "<html>" in content.lower() or "<div" in content:
        html_body = content

    return {
        "generated_email_subject": subject,
        "generated_sms_text": sms_text,
        "generated_email_html": html_body,
        "linter_attempts": attempts,
        "linter_feedback": "", # Clear feedback for next inspection
        "audit_log": [f"[COPYWRITER] Drafted personalized offer email & SMS (Attempt {attempts})."]
    }
