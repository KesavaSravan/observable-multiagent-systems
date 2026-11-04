# Module 05: Persistence, Thread Isolation & State Time-Travel

Welcome to **Module 05** of the *LangGraph + LangSmith + Grafana Observability* curriculum.

## 🎯 Learning Objectives
By completing this module, you will:
1. Enable durable state checkpointing using `MemorySaver` and `SqliteSaver`.
2. Manage session isolation using the `configurable: {"thread_id": "..."}` runtime pattern.
3. Perform **state history inspection** and **time-travel debugging** (replaying or branching from past checkpoints).
4. Observe how LangSmith automatically organizes and groups traces by **Session / Thread ID**.

---

## 📂 Scripts in this Module

| Script | Purpose | What it Teaches |
|---|---|---|
| `01_memory_saver_threads.py` | Thread Isolation Basics | Configuring `MemorySaver` and isolating two parallel user threads (`thread_1` vs `thread_2`). |
| `02_multi_turn_conversations.py` | Multi-Turn Memory | Executing multiple conversational turns while preserving full message context. |
| `03_state_history_time_travel.py` | State Time-Travel & Branching | Querying `graph.get_state_history()` and re-executing from an earlier checkpoint. |
| `04_sqlite_persistent_checkpointer.py` | Production SQLite Checkpointing | Persisting state across script restarts using SQLite database tables. |

---

## 🔍 What to Check in the LangSmith UI

After running `02_multi_turn_conversations.py`:
1. Open [LangSmith Cloud](https://smith.langchain.com).
2. Go to the **Threads / Sessions** tab (or filter runs by metadata `session_id` or `thread_id`).
3. Select `thread_id: incident-session-901`.
4. Observe the continuous timeline of runs tied to this single session across multiple turns.
