"""
Autonomous E-Commerce Cart Recovery & Dynamic Merchandising Swarm
Interactive Terminal CLI Runner with Real-Time SQLite Inventory
"""

import sys
import os
import argparse
import uuid
import time
from pathlib import Path

# Reconfigure Windows stdout encoding for UTF-8 compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langgraph.checkpoint.sqlite import SqliteSaver
from shared.metrics import (
    start_metrics_server_once,
    track_ecommerce_cart,
    track_workflow_duration,
    track_agent_iterations
)
from shared.config import settings, update_env_file
from shared.llm_factory import prompt_model_selection, infer_provider_from_model
from ecommerce_agent.data.catalog import ABANDONED_CART_PRESETS, PRODUCT_CATALOG
from ecommerce_agent.core.graph import build_cart_recovery_graph
from ecommerce_agent.core.checkpoint import get_sqlite_checkpointer
from ecommerce_agent.tools.inventory_tools import sync_all_inventory_gauges, list_inventory_status


def print_agentic_workflow_diagram():
    """Prints a clear architectural diagram of the multi-agent swarm workflow."""
    print("""
==============================================================================
 🧭 CAPSTONE MULTI-AGENT STATEGRAPH ARCHITECTURE & WORKFLOW FLOW:
==============================================================================

  [ Abandoned Cart Telemetry Ingestion / Custom User Query ]
                             │
                             ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 1. 🔍 INTENT ANALYZER AGENT                                            │
  │    • Ingests checkout dwell, exit screen, cart value & customer tier   │
  │    • Diagnoses hesitation: price_hesitation | shipping_sticker_shock   │
  └──────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 2. 📦 OVERSTOCK MATCHER AGENT                                          │
  │    • Queries real-time SQLite warehouse for high-margin clearance stock│
  │    • Pairs complementary accessory (e.g. 78% margin clearance item)    │
  └──────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 3. ⚖️  MARGIN SIMULATOR TOOL AGENT                                     │
  │    • Solves unit economics sandbox: blended gross margin               │
  │    • Computes max permissible discount code (Target: Blended >= 30%)   │
  └──────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 4. 🛑 MERCHANDISER GATEKEEPER AGENT (HITL Safety Breakpoint)           │
  │    • Hard margin safety gate: Pauses execution if margin < 30%         │
  │    • Awaits Merchandiser review / policy auto-approval                 │
  └──────────────────────────────┬─────────────────────────────────────────┘
                                 │ (Approved by Merchandiser)
                                 ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 5. ✍️  COPYWRITER AGENT                                                 │
  │    • Crafts personalized omnichannel recovery copy (Email HTML + SMS)  │
  └──────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 6. 🧐 COPY LINTER AGENT (Self-Correction Loop)                         │
  │    • Audits spam keywords, discount accuracy & brand safety guardrail  │
  │    • 🔄 If score < 80: Loops back to Copywriter with critique          │
  └──────────────────────────────┬─────────────────────────────────────────┘
                                 │ (Passed Linter Quality Gate)
                                 ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 7. 🚀 DISPATCHER AGENT                                                 │
  │    • Registers dynamic promo code in coupon DB                         │
  │    • Decrements live SQLite inventory & updates Prometheus gauges      │
  │    • Dispatches recovery campaign across Email & SMS                   │
  └────────────────────────────────────────────────────────────────────────┘
==============================================================================
""")


def display_inventory_table():
    """Displays a formatted snapshot of live warehouse inventory."""
    items = list_inventory_status()
    print("\n" + "=" * 90)
    print(" 📦 REAL-TIME WAREHOUSE INVENTORY & CLEARANCE OVERSTOCK SNAPSHOT (SQLite)")
    print("=" * 90)
    print(f" {'SKU':<16} | {'CATEGORY':<12} | {'PRICE':<8} | {'COGS':<7} | {'STOCK':<6} | {'OVERSTOCK':<10} | {'BUNDLED'}")
    print("-" * 90)
    for i in items:
        ov = "🔥 YES" if i["is_overstock"] else "  NO"
        print(f" {i['sku']:<16} | {i['category'].capitalize():<12} | ${i['price']:<7.2f} | ${i['cogs']:<6.2f} | {i['stock_units']:<6} | {ov:<10} | {i['times_bundled']}")
    print("=" * 90 + "\n")


