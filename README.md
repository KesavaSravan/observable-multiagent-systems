# 🔭 Observable Multi-Agent Systems: LangGraph + LangSmith + Grafana

> A production-grade hands-on platform and enterprise curriculum for building autonomous multi-agent state machines instrumented with **LangSmith Distributed Tracing**, **Prometheus Real-Time Metrics**, and **Pre-Provisioned Grafana Dashboards** from line one.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-orange.svg)](https://github.com/langchain-ai/langgraph)
[![LangSmith](https://img.shields.io/badge/LangSmith-Tracing%20%26%20Evals-purple.svg)](https://smith.langchain.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-Telemetry-red.svg)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800.svg)](https://grafana.com/)
[![SQLite](https://img.shields.io/badge/SQLite-WAL%20Persistence-003B57.svg)](https://www.sqlite.org/)

---

## 🧭 Observability Duality: Traces vs Metrics

Production LLM swarms require two complementary lenses of visibility:

```
                         ┌─────────────────────────────────────────────────────────┐
                         │              LangGraph Multi-Agent Runtime              │
                         │          (State, Sub-agents, Tools, HITL Checkpoints)   │
                         └───────────────────────────┬─────────────────────────────┘
                                                     │
                         ┌───────────────────────────┴─────────────────────────────┐
                         │                                                         │
                         ▼ (Deep Trace & Run Trees)                                ▼ (Real-Time Metrics)
             ┌───────────────────────┐                                 ┌───────────────────────┐
             │    LangSmith Cloud    │                                 │   Prometheus Client   │
             │   (Trace Observability│                                 │   (Aggregated Metrics)│
             └───────────┬───────────┘                                 └───────────┬───────────┘
                         │                                                         │
             ┌───────────▼───────────┐                                 ┌───────────▼───────────┐
             │ • Nested Span Trees   │                                 │ • Node Latencies (s)  │
             │ • Full Prompts/Outputs│                                 │ • Error Rate Counters │
             │ • Token Usage Rollup  │                                 │ • Token & Cost Meters │
             │ • Self-Correction Runs│                                 │ • Real-Time Stock (DB)│
             │ • Checkpoint Versions │                                 │ • PromQL Alert Rules  │
             └───────────────────────┘                                 └───────────┬───────────┘
                                                                                   │ Scraped by
                                                                       ┌───────────▼───────────┐
                                                                       │    Grafana Dashboards │
                                                                       │  - SRE LLM Tracker    │
                                                                       │  - E-Commerce KPIs    │
                                                                       └───────────────────────┘
```

---

## 🏆 Capstone Architecture: Autonomous E-Commerce Cart Recovery Swarm

Located in [`ecommerce_agent/`](ecommerce_agent/), this platform ingests abandoned shopping carts and deploys an autonomous multi-agent swarm to recover lost revenue while mathematically guaranteeing positive unit economics:

```text
  [ Abandoned Cart Telemetry Ingestion / Custom User Query ]
                             │
                             ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 1. 🔍 INTENT ANALYZER AGENT                                            │
  │    • Ingests checkout dwell, exit screen, cart value & customer tier   │
  │    • Diagnoses drop-off: price_hesitation | shipping_sticker_shock     │
  └──────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 2. 📦 OVERSTOCK MATCHER AGENT                                          │
  │    • Scans real-time SQLite warehouse for clearance accessories        │
  │    • Pairs complementary clearance items (e.g. 78% margin stock)       │
  └──────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 3. ⚖️  MARGIN SIMULATOR TOOL AGENT                                     │
  │    • Unit economics sandbox: computes blended gross margin             │
  │    • Solves maximum permissible discount (Target: Blended Margin >= 30%)│
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
```

---

## 📂 Project Structure

```text
├── ecommerce_agent/                   # 🏆 Capstone Multi-Agent Swarm
│   ├── agents/                        # Swarm agents (Intent, Matcher, Copywriter, Linter, etc.)
│   ├── core/                          # StateGraph architecture, checkpoints & TypedDict state
│   ├── data/                          # SQLite warehouse database & 24 catalog products
│   ├── tools/                         # Inventory queries, margin sandbox & coupon tools
│   ├── cli.py                         # Interactive CLI with real-time agent execution stream
│   ├── simulate.py                    # Multi-cart continuous traffic simulator
│   └── inspect_checkpoints.py         # SQLite state history & time-travel inspector
│
├── modules/                           # 📚 11 Progressive Hands-On Learning Modules
│   ├── 01_setup_and_tracing/          # Multi-provider LLM factory & first LangSmith trace
│   ├── 02_state_and_nodes/            # TypedDict state, reducers & node execution spans
│   ├── 03_react_agent_loop/           # Tool calling, ReAct loops & trace metadata
│   ├── 04_conditional_routing/        # Semantic routing & parallel fan-out/fan-in
│   ├── 05_persistence_and_sessions/   # SqliteSaver persistence, threads & state history
│   ├── 06_multiagent_supervisor/      # Multi-agent supervisor pattern & subgraphs
│   ├── 07_human_in_the_loop/          # Breakpoints (interrupt_before) & state editing
│   ├── 08_langsmith_evaluators/       # LLM-as-a-judge, datasets & evaluate() runs
│   ├── 09_cost_token_analytics/       # Token attribution & latency bottleneck analysis
│   ├── 10_prometheus_grafana/         # Custom Prometheus metrics & exporter setup
│   └── 11_production_readiness/       # Circuit breakers & production fallback chains
│
├── monitoring/                        # 📊 Docker Observability Infrastructure
│   ├── docker-compose.yml             # Prometheus (9090) + Grafana (3000) stack
│   ├── prometheus/prometheus.yml      # Scrape configuration (scrapes port 8000)
│   └── grafana/
│       ├── provisioning/              # Auto-provisioned data sources and dashboards
│       └── dashboards/
│           ├── llm_agent_tracker.json # Dashboard 1: Technical LLM Tracker
│           └── ecommerce_cart_recovery.json # Dashboard 2: E-Commerce Business KPIs
│
├── shared/                            # ⚙️ Shared Framework Infrastructure
│   ├── config.py                      # Pydantic v2 settings & environment loader
│   ├── llm_factory.py                 # Multi-provider factory, policy allowlists & fallbacks
│   └── metrics.py                     # Prometheus metric definitions & @instrument_node
│
├── runner.py                          # ⚡ Master interactive console launcher
├── requirements.txt                   # Production dependencies
├── .env.example                       # Documented environment template
└── .gitignore                         # Secret protection & artifact exclusion rules
```

---

## 🛠️ Prerequisites & Setup

### 1. System Requirements
- **Python**: 3.10, 3.11, 3.12, or 3.13
- **Docker & Docker Compose**: Installed and running (for Prometheus & Grafana)
- **Git**: Installed

### 2. Clone Repository & Setup Virtual Environment
```bash
# Clone the repository
git clone <your-repo-url>
cd "LangGraph + LangSmith observability"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔐 Environment Configuration (`.env`)

Copy the template to create your `.env` file:
```bash
cp .env.example .env
```

Open `.env` in your editor and configure:

```bash
# ==============================================================================
# LangGraph + LangSmith + Grafana Observability Configuration
# ==============================================================================

# --- LangSmith Distributed Tracing ---
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_your_langsmith_api_key_here
LANGCHAIN_PROJECT=langgraph-observability-course

# --- Multi-Project Governance & FinOps Cost Center ---
# Default active project for general learning modules and unlisted scripts
PROJECT_ID=course_learning

# Multi-Project Allowlists (Configure multiple projects in one .env!)
# Format: PROJECT_<PROJECT_ID_UPPERCASE>_MODELS=model1,model2,...
PROJECT_COURSE_LEARNING_MODELS=openai/gpt-oss-120b,llama-3.3-70b-versatile,llama-3.1-8b-instant,gemini-1.5-flash,gemini-2.0-flash,gpt-4o-mini,claude-3-5-haiku-20241022,mock-model
PROJECT_COURSE_LEARNING_DEFAULT_MODEL=openai/gpt-oss-120b

# Capstone E-Commerce Project Allowlist (Cost-isolated in Prometheus & Grafana)
PROJECT_ECOMMERCE_RECOVERY_MODELS=openai/gpt-oss-120b,llama-3.3-70b-versatile,llama-3.1-8b-instant,gemini-1.5-flash,gpt-4o-mini,mock-model
PROJECT_ECOMMERCE_RECOVERY_DEFAULT_MODEL=openai/gpt-oss-120b

# --- Active Multi-Provider LLM Configuration ---
# Choose one of: openai | anthropic | google | groq
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-120b
LLM_TEMPERATURE=0.0

# --- Provider API Keys (Fill the one you are actively using) ---
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...

# --- Prometheus Metrics Exporter ---
PROMETHEUS_PORT=8000
PROMETHEUS_METRICS_PATH=/metrics
```

> [!NOTE]
> **Offline / Missing API Key Fallback**: If an API key is missing or offline, the framework automatically uses built-in `MockChatModel` with simulated token usage and realistic responses, so you can test all workflows and dashboards offline!

---

## 🐳 Starting the Observability Stack (Docker)

Start Prometheus and Grafana in the background:
```powershell
docker compose -f monitoring/docker-compose.yml up -d
```

Verify that both containers are running:
```powershell
docker ps
```

| Service | Port | Default Credentials | Description |
| :--- | :--- | :--- | :--- |
| **Grafana** | `3000` | User: `admin`<br>Password: `admin` | Real-time dashboards with pre-provisioned data sources |
| **Prometheus** | `9090` | None | Time-series database scraping agent metrics |
| **Agent Exporter** | `8000` | None | Live metrics endpoint served by running agents (`/metrics`) |

---

## 🚀 How to Run

### Mode 1: Master Interactive Curriculum Runner
Navigate all 11 modules and 43 scripts from a unified terminal UI:
```powershell
.venv\Scripts\python.exe runner.py
```
- Select `[1]` - `[11]` to browse any learning module.
- Select `[M]` to switch LLM provider and model interactively.
- Select `[D]` to run system diagnostics (API keys, ports, connectivity).
- Select `[C]` to launch the Capstone E-Commerce Swarm.

---

### Mode 2: Capstone Interactive Swarm CLI
Run realistic abandoned cart recovery workflows with live agent execution feedback:
```powershell
.venv\Scripts\python.exe ecommerce_agent/cli.py
```

**Key Interactive Features**:
1. **Agentic Flow Diagram**: Displayed visually on launch before scenario selection.
2. **Preset Scenarios (`[1]` - `[6]`)**: Select from realistic carts across Coffee/Kitchen, Audio, Computing, Fitness, and Photography.
3. **Inspect Real-Time Warehouse Inventory (`[I]`)**: Prints live SQLite inventory table (SKU, Price, COGS, Stock Units, Overstock flag, Times Bundled).
4. **Custom Manual Query (`[C]`)**: Enter your own customer name, product, retail price, COGS, and checkout exit reason.
5. **Real-Time Agent Stepping**: Displays formatted live cards as each agent executes (Intent Analyzer ➔ Overstock Matcher ➔ Margin Simulator ➔ Gatekeeper ➔ Copywriter ➔ Copy Linter ➔ Dispatcher).
6. **Human-in-the-Loop Gatekeeper**: Prompts operator to `[A]` Approve or `[R]` Reject bundles on high-ticket items.

---

### Mode 3: Continuous Traffic Simulator
Generate continuous abandoned cart traffic to watch live data stream into Grafana:
```powershell
.venv\Scripts\python.exe ecommerce_agent/simulate.py
```
- Simulates realistic carts across customer tiers (FIRST_TIME, REPEAT, VIP).
- Depletes clearance stock in real-time in SQLite.
- Pushes live revenue, margin, and token metrics to Prometheus on port `8000`.

---

### Mode 4: SQLite Checkpoint State Inspector
Inspect durable SQLite state checkpoints, audit logs, and graph state history:
```powershell
.venv\Scripts\python.exe ecommerce_agent/inspect_checkpoints.py
```

---

## 📊 Pre-Provisioned Grafana Dashboards

Both dashboards are automatically provisioned when Docker starts:

### 1. Dashboard 1: LLM & Technical SRE Performance Tracker
- **URL**: [http://localhost:3000/d/llm-agent-tracker](http://localhost:3000/d/llm-agent-tracker)
- **Multi-Project Filter**: Switch between `ecommerce_recovery`, `course_learning`, or `All` in the top bar.
- **Panels**:
  - Node Latency Heatmap & p95/p99 Duration Percentiles
  - Token Consumption by Model (Prompt vs Completion)
  - Live Cumulative USD Cost per Project & Model
  - Node Error Rates & Circuit Breaker Events
  - Tool Invocation Frequency

### 2. Dashboard 2: E-Commerce Business & Cart Recovery Analytics
- **URL**: [http://localhost:3000/d/ecommerce-cart-recovery](http://localhost:3000/d/ecommerce-cart-recovery)
- **Panels**:
  - Total Ingested Cart Value & Projected Recovered Revenue
  - Real-Time Gross Margin Health (Policy Minimum: 30%)
  - Recovered Revenue Rate vs Discount Burn ($ / hour)
  - Real-Time Warehouse Stock by SKU (SQLite 24-SKU live stock gauge)
  - Cumulative Overstock Units Bundled & Sold
  - Merchandiser HITL Approval Rate vs Auto-Approvals
  - Copywriter Linter Quality & Self-Correction Loop Passes

---

## 📦 Dynamic Real-Time Warehouse Inventory (SQLite)

The warehouse database is located at [`ecommerce_agent/data/warehouse.db`](ecommerce_agent/data/) and features **24 SKUs across 5 categories**:

| Category | Primary High-Ticket SKUs | High-Margin Clearance Complements (65%–85% Margin) |
| :--- | :--- | :--- |
| **Kitchen & Coffee** | `COFFEE-MCH-01` ($280) | `COFFEE-BEAN-02` ($34), `COFFEE-ACC-03` ($28), `COFFEE-SYRUP-04` ($19.50) |
| **Audio & Electronics** | `AUDIO-NC-01` ($220) | `AUDIO-CASE-02` ($39), `AUDIO-CABLE-03` ($24), `AUDIO-STAND-04` ($36) |
| **Computing & Workstation** | `MONITOR-4K-01` ($899), `KB-MECH-01` ($160) | `KB-REST-02` ($35), `DESK-MAT-03` ($30), `MONITOR-ARM-02` ($75) |
| **Fitness & Workout** | `FIT-ROWER-01` ($799) | `FIT-MAT-02` ($45), `FIT-ELECTRO-03` ($22), `FIT-ROLLER-04` ($28) |
| **Photography & Creator** | `CAM-VLOG-01` ($640) | `CAM-STRAP-02` ($32), `CAM-CLEAN-03` ($25) |

**Real-Time Engine Rules**:
- **Automatic Stock Depletion**: Every time the Dispatcher Agent sends an approved offer, stock is decremented in SQLite (`stock_units - 1`) and Prometheus gauges update live.
- **Overstock Flip Guardrail**: If clearance stock drops to $\le 20$ units, it automatically flips `is_overstock = 0`, preventing further clearance discounts.
- **Audit Logging**: Every transaction is saved to `inventory_audit_log` with previous stock, remaining stock, cart ID, and timestamp.

---

## 🛡️ FinOps Model Allowlist & Multi-Project Governance

Prevent accidental use of expensive models and isolate costs between teams:

1. **In `.env`**:
   ```bash
   PROJECT_ECOMMERCE_RECOVERY_MODELS=llama-3.3-70b-versatile,gpt-4o-mini,gemini-1.5-flash
   ```
2. **Policy Enforcement Gate**:
   If an agent requests an unapproved model, the factory immediately blocks execution with:
   ```text
   UnauthorizedModelPolicyError: ❌ Model 'claude-3-5-sonnet' is NOT authorized for project 'ecommerce_recovery'.
   ```
3. **Cost Isolation**:
   Every token and USD cent is labeled with `project_id="ecommerce_recovery"` in Prometheus, making multi-tenant cost attribution in Grafana seamless.

---

## ❓ Troubleshooting & FAQ

### 1. Grafana says "No data"
- **Cause**: The Prometheus metrics exporter on port `8000` only serves metrics while a script or simulator is running.
- **Fix**: Run `.venv\Scripts\python.exe ecommerce_agent/simulate.py` in a separate terminal. Set Grafana refresh to `5s` and time range to `Last 15 minutes`.

### 2. Windows UTF-8 Console Error (`UnicodeEncodeError: 'charmap' codec...`)
- **Fix**: All CLI entry points automatically reconfigure stdout to UTF-8. If running custom scripts, add:
  ```python
  import sys
  if hasattr(sys.stdout, "reconfigure"):
      sys.stdout.reconfigure(encoding="utf-8", errors="replace")
  ```

### 3. Docker Port Conflicts
- If port `3000` (Grafana) or `9090` (Prometheus) is already in use by another local service, change the host port mapping in [`monitoring/docker-compose.yml`](monitoring/docker-compose.yml) (e.g. `"3001:3000"`).

---

## 📄 License
This project is licensed under the MIT License. Feel free to use it for learning, research, or commercial multi-agent deployments.
