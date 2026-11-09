"""
Module 10 - Script 04: Continuous Live Traffic Generator for Grafana

Demonstrates:
1. Running a continuous loop generating realistic multi-agent incident traffic
2. Emitting diverse latencies, token usages, and occasional node errors
3. Supplying live telemetry data for Grafana dashboard visualization
"""

import sys
import time
import random
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from shared.metrics import (
    start_metrics_server_once,
    NODE_LATENCY_HISTOGRAM,
    NODE_ERRORS_COUNTER,
    TOOL_INVOCATIONS_COUNTER,
    track_tokens,
    ACTIVE_THREADS_GAUGE
)
from shared.config import settings


def generate_synthetic_traffic(iterations: int = 15):
    print("=" * 70)
    print("  MODULE 10: CONTINUOUS LIVE TRAFFIC GENERATOR FOR GRAFANA")
    print("=" * 70)

    start_metrics_server_once(settings.PROMETHEUS_PORT)
    print(f"\n📡 Telemetry server active at http://localhost:{settings.PROMETHEUS_PORT}/metrics")
    print(f"🔄 Generating {iterations} simulated multi-agent incident runs...\n")

    nodes = ["supervisor_triage", "log_researcher", "metric_correlator", "remediation_coder", "gatekeeper"]
    tools = ["k8s_log_fetcher", "prometheus_query", "git_patch_generator", "slack_notifier"]
    models = [("openai", "gpt-4o-mini", 0.00015), ("anthropic", "claude-3-5-haiku", 0.0008), ("google", "gemini-1.5-flash", 0.000075)]

    for i in range(1, iterations + 1):
        active_sessions = random.randint(1, 5)
        ACTIVE_THREADS_GAUGE.labels(status="running").set(active_sessions)

        # Simulate node executions
        for node in nodes:
            latency = random.uniform(0.1, 1.8)
            is_error = random.random() < 0.08  # 8% error rate

            if is_error:
                NODE_LATENCY_HISTOGRAM.labels(node_name=node, status="error").observe(latency)
                NODE_ERRORS_COUNTER.labels(node_name=node, error_type="TimeoutError").inc()
            else:
                NODE_LATENCY_HISTOGRAM.labels(node_name=node, status="success").observe(latency)

        # Simulate tool call
        tool = random.choice(tools)
        TOOL_INVOCATIONS_COUNTER.labels(tool_name=tool, status="success").inc()

        # Simulate token & cost emission
        prov, mod, base_cost = random.choice(models)
        p_tok = random.randint(300, 1800)
        c_tok = random.randint(80, 450)
        cost = ((p_tok + c_tok) / 1000) * base_cost
        track_tokens(provider=prov, model=mod, prompt_tokens=p_tok, completion_tokens=c_tok, cost_usd=cost)

        print(f"  [Run {i:>2}/{iterations}] Emitted metrics | Active Sessions: {active_sessions} | Tool: {tool:<22} | Model: {mod}")
        time.sleep(0.4)

    ACTIVE_THREADS_GAUGE.labels(status="running").set(0)
    print("\n" + "=" * 70)
    print("✅ Traffic generation batch finished!")
    print(f"📊 View metrics at: http://localhost:{settings.PROMETHEUS_PORT}/metrics")
    print("=" * 70)


if __name__ == "__main__":
    generate_synthetic_traffic(iterations=15)
