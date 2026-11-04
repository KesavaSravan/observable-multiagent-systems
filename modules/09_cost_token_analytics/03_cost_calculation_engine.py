"""
Module 09 - Script 03: Multi-Provider Pricing Matrix & Cost Engine

Demonstrates:
1. Multi-provider pricing matrix (OpenAI, Anthropic Claude, Google Gemini, Groq)
2. Computing exact USD costs for prompt tokens and completion tokens
3. Projecting costs per 1,000 incident runs
"""

import sys
from typing import Dict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Pricing matrix per 1 Million tokens (USD)
PRICING_PER_MILLION = {
    # OpenAI
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    # Anthropic
    "claude-3-5-sonnet": {"prompt": 3.00, "completion": 15.00},
    "claude-3-5-haiku": {"prompt": 0.80, "completion": 4.00},
    # Google
    "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    "gemini-1.5-pro": {"prompt": 1.25, "completion": 5.00},
    # Groq (Llama 3.3)
    "llama-3.3-70b-versatile": {"prompt": 0.59, "completion": 0.79}
}


def calculate_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Computes exact USD cost for a given model invocation."""
    pricing = PRICING_PER_MILLION.get(model_name, {"prompt": 1.0, "completion": 2.0})
    cost_prompt = (prompt_tokens / 1_000_000) * pricing["prompt"]
    cost_comp = (completion_tokens / 1_000_000) * pricing["completion"]
    return cost_prompt + cost_comp


def main():
    print("=" * 70)
    print("  MODULE 09: MULTI-PROVIDER PRICING MATRIX & COST ENGINE")
    print("=" * 70)

    # Sample agent run consuming 5,000 prompt tokens and 1,200 completion tokens
    test_prompt_tokens = 5_000
    test_completion_tokens = 1_200

    print(f"\n📦 Sample Multi-Agent Run Profile:")
    print(f"   • Prompt Tokens    : {test_prompt_tokens:,}")
    print(f"   • Completion Tokens: {test_completion_tokens:,}")
    print(f"   • Total Tokens     : {test_prompt_tokens + test_completion_tokens:,}\n")

    print(f"{'Provider / Model':<28} | {'Cost / Run ($)':<16} | {'Cost / 10k Runs ($)':<20}")
    print("-" * 70)

    for model, rates in PRICING_PER_MILLION.items():
        cost_single = calculate_cost(model, test_prompt_tokens, test_completion_tokens)
        cost_10k = cost_single * 10_000
        print(f"{model:<28} | ${cost_single:>12.6f} | ${cost_10k:>16.2f}")

    print("-" * 70)
    print("💡 Cost Takeaway:")
    print("   Switching high-frequency triage nodes to 'gemini-1.5-flash' or 'gpt-4o-mini'")
    print("   reduces operational costs by over 90% compared to frontier models.")
    print("\n" + "=" * 70)
    print("✅ Completed Script 03 successfully!\n")


if __name__ == "__main__":
    main()
