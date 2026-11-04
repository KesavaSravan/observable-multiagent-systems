"""
Module 08 - Script 02: Deterministic & Semantic Custom Evaluators

Demonstrates:
1. Writing deterministic Python evaluator functions compatible with LangSmith
2. Scoring keyword relevance and structure
3. Returning structured feedback dictionaries {"key": "...", "score": ...}
"""

import sys
from typing import Dict, Any
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def actionability_evaluator(run: Any, example: Any) -> Dict[str, Any]:
    """
    Evaluates whether the agent output contains actionable remediation verbs
    (e.g., scale, restart, update, block, index).
    """
    output_text = str(run.outputs.get("output", "") if run.outputs else "").lower()
    action_keywords = ["scale", "restart", "index", "increase", "rotate", "block", "patch", "rollout"]
    
    score = 1.0 if any(kw in output_text for kw in action_keywords) else 0.0
    return {
        "key": "actionability_score",
        "score": score,
        "comment": f"Found action keywords: {[kw for kw in action_keywords if kw in output_text]}"
    }


def category_match_evaluator(run: Any, example: Any) -> Dict[str, Any]:
    """
    Evaluates whether the classified category matches the benchmark expected category.
    """
    expected_cat = (example.outputs.get("category", "") if example.outputs else "").lower()
    actual_output = str(run.outputs.get("output", "") if run.outputs else "").lower()
    
    match = expected_cat in actual_output
    return {
        "key": "category_accuracy",
        "score": 1.0 if match else 0.0,
        "comment": f"Expected '{expected_cat}' present in output: {match}"
    }


def main():
    print("=" * 70)
    print("  MODULE 08: DETERMINISTIC & SEMANTIC CUSTOM EVALUATORS")
    print("=" * 70)

    # Mock run and example for local verification
    class MockRun:
        outputs = {"output": "Remediation plan: Increase memory limits and restart deployment to fix infrastructure crash."}

    class MockExample:
        outputs = {"category": "infrastructure", "expected_action": "Increase memory limits"}

    mock_run = MockRun()
    mock_eg = MockExample()

    res1 = actionability_evaluator(mock_run, mock_eg)
    res2 = category_match_evaluator(mock_run, mock_eg)

    print("\n🔍 1. Actionability Evaluator Result:")
    print(f"   • Score  : {res1['score']}")
    print(f"   • Comment: {res1['comment']}")

    print("\n🔍 2. Category Match Evaluator Result:")
    print(f"   • Score  : {res2['score']}")
    print(f"   • Comment: {res2['comment']}")

    print("\n" + "=" * 70)
    print("✅ Completed Script 02 successfully!\n")


if __name__ == "__main__":
    main()
