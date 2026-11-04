"""
Module 01 - Script 01: Environment and SDK Verification

This script verifies:
1. Python dependencies (langgraph, langsmith, langchain, etc.)
2. Environment variables from .env
3. Connectivity to LangSmith API endpoint
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared.config import settings


def verify_environment():
    print("=" * 70)
    print("  LANGGRAPH + LANGSMITH OBSERVABILITY: ENVIRONMENT VERIFICATION")
    print("=" * 70)

    # 1. Inspect loaded settings
    settings.print_diagnostics()

    # 2. Check LangSmith Client connectivity
    print("\n🔍 Testing connection to LangSmith API...")
    if settings.LANGCHAIN_API_KEY and not settings.LANGCHAIN_API_KEY.startswith("lsv2_pt_your"):
        try:
            from langsmith import Client
            client = Client(api_key=settings.LANGCHAIN_API_KEY, api_url=settings.LANGCHAIN_ENDPOINT)
            projects = list(client.list_projects(limit=5))
            print(f"✅ Successfully connected to LangSmith! Found {len(projects)} existing project(s).")
            print(f"🎯 Target Project: '{settings.LANGCHAIN_PROJECT}'")
        except Exception as e:
            print(f"⚠️ LangSmith connection check failed: {e}")
            print("   Please check your LANGCHAIN_API_KEY in .env.")
    else:
        print("ℹ️ LANGCHAIN_API_KEY is not configured yet. Traces will run locally / offline.")
        print("   To enable cloud tracing, create an API key at https://smith.langchain.com and update .env")

    print("\n" + "=" * 70)
    print("🎉 Verification complete. Ready for Script 02!")
    print("=" * 70)


if __name__ == "__main__":
    verify_environment()
