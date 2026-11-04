"""
Module 03 - Script 01: Tool Definition Basics & Schema Inspection

Demonstrates:
1. Creating type-annotated tools with @tool decorator
2. Inspecting the generated JSON schema passed to LLMs
3. Binding tools to multi-provider chat models
"""

import sys
import json
from typing import Dict, Any
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_core.tools import tool
from shared.llm_factory import get_chat_model


# 1. Define Observability & SRE Tools using @tool
@tool
def query_k8s_logs(service_name: str, lines: int = 20) -> str:
    """
    Fetch the latest container logs from Kubernetes for a given microservice.

    Args:
        service_name: The name of the microservice (e.g. 'auth-service', 'billing-service').
        lines: Number of log lines to retrieve (default: 20).
    """
    # Mock log response
    return (
        f"[INFO] 2026-09-23T10:14:02Z {service_name} received GET /health -> 200 OK\n"
        f"[ERROR] 2026-09-23T10:14:05Z {service_name} Database connection timeout after 30000ms\n"
        f"[FATAL] 2026-09-23T10:14:06Z {service_name} Panic: uncaught exception pool exhausted\n"
    )


@tool
def get_service_metrics(service_name: str) -> Dict[str, Any]:
    """
    Query Prometheus for the CPU, memory, and error rate metrics of a service.

    Args:
        service_name: The name of the service to inspect.
    """
    return {
        "service": service_name,
        "cpu_usage_cores": 3.8,
        "memory_utilization_pct": 94.2,
        "http_5xx_rate_pct": 18.5,
        "active_replicas": 4
    }


def main():
    print("=" * 70)
    print("  MODULE 03: TOOL DEFINITION BASICS & SCHEMA INSPECTION")
    print("=" * 70)

    tools = [query_k8s_logs, get_service_metrics]

    print("\n🔍 1. Inspecting Generated Tool Schemas:")
    for t in tools:
        print(f"\n• Tool Name: {t.name}")
        print(f"  Description: {t.description.strip()}")
        print(f"  Schema Args: {json.dumps(t.args, indent=2)}")

    print("\n🤖 2. Binding Tools to Multi-Provider Model:")
    model = get_chat_model(allow_mock_fallback=True)
    
    if hasattr(model, "bind_tools"):
        model_with_tools = model.bind_tools(tools)
        print(f"✅ Tools successfully bound to {type(model).__name__}!")
    else:
        print("ℹ️ Model does not support bind_tools (mock mode).")

    print("\n" + "=" * 70)
    print("✅ Completed Script 01 successfully!\n")


if __name__ == "__main__":
    main()
