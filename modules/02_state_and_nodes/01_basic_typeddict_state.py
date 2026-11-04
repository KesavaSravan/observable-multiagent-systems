"""
Module 02 - Script 01: Basic TypedDict State and Single Traced Node

Demonstrates:
1. Defining a TypedDict state schema
2. Creating a node function that modifies state
3. Compiling a StateGraph with START and END edges
4. Invoking the graph with LangSmith tracing enabled
"""

import sys
from typing import TypedDict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from shared.llm_factory import get_chat_model


# 1. Define Graph State Schema
class SimpleAgentState(TypedDict):
    input_query: str
    intermediate_notes: str
    final_answer: str
    step_count: int


# 2. Define Node Function
def analyze_query_node(state: SimpleAgentState) -> dict:
    """Node that uses LLM to analyze the input query."""
    print(f" [Node: analyze_query] Processing query: '{state['input_query']}'")
    
    model = get_chat_model(allow_mock_fallback=True)
    prompt = f"Analyze this incident alert in 2 bullet points: {state['input_query']}"
    response = model.invoke(prompt)
    
    return {
        "intermediate_notes": "Identified high memory saturation on pod-auth-service.",
        "final_answer": response.content if hasattr(response, "content") else str(response),
        "step_count": state.get("step_count", 0) + 1
    }


def main():
    print("=" * 70)
    print("  MODULE 02: BASIC TYPEDDICT STATE & SINGLE NODE")
    print("=" * 70)

    # 3. Build Graph
    builder = StateGraph(SimpleAgentState)
    builder.add_node("analyze_query", analyze_query_node)
    builder.add_edge(START, "analyze_query")
    builder.add_edge("analyze_query", END)
    
    # 4. Compile Graph
    graph = builder.compile()

    # 5. Execute with Traced Config
    initial_state: SimpleAgentState = {
        "input_query": "ALERT: OOMKilled on auth-service-pod-789 in us-east-1 production cluster.",
        "intermediate_notes": "",
        "final_answer": "",
        "step_count": 0
    }

    config = {
        "run_name": "basic-typeddict-state-run",
        "tags": ["module:02_state", "node_count:1"]
    }

    print("\n▶️ Invoking StateGraph...")
    result = graph.invoke(initial_state, config=config)

    print("\n" + "-" * 70)
    print("🎯 Execution Result State:")
    for k, v in result.items():
        print(f"  • {k}: {v}")
    print("-" * 70)
    print("✅ Completed Script 01 successfully!\n")


if __name__ == "__main__":
    main()