def display_agent_step(node_name: str, updates: dict, state: dict):
    """Displays real-time terminal indicators for the currently executing agent node."""
    time.sleep(0.2)  # Visual pacing for terminal observation

    if node_name == "intent_analyzer":
        reason = updates.get("hesitation_reason") or state.get("hesitation_reason", "unknown")
        summary = updates.get("hesitation_summary") or state.get("hesitation_summary", "")
        print("┌" + "─" * 76 + "┐")
        print("│ ⚡ [RUNNING] AGENT 1/7: INTENT ANALYZER AGENT                             │")
        print("└" + "─" * 76 + "┘")
        print(f"  • Mission     : Diagnosing cart abandonment from telemetry signals")
        print(f"  • Ingested    : Exit Screen='{state.get('exit_point')}', Dwell={state.get('dwell_seconds')}s, Value=${state.get('cart_total', 0):.2f}")
        print(f"  • Diagnosed   : Hesitation Reason = [{reason.upper()}]")
        print(f"  • LLM Insight : {summary}")
        print(f"  • Handover    -> Routing state to [Overstock Matcher Agent]\n")

    elif node_name == "overstock_matcher":
        matched = updates.get("matched_overstock_item") or state.get("matched_overstock_item") or {}
        print("┌" + "─" * 76 + "┐")
        print("│ ⚡ [RUNNING] AGENT 2/7: OVERSTOCK MATCHER AGENT                            │")
        print("└" + "─" * 76 + "┘")
        print(f"  • Mission     : Real-time SQLite warehouse inventory scan for clearance stock")
        print(f"  • Matched SKU : {matched.get('sku', 'N/A')} - {matched.get('name', 'None')}")
        print(f"  • Economics   : Retail ${matched.get('price', 0):.2f} | COGS ${matched.get('cogs', 0):.2f} | Live Stock: {matched.get('units_in_stock', 0)} units")
        print(f"  • Handover    -> Routing state to [Margin Simulator Tool Agent]\n")

    elif node_name == "margin_simulator":
        margin = updates.get("projected_gross_margin_pct", state.get("projected_gross_margin_pct", 0.0))
        passed = updates.get("passed_guardrail", state.get("passed_guardrail", False))
        req_hitl = updates.get("requires_hitl", state.get("requires_hitl", False))
        bundle_val = updates.get("bundle_retail_value", state.get("bundle_retail_value", 0.0))
        pay_price = updates.get("customer_pay_price", state.get("customer_pay_price", 0.0))
        discount = updates.get("discount_amount_usd", state.get("discount_amount_usd", 0.0))
        print("┌" + "─" * 76 + "┐")
        print("│ ⚡ [RUNNING] AGENT 3/7: MARGIN SIMULATOR TOOL AGENT                        │")
        print("└" + "─" * 76 + "┘")
        print(f"  • Mission     : Unit economics simulation & dynamic bundle pricing sandbox")
        print(f"  • Bundle Value: Total Retail = ${bundle_val:.2f} | Customer Pays = ${pay_price:.2f}")
        print(f"  • Discount    : Free Clearance Add-On (-${discount:.2f} savings)")
        print(f"  • Margin Math : Blended Gross Margin = {margin:.1f}% ({'✅ PASS (Above 30% Floor)' if passed else '⚠️ MARGIN DEFICIT'})")
        print(f"  • HITL Needed : {'Yes (Operator approval required)' if req_hitl else 'No (Auto-approved by policy)'}")
        print(f"  • Handover    -> Routing state to [Merchandiser Gatekeeper Agent]\n")

    elif node_name == "gatekeeper":
        status = updates.get("execution_status", state.get("execution_status", ""))
        print("┌" + "─" * 76 + "┐")
        print("│ ⚡ [RUNNING] AGENT 4/7: MERCHANDISER GATEKEEPER AGENT                      │")
        print("└" + "─" * 76 + "┘")
        print(f"  • Mission     : Executive margin policy enforcement & operator gate")
        print(f"  • Verdict     : Status = {status.upper()} (Note: {state.get('human_notes', 'Approved by Merchandiser')})")
        next_agent = "Copywriter Agent" if status != "rejected" else "Dispatcher Agent"
        print(f"  • Handover    -> Routing state to [{next_agent}]\n")

    elif node_name == "copywriter":
        subj = updates.get("generated_email_subject", state.get("generated_email_subject", ""))
        sms_preview = updates.get("generated_sms_text", state.get("generated_sms_text", ""))
        if len(sms_preview) > 65:
            sms_preview = sms_preview[:65] + "..."
        print("┌" + "─" * 76 + "┐")
        print("│ ⚡ [RUNNING] AGENT 5/7: COPYWRITER AGENT                                   │")
        print("└" + "─" * 76 + "┘")
        print(f"  • Mission     : Multichannel high-conversion recovery copy generation")
        print(f"  • Email Subj  : \"{subj}\"")
        print(f"  • SMS Preview : \"{sms_preview}\"")
        print(f"  • Handover    -> Routing state to [Copy Linter Agent]\n")

    elif node_name == "copy_linter":
        l_pass = updates.get("linter_pass", state.get("linter_pass", True))
        attempts = updates.get("linter_attempts", state.get("linter_attempts", 1))
        feedback = updates.get("linter_feedback", state.get("linter_feedback", "Passed quality audit."))
        print("┌" + "─" * 76 + "┐")
        print("│ ⚡ [RUNNING] AGENT 6/7: COPY LINTER AGENT (Self-Correction Loop)           │")
        print("└" + "─" * 76 + "┘")
        print(f"  • Mission     : Brand compliance, spam audit & anti-hallucination verification")
        print(f"  • Evaluation  : Quality Gate = {'✅ PASS' if l_pass else '❌ REJECT (Triggering Self-Correction Loop)'} (Iteration: {attempts}/2)")
        print(f"  • Feedback    : {feedback}")
        next_dest = "Dispatcher Agent" if l_pass or attempts >= 2 else "Copywriter Agent (Looping Back)"
        print(f"  • Handover    -> Routing state to [{next_dest}]\n")

    elif node_name == "dispatcher":
        status = updates.get("execution_status", state.get("execution_status", ""))
        print("┌" + "─" * 76 + "┐")
        print("│ ⚡ [RUNNING] AGENT 7/7: DISPATCHER AGENT                                   │")
        print("└" + "─" * 76 + "┘")
        print(f"  • Mission     : Final promo registration, live stock deduction & dispatch")
        print(f"  • Promo Code  : [{state.get('discount_code', 'N/A')}] (Registered live in database)")
        print(f"  • Channels    : Email -> {state.get('customer_email')} | SMS -> Confirmed")
        print(f"  • Final Status: {status.upper()}\n")


