"""
Module 08 - Script 04: Running Complete LangSmith Evaluation Experiments

Demonstrates:
1. Defining a target LangGraph app function to evaluate
2. Running the evaluate() function from langsmith.evaluation
3. Logging experiment metrics and viewing scorecards
"""

import sys
from typing import Dict, Any
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared.config import settings
from shared.llm_factory import get_chat_model


# 1. Target function being evaluated
def target_agent_pipeline(inputs: Dict[str, Any]) -> Dict[str, Any]:
    alert = inputs.get("alert", "")
    model = get_chat_model(allow_mock_fallback=True)
    prompt = f"You are an SRE incident agent. Propose remediation for alert: {alert}"
    response = model.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)
    return {"output": content}


# 2. Local Evaluator
def keyword_evaluator(run: Any, example: Any) -> Dict[str, Any]:
    expected = (example.outputs.get("expected_action", "") if example and hasattr(example, "outputs") else "").lower()
    actual = (run.outputs.get("output", "") if run and hasattr(run, "outputs") else "").lower()
    words = expected.split()
    matched = sum(1 for w in words if w in actual)
    score = (matched / len(words)) if words else 1.0
    return {"key": "keyword_coverage", "score": min(score, 1.0)}


def main():
    print("=" * 70)
    print("  MODULE 08: RUNNING LANGSMITH EVALUATION EXPERIMENTS")
    print("=" * 70)

    dataset_name = "sre-incident-benchmarks"

    if not settings.LANGCHAIN_API_KEY or settings.LANGCHAIN_API_KEY.startswith("lsv2_pt_your"):
        print("ℹ️ LANGCHAIN_API_KEY not configured. Simulating local benchmark run:")
        from modules.08_langsmith_evaluators.01_create_dataset_programmatic import BENCHMARK_EXAMPLES
        
        scores = []
        for idx, eg in enumerate(BENCHMARK_EXAMPLES, 1):
            out = target_agent_pipeline(eg["inputs"])
            class LocalRun:
                outputs = out
            score_res = keyword_evaluator(LocalRun(), type("Eg", (), {"outputs": eg["outputs"]})())
            scores.append(score_res["score"])
            print(f"  [{idx}] Alert: {eg['inputs']['alert'][:40]}...")
            print(f"      Score: {score_res['score']:.2f} | Output: {out['output'][:60]}...\n")
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        print(f"📊 Mean Benchmark Score: {avg_score * 100:.1f}%")
        print("\n💡 Configure LANGCHAIN_API_KEY in .env to run cloud evaluate() experiments.")
        return

    try:
        from langsmith.evaluation import evaluate
        print(f"🚀 Launching LangSmith evaluate() on dataset '{dataset_name}'...")
        results = evaluate(
            target_agent_pipeline,
            data=dataset_name,
            evaluators=[keyword_evaluator],
            experiment_prefix="sre-agent-eval",
            max_concurrency=2
        )
        print(f"\n✅ Evaluation experiment completed successfully!")
        print(f"🔗 View Experiment in LangSmith: https://smith.langchain.com/o/default/datasets")
    except Exception as exc:
        print(f"⚠️ Error during evaluate(): {exc}")

    print("\n" + "=" * 70)
    print("🎉 Module 08 completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
