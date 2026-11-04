"""
Agent 5: Copy Quality Linter & Self-Correction Verifier
"""

from shared.metrics import instrument_node, track_ecommerce_linter
from ecommerce_agent.core.state import CartRecoveryState


@instrument_node(node_name="copy_linter_node")
def copy_linter_agent(state: CartRecoveryState) -> dict:
    """
    Validates email HTML syntax, SMS character bounds, and coupon code presence.
    Triggers self-correction loops back to the copywriter if defects are detected.
    """
    sms = state.get("generated_sms_text", "")
    html = state.get("generated_email_html", "")
    code = state.get("discount_code", "")
    attempts = state.get("linter_attempts", 1)

    errors = []

    # Check 1: Coupon code presence
    if code and code not in sms and code not in html:
        errors.append(f"Missing coupon code '{code}' in promotional messaging.")

    # Check 2: SMS character length bounds
    if len(sms) > 220:
        errors.append(f"SMS length ({len(sms)} chars) exceeds maximum boundary of 220 characters.")

    # Check 3: HTML content presence
    if "<" not in html or ">" not in html:
        errors.append("Email draft is missing standard HTML markup container.")

    if errors:
        linter_pass = False
        feedback = "; ".join(errors)
        status_metric = "failed" if attempts >= 2 else "needs_retry"
        audit_msg = f"[LINTER] ⚠️ Quality check failed on attempt {attempts}: {feedback} -> Routing for self-correction."
    else:
        linter_pass = True
        feedback = ""
        status_metric = "self_corrected_pass" if attempts > 1 else "first_attempt_pass"
        audit_msg = f"[LINTER] ✅ Quality check PASSED on attempt {attempts}. Email & SMS verified for production."

    track_ecommerce_linter(status_metric)

    return {
        "linter_pass": linter_pass,
        "linter_feedback": feedback,
        "audit_log": [audit_msg]
    }
