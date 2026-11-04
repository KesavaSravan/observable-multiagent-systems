# Module 07: Human-in-the-Loop (HITL), Breakpoints & State Intervention

Welcome to **Module 07** of the *LangGraph + LangSmith + Grafana Observability* curriculum.

## 🎯 Learning Objectives
By completing this module, you will:
1. Implement static breakpoints using `compile(interrupt_before=["node_name"])`.
2. Pause autonomous agent execution prior to destructive actions (e.g. database schema migrations, restarting pods, rotating secrets).
3. Inspect and edit the in-flight state via `graph.get_state()` and `graph.update_state()`.
4. Resume execution and observe how LangSmith maintains **trace continuity** across disjoint execution intervals.

---

## 📂 Scripts in this Module

| Script | Purpose | What it Teaches |
|---|---|---|
| `01_interrupt_before_action.py` | Static Breakpoints | Halting graph execution automatically right before a dangerous node runs. |
| `02_state_inspection_and_update.py` | State Interventions | Reading paused state, human editing variables, and resuming with modified state. |
| `03_approval_rejection_workflows.py` | Approval / Rejection Logic | Complete approval flow: human provides explicit YES/NO decision. |
| `04_trace_continuity_on_resume.py` | Trace Continuity Telemetry | Showing how LangSmith correlates the initial run and the resumed run under one thread history. |

---

## 🔍 What to Check in the LangSmith UI

After running `04_trace_continuity_on_resume.py`:
1. Open [LangSmith Cloud](https://smith.langchain.com).
2. Filter by the thread ID (e.g. `hitl-thread-701`).
3. Notice that:
   - The first run stopped cleanly at the breakpoint without crashing.
   - The second resumed run picked up the exact state without losing earlier span context.
