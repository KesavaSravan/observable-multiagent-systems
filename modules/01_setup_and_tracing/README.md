# Module 01: Setup, Multi-Provider Architecture & Tracing Verification

Welcome to **Module 01** of the *LangGraph + LangSmith + Grafana Observability* curriculum.

## 🎯 Learning Objectives
By completing this module, you will:
1. Understand how LangChain / LangGraph natively integrates with **LangSmith distributed tracing** using standard environment variables (`LANGCHAIN_TRACING_V2=true`).
2. Build a **vendor-agnostic LLM factory** supporting OpenAI, Anthropic Claude, Google Gemini, and Groq with seamless runtime switching.
3. Execute your first traced LLM invocation and inspect the live run tree, token counts, and latency in the LangSmith Web UI.

---

## 📂 Scripts in this Module

| Script | Purpose | What it Teaches |
|---|---|---|
| `01_env_and_sdk_verification.py` | Environment Health Check | Validates API keys, SDK installation, and LangSmith connectivity. |
| `02_llm_factory_multi_provider.py` | Multi-Provider Dynamic Switcher | Demonstrates instantiation of OpenAI, Anthropic, Gemini, Groq, or Mock fallback. |
| `03_first_traced_call.py` | First Traced LLM Invocation | Fires a traced prompt, prints the run ID, and generates the LangSmith Run URL. |

---

## 🔍 What to Check in the LangSmith UI

After running `03_first_traced_call.py`:
1. Open [LangSmith Cloud](https://smith.langchain.com).
2. Click on your project (default: `langgraph-observability-course`).
3. Find the run named `first-traced-llm-call`.
4. Inspect:
   - **Input**: The user prompt and system instruction.
   - **Output**: The exact completion from the LLM.
   - **Latency**: Total execution time in milliseconds.
   - **Tokens**: Breakdown of prompt tokens vs. completion tokens.
   - **Metadata / Tags**: Tags like `env:development`, `module:01_setup`.
