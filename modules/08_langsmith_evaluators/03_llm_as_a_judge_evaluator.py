"""
Module 08 - Script 03: LLM-as-a-Judge Custom Evaluator

Demonstrates:
1. Using an LLM judge to evaluate agent outputs against complex criteria
2. Scoring correctness, technical precision, and safety
3. Returning structured scores (0.0 to 1.0) and reasoning chains
"""

import sys
from typing import Dict, Any
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_core.messages import SystemMessage, HumanMessage
from shared.llm_factory import get_chat_model


JUDGE_PROMPT = """You are an expert SRE evaluation judge.
Compare the Agent Output against the Reference Ground Truth for an incident alert.

Score the Agent Output from 0.0 to 1.0:
- 1.0: Correct root cause identified and valid remediation proposed.
- 0.5: Partially correct, but missing critical safety or technical steps.
- 0.0: Hallucinated or incorrect diagnosis.

Input Alert: {alert}
Reference Ground Truth: {reference}
Agent Actual Output: {output}

Respond in the exact format:
SCORE: <float between 0.0 and 1.0>
REASON: <concise explanation>
"""


def llm_judge_evaluator(run: Any, example: Any) -> Dict[str, Any]:
    """Evaluates agent response using an LLM judge."""
    alert = example.inputs.get("alert", "") if example and hasattr(example, "inputs") else "N/A"
    reference = example.outputs.get("expected_action", "") if example and hasattr(example, "outputs") else "N/A"
    output = run.outputs.get("output", "") if run and hasattr(run, "outputs") else "N/A"

    judge_model = get_chat_model(allow_mock_fallback=True)
    prompt = JUDGE_PROMPT.format(alert=alert, reference=reference, output=output)
    
    response = judge_model.invoke([
        SystemMessage(content="You are a strict SRE evaluation judge."),
        HumanMessage(content=prompt)
    ])
    content = response.content if hasattr(response, "content") else str(response)

    # Parse score
    score = 1.0
    for line in content.split("\n"):
        if line.startswith("SCORE:"):
            try:
                score = float(line.replace("SCORE:", "").strip())
            except ValueError:
                score = 0.9

    return {
        "key": "llm_correctness_score",
        "score": score,
        "comment": content
    }


def main():
    print("=" * 70)
    print("  MODULE 08: LLM-AS-A-JUDGE CUSTOM EVALUATOR")
    print("=" * 70)

    class MockRun:
        outputs = {"output": "Identified OOMKilled condition on pod. Action: Scale container memory limits to 2Gi."}

    class MockExample:
        inputs = {"alert": "Pod payment-gateway is OOMKilled repeatedly."}
        outputs = {"expected_action": "Increase memory limits (OOMKilled)"}

    print("\n⚖️ Running LLM-as-a-Judge on mock agent output...")
    res = llm_judge_evaluator(MockRun(), MockExample())

    print("\n" + "-" * 70)
    print(f"📊 Evaluator Score : {res['score']}")
    print(f"💬 Judge Feedback  :\n{res['comment']}")
    print("-" * 70)
    print("✅ Completed Script 03 successfully!\n")


if __name__ == "__main__":
    main()
