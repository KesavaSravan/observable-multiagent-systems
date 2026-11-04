# Module 06: Multi-Agent Systems, Supervisor Orchestration & Nested Traces

Welcome to **Module 06** of the *LangGraph + LangSmith + Grafana Observability* curriculum.

## 🎯 Learning Objectives
By completing this module, you will:
1. Architect hierarchical multi-agent systems using the **Supervisor Orchestration Pattern**.
2. Embed compiled sub-graphs as isolated nodes within a parent workflow.
3. Manage multi-agent **state handoffs, task delegation, and consensus loops**.
4. Visualize deep, hierarchical **nested span trees** in LangSmith using `@traceable`.

---

## 📂 Scripts in this Module

| Script | Purpose | What it Teaches |
|---|---|---|
| `01_subagent_as_graph_node.py` | Subgraph Composition | Compiling a self-contained sub-agent graph and attaching it directly as a node in a parent graph. |
| `02_supervisor_router_pattern.py` | Central Supervisor Router | The Supervisor evaluates tasks, delegates to `ResearchAgent` or `CodeAgent`, and determines when the mission is COMPLETE. |
| `03_agent_handoffs_and_consensus.py` | Peer-to-Peer Handoffs | Direct agent handoffs where Researcher passes state to Coder, who iterates until reaching consensus. |
| `04_nested_trace_trees.py` | Deep Trace Tree Telemetry | Using `@traceable` and LangSmith run hierarchy to inspect multi-agent reasoning trees. |

---

## 🔍 What to Check in the LangSmith UI

After running `04_nested_trace_trees.py`:
1. Open your project in [LangSmith Cloud](https://smith.langchain.com).
2. Look for the top-level run named `supervisor-multiagent-run`.
3. Notice the hierarchical span tree:
   - `Supervisor` (Parent Span)
     - ├─ `ResearchAgent Sub-Graph` (Child Span)
     - │    ├─ `search_tool` (Grandchild Span)
     - │    └─ `summarize_logs` (Grandchild Span)
     - └─ `CoderAgent Sub-Graph` (Child Span)
          ├─ `generate_patch` (Grandchild Span)
          └─ `syntax_check` (Grandchild Span)
4. Each agent's tokens, latency, and inputs/outputs are individually isolated and rolled up to the parent!
