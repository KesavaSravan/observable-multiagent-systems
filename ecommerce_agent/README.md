# 🛒 High-Margin Cart Abandonment & Dynamic Bundle Recovery Agent

An enterprise-grade autonomous E-Commerce Merchandising multi-agent platform engineered with **LangGraph**, **LangSmith Distributed Tracing**, and **Dual Grafana Telemetry Dashboards**.

---

## 🎯 The Core Business Problem

Standard cart recovery tools (Klaviyo, Mailchimp) blast generic *"You left this in your cart! Here is 10% off"* emails. This has two massive flaws:
1. **Margin Erosion**: It gives away discounts to price-insensitive buyers who would have bought anyway.
2. **Ignored Context**: It fails to resolve *why* the customer abandoned (e.g. shipping sticker shock, missing accessories, or high-ticket hesitation).

This multi-agent platform solves this by:
* Diagnosing clickstream dwell time and exit point to identify the true hesitation reason.
* Searching warehouse stock for **high-margin overstocked accessories** (e.g. pairing an espresso machine with 80% margin artisan coffee beans).
* Running a **sandboxed Python math simulator** to guarantee the bundle preserves the store's **>= 30% gross margin target**.
* Enforcing **Human-in-the-Loop (HITL) Merchandiser approvals** on high-value carts (> $500) or margin deficits.
* Employing a **Self-Correction Linter Loop** (Reflexion pattern) to verify email HTML and SMS copy quality before customer transmission.

---

## 🏗️ Architectural Topology

```
                          ┌──────────────────────────────────────────────┐
                          │    INGEST ABANDONED CART EVENT               │
                          │ (Items, Dwell Time, Exit Screen, LTV Tier)   │
                          └──────────────────────┬───────────────────────┘
                                                 │
                                                 ▼
                          ┌──────────────────────────────────────────────┐
                          │ 🧠 1. INTENT & HESITATION ANALYZER AGENT     │
                          │ (Shipping Shock / Price Hesitation / Access.)│
                          └──────────────────────┬───────────────────────┘
                                                 │
                                                 ▼
                          ┌──────────────────────────────────────────────┐
                          │ 📦 2. INVENTORY & OVERSTOCK MATCHER AGENT    │
                          │ (Queries Warehouse Catalog for High-Margin)  │
                          └──────────────────────┬───────────────────────┘
                                                 │
                                                 ▼
                          ┌──────────────────────────────────────────────┐
                          │ 🧮 3. UNIT ECONOMICS SANDBOX (Python REPL)   │
                          │ (Simulates Net Margin % & Generates Coupon)  │
                          └──────────────────────┬───────────────────────┘
                                                 │
                                                 ▼
                          ┌──────────────────────────────────────────────┐
                          │ 🛡️ 4. MERCHANDISER RISK GATEKEEPER (HITL)    │
                          │ (Pauses on Cart > $500 or Margin Deficit)    │
                          └──────────────┬───────────────────────────────┘
                                         │
                         Approved by HITL│or Auto-Passed
                                         ▼
                          ┌──────────────────────────────────────────────┐
                          │ ✍️ 5. OMNICHANNEL COPYWRITER AGENT           │
                          │ (Generates Personalized HTML Email + SMS)    │
                          └──────────────┬───────────────────────────────┘
                                         │
                                         ▼
                          ┌──────────────────────────────────────────────┐
                          │ 🧪 6. QUALITY LINTER & SELF-CORRECTION       │
                          │ (Validates Coupon, HTML, SMS character count)│
                          └──────────────┬───────────────┬───────────────┘
                                         │               │
                            Passed Check │               │ Failed (< 2 attempts)
                                         │               │ (Routes Back for Self-Correction)
                                         │               └───────────────┐
                                         │                               │
                                         ▼                               ▼
                          ┌──────────────────────────────┐   ┌───────────────────────────┐
                          │ 🚀 7. OMNICHANNEL DISPATCHER │   │ 🔄 RETRY WITH LINTER      │
                          │ (Simulated SendGrid + Twilio)│   │    FEEDBACK (Reflexion)   │
                          └──────────────┬───────────────┘   └───────────────────────────┘
                                         │
                                         ▼
                          ┌──────────────────────────────┐
                          │ 📊 PROMETHEUS / GRAFANA &    │
                          │    LANGSMITH DISTRIBUTED     │
                          └──────────────────────────────┘
```

---

## 📊 Dual Grafana Dashboards

The system provisions **two distinct dashboards** in Grafana:

### 1. Dashboard 1: LLM & Multi-Agent SRE Performance Tracker
* **URL**: [http://localhost:3000/d/llm-agent-tracker](http://localhost:3000/d/llm-agent-tracker)
* **Metrics**:
  * Per-Model Cost Burn Rate (`$/hr`) and Cumulative Spend ($)
  * Token Velocity (`prompt` vs `completion` tokens/min)
  * P95 Node Latency & Error Invocations with **1-click deep links to LangSmith traces**
  * Latency Distribution Heatmap
  * Interactive filter dropdowns: `$model` and `$node_name`

### 2. Dashboard 2: E-Commerce Business & Cart Recovery Analytics
* **URL**: [http://localhost:3000/d/ecommerce-cart-recovery](http://localhost:3000/d/ecommerce-cart-recovery)
* **Metrics**:
  * Total Ingested Abandoned Cart Value ($)
  * Projected Recovered Revenue ($)
  * Real-Time Average Preserved Gross Margin (%) with **>= 30% Policy Gauge**
  * Total Promotional Discount Burned ($)
  * Warehouse Overstock Inventory Units Cleared
  * Cart Abandonment Hesitation Breakdown (Shipping Shock vs Price vs Accessories)
  * Copywriter Linter Quality & Self-Correction Rate
  * Merchandiser Human Sign-Offs (Auto-Approved vs Human Approved vs Rejected)

---

## 🚀 How to Run

### Option 1: Via Master Runner (Recommended)
```bash
python runner.py
```
Type **`E`** to open the E-Commerce Swarm menu:
* `[1]` Run Interactive Terminal CLI (`cli.py`)
* `[2]` Run Multi-Cart Continuous Traffic Generator (`simulate.py`)
* `[3]` View Grafana Dashboard URLs

### Option 2: Run CLI Directly
```bash
python ecommerce_agent/cli.py
```

### Option 3: Run Continuous Simulation (Populates Grafana live)
```bash
python ecommerce_agent/simulate.py
```
