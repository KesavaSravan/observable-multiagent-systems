"""
Module 01 - Script 02: Multi-Provider LLM Factory Demonstration

Demonstrates how to dynamically instantiate chat models across multiple providers:
- OpenAI
- Anthropic Claude
- Google Gemini
- Groq
- Mock Fallback (for offline testing)
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_core.messages import HumanMessage, SystemMessage
from shared.llm_factory import get_chat_model, RECOMMENDED_MODELS, UnauthorizedModelPolicyError
from shared.config import settings


def demonstrate_providers():
    print("=" * 70)
    print("  MULTI-PROVIDER LLM FACTORY IN ACTION")
    print("=" * 70)

    test_prompt = [
        SystemMessage(content="You are an expert distributed systems observability engineer."),
        HumanMessage(content="Explain in one sentence why distributed tracing is crucial for multi-agent LLM systems.")
    ]

    # Test providers list
    providers = ["openai", "anthropic", "google", "groq"]
    
    current_active_provider = os.getenv("LLM_PROVIDER", settings.LLM_PROVIDER)
    print(f"👉 Current Active Provider in environment: [{current_active_provider.upper()}]\n")

    # 1. Test Active Configured Model
    print(f"--- 1. Invoking Configured Default Model ({current_active_provider}) ---")
    model = get_chat_model(allow_mock_fallback=True)
    try:
        response = model.invoke(test_prompt)
        print(f"Response ({type(model).__name__}):\n{response.content.strip()}\n")
    except Exception as e:
        print(f"Execution notice: {e}\n")

    # 2. Test Explicit Overrides
    print("--- 2. Programmatic Provider Switching Examples ---")
    for prov in providers:
        rec_model = RECOMMENDED_MODELS.get(prov, ["default"])[0]
        print(f"• Instantiating [{prov.upper()}] with model '{rec_model}'...")
        try:
            prov_model = get_chat_model(provider=prov, model=rec_model, project_id="course_learning", allow_mock_fallback=True)
            print(f"  Initialized class: {prov_model.__class__.__name__}")
        except UnauthorizedModelPolicyError as pe:
            print(f"  🛡️ Policy Guardrail: {pe}")

    print("\n" + "=" * 70)
    print("💡 Key Takeaway: You can switch between any LLM provider at any time by")
    print("   setting LLM_PROVIDER in .env or passing provider='...' to get_chat_model().")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_providers()
