"""
Module 10 - Script 01: Prometheus Client Metrics Primitives

Demonstrates:
1. Creating Prometheus Counter, Gauge, and Histogram metrics
2. Incrementing counters, updating gauges, and observing histogram latencies
3. Inspecting the formatted OpenMetrics / Prometheus exposition text
"""

import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from prometheus_client import Counter, Gauge, Histogram, generate_latest, CollectorRegistry


def main():
    print("=" * 70)
    print("  MODULE 10: PROMETHEUS CLIENT METRICS PRIMITIVES")
    print("=" * 70)

    # Use a custom registry for demo inspection
    registry = CollectorRegistry()

    # 1. Counter: Only increments (e.g. invocations, errors)
    invocations_counter = Counter(
        "agent_invocations_total",
        "Total number of agent invocations",
        ["agent_type", "status"],
        registry=registry
    )

    # 2. Gauge: Can go up and down (e.g. active sessions, memory, queue depth)
    active_sessions_gauge = Gauge(
        "agent_active_sessions",
        "Currently active in-flight agent sessions",
        registry=registry
    )

    # 3. Histogram: Samples observations in buckets (e.g. latency)
    latency_histogram = Histogram(
        "agent_response_latency_seconds",
        "Response duration of agent in seconds",
        ["agent_type"],
        buckets=[0.1, 0.5, 1.0, 2.5, 5.0],
        registry=registry
    )

    print("\n▶️ Simulating metric recordings...")
    invocations_counter.labels(agent_type="supervisor", status="success").inc()
    invocations_counter.labels(agent_type="researcher", status="success").inc(3)
    invocations_counter.labels(agent_type="coder", status="error").inc()

    active_sessions_gauge.set(4)

    latency_histogram.labels(agent_type="supervisor").observe(0.35)
    latency_histogram.labels(agent_type="researcher").observe(1.42)
    latency_histogram.labels(agent_type="coder").observe(3.80)

    # Generate and print Prometheus exposition text
    metrics_output = generate_latest(registry).decode("utf-8")

    print("\n" + "-" * 70)
    print("📊 Formatted Prometheus Output (Exposition Format):")
    print(metrics_output[:800] + "\n... [truncated]")
    print("-" * 70)
    print("✅ Completed Script 01 successfully!\n")


if __name__ == "__main__":
    main()
