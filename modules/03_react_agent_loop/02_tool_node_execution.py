"""
Module 03 - Script 02: ToolNode Execution and Error Resilience

Demonstrates:
1. Instantiating LangGraph's prebuilt ToolNode
2. Invoking ToolNode directly with simulated AIMessages containing tool_calls
3. Inspecting the returned ToolMessage objects
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode


@tool
def fetch_disk_usage(node_ip: str) -> str:
    """Check disk utilization percentage on a specific cluster node."""
    if "error" in node_ip.lower():
        raise RuntimeError(f"Connection refused to host {node_ip}")
    return f"Host {node_ip}: /dev/sda1 is at 88% capacity (52GB available)."


def main():
    print("=" * 70)
    print("  MODULE 03: TOOLNODE EXECUTION AND RESILIENCE")
    print("=" * 70)

    # 1. Initialize ToolNode
    tools = [fetch_disk_usage]
    tool_node = ToolNode(tools)

    # 2. Simulate Model Output requesting a tool call
    simulated_ai_message = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "fetch_disk_usage",
                "args": {"node_ip": "10.0.1.45"},
                "id": "call_disk_check_001"
            }
        ]
    )

    print("\n🤖 Input AI Message with tool_calls payload:")
    print(f"  Tool: {simulated_ai_message.tool_calls[0]['name']}")
    print(f"  Args: {simulated_ai_message.tool_calls[0]['args']}")

    # 3. Invoke ToolNode
    print("\n⚙️ Invoking ToolNode...")
    response_state = tool_node.invoke({"messages": [simulated_ai_message]})

    print("\n📦 Output Messages from ToolNode:")
    for msg in response_state["messages"]:
        print(f"  • Type: {type(msg).__name__}")
        print(f"  • Tool Call ID: {getattr(msg, 'tool_call_id', 'N/A')}")
        print(f"  • Content: {msg.content}")

    print("\n" + "=" * 70)
    print("✅ Completed Script 02 successfully!\n")


if __name__ == "__main__":
    main()
