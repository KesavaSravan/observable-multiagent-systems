# Module 04: Conditional Routing, Dynamic Branching & Tagged Filtering

Welcome to **Module 04** of the *LangGraph + LangSmith + Grafana Observability* curriculum.

## 🎯 Learning Objectives
By completing this module, you will:
1. Implement deterministic and LLM-driven **Conditional Routing** using `builder.add_conditional_edges`.
2. Construct **parallel fan-out / fan-in** topologies to run concurrent diagnostic workers and reduce findings.
3. Dynamically inject **route tags** (e.g. `route:security`, `route:database`, `priority:critical`) into LangSmith execution configs.
4. Filter, isolate, and debug specific branch failures in the LangSmith Runs table.

---

## 📂 Scripts in this Module

| Script | Purpose | What it Teaches |
|---|---|---|
| `01_intent_classification_router.py` | LLM Intent Router | Using an LLM classifier to determine whether to route to `database_team`, `security_team`, or `network_team`. |
| `02_dynamic_conditional_edges.py` | Robust Edge Mappings | Mapping return keys to target nodes with safe fallback paths. |
| `03_parallel_fanout_fanin.py` | Parallel Fan-out & Fan-in | Dispatching queries to 3 diagnostic nodes in parallel and aggregating results via reducers. |
| `04_trace_tagging_for_filters.py` | Tagged Observability Filtering | Attaching route-specific tags to enable granular filtering in LangSmith. |

---

## 🔍 What to Check in the LangSmith UI

After running `04_trace_tagging_for_filters.py`:
1. Open [LangSmith Cloud](https://smith.langchain.com).
2. Use the **Filter Tag** search bar at the top:
   - Filter by: `route:security` -> Observe only security incident runs.
   - Filter by: `route:database` -> Observe database latency investigations.
3. Notice how branch tags allow you to isolate performance metrics and error rates for specific business workflows.
