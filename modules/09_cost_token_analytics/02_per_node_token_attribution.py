"""
Module 09 - Script 02: Per-Node Token Attribution and Rollup

Demonstrates:
1. Decomposing total execution token counts into node-level contributions
2. Calculating prompt tokens vs completion tokens per graph step
3. Formatting a token attribution summary table
"""

import sys
from typing import Dict, List, Any
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def calculate_token_attribution(simulated_run_tree: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregates token consumption per node and rolls up to total."""
    node_summary = {}
    total_prompt = 0
    total_completion = 0

    for node in simulated_run_tree:
        name = node["node_name"]
        p_tok = node.get("prompt_tokens", 0)
        c_tok = node.get("completion_tokens", 0)
        tot = p_tok + c_tok

        node_summary[name] = {
            "prompt_tokens": p_tok,
            "completion_tokens": c_tok,
            "total_tokens": tot
        }
        total_prompt += p_tok
        total_completion += c_tok

    return {
        "nodes": node_summary,
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "grand_total_tokens": total_prompt + total_completion
    }


def main():
    print("=" * 70)
    print("  MODULE 09: PER-NODE TOKEN ATTRIBUTION AND ROLLUP")
    print("=" * 70)

    # Simulated multi-agent run tree with realistic token usages
    mock_run_tree = [
        {"node_name": "supervisor_triage", "prompt_tokens": 450, "completion_tokens": 85},
        {"node_name": "log_researcher_agent", "prompt_tokens": 1250, "completion_tokens": 320},
        {"node_name": "k8s_log_tool", "prompt_tokens": 0, "completion_tokens": 0},
        {"node_name": "remediation_coder_agent", "prompt_tokens": 1850, "completion_tokens": 410},
        {"node_name": "final_summary_node", "prompt_tokens": 620, "completion_tokens": 150}
    ]

    attribution = calculate_token_attribution(mock_run_tree)

    print("\n📊 Per-Node Token Breakdown:")
    print(f"{'Node Name':<28} | {'Prompt':<10} | {'Completion':<10} | {'Total':<10} | {'Share (%)':<10}")
    print("-" * 75)

    grand_total = attribution["grand_total_tokens"]
    for node, data in attribution["nodes"].items():
        pct = (data["total_tokens"] / grand_total * 100) if grand_total else 0.0
        print(f"{node:<28} | {data['prompt_tokens']:<10} | {data['completion_tokens']:<10} | {data['total_tokens']:<10} | {pct:>8.1f}%")

    print("-" * 75)
    print(f"{'GRAND TOTAL':<28} | {attribution['total_prompt_tokens']:<10} | {attribution['total_completion_tokens']:<10} | {grand_total:<10} | {'100.0%':>8}")

    print("\n💡 Key Insight: 'remediation_coder_agent' accounts for the largest token share (44%).")
    print("   Prompt caching or few-shot pruning on this node yields the greatest cost reduction.")
    print("\n" + "=" * 70)
    print("✅ Completed Script 02 successfully!\n")


if __name__ == "__main__":
    main()
