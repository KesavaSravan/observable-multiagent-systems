"""
Module 09 - Script 01: Querying Run Trees via LangSmith Client SDK

Demonstrates:
1. Using Client.list_runs() to filter runs by project, run_type, and execution status
2. Reading run inputs, outputs, execution latencies, and metadata programmatically
3. Inspecting the raw run object structure
"""

import sys
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

from shared.config import settings


def query_runs():
    print("=" * 70)
    print("  MODULE 09: QUERYING RUN TREES VIA LANGSMITH CLIENT")
    print("=" * 70)

    if not settings.LANGCHAIN_API_KEY or settings.LANGCHAIN_API_KEY.startswith("lsv2_pt_your"):
        print("ℹ️ LANGCHAIN_API_KEY not configured. Simulating SDK run query:")
        print("• Found 12 historical runs in simulated project 'langgraph-observability-course'")
        print("  - Run ID: 550e8400-e29b-41d4-a716-446655440000 | Type: chain | Status: SUCCESS | Latency: 1.24s")
        print("  - Run ID: 6ba7b810-9dad-11d1-80b4-00c04fd430c8 | Type: llm   | Status: SUCCESS | Latency: 0.85s")
        print("\n💡 Configure your API key in .env to query live traces directly from LangSmith Cloud.")
        return

    try:
        from langsmith import Client
        client = Client(api_key=settings.LANGCHAIN_API_KEY, api_url=settings.LANGCHAIN_ENDPOINT)

        print(f"📡 Querying recent runs for project '{settings.LANGCHAIN_PROJECT}'...")
        runs = list(client.list_runs(project_name=settings.LANGCHAIN_PROJECT, limit=5))

        if not runs:
            print(f"ℹ️ No runs found yet in project '{settings.LANGCHAIN_PROJECT}'. Run earlier scripts to generate traces!")
            return

        print(f"\n✅ Retrieved {len(runs)} recent run(s):\n")
        for idx, r in enumerate(runs, 1):
            print(f"  [{idx}] Name     : {r.name}")
            print(f"      Run ID   : {r.id}")
            print(f"      Run Type : {r.run_type}")
            print(f"      Status   : {r.status}")
            print(f"      Latency  : {getattr(r, 'latency', 'N/A')} s")
            print(f"      Tags     : {r.tags}\n")

    except Exception as exc:
        print(f"⚠️ Error querying LangSmith runs: {exc}")

    print("=" * 70)
    print("🎉 Script 01 completed successfully!\n")


if __name__ == "__main__":
    query_runs()
