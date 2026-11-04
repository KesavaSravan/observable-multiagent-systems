"""
Module 03 - Script 04: ReAct Tracing, Metadata Tags & Run Inspection

Demonstrates:
1. Injecting rich runtime metadata and tags into the ReAct graph execution
2. Capturing and inspecting the nested tool call spans in LangSmith
3. Outputting direct LangSmith run URLs
"""

import sys
from typing import TypedDict, Annotated, Sequence
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.tracers.context import collect_runs
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from shared.llm_factory import get_chat_model
from shared.config import settings


@tool
def inspect_pod_crashloops(namespace: str) -> str:
    """Inspect pods in CrashLoopBackOff state in a Kubernetes namespace."""
    return f"Namespace '{namespace}': Found 1 failing pod -> 'payment-worker-84fb-x2' (ExitCode: 137 OOMKilled)."


@tool
def get_memory_limits(namespace: str) -> str:
    """Check configured memory limits and requests for pods in a namespace."""
    return f"Namespace '{namespace}': 'payment-worker' has request: 512Mi, limit: 1Gi."


tools = [inspect_pod_crashloops, get_memory_limits]


class ReActState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def agent_node(state: ReActState) -> dict:
    model = get_chat_model(allow_mock_fallback=True)
    if hasattr(model, "bind_tools"):
        model = model.bind_tools(tools)
    res = model.invoke(state["messages"])
    return {"messages": [res]}


def main():
    print("=" * 70)
    print("  MODULE 03: REACT TRACING, METADATA TAGS & RUN INSPECTION")
    print("=" * 70)

    # Build Graph
    builder = StateGraph(ReActState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    graph = builder.compile()

    # Detailed production tags and metadata for LangSmith
    config = {
        "run_name": "react-agent-investigation",
        "tags": [
            "module:03_react",
            "tier:production",
            "agent_type:k8s_debugger",
            "tools:k8s_crashloops_memory"
        ],
        "metadata": {
            "cluster": "us-west-2-prod-eks",
            "target_namespace": "payments-prod",
            "trigger": "pagerduty_alert_8912"
        }
    }

    initial_messages = [
        SystemMessage(content="You are an autonomous Kubernetes SRE agent. Investigate crash loops in the namespace."),
        HumanMessage(content="Investigate why pods are failing in the 'payments-prod' namespace and check their memory limits.")
    ]

    print("\n▶️ Invoking Traced ReAct Agent Graph...")
    with collect_runs() as cb:
        result = graph.invoke({"messages": initial_messages}, config=config)
        root_run = cb.traced_runs[0] if cb.traced_runs else None

    print("\n" + "-" * 70)
    print("🤖 Agent Final Response:")
    last_msg = result["messages"][-1]
    print(last_msg.content if last_msg.content else "[Completed Tool Calls]")
    print("-" * 70)

    if root_run:
        print("\n🔍 LangSmith Trace Decomposition:")
        print(f"   • Root Run ID   : {root_run.id}")
        print(f"   • Tags Attached : {config['tags']}")
        print(f"   • Metadata      : {config['metadata']}")
        if settings.LANGCHAIN_API_KEY and not settings.LANGCHAIN_API_KEY.startswith("lsv2_pt_your"):
            print(f"   🔗 LangSmith URL: https://smith.langchain.com/o/default/projects/p/{settings.LANGCHAIN_PROJECT}/r/{root_run.id}")

    print("\n" + "=" * 70)
    print("🎉 Module 03 completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