def run_ecommerce_cli():
    # Parse CLI flags for model/provider override
    parser = argparse.ArgumentParser(description="Autonomous E-Commerce Cart Recovery Swarm CLI")
    parser.add_argument("--provider", type=str, help="Override LLM provider for ecommerce project (e.g. groq, openai, google, anthropic)")
    parser.add_argument("--model", type=str, help="Override LLM model name for ecommerce project (e.g. llama-3.3-70b-versatile)")
    args, _ = parser.parse_known_args()

    env_updates = {}
    if args.model:
        m_val = args.model.strip()
        os.environ["PROJECT_ECOMMERCE_RECOVERY_DEFAULT_MODEL"] = m_val
        env_updates["PROJECT_ECOMMERCE_RECOVERY_DEFAULT_MODEL"] = m_val
        if not args.provider:
            inferred = infer_provider_from_model(m_val)
            if inferred:
                os.environ["PROJECT_ECOMMERCE_RECOVERY_PROVIDER"] = inferred
                env_updates["PROJECT_ECOMMERCE_RECOVERY_PROVIDER"] = inferred

    if args.provider:
        p_val = args.provider.lower().strip()
        os.environ["PROJECT_ECOMMERCE_RECOVERY_PROVIDER"] = p_val
        env_updates["PROJECT_ECOMMERCE_RECOVERY_PROVIDER"] = p_val

    if env_updates:
        update_env_file(env_updates)

    active_provider = (
        os.getenv("PROJECT_ECOMMERCE_RECOVERY_PROVIDER")
        or os.getenv("LLM_PROVIDER")
        or settings.LLM_PROVIDER
    ).upper()
    active_model = (
        os.getenv("PROJECT_ECOMMERCE_RECOVERY_DEFAULT_MODEL")
        or os.getenv("LLM_MODEL")
        or "default-model"
    )

    print("\n" + "=" * 78)
    print(" 🛒  AUTONOMOUS E-COMMERCE CART RECOVERY & HIGH-MARGIN BUNDLE SWARM")
    print("=" * 78)
    print(f" ⚙️  Project LLM Model       : [{active_provider}] -> {active_model} (Project: ecommerce_recovery)")

    # 1. Start Prometheus metrics server & sync inventory gauges
    start_metrics_server_once(settings.PROMETHEUS_PORT)
    sync_all_inventory_gauges()
    print(f" 📊 Prometheus Live Exporter : http://localhost:{settings.PROMETHEUS_PORT}/metrics")
    print(f" 📡 LangSmith Tracing Target : Project '{settings.LANGCHAIN_PROJECT}'")
    print(f" 📦 Real-Time SQLite DB      : Active & Synchronized")
    print("=" * 78)

    # 2. Display the Agentic Workflow Diagram BEFORE the user selects / inputs a query
    print_agentic_workflow_diagram()

    # 3. Select an Abandoned Cart Scenario or Enter Custom Query
    while True:
        curr_p = (
            os.getenv("PROJECT_ECOMMERCE_RECOVERY_PROVIDER")
            or os.getenv("LLM_PROVIDER")
            or settings.LLM_PROVIDER
        ).upper()
        curr_m = (
            os.getenv("PROJECT_ECOMMERCE_RECOVERY_DEFAULT_MODEL")
            or os.getenv("LLM_MODEL")
            or "default-model"
        )
        print("Select an Abandoned Cart Scenario:")
        for idx, preset in enumerate(ABANDONED_CART_PRESETS, 1):
            total = sum([i["price"] for i in preset["cart_items"]])
            print(f"  [{idx}] {preset['customer_name'].ljust(16)} | Cart: ${total:<6.2f} | Exit: {preset['exit_point'].ljust(20)}")
            print(f"      └─ Scenario: {preset['description']}")
        print(f"  [M] 🔄 Switch E-Commerce Model & Provider (Current: [{curr_p}] {curr_m})")
        print(f"  [I] 📦 Inspect Live Warehouse Inventory & Overstock Levels (SQLite)")
        print(f"  [C] ✍️  Custom Manual Query (Enter your own customer, product & exit reason)")

        choice = input("\nChoose Scenario [1-6/M/I/C] (Default: 1): ").strip().upper()
        if choice == "M":
            prompt_model_selection(project_id="ecommerce_recovery")
            continue
        elif choice == "I":
            display_inventory_table()
            continue
        break

    if choice == "2":
        selected = ABANDONED_CART_PRESETS[1]
    elif choice == "3":
        selected = ABANDONED_CART_PRESETS[2]
    elif choice == "4":
        selected = ABANDONED_CART_PRESETS[3]
    elif choice == "5":
        selected = ABANDONED_CART_PRESETS[4]
    elif choice == "6":
        selected = ABANDONED_CART_PRESETS[5]
    elif choice == "C":
        print("\n--- Enter Custom Cart Details ---")
        c_name = input("Customer Name (e.g. Alex Rivera): ").strip() or "Alex Rivera"
        c_email = input(f"Customer Email (default: {c_name.lower().replace(' ', '.')}@example.com): ").strip() or f"{c_name.lower().replace(' ', '.')}@example.com"
        tier = input("Customer Tier [VIP / REPEAT / FIRST_TIME] (Default: REPEAT): ").strip().upper() or "REPEAT"
        prod_name = input("Product Name (e.g. Premium Noise-Cancelling Headphones): ").strip() or "Custom Studio Headphones"
        cat = input("Category [audio / kitchen / computing / fitness / photography] (Default: audio): ").strip().lower() or "audio"
        price_in = input("Retail Price USD (e.g. 240.00): ").strip() or "240.00"
        cogs_in = input("Cost of Goods / COGS USD (e.g. 90.00): ").strip() or "90.00"
        exit_p = input("Exit Screen [shipping_calculator / payment_step / cart_view] (Default: payment_step): ").strip() or "payment_step"
        ship_in = input("Shipping Quote USD (e.g. 18.00): ").strip() or "18.00"
        dwell_in = input("Dwell Time Seconds (e.g. 240): ").strip() or "240"

        prod_price = float(price_in)
        prod_cogs = float(cogs_in)

        selected = {
            "cart_id": f"CART-{uuid.uuid4().hex[:4].upper()}",
            "customer_name": c_name,
            "customer_email": c_email,
            "customer_tier": tier,
            "cart_items": [{
                "sku": f"CUSTOM-{cat.upper()}-01",
                "name": prod_name,
                "category": cat,
                "price": prod_price,
                "cogs": prod_cogs,
                "compatibility_tags": [cat, "general"]
            }],
            "checkout_dwell_seconds": int(dwell_in),
            "exit_point": exit_p,
            "shipping_quote_usd": float(ship_in),
            "description": f"Custom manual query for {c_name} with {prod_name} (${prod_price:.2f})."
        }
    else:
        selected = ABANDONED_CART_PRESETS[0]

    cart_id = selected["cart_id"]
    thread_id = f"session-{cart_id}-{uuid.uuid4().hex[:4]}"
    cart_total = sum([i["price"] for i in selected["cart_items"]])

    track_ecommerce_cart(cart_total)

    # 4. Compile Graph with durable SQLite checkpointing
    checkpointer = get_sqlite_checkpointer()
    graph = build_cart_recovery_graph(checkpointer=checkpointer, enable_hitl=True)

    config = {
        "configurable": {"thread_id": thread_id},
        "tags": ["agent:ecommerce_recovery", f"cart:{cart_id}", f"tier:{selected['customer_tier']}"],
        "metadata": {"cart_id": cart_id, "customer": selected["customer_name"]}
    }

    initial_state = {
        "cart_id": cart_id,
        "customer_name": selected["customer_name"],
        "customer_email": selected["customer_email"],
        "customer_tier": selected["customer_tier"],
        "cart_items": selected["cart_items"],
        "cart_total": cart_total,
        "dwell_seconds": selected["checkout_dwell_seconds"],
        "exit_point": selected["exit_point"],
        "shipping_quote_usd": selected.get("shipping_quote_usd", 0.0),
        "hesitation_reason": "",
        "hesitation_summary": "",
        "matched_overstock_item": None,
        "bundle_retail_value": 0.0,
        "customer_pay_price": 0.0,
        "discount_amount_usd": 0.0,
        "discount_code": "",
        "projected_gross_margin_pct": 0.0,
        "passed_guardrail": True,
        "requires_hitl": False,
        "human_approved": None,
        "human_notes": "",
        "generated_email_subject": "",
        "generated_email_html": "",
        "generated_sms_text": "",
        "linter_attempts": 0,
        "linter_pass": False,
        "linter_feedback": "",
        "next_step": "intent_analyzer",
        "iteration": 0,
        "execution_status": "analyzing",
        "audit_log": [f"[INIT] Abandoned cart {cart_id} ingested (${cart_total:.2f})."]
    }

    print("\n" + "=" * 78)
    print(f"🚀 INGESTING ABANDONED CART: {cart_id}")
    print(f"   Customer: {selected['customer_name']} ({selected['customer_tier']} Tier)")
    print(f"   Value   : ${cart_total:.2f}")
    print(f"   Exit    : {selected['exit_point']} (Dwell: {selected['checkout_dwell_seconds']}s)")
    print("=" * 78 + "\n")

    start_time = time.time()

    # 5. Phase 1: Stream nodes in real time until Gatekeeper breakpoint
    print("⏳ [PHASE 1] Initiating Autonomous Agent Execution...\n")
    for chunk in graph.stream(initial_state, config=config, stream_mode="updates"):
        for node_name, output_data in chunk.items():
            curr_state = graph.get_state(config).values
            display_agent_step(node_name, output_data, curr_state)

    # 6. Check In-Flight State at Gatekeeper
    snapshot = graph.get_state(config)
    requires_hitl = snapshot.values.get("requires_hitl", False)

    if requires_hitl:
        print("🛑" * 39)
        print(" ⏸️  MERCHANDISER HUMAN-IN-THE-LOOP SAFETY GATEKEEPER REACHED")
        print("🛑" * 39)
        matched = snapshot.values.get("matched_overstock_item") or {}
        margin = snapshot.values.get("projected_gross_margin_pct", 0.0)
        passed = snapshot.values.get("passed_guardrail", False)

        print(f"\n📋 Proposed Bundle & Unit Economics:")
        print(f"  • Diagnosed Hesitation : {snapshot.values.get('hesitation_reason', '').upper()}")
        print(f"  • Primary Item(s)      : ${snapshot.values.get('cart_total', 0):.2f}")
        print(f"  • Bundled Accessory    : {matched.get('name', 'None')} (+${matched.get('price', 0):.2f} retail)")
        print(f"  • Total Retail Value   : ${snapshot.values.get('bundle_retail_value', 0):.2f}")
        print(f"  • Proposed Discount    : -${snapshot.values.get('discount_amount_usd', 0):.2f}")
        print(f"  • Customer Pay Price   : ${snapshot.values.get('customer_pay_price', 0):.2f}")
        print(f"  • Projected Net Margin : {margin:.1f}% ({'✅ PASS' if passed else '⚠️ MARGIN DEFICIT'})")

        print("\n--- Merchandiser Decision Required ---")
        print("  [A] APPROVE  -> Authorize bundle offer and generate recovery copy.")
        print("  [R] REJECT   -> Cancel offer to protect high-ticket margins.")

        op_choice = input("\nEnter Decision [A/R] (Default: A): ").strip().upper()
        is_approved = op_choice != "R"
        notes = "Approved by Merchandiser" if is_approved else "Rejected: protect catalog margin"

        # Update state with human decision
        graph.update_state(config, {
            "human_approved": is_approved,
            "human_notes": notes
        })
        print(f"  └─ Merchandiser Recorded: {'APPROVED ✅' if is_approved else 'REJECTED ❌'}\n")

    # 7. Phase 2: Resume Graph Execution and stream remaining nodes
    print("▶️ [PHASE 2] Resuming Swarm Execution (Gatekeeper ➔ Copywriter ➔ Linter ➔ Dispatcher)...\n")
    for chunk in graph.stream(None, config=config, stream_mode="updates"):
        for node_name, output_data in chunk.items():
            curr_state = graph.get_state(config).values
            display_agent_step(node_name, output_data, curr_state)

    final_snapshot = graph.get_state(config)
    final_res = final_snapshot.values
    duration = time.time() - start_time

    track_workflow_duration("ecommerce_cart_recovery", duration, final_res.get("execution_status"))
    track_agent_iterations("cart_recovery_graph", final_res.get("linter_attempts", 1), "completed")

    print("=" * 78)
    print(" 📨 GENERATED OMNICHANNEL RECOVERY ASSETS:")
    print("=" * 78)
    print(f"📧 EMAIL SUBJECT: {final_res.get('generated_email_subject')}")
    print(f"📱 SMS TEXT    : {final_res.get('generated_sms_text')}")
    print("-" * 78)
    print("📄 EMAIL HTML BODY (Preview):")
    html_body = final_res.get("generated_email_html", "")
    print(html_body[:320] + "\n...[truncated]..." if len(html_body) > 320 else html_body)
    print("=" * 78)

    print("\n📜 Autonomous Audit Trail:")
    for log in final_res.get("audit_log", []):
        print(f"  • {log}")

    print("\n" + "-" * 78)
    print("📊 Observability Dashboards:")
    print(f"  • Dashboard 1 (LLM & Technical SRE)   : http://localhost:3000/d/llm-agent-tracker")
    print(f"  • Dashboard 2 (E-Commerce Business)   : http://localhost:3000/d/ecommerce-cart-recovery")
    print(f"  • Raw Prometheus Metrics Exporter    : http://localhost:{settings.PROMETHEUS_PORT}/metrics")
    print("-" * 78)
    print(f"🎉 Cart Recovery Workflow Completed: Status = {final_res.get('execution_status', '').upper()}\n")
    print("=" * 78)
    print("📡 Prometheus Telemetry Server is running on http://localhost:8000/metrics")
    print("   Open Grafana now to inspect live charts: http://localhost:3000/d/llm-agent-tracker")
    input("👉 Press [Enter] to exit and stop the telemetry server...")


if __name__ == "__main__":
    run_ecommerce_cli()
