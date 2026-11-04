# Module 03: Tool-Calling ReAct Loop & Trace Metadata

Welcome to **Module 03** of the *LangGraph + LangSmith + Grafana Observability* curriculum.

## 🎯 Learning Objectives
By completing this module, you will:
1. Define deterministic, type-safe tools using the `@tool` decorator.
2. Bind tools to multi-provider LLMs and utilize LangGraph's prebuilt `ToolNode`.
3. Construct a standard **ReAct (Reason + Act)** cyclic loop using `tools_condition` conditional edges.
4. Instrument tool invocations with custom **LangSmith metadata, run tags, and execution status**.

---

## 📂 Scripts in this Module

| Script | Purpose | What it Teaches |
|---|---|---|
| `01_tool_definition_basics.py` | Tool Schemas & Decorator | How `@tool` converts Python functions into JSON schemas for OpenAI/Anthropic/Gemini/Groq tool calling. |
| `02_tool_node_execution.py` | ToolNode Mechanics | Direct execution of `ToolNode`, error handling, and tool message output structures. |
| `03_react_graph_loop.py` | ReAct StateGraph Cycle | Building the cyclic agent loop: `agent_node -> tools_condition -> [ToolNode -> agent_node \| END]`. |
| `04_react_tracing_metadata.py` | Tracing & Metadata Injection | Tracking tool parameters, return values, tool latency, and metadata tags in LangSmith. |

---

## 🔍 What to Check in the LangSmith UI

After running `04_react_tracing_metadata.py`:
1. Open your project in [LangSmith Cloud](https://smith.langchain.com).
2. Click on the run named `react-agent-investigation`.
3. In the run tree, observe:
   - **`agent` node span**: Contains the model's reasoning and the generated `tool_calls` payload.
   - **`tools` node span**: Expands into individual tool executions (e.g. `query_k8s_logs`, `get_service_health`).
   - **Tool Input / Output**: Expand each tool span to see the exact input parameters and JSON outputs.
   - **Loop iterations**: If the model called multiple tools sequentially, each cycle appears cleanly nested.
