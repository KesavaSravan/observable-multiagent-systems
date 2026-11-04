# Module 08: LangSmith Evaluators, Datasets & LLM-as-a-Judge

Welcome to **Module 08** of the *LangGraph + LangSmith + Grafana Observability* curriculum.

## 🎯 Learning Objectives
By completing this module, you will:
1. Programmatically curate and manage **Evaluation Datasets** using the `langsmith.Client` SDK.
2. Build custom evaluators (Exact string match, JSON schema compliance, and Semantic heuristics).
3. Implement **LLM-as-a-Judge** evaluators to score response correctness, toxicity, and tool-calling precision.
4. Execute `evaluate()` experiments and visualize benchmark regression tables in the LangSmith Web UI.

---

## 📂 Scripts in this Module

| Script | Purpose | What it Teaches |
|---|---|---|
| `01_create_dataset_programmatic.py` | Dataset Creation | Programmatically creating an SRE incident evaluation dataset with 5 benchmark examples. |
| `02_exact_and_semantic_evaluators.py` | Deterministic Evaluators | Custom Python evaluators verifying output structure, key terms, and response brevity. |
| `03_llm_as_a_judge_evaluator.py` | LLM-as-a-Judge | Using a judge model to grade accuracy on a scale of 0.0 to 1.0. |
| `04_run_eval_experiment.py` | Experiment Suite Execution | Running `evaluate()` across the full dataset and logging experiment scorecards. |

---

## 🔍 What to Check in the LangSmith UI

After running `04_run_eval_experiment.py`:
1. Open [LangSmith Cloud](https://smith.langchain.com).
2. Click **Datasets & Testing** in the left navigation.
3. Select `sre-incident-benchmarks`.
4. Click on the latest **Experiment Run** (e.g. `eval-experiment-...`).
5. Inspect:
   - **Aggregate Scorecard**: Mean correctness score (e.g. 0.95), average latency, total token cost.
   - **Example Diff Viewer**: Side-by-side comparison of input question, actual graph output, and reference answer.
