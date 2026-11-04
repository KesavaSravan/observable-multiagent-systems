# Module 10: Prometheus Telemetry, Exporters & Grafana Dashboarding

Welcome to **Module 10** of the *LangGraph + LangSmith + Grafana Observability* curriculum.

## 🎯 Learning Objectives
By completing this module, you will:
1. Instrument LangGraph nodes with native Prometheus metrics (`Histogram`, `Counter`, `Gauge`).
2. Expose standard OpenMetrics format via HTTP endpoint on `http://localhost:8000/metrics`.
3. Generate realistic multi-agent traffic to populate time-series metrics.
4. Construct and validate **PromQL queries** for Grafana panels (P95 latency, error rates, token burn, cost rate).

---

## 📂 Scripts in this Module

| Script | Purpose | What it Teaches |
|---|---|---|
| `01_prometheus_metrics_basics.py` | Core Prometheus Primitives | Creating Counters, Histograms, and Gauges with `prometheus_client`. |
| `02_instrumenting_langgraph_nodes.py` | Node Decorator Instrumentation | Wrapping LangGraph nodes with `@instrument_node` to automatically capture duration and exceptions. |
| `03_token_cost_metrics_exporter.py` | Live `/metrics` Exporter | Exposing live metrics HTTP server on port 8000. |
| `04_live_traffic_generator.py` | Continuous Traffic Generator | Simulating steady multi-agent traffic with occasional errors for real-time dashboard testing. |
| `05_grafana_dashboard_queries.py` | PromQL Query Test Suite | Testing the exact PromQL expressions used in the Grafana dashboard panels. |

---

## 🔍 What to Check in Prometheus & Grafana

1. **Verify Raw Metrics**:
   - Open [http://localhost:8000/metrics](http://localhost:8000/metrics) in your browser.
   - Look for `langgraph_node_execution_seconds_bucket`, `langgraph_llm_tokens_total`, `langgraph_node_errors_total`.
2. **Prometheus UI**:
   - Start the stack: `cd monitoring && docker-compose up -d`
   - Open [http://localhost:9090](http://localhost:9090).
   - Query: `histogram_quantile(0.95, sum(rate(langgraph_node_execution_seconds_bucket[5m])) by (le, node_name))`
3. **Grafana Dashboard**:
   - Open [http://localhost:3000](http://localhost:3000) (User: `admin` / Password: `admin`).
   - Open the auto-provisioned **"LangGraph Multi-Agent Health & Cost"** dashboard!
