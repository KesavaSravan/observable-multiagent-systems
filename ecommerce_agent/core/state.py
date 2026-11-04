"""
E-Commerce Cart Recovery State Schema
"""

from typing import TypedDict, List, Dict, Any, Optional


class CartRecoveryState(TypedDict):
    # 1. Ingestion Data
    cart_id: str
    customer_name: str
    customer_email: str
    customer_tier: str              # "VIP", "REPEAT", "FIRST_TIME"
    cart_items: List[Dict[str, Any]]
    cart_total: float
    dwell_seconds: int
    exit_point: str                  # "shipping_calculator", "payment_step", "cart_view"
    shipping_quote_usd: float

    # 2. Intent Analysis
    hesitation_reason: str           # "shipping_sticker_shock", "price_hesitation", "missing_accessory"
    hesitation_summary: str
    matched_overstock_item: Optional[Dict[str, Any]]

    # 3. Unit Economics & Margins
    bundle_retail_value: float
    customer_pay_price: float
    discount_amount_usd: float
    discount_code: str
    projected_gross_margin_pct: float
    passed_guardrail: bool
    requires_hitl: bool
    human_approved: Optional[bool]
    human_notes: str

    # 4. Copy Generation & Linter Loop
    generated_email_subject: str
    generated_email_html: str
    generated_sms_text: str
    linter_attempts: int
    linter_pass: bool
    linter_feedback: str

    # 5. Execution, Audit & Navigation
    next_step: str
    iteration: int
    execution_status: str            # "analyzing", "waiting_for_merchandiser", "dispatched", "rejected"
    audit_log: List[str]
