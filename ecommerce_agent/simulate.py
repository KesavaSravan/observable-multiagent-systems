"""
Continuous Multi-Cart Simulation Engine for Live Grafana Dashboard Testing
"""

import sys
import time
import random
import uuid
from pathlib import Path

# Reconfigure Windows stdout encoding for UTF-8 compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared.metrics import (
    start_metrics_server_once,
    track_ecommerce_cart,
    track_ecommerce_recovery,
    track_ecommerce_margin,
    track_ecommerce_overstock_cleared,
    track_ecommerce_hesitation,
    track_ecommerce_linter,
    track_ecommerce_merchandiser_hitl,
    track_tokens,
    NODE_LATENCY_HISTOGRAM
)
from shared.config import settings
from ecommerce_agent.data.catalog import ABANDONED_CART_PRESETS
from ecommerce_agent.tools.inventory_tools import sync_all_inventory_gauges, deplete_item_stock


def run_continuous_simulation(iterations: int = 25, delay_seconds: float = 1.5):
    print("\n" + "=" * 78)
    print(" 🚀  E-COMMERCE LIVE METRICS & MULTI-DASHBOARD TRAFFIC SIMULATOR")
    print("=" * 78)
    start_metrics_server_once(settings.PROMETHEUS_PORT)
    sync_all_inventory_gauges()
    print(f" 📊 Metrics Exporter Live: http://localhost:{settings.PROMETHEUS_PORT}/metrics")
    print(f" 📈 Dashboard 1 (LLM Tracker)      : http://localhost:3000/d/llm-agent-tracker")
    print(f" 🛒 Dashboard 2 (E-Commerce KPIs) : http://localhost:3000/d/ecommerce-cart-recovery")
    print(f" 📦 Real-Time SQLite Inventory    : Initialized & Synchronized")
    print("=" * 78 + "\n")

    models = [
        ("groq", "llama-3.3-70b-versatile", 0.0006),
        ("openai", "gpt-4o-mini", 0.0004),
        ("anthropic", "claude-3-5-haiku-20241022", 0.0008),
        ("google", "gemini-1.5-flash", 0.0002)
    ]

    clearance_skus = [
        "COFFEE-BEAN-02", "COFFEE-ACC-03", "COFFEE-SYRUP-04",
        "AUDIO-CASE-02", "AUDIO-CABLE-03", "AUDIO-STAND-04",
        "KB-REST-02", "DESK-MAT-03", "MONITOR-ARM-02",
        "FIT-MAT-02", "FIT-ELECTRO-03", "FIT-ROLLER-04",
        "CAM-STRAP-02", "CAM-CLEAN-03"
    ]

    for i in range(1, iterations + 1):
        preset = random.choice(ABANDONED_CART_PRESETS)
        cart_total = sum([item["price"] for item in preset["cart_items"]])
        c_name = preset["customer_name"]
        hesitation = preset["exit_point"]
        
        # 1. Ingest Cart
        track_ecommerce_cart(cart_total)
        track_ecommerce_hesitation(preset["exit_point"])

        # 2. Simulate Node Latency
        for node in ["intent_analyzer", "overstock_matcher", "margin_simulator", "copywriter", "copy_linter", "dispatcher"]:
            latency = random.uniform(0.12, 1.45)
            NODE_LATENCY_HISTOGRAM.labels(node_name=node, status="success").observe(latency)

        # 3. Simulate Economics
        discount_rate = random.choice([0.10, 0.15, 0.05])
        discount_usd = cart_total * discount_rate
        recovered_usd = cart_total - discount_usd + (35.0 if random.random() > 0.4 else 0.0)
        margin_pct = random.uniform(28.5, 42.0)

        track_ecommerce_recovery(recovered_usd, discount_usd, strategy="dynamic_bundle")
        track_ecommerce_margin(margin_pct)

        # 4. Overstock clearance & SQLite Real-Time Stock Depletion
        cleared_sku = random.choice(clearance_skus)
        dep_res = deplete_item_stock(cleared_sku, quantity=1, cart_id=preset["cart_id"])
        track_ecommerce_overstock_cleared(
            sku=cleared_sku,
            category=dep_res.get("category", "general"),
            units=1
        )

        # 5. Quality linter & HITL
        track_ecommerce_linter("first_attempt_pass" if random.random() > 0.2 else "self_corrected_pass")
        if cart_total > 500:
            track_ecommerce_merchandiser_hitl("human_approved" if random.random() > 0.15 else "human_rejected")
        else:
            track_ecommerce_merchandiser_hitl("auto_approved")

        # 6. LLM Token & Cost Attribution (Tagged with active project_id)
        prov, mod, base_cost = random.choice(models)
        p_tok = random.randint(450, 1800)
        c_tok = random.randint(120, 500)
        track_tokens(prov, mod, p_tok, c_tok, cost_usd=base_cost * random.uniform(0.8, 1.2))

        rem_stock = dep_res.get("remaining_stock", "N/A")
        print(f"[{i:02d}/{iterations:02d}] Cart {preset['cart_id']} ({c_name[:12]}) | Val: ${cart_total:>6.2f} | Recv: ${recovered_usd:>6.2f} ({margin_pct:.1f}% Margin) | Bundled: {cleared_sku} (Stock: {rem_stock})")
        time.sleep(delay_seconds)

    print("\n" + "=" * 78)
    print("✅ Completed Simulation Run! Check Grafana Dashboards to see the live metrics.")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    run_continuous_simulation(iterations=25, delay_seconds=1.5)
