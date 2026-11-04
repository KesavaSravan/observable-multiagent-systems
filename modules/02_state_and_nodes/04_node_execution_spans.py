"""
Module 02 - Script 04: Inspecting Node Execution Spans & State Deltas

Demonstrates:
1. Multi-step LangGraph with sequential state transitions
2. Capturing intermediate state snapshots using LangSmith run collector
3. Programmatically inspecting parent and child execution spans
"""

import sys
import operator
from typing import TypedDict, Annotated, List
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langgraph.graph import StateGraph, START, END
from langchain_core.tracers.context import collect_runs
from shared.llm_factory import get_chat_model
from shared.config import settings


class PipelineState(TypedDict):
    raw_query: str
    cleaned_query: str
    generated_analysis: str
    final_markdown: str
    execution_steps: Annotated[List[str], operator.add]


# Node 1: Pre-process
def preprocess_node(state: PipelineState) -> dict:
    print(" [Span 1/3: preprocess_node] Sanitizing input...")
    cleaned = state["raw_query"].strip().replace("\n", " ")
    return {
        "cleaned_query": cleaned,
        "execution_steps": ["step:preprocessed"]
    }


# Node 2: Generate LLM Analysis
def analysis_node(state: PipelineState) -> dict:
    print(" [Span 2/3: analysis_node] Invoking LLM for root-cause analysis...")
    model = get_chat_model(allow_mock_fallback=True)
    prompt = f"Analyze this infrastructure issue in 1 brief sentence: {state['cleaned_query']}"
    resp = model.invoke(prompt)
    content = resp.content if hasattr(resp, "content") else str(resp)
    return {
        "generated_analysis": content,
        "execution_steps": ["step:llm_analyzed"]
    }


# Node 3: Format Output
def formatter_node(state: PipelineState) -> dict:
    print(" [Span 3/3: formatter_node] Formatting final report...")
    formatted = f"### SRE Incident Report\n\n**Finding**: {state['generated_analysis']}\n"
    return {
        "final_markdown": formatted,
        "execution_steps": ["step:formatted"]
    }


def main():
    print("=" * 70)
    print("  MODULE 02: NODE EXECUTION SPANS & STATE DELTAS")
    print("=" * 70)

    # Compile Graph
    builder = StateGraph(PipelineState)
    builder.add_node("preprocess", preprocess_node)
    builder.add_node("analyzer", analysis_node)
    builder.add_node("formatter", formatter_node)

    builder.add_edge(START, "preprocess")
    builder.add_edge("preprocess", "analyzer")
    builder.add_edge("analyzer", "formatter")
    builder.add_edge("formatter", END)

    graph = builder.compile()

    initial_input: PipelineState = {
        "raw_query": "   CRITICAL: Disk usage on /var/log hit 98% on host-prod-node-04  \n\n ",
        "cleaned_query": "",
        "generated_analysis": "",
        "final_markdown": "",
        "execution_steps": []
    }

    config = {
        "run_name": "multi-node-span-inspection",
        "tags": ["module:02_state", "span_depth:3", "pipeline:sequential"]
    }

    print("\n▶️ Invoking 3-Step Graph with Span Collection...")
    with collect_runs() as cb:
        result = graph.invoke(initial_input, config=config)
        root_run = cb.traced_runs[0] if cb.traced_runs else None

    print("\n" + "-" * 70)
    print("📄 Synthesized Output:")
    print(result["final_markdown"])
    print(f"👣 Recorded Execution Steps: {result['execution_steps']}")
    print("-" * 70)

    if root_run:
        print("\n🔍 LangSmith Span Decomposition:")
        print(f"   • Root Run ID : {root_run.id}")
        print(f"   • Root Name   : {root_run.name}")
        print(f"   • Child Nodes : preprocess -> analyzer -> formatter")
        if settings.LANGCHAIN_API_KEY and not settings.LANGCHAIN_API_KEY.startswith("lsv2_pt_your"):
            print(f"   🔗 View Tree : https://smith.langchain.com/o/default/projects/p/{settings.LANGCHAIN_PROJECT}/r/{root_run.id}")
    
    print("\n" + "=" * 70)
    print("🎉 Module 02 completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
