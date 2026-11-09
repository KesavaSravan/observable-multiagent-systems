"""
Interactive Master Runner & Model Switcher for LangGraph + LangSmith + Grafana.

Run this script to launch any module, inspect diagnostics, switch LLM providers
on the fly, or execute the final project without typing file paths manually.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Reconfigure Windows stdout encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add workspace root to sys.path
ROOT_DIR = Path(__file__).parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared.config import settings
from shared.llm_factory import get_chat_model, prompt_model_selection, RECOMMENDED_MODELS

# List of all modules with metadata
MODULES_METADATA = [
    {
        "id": "01",
        "folder": "01_setup_and_tracing",
        "title": "Setup & Tracing Verification",
        "desc": "SDK verification, multi-provider tests, first distributed trace",
        "scripts": [
            ("01_env_and_sdk_verification.py", "Verify LangSmith SDK, API keys, and connection"),
            ("02_llm_factory_multi_provider.py", "Test OpenAI, Anthropic, Gemini, Groq via factory"),
            ("03_first_traced_call.py", "Generate first LangSmith trace and print trace run URL"),
        ]
    },
    {
        "id": "02",
        "folder": "02_state_and_nodes",
        "title": "State Schemas & Traced Nodes",
        "desc": "TypedDict state, custom reducers, Pydantic validation, node execution spans",
        "scripts": [
            ("01_basic_typeddict_state.py", "TypedDict state, single node, state mutation trace"),
            ("02_custom_state_reducers.py", "Annotated reducers (add_messages, custom operator)"),
            ("03_pydantic_state_validation.py", "Strict state validation with Pydantic v2"),
            ("04_node_execution_spans.py", "Inspect input/output state snapshots in LangSmith"),
        ]
    },
    {
        "id": "03",
        "folder": "03_react_agent_loop",
        "title": "ReAct Agent Loop & Tool Calling",
        "desc": "@tool decorator, ToolNode execution, cyclic loops, metadata tags",
        "scripts": [
            ("01_tool_definition_basics.py", "@tool decorator, docstrings, schema generation"),
            ("02_tool_node_execution.py", "ToolNode execution and error handling"),
            ("03_react_graph_loop.py", "Complete ReAct loop with tools_condition"),
            ("04_react_tracing_metadata.py", "Injecting run tags, metadata, and custom run names"),
        ]
    },
    {
        "id": "04",
        "folder": "04_conditional_routing",
        "title": "Conditional Routing & Dynamic Branching",
        "desc": "Intent routers, dynamic conditional edges, parallel fan-out/fan-in, trace tagging",
        "scripts": [
            ("01_intent_classification_router.py", "Single LLM router deciding execution path"),
            ("02_dynamic_conditional_edges.py", "Multi-branch routing with dynamic fallback"),
            ("03_parallel_fanout_fanin.py", "Fan-out to parallel workers, fan-in reducer"),
            ("04_trace_tagging_for_filters.py", "Tagging branches (tag:billing, tag:critical)"),
        ]
    },
    {
        "id": "05",
        "folder": "05_persistence_and_sessions",
        "title": "Persistence, Threads & State History",
        "desc": "MemorySaver, thread_id session grouping, state history & time travel, SQLite",
        "scripts": [
            ("01_memory_saver_threads.py", "MemorySaver checkpointing & thread_id isolation"),
            ("02_multi_turn_conversations.py", "Conversation memory across multiple turns"),
            ("03_state_history_time_travel.py", "Inspect previous states and branch from history"),
            ("04_sqlite_persistent_checkpointer.py", "Production durable SQLite checkpointing"),
        ]
    },
    {
        "id": "06",
        "folder": "06_multiagent_supervisor",
        "title": "Multi-Agent Systems & Nested Traces",
        "desc": "Sub-agent graphs, Supervisor router pattern, agent handoffs, nested trace trees",
        "scripts": [
            ("01_subagent_as_graph_node.py", "Compiling sub-graphs as nodes within parent graph"),
            ("02_supervisor_router_pattern.py", "Central supervisor delegating to specialist workers"),
            ("03_agent_handoffs_and_consensus.py", "Worker-to-worker direct handoffs with state transfer"),
            ("04_nested_trace_trees.py", "LangSmith visualization of multi-agent nested spans"),
        ]
    },
    {
        "id": "07",
        "folder": "07_human_in_the_loop",
        "title": "Human-in-the-Loop & Breakpoints",
        "desc": "interrupt_before on risky tools, state inspection/mutation, approval/resume",
        "scripts": [
            ("01_interrupt_before_action.py", "interrupt_before on dangerous action node"),
            ("02_state_inspection_and_update.py", "Human inspecting & editing state before resume"),
            ("03_approval_rejection_workflows.py", "Resume with approval flag vs rejection rewrite"),
            ("04_trace_continuity_on_resume.py", "LangSmith trace continuity across paused runs"),
        ]
    },
    {
        "id": "08",
        "folder": "08_langsmith_evaluators",
        "title": "LangSmith Evaluators & Datasets",
        "desc": "Programmatic dataset creation, exact/semantic evaluators, LLM-as-a-judge",
        "scripts": [
            ("01_create_dataset_programmatic.py", "Create LangSmith Dataset with test inputs/outputs"),
            ("02_exact_and_semantic_evaluators.py", "Custom string matching and semantic evaluators"),
            ("03_llm_as_a_judge_evaluator.py", "LLM judge evaluating correctness & tool accuracy"),
            ("04_run_eval_experiment.py", "Execute evaluate() suite and view experiment runs"),
        ]
    },
    {
        "id": "09",
        "folder": "09_cost_token_analytics",
        "title": "Cost, Token & Bottleneck Analytics",
        "desc": "Client.read_run(), token attribution per node, pricing engines, failure detection",
        "scripts": [
            ("01_read_run_metadata_client.py", "Query run trees programmatically via LangSmith SDK"),
            ("02_per_node_token_attribution.py", "Calculating prompt/completion tokens per node"),
            ("03_cost_calculation_engine.py", "Multi-provider pricing matrix calculation"),
            ("04_bottleneck_failure_analyzer.py", "Automated script finding slowest/costliest nodes"),
        ]
    },
    {
        "id": "10",
        "folder": "10_prometheus_grafana",
        "title": "Prometheus & Grafana Telemetry",
        "desc": "Histograms, counters, node decorators, live metrics server, PromQL queries",
        "scripts": [
            ("01_prometheus_metrics_basics.py", "Counters, Gauges, Histograms with prometheus_client"),
            ("02_instrumenting_langgraph_nodes.py", "Custom node execution timer & error decorator"),
            ("03_token_cost_metrics_exporter.py", "Exposing token gauges and cost counters to /metrics"),
            ("04_live_traffic_generator.py", "Simulating realistic traffic for dashboard testing"),
            ("05_grafana_dashboard_queries.py", "PromQL query validation for panels and alerts"),
        ]
    },
    {
        "id": "11",
        "folder": "11_production_readiness",
        "title": "Production Readiness & SRE Operations",
        "desc": "Observability duality, circuit breakers, backoff retries, production audit",
        "scripts": [
            ("01_observability_duality_demo.py", "Trace-level (LangSmith) vs Aggregate (Grafana) in action"),
            ("02_circuit_breaker_fallback.py", "Graceful degradation on LLM rate limits/outages"),
            ("03_rate_limiting_and_retry_node.py", "Backoff retries with Prometheus retry counter"),
            ("04_production_readiness_audit.py", "Automated environment & configuration validator"),
        ]
    }
]


def print_banner():
    """Prints the main interactive banner."""
    provider = os.getenv("LLM_PROVIDER", settings.LLM_PROVIDER).upper()
    model = os.getenv("LLM_MODEL", settings.LLM_MODEL)
    tracing = "ENABLED" if settings.LANGCHAIN_TRACING_V2 else "DISABLED"
    print("\n" + "=" * 76)
    print(" 🚀  LANGGRAPH + LANGSMITH + GRAFANA — MASTER INTERACTIVE RUNNER")
    print("=" * 76)
    print(f" ⚙️  Active LLM Provider : [{provider}] -> Model: {model}")
    print(f" 📡  LangSmith Tracing  : [{tracing}] (Project: {settings.LANGCHAIN_PROJECT})")
    print(f" 📊  Prometheus Port    : http://localhost:{settings.PROMETHEUS_PORT}/metrics")
    print("=" * 76)


def run_script(script_path: Path):
    """Executes a Python script in a subprocess using the active python interpreter."""
    if not script_path.exists():
        print(f"\n❌ Error: Script not found: {script_path}\n")
        return
    
    print("\n" + "-" * 76)
    print(f"▶️  EXECUTING: {script_path.name}")
    print(f"   Path: {script_path}")
    print("-" * 76 + "\n")

    env = os.environ.copy()
    # Pass root dir to PYTHONPATH and enforce UTF-8 IO encoding on Windows
    env["PYTHONPATH"] = str(ROOT_DIR) + (os.pathsep + env.get("PYTHONPATH", ""))
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    try:
        res = subprocess.run([sys.executable, str(script_path)], env=env)
        print("\n" + "-" * 76)
        if res.returncode == 0:
            print(f"✅ Finished {script_path.name} successfully (Exit code: 0)")
        else:
            print(f"⚠️ {script_path.name} finished with exit code: {res.returncode}")
        print("-" * 76 + "\n")
    except KeyboardInterrupt:
        print(f"\n⏸️ Execution interrupted by user.\n")
    except Exception as e:
        print(f"\n❌ Execution failed: {e}\n")


def browse_and_run_module(mod_meta: dict):
    """Interactive submenu for a specific module."""
    mod_folder = ROOT_DIR / "modules" / mod_meta["folder"]
    while True:
        print("\n" + "=" * 76)
        print(f" 📁 MODULE {mod_meta['id']}: {mod_meta['title']}")
        print(f"    {mod_meta['desc']}")
        print("=" * 76)
        for idx, (s_name, s_desc) in enumerate(mod_meta["scripts"], 1):
            print(f"  [{idx}] {s_name.ljust(36)} -> {s_desc}")
        print(f"  [A] Run ALL scripts in Module {mod_meta['id']} sequentially")
        print(f"  [R] View Module README.md")
        print(f"  [0] Back to Main Menu")
        print("-" * 76)

        choice = input("Select an option [1-N/A/R/0]: ").strip().upper()
        if choice == "0":
            break
        elif choice == "R":
            readme_path = mod_folder / "README.md"
            if readme_path.exists():
                print("\n" + "=" * 76)
                print(readme_path.read_text(encoding="utf-8"))
                print("=" * 76 + "\n")
            else:
                print(f"\nREADME not found at {readme_path}\n")
        elif choice == "A":
            print(f"\n🔄 Running all {len(mod_meta['scripts'])} scripts in Module {mod_meta['id']}...\n")
            for s_name, _ in mod_meta["scripts"]:
                run_script(mod_folder / s_name)
        elif choice.isdigit() and 1 <= int(choice) <= len(mod_meta["scripts"]):
            s_name, _ = mod_meta["scripts"][int(choice) - 1]
            run_script(mod_folder / s_name)
        else:
            print("Invalid selection. Try again.")


def main_interactive_loop():
    """Main terminal loop."""
    while True:
        print_banner()
        print(" 🎯 AVAILABLE ACTIONS & MODULES:")
        print("   [P] 🔄 Switch Active LLM Provider & Model on the Fly")
        print("   [D] 🩺 Run Environment & API Key Diagnostics Check")
        print("   [M] 📊 Observability Stack Status (Prometheus & Grafana URLs)")
        print("   [C] 🏆 Launch Capstone Project: 'High-Margin Cart Recovery Agent'")
        print("   " + "-" * 72)

        for m in MODULES_METADATA:
            print(f"   [{m['id']}] Module {m['id']}: {m['title'].ljust(35)} ({len(m['scripts'])} scripts)")

        print("   [0] 🚪 Exit")
        print("-" * 76)

        choice = input("Enter choice [01-11, P, D, M, C, 0]: ").strip().upper()

        if choice == "0":
            print("\n👋 Happy building observable agent systems!\n")
            break
        elif choice == "P":
            prompt_model_selection()
        elif choice == "D":
            settings.print_diagnostics()
            input("\nPress [Enter] to return to menu...")
        elif choice == "M":
            print("\n" + "=" * 60)
            print(" 📊 OBSERVABILITY STACK ENDPOINTS")
            print("=" * 60)
            print(" • Prometheus Exporter (Agent App) : http://localhost:8000/metrics")
            print(" • Prometheus Server (Scraper)    : http://localhost:9090")
            print(" • Grafana Dashboard UI           : http://localhost:3000 (admin/admin)")
            print(" • LangSmith Cloud Console        : https://smith.langchain.com")
            print("=" * 60)
            print(" To start Docker monitoring: cd monitoring && docker-compose up -d\n")
            input("Press [Enter] to return to menu...")
        elif choice in ("C", "E"):
            launch_ecommerce_menu()
        else:
            # Check if user selected a module number
            target_mod = next((m for m in MODULES_METADATA if m["id"] == choice or m["id"] == choice.zfill(2)), None)
            if target_mod:
                browse_and_run_module(target_mod)
            else:
                print("\n⚠️ Unknown option. Please choose a valid item.\n")


def launch_ecommerce_menu():
    """E-Commerce Cart Recovery launcher submenu."""
    ecom_dir = ROOT_DIR / "ecommerce_agent"
    while True:
        ecom_provider = (
            os.getenv("PROJECT_ECOMMERCE_RECOVERY_PROVIDER")
            or os.getenv("LLM_PROVIDER")
            or settings.LLM_PROVIDER
        ).upper()
        ecom_model = (
            os.getenv("PROJECT_ECOMMERCE_RECOVERY_DEFAULT_MODEL")
            or os.getenv("LLM_MODEL")
            or "default-model"
        )
        print("\n" + "=" * 76)
        print(" 🛒 E-COMMERCE SWARM: HIGH-MARGIN CART RECOVERY & BUNDLE AGENT")
        print("=" * 76)
        print(f" ⚙️  Active Model for E-Commerce: [{ecom_provider}] -> {ecom_model}")
        print("-" * 76)
        print("  [1] Run Interactive Terminal CLI (cli.py)")
        print("  [2] Run Multi-Cart Continuous Traffic Generator (simulate.py)")
        print("  [3] Inspect SQLite Checkpoints & State History (inspect_checkpoints.py)")
        print("  [4] Open Grafana Dashboards Information")
        print("  [M] 🔄 Switch E-Commerce Project Model & Provider")
        print("  [0] Back to Main Menu")
        print("-" * 76)

        e_choice = input("Choose Option [1-4/M/0]: ").strip().upper()
        if e_choice == "0":
            break
        elif e_choice == "M":
            prompt_model_selection(project_id="ecommerce_recovery")
        elif e_choice == "1":
            run_script(ecom_dir / "cli.py")
        elif e_choice == "2":
            run_script(ecom_dir / "simulate.py")
        elif e_choice == "3":
            run_script(ecom_dir / "inspect_checkpoints.py")
        elif e_choice == "4":
            print("\n" + "=" * 60)
            print(" 📊 DUAL GRAFANA DASHBOARDS (AgentOps Folder)")
            print("=" * 60)
            print(" • Dashboard 1 (LLM & SRE Tracker)     : http://localhost:3000/d/llm-agent-tracker")
            print(" • Dashboard 2 (E-Commerce Business)   : http://localhost:3000/d/ecommerce-cart-recovery")
            print(" • Prometheus Exporter Endpoint       : http://localhost:8000/metrics")
            print("=" * 60)
            input("\nPress [Enter] to return...")
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangGraph + LangSmith + Grafana Master Runner")
    parser.add_argument("--provider", type=str, help="Override LLM provider (openai, anthropic, google, groq, ollama, mock)")
    parser.add_argument("--model", type=str, help="Override LLM model name")
    parser.add_argument("--module", type=str, help="Run specific module directly (e.g. 01, 02, 10)")
    parser.add_argument("--script", type=str, help="Run a specific script path directly")
    args = parser.parse_args()

    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
    if args.model:
        os.environ["LLM_MODEL"] = args.model

    if args.script:
        run_script(Path(args.script))
    elif args.module:
        mod_id = args.module.zfill(2)
        target = next((m for m in MODULES_METADATA if m["id"] == mod_id), None)
        if target:
            browse_and_run_module(target)
        else:
            print(f"Module {args.module} not found.")
    else:
        main_interactive_loop()
