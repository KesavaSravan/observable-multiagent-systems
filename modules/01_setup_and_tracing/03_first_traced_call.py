"""
Module 01 - Script 03: First Traced LLM Invocation with LangSmith

Demonstrates:
1. Enabling automatic tracing via LANGCHAIN_TRACING_V2
2. Passing custom tags and metadata to the invocation config
3. Extracting and printing the LangSmith run trace URL
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

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tracers.context import collect_runs
from shared.llm_factory import get_chat_model
from shared.config import settings


def run_first_traced_call():
    print("=" * 70)
    print("  FIRST DISTRIBUTED TRACED INVOCATION")
    print("=" * 70)

    # 1. Initialize model
    model = get_chat_model(allow_mock_fallback=True)

    # 2. Build messages
    messages = [
        SystemMessage(content="You are an SRE AI assistant specializing in observability."),
        HumanMessage(content="What are the three pillars of observability in cloud computing, and how does tracing apply to LLM agents?")
    ]

    # 3. Invocation configuration with rich tags and metadata for LangSmith filtering
    config = {
        "run_name": "first-traced-llm-call",
        "tags": ["module:01_setup", "env:development", "type:verification"],
        "metadata": {
            "course": "LangGraph + LangSmith + Grafana",
            "engineer_role": "System Engineer",
            "provider": settings.LLM_PROVIDER,
            "model": settings.LLM_MODEL,
        }
    }

    print(f"📡 Executing LLM invocation with LangSmith tracing enabled...")
    print(f"   Project : '{settings.LANGCHAIN_PROJECT}'")
    print(f"   Tags    : {config['tags']}")
    print(f"   Metadata: {config['metadata']}\n")

    # 4. Use collect_runs context manager to capture the exact run ID
    with collect_runs() as cb:
        response = model.invoke(messages, config=config)
        run = cb.traced_runs[0] if cb.traced_runs else None

    print("-" * 70)
    print(f"🤖 LLM Response ({type(model).__name__}):\n")
    print(response.content)
    print("-" * 70)

    # 5. Output trace diagnostics
    if run:
        print(f"\n✅ LangSmith Trace Captured:")
        print(f"   • Run ID     : {run.id}")
        print(f"   • Run Name   : {run.name}")
        print(f"   • Latency    : {getattr(run, 'latency', 'N/A')} s")
        if settings.LANGCHAIN_API_KEY and not settings.LANGCHAIN_API_KEY.startswith("lsv2_pt_your"):
            print(f"   🔗 Trace URL : https://smith.langchain.com/o/default/projects/p/{settings.LANGCHAIN_PROJECT}/r/{run.id}")
        else:
            print(f"   ℹ️ Cloud URL: Configure your LANGCHAIN_API_KEY in .env to view in LangSmith Web UI.")
    else:
        print("ℹ️ Run completed in local mode.")

    print("\n" + "=" * 70)
    print("🎉 Module 01 completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    run_first_traced_call()
