"""
Python Unit Economics Sandbox Tool for Margin & Profit Simulation
"""

import time
from typing import Dict, Any
from langchain_core.tools import tool
from shared.metrics import TOOL_INVOCATIONS_COUNTER


@tool
def simulate_bundle_economics(
    base_price: float,
    base_cogs: float,
    accessory_price: float,
    accessory_cogs: float,
    discount_pct: float = 0.0,
    waive_shipping: bool = False,
    shipping_cost: float = 0.0,
    minimum_margin_threshold: float = 30.0
) -> Dict[str, Any]:
    """
    Sandboxed mathematical simulator for e-commerce bundle pricing and margin protection.
    Computes exact gross profit, discounts, and checks compliance against store margin policy.

    Args:
        base_price: Retail price of primary abandoned item in USD.
        base_cogs: Cost of goods sold for primary item in USD.
        accessory_price: Retail price of bundled accessory item in USD.
        accessory_cogs: Cost of goods sold for bundled accessory in USD.
        discount_pct: Percentage discount applied to the bundle (e.g. 15 for 15%).
        waive_shipping: Whether free shipping is granted.
        shipping_cost: Actual shipping cost absorbed by store if waived.
        minimum_margin_threshold: Minimum allowable gross margin percentage (default: 30%).
    """
    TOOL_INVOCATIONS_COUNTER.labels(tool_name="simulate_bundle_economics", status="success").inc()
    time.sleep(0.02)

    total_retail_value = round(base_price + accessory_price, 2)
    discount_amount = round(total_retail_value * (discount_pct / 100.0), 2)
    customer_pay_price = round(total_retail_value - discount_amount, 2)
    
    total_cogs = round(base_cogs + accessory_cogs, 2)
    absorbed_shipping = round(shipping_cost if waive_shipping else 0.0, 2)
    
    # Net Gross Profit = Customer Pay Price - Total COGS - Absorbed Shipping
    net_gross_profit_usd = round(customer_pay_price - total_cogs - absorbed_shipping, 2)
    
    if customer_pay_price > 0:
        gross_margin_pct = round((net_gross_profit_usd / customer_pay_price) * 100.0, 2)
    else:
        gross_margin_pct = 0.0

    passed_guardrail = gross_margin_pct >= minimum_margin_threshold

    return {
        "total_retail_value": total_retail_value,
        "discount_pct": discount_pct,
        "discount_amount_usd": discount_amount,
        "customer_pay_price": customer_pay_price,
        "total_cogs": total_cogs,
        "absorbed_shipping_usd": absorbed_shipping,
        "net_gross_profit_usd": net_gross_profit_usd,
        "gross_margin_pct": gross_margin_pct,
        "minimum_margin_threshold": minimum_margin_threshold,
        "passed_margin_guardrail": passed_guardrail,
        "summary": (
            f"Bundle Retail: ${total_retail_value:.2f} | Customer Pays: ${customer_pay_price:.2f} "
            f"(-${discount_amount:.2f} off) | Net Profit: ${net_gross_profit_usd:.2f} "
            f"({gross_margin_pct:.1f}% Margin - {'PASS' if passed_guardrail else 'FAIL'})"
        )
    }
