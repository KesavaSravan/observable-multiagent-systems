"""
Module 03 - Script 03: Complete Cyclic ReAct Agent Graph

Demonstrates:
1. Constructing a complete ReAct loop: agent -> tools_condition -> [tools -> agent | END]
2. Passing messages state channel with add_messages reducer
3. Multi-turn reasoning where the agent queries a tool and then answers
"""

import sys
from typing import TypedDict, Annotated, Sequence
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

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from shared.llm_factory import get_chat_model


# 1. Define Tools
@tool
def lookup_database_latency(db_cluster: str) -> str:
    """Check query latency and active connection pool size for a database cluster."""
    return f"Cluster '{db_cluster}': P99 Latency = 320ms (Spike detected), Active Connections = 490/500."


tools = [lookup_database_latency]


# 2. Define State with add_messages reducer
class ReActAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# 3. Define Model Node
def call_agent_model(state: ReActAgentState) -> dict:
    """Agent node that calls the LLM with bound tools."""
    print(" [Node: agent] Reason step...")
    model = get_chat_model(allow_mock_fallback=True)
    if hasattr(model, "bind_tools"):
        model = model.bind_tools(tools)
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def main():
    print("=" * 70)
    print("  MODULE 03: COMPLETE REACT AGENT GRAPH LOOP")
    print("=" * 70)

    # 4. Build Graph
    builder = StateGraph(ReActAgentState)
    builder.add_node("agent", call_agent_model)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    # tools_condition routes to 'tools' if the last message has tool_calls, otherwise END
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    graph = builder.compile()

    # 5. Execute ReAct Loop
    initial_messages = [
        SystemMessage(content="You are an SRE assistant. Use tools when needed to investigate system alerts."),
        HumanMessage(content="Check database latency for the 'postgres-orders-primary' cluster.")
    ]

    print("\n▶️ Running ReAct Agent Loop...")
    final_state = graph.invoke(
        {"messages": initial_messages},
        config={"run_name": "react-agent-loop-run", "tags": ["module:03_react", "loop:cyclic"]}
    )

    print("\n" + "-" * 70)
    print("📜 Complete Message History Across ReAct Cycles:")
    for idx, msg in enumerate(final_state["messages"], 1):
        role = type(msg).__name__.replace("Message", "").upper()
        content = msg.content if msg.content else f"[Tool Calls: {getattr(msg, 'tool_calls', [])}]"
        print(f"  {idx}. [{role}]: {content}")
    print("-" * 70)
    print("✅ Completed Script 03 successfully!\n")


if __name__ == "__main__":
    main()
