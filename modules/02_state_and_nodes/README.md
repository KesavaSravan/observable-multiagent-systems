# Module 02: State Schemas, Custom Reducers & Traced Nodes

Welcome to **Module 02** of the *LangGraph + LangSmith + Grafana Observability* curriculum.

## 🎯 Learning Objectives
By completing this module, you will:
1. Master LangGraph's central primitive: the **Graph State Schema** using `TypedDict` and `Pydantic v2`.
2. Understand state channels and **reducers** (`Annotated[list, operator.add]` and `add_messages`).
3. Construct your first compiled `StateGraph` and observe how LangSmith decomposes graph execution into **node-level child spans**.
4. Learn how state mutations, inputs, and outputs are automatically captured across the execution lifecycle.

---

## 📂 Scripts in this Module

| Script | Purpose | What it Teaches |
|---|---|---|
| `01_basic_typeddict_state.py` | Foundational StateGraph | `TypedDict` state schema, defining node functions, compiling and invoking a single-node graph. |
| `02_custom_state_reducers.py` | State Reducer Channels | How `Annotated[list, operator.add]` and custom reducer functions prevent state overwrites in multi-step graphs. |
| `03_pydantic_state_validation.py` | Schema Validation & Safety | Using Pydantic `BaseModel` for strict state validation, type enforcement, and runtime schema tracing. |
| `04_node_execution_spans.py` | Deep Span Inspection | Tracking exact input/output state deltas at each node step within LangSmith run trees. |

---

## 🔍 What to Check in the LangSmith UI

After running `04_node_execution_spans.py`:
1. Open your project in [LangSmith Cloud](https://smith.langchain.com).
2. Look for the top-level run named `StateGraph Execution`.
3. Expand the **Tree View** on the left panel:
   - Root Span: `LangGraph` (Total graph latency and cumulative tokens)
   - Child Span 1: `input_processor` node (Shows raw user query converted to structured state)
   - Child Span 2: `analysis_generator` node (Shows LLM call, token consumption, and state delta)
   - Child Span 3: `output_formatter` node (Shows final synthesized response)
4. Notice how each child node clearly reveals the state before and after execution.
