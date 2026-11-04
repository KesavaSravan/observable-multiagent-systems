"""
Module 05 - Script 02: Multi-Turn Conversations with Thread Memory

Demonstrates:
1. Multi-turn conversational chatbot remembering prior context across invocations
2. Preserving messages channel via MemorySaver checkpointer
3. Attaching session metadata for LangSmith thread visualization
"""

import sys
from typing import TypedDict, Annotated, Sequence
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from shared.llm_factory import get_chat_model


class ChatState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def chatbot_node(state: ChatState) -> dict:
    model = get_chat_model(allow_mock_fallback=True)
    resp = model.invoke(state["messages"])
    return {"messages": [resp]}


def main():
    print("=" * 70)
    print("  MODULE 05: MULTI-TURN CONVERSATIONS WITH THREAD MEMORY")
    print("=" * 70)

    memory = MemorySaver()
    builder = StateGraph(ChatState)
    builder.add_node("chatbot", chatbot_node)
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)

    graph = builder.compile(checkpointer=memory)

    session_id = "sre-incident-session-901"
    config = {
        "configurable": {"thread_id": session_id},
        "tags": ["module:05_persistence", f"session:{session_id}"],
        "metadata": {"user_id": "engineer_sravan", "channel": "cli"}
    }

    # Turn 1: Provide context
    print(f"\n▶️ Turn 1: Providing context to session '{session_id}'...")
    msg1 = HumanMessage(content="Hello! Our Kubernetes cluster in us-west-2 is called 'prod-cluster-01'. Remember that.")
    res1 = graph.invoke({"messages": [msg1]}, config=config)
    print(f"🤖 Bot: {res1['messages'][-1].content}")

    # Turn 2: Ask a question relying on past context
    print(f"\n▶️ Turn 2: Querying memory without repeating cluster name...")
    msg2 = HumanMessage(content="What was the name and region of the cluster I just told you about?")
    res2 = graph.invoke({"messages": [msg2]}, config=config)
    print(f"🤖 Bot: {res2['messages'][-1].content}")

    print("\n" + "-" * 70)
    print(f"📜 Total messages stored in checkpoint for thread '{session_id}': {len(res2['messages'])}")
    print("-" * 70)
    print("✅ Completed Script 02 successfully!\n")


if __name__ == "__main__":
    main()
