# Module 11: Production Readiness, Observability Duality & SRE Operations

Welcome to **Module 11** of the *LangGraph + LangSmith + Grafana Observability* curriculum.

## 🎯 Learning Objectives
By completing this module, you will:
1. Deeply understand the **Observability Duality**:
   - **LangSmith**: High-cardinality, deep trace trees, root-cause debugging, payload inspection, and LLM evaluations.
   - **Prometheus + Grafana**: Low-latency aggregate time-series, SLO/SLA alerts, cluster capacity, and cost anomaly detection.
2. Implement robust **Circuit Breakers** and provider fallback chains (e.g. Primary OpenAI -> Fallback Claude / Gemini).
3. Build **Exponential Backoff Retries** instrumented with Prometheus retry counters.
4. Execute an automated **Production Readiness Audit** to certify agent systems before enterprise deployment.

---

## 📂 Scripts in this Module

| Script | Purpose | What it Teaches |
|---|---|---|
| `01_observability_duality_demo.py` | Trace vs Metric Duality | Interactive demonstration showing how Grafana triggers the alert and LangSmith pinpoints the exact bug. |
| `02_circuit_breaker_fallback.py` | Multi-Provider Circuit Breaker | Automatically falling back to an alternate LLM provider when primary rate-limits or times out. |
| `03_rate_limiting_and_retry_node.py` | Resilient Retries & Backoff | Node-level retry loop with exponential jitter and Prometheus retry tracking. |
| `04_production_readiness_audit.py` | Production Certification Audit | 12-point automated checklist auditing tracing, security, timeout thresholds, and monitoring. |

---

## 🔍 The SRE Operational Workflow

```
 ┌────────────────────────────────────────────────────────┐
 │ 1. ALERT FIRES IN GRAFANA                              │
 │    PromQL: rate(langgraph_node_errors_total[5m]) > 5%  │
 └──────────────────────────┬─────────────────────────────┘
                            │
                            ▼
 ┌────────────────────────────────────────────────────────┐
 │ 2. ISOLATE AFFECTED NODE IN GRAFANA                    │
 │    Node: 'k8s_log_fetcher' | Model: 'claude-3-5-sonnet'│
 └──────────────────────────┬─────────────────────────────┘
                            │
                            ▼
 ┌────────────────────────────────────────────────────────┐
 │ 3. JUMP TO LANGSMITH CLOUD TRACE                       │
 │    Search by tag: 'node:k8s_log_fetcher'               │
 │    Inspect exact stack trace, input prompt, and payload│
 └──────────────────────────┬─────────────────────────────┘
                            │
                            ▼
 ┌────────────────────────────────────────────────────────┐
 │ 4. DEPLOY REMEDIATION / CIRCUIT BREAKER FALLBACK       │
 └────────────────────────────────────────────────────────┘
```
