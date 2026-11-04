"""
Warehouse Inventory & Real-Time Dynamic Overstock Matching Tools
"""

import time
from typing import List, Dict, Any
from langchain_core.tools import tool
from shared.metrics import TOOL_INVOCATIONS_COUNTER, track_inventory_stock
from ecommerce_agent.data.warehouse_db import (
    query_overstock_complements,
    get_product,
    deplete_stock,
    list_inventory_status
)


@tool
def search_overstock_accessories(category: str, compatibility_tag: str) -> List[Dict[str, Any]]:
    """
    Search warehouse inventory for high-margin, overstocked accessories that complement
    the customer's abandoned product in real time.

    Args:
        category: Product category (e.g. 'kitchen', 'audio', 'computing', 'fitness', 'photography').
        compatibility_tag: Specific compatibility tag (e.g. 'coffee', 'espresso', 'wireless', 'desk', 'cardio').
    """
    TOOL_INVOCATIONS_COUNTER.labels(tool_name="search_overstock_accessories", status="success").inc()
    time.sleep(0.04)
    matches = query_overstock_complements(category=category, compatibility_tag=compatibility_tag)
    return matches


@tool
def check_warehouse_stock(sku: str) -> Dict[str, Any]:
    """
    Verify live warehouse stock levels and unit cost for a specific product SKU from SQLite.
    """
    TOOL_INVOCATIONS_COUNTER.labels(tool_name="check_warehouse_stock", status="success").inc()
    item = get_product(sku)
    if not item:
        return {"error": f"SKU {sku} not found in live warehouse database."}
    return {
        "sku": item["sku"],
        "name": item["name"],
        "category": item["category"],
        "stock_units": item["stock_units"],
        "is_overstock": item["is_overstock"],
        "price": item["price"],
        "cogs": item["cogs"]
    }


def deplete_item_stock(sku: str, quantity: int = 1, cart_id: str = "") -> Dict[str, Any]:
    """
    Deducts stock from SQLite and updates Prometheus real-time gauge.
    """
    res = deplete_stock(sku=sku, quantity=quantity, cart_id=cart_id)
    if res.get("success"):
        track_inventory_stock(
            sku=res["sku"],
            name=res["name"],
            category=res["category"],
            units=res["remaining_stock"],
            is_overstock=res["is_overstock"]
        )
    return res


def sync_all_inventory_gauges():
    """Syncs all inventory SKU levels into Prometheus gauges."""
    for item in list_inventory_status():
        track_inventory_stock(
            sku=item["sku"],
            name=item["name"],
            category=item["category"],
            units=item["stock_units"],
            is_overstock=bool(item["is_overstock"])
        )
