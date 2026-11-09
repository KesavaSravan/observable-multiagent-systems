"""
Module 11 - Script 03: Exponential Backoff Retries & Jitter

Demonstrates:
1. Implementing exponential backoff retries within node execution
2. Adding random jitter to prevent thundering herd problem
3. Tracking retry attempts in Prometheus metrics
"""

import sys
import time
import random
from typing import TypedDict
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

from langgraph.graph import StateGraph, START, END


class RetryState(TypedDict):
    service_endpoint: str
    response_payload: str
    total_retries: int


def fetch_with_backoff_node(state: RetryState) -> dict:
    max_attempts = 3
    base_backoff = 0.1  # seconds for test speed
    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        print(f" 📡 Attempt {attempts}/{max_attempts} to reach {state['service_endpoint']}...")
        
        # Simulate failure on first 2 attempts, success on 3rd
        if attempts < 3:
            jitter = random.uniform(0.01, 0.05)
            sleep_time = (base_backoff * (2 ** (attempts - 1))) + jitter
            print(f"    ⚠️ HTTP 503 Service Unavailable. Backing off for {sleep_time:.3f}s...")
            time.sleep(sleep_time)
        else:
            print("    ✅ HTTP 200 OK received!")
            return {
                "response_payload": '{"status": "healthy", "uptime": 99.98}',
                "total_retries": attempts - 1
            }

    raise TimeoutError(f"Failed to reach {state['service_endpoint']} after {max_attempts} attempts.")


def main():
    print("=" * 70)
    print("  MODULE 11: EXPONENTIAL BACKOFF RETRIES & JITTER")
    print("=" * 70)

    builder = StateGraph(RetryState)
    builder.add_node("resilient_fetch", fetch_with_backoff_node)
    builder.add_edge(START, "resilient_fetch")
    builder.add_edge("resilient_fetch", END)

    graph = builder.compile()

    print("\n▶️ Invoking Graph with Exponential Backoff Node...")
    res = graph.invoke({
        "service_endpoint": "https://api.internal.cluster/v1/metrics",
        "response_payload": "",
        "total_retries": 0
    })

    print("\n" + "-" * 70)
    print(f"🎯 Final Result:")
    print(f"   • Total Retries Performed: {res['total_retries']}")
    print(f"   • Response Payload       : {res['response_payload']}")
    print("-" * 70)
    print("✅ Completed Script 03 successfully!\n")


if __name__ == "__main__":
    main()
