"""
Agent 2: Warehouse Inventory & Overstock Matching Sub-Agent
"""

from shared.metrics import instrument_node, track_ecommerce_overstock_cleared
from ecommerce_agent.core.state import CartRecoveryState
from ecommerce_agent.tools.inventory_tools import search_overstock_accessories


@instrument_node(node_name="overstock_matcher_node")
def overstock_matcher_agent(state: CartRecoveryState) -> dict:
    """
    Scans the warehouse inventory for high-margin, overstocked accessories
    that pair naturally with the customer's cart items.
    """
    items = state.get("cart_items", [])
    primary_item = items[0] if items else {}
    category = primary_item.get("category", "computing")
    tags = primary_item.get("compatibility_tags", ["desk"])
    first_tag = tags[0] if tags else "general"

    # Query warehouse inventory for overstock accessories
    candidates = search_overstock_accessories.invoke({
        "category": category,
        "compatibility_tag": first_tag
    })

    if candidates:
        best_match = candidates[0]
        audit_msg = (
            f"[INVENTORY MATCHER] Matched primary item '{primary_item.get('name')}' with "
            f"overstock accessory '{best_match.get('name')}' ({best_match.get('margin_pct')}% margin, "
            f"{best_match.get('units_in_stock')} units in warehouse)."
        )
    else:
        best_match = None
        audit_msg = f"[INVENTORY MATCHER] No compatible overstock accessory found for category: {category}."

    return {
        "matched_overstock_item": best_match,
        "audit_log": [audit_msg]
    }
