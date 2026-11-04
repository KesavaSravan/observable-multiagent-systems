"""
Module 08 - Script 01: Programmatic Dataset Creation with LangSmith SDK

Demonstrates:
1. Connecting to LangSmith Client
2. Creating an evaluation dataset 'sre-incident-benchmarks'
3. Adding 5 gold standard evaluation examples with inputs and reference outputs
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared.config import settings

# Benchmark examples
BENCHMARK_EXAMPLES = [
    {
        "inputs": {"alert": "Pod payment-gateway-78x is in CrashLoopBackOff with ExitCode 137"},
        "outputs": {"expected_action": "Increase memory limits (OOMKilled)", "category": "infrastructure"}
    },
    {
        "inputs": {"alert": "PostgreSQL database CPU 100% due to full table scans on orders table"},
        "outputs": {"expected_action": "Add B-tree index on queried columns", "category": "database"}
    },
    {
        "inputs": {"alert": "Multiple unauthorized 401 requests from untrusted IP ranges"},
        "outputs": {"expected_action": "Block IP via Cloudflare WAF and rotate tokens", "category": "security"}
    },
    {
        "inputs": {"alert": "Redis cache connection pool timeout on checkout service"},
        "outputs": {"expected_action": "Scale Redis cluster nodes and connection pool", "category": "caching"}
    },
    {
        "inputs": {"alert": "Kafka consumer group lag growing above 50,000 messages"},
        "outputs": {"expected_action": "Scale consumer partitions and replicas", "category": "streaming"}
    }
]


def create_dataset():
    print("=" * 70)
    print("  MODULE 08: PROGRAMMATIC DATASET CREATION WITH LANGSMITH")
    print("=" * 70)

    dataset_name = "sre-incident-benchmarks"

    if not settings.LANGCHAIN_API_KEY or settings.LANGCHAIN_API_KEY.startswith("lsv2_pt_your"):
        print("ℹ️ LANGCHAIN_API_KEY not configured. Simulating local dataset creation:")
        for idx, eg in enumerate(BENCHMARK_EXAMPLES, 1):
            print(f"  [{idx}] Input: {eg['inputs']['alert']}")
            print(f"      Expected: {eg['outputs']['expected_action']} ({eg['outputs']['category']})\n")
        print("💡 Once your API key is in .env, this script will upload them to LangSmith cloud.")
        return

    try:
        from langsmith import Client
        client = Client(api_key=settings.LANGCHAIN_API_KEY, api_url=settings.LANGCHAIN_ENDPOINT)

        # Check if dataset exists or create new
        if client.has_dataset(dataset_name=dataset_name):
            print(f"ℹ️ Dataset '{dataset_name}' already exists. Retrieving...")
            dataset = client.read_dataset(dataset_name=dataset_name)
        else:
            print(f"✨ Creating new LangSmith Dataset: '{dataset_name}'...")
            dataset = client.create_dataset(
                dataset_name=dataset_name,
                description="Gold benchmark test cases for SRE incident response multi-agent system."
            )

        # Upload benchmark examples
        print(f"📤 Uploading {len(BENCHMARK_EXAMPLES)} benchmark examples...")
        for eg in BENCHMARK_EXAMPLES:
            client.create_example(
                inputs=eg["inputs"],
                outputs=eg["outputs"],
                dataset_id=dataset.id
            )

        print(f"✅ Successfully created and populated dataset '{dataset_name}' (ID: {dataset.id})!")
        print(f"🔗 View in LangSmith: https://smith.langchain.com/o/default/datasets/{dataset.id}")

    except Exception as exc:
        print(f"⚠️ Error uploading dataset to LangSmith: {exc}")

    print("\n" + "=" * 70)
    print("🎉 Script 01 completed successfully!\n")


if __name__ == "__main__":
    create_dataset()
