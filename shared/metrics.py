"""
Prometheus Metrics Registry & Observability Instrumentation for LangGraph.
"""

import time
import functools
from typing import Callable, Any, Optional
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    start_http_server,
    REGISTRY
)

# ------------------------------------------------------------------------------
# Prometheus Metric Definitions
# ------------------------------------------------------------------------------

NODE_LATENCY_HISTOGRAM = Histogram(
    "langgraph_node_execution_seconds",
    "Execution duration of individual LangGraph nodes in seconds",
    ["node_name", "status"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

NODE_ERRORS_COUNTER = Counter(
    "langgraph_node_errors_total",
    "Total number of errors encountered within LangGraph nodes",
    ["node_name", "error_type"]
)

TOOL_INVOCATIONS_COUNTER = Counter(
    "langgraph_tool_invocations_total",
    "Total number of tool calls executed by agents",
    ["tool_name", "status"]
)

LLM_TOKENS_COUNTER = Counter(
    "langgraph_llm_tokens_total",
    "Total prompt and completion tokens consumed by models",
    ["project_id", "provider", "model", "token_type"]
)

ESTIMATED_COST_COUNTER = Counter(
    "langgraph_estimated_cost_usd_total",
    "Accumulated estimated cost in USD for model executions",
    ["project_id", "provider", "model"]
)

ACTIVE_THREADS_GAUGE = Gauge(
    "langgraph_active_threads",
    "Number of concurrent active state threads/sessions",
    ["status"]
)

HITL_INTERRUPTS_COUNTER = Counter(
    "langgraph_hitl_interrupts_total",
    "Total human-in-the-loop pause and resume decisions",
    ["action_name", "decision"]
)

AGENT_RECURSION_HISTOGRAM = Histogram(
    "langgraph_agent_loop_iterations",
    "Number of iterations/turns taken per session before finishing",
    ["graph_name", "status"],
    buckets=[1, 2, 5, 10, 15, 25, 50]
)

WORKFLOW_DURATION_HISTOGRAM = Histogram(
    "langgraph_workflow_duration_seconds",
    "End-to-end execution time for full graph resolution",
    ["service_name", "status"],
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 15.0, 30.0, 60.0, 120.0]
)

PROVIDER_FALLBACK_COUNTER = Counter(
    "langgraph_provider_fallback_total",
    "LLM provider fallbacks triggered by rate limits or errors",
    ["primary_provider", "fallback_provider", "reason"]
)

# ------------------------------------------------------------------------------
# E-Commerce Cart Recovery Business Metrics
# ------------------------------------------------------------------------------

ECOMMERCE_CART_VALUE_COUNTER = Counter(
    "ecommerce_cart_value_total",
    "Total value of ingested abandoned carts in USD",
    ["currency"]
)

ECOMMERCE_RECOVERED_REVENUE_COUNTER = Counter(
    "ecommerce_recovered_revenue_total",
    "Projected revenue recovered from abandoned carts in USD",
    ["status"]
)

ECOMMERCE_DISCOUNT_BURNED_COUNTER = Counter(
    "ecommerce_discount_burned_total",
    "Total promotional discount dollars granted in USD",
    ["strategy"]
)

ECOMMERCE_GROSS_MARGIN_GAUGE = Gauge(
    "ecommerce_average_gross_margin_pct",
    "Average preserved gross margin percentage across active recovery bundles"
)

ECOMMERCE_OVERSTOCK_CLEARED_COUNTER = Counter(
    "ecommerce_overstock_cleared_total",
    "Total units of warehouse overstock bundled and sold",
    ["sku", "category"]
)

ECOMMERCE_HESITATION_COUNTER = Counter(
    "ecommerce_hesitation_reasons_total",
    "Categorized reasons for customer cart abandonment",
    ["reason"]
)

ECOMMERCE_LINTER_VALIDATION_COUNTER = Counter(
    "ecommerce_copy_validation_total",
    "Email and SMS copy linter quality results",
    ["status"]
)

ECOMMERCE_MERCHANDISER_HITL_COUNTER = Counter(
    "ecommerce_merchandiser_hitl_decisions_total",
    "Decisions on discount approvals by Merchandiser / Operator",
    ["decision"]
)

ECOMMERCE_INVENTORY_STOCK_GAUGE = Gauge(
    "ecommerce_inventory_stock_units",
    "Real-time warehouse stock units available per SKU",
    ["sku", "name", "category", "is_overstock"]
)


# ------------------------------------------------------------------------------
# Node Instrumentation Decorator
# ------------------------------------------------------------------------------

def instrument_node(node_name: str):
    """
    Decorator to wrap a LangGraph node function and record latency,
    success/failure status, and exception metrics into Prometheus.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(state: Any, *args: Any, **kwargs: Any):
            start_time = time.time()
            status = "success"
            try:
                result = func(state, *args, **kwargs)
                return result
            except Exception as exc:
                status = "error"
                NODE_ERRORS_COUNTER.labels(
                    node_name=node_name,
                    error_type=type(exc).__name__
                ).inc()
                raise exc
            finally:
                duration = time.time() - start_time
                NODE_LATENCY_HISTOGRAM.labels(
                    node_name=node_name,
                    status=status
                ).observe(duration)
        return wrapper
    return decorator


def track_tokens(
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    cost_usd: float = 0.0,
    project_id: Optional[str] = None
):
    """Utility to track token usage and cost partitioned by project."""
    import os
    pid = (project_id or os.getenv("PROJECT_ID", "default_project")).strip()
    LLM_TOKENS_COUNTER.labels(project_id=pid, provider=provider, model=model, token_type="prompt").inc(prompt_tokens)
    LLM_TOKENS_COUNTER.labels(project_id=pid, provider=provider, model=model, token_type="completion").inc(completion_tokens)
    if cost_usd > 0.0:
        ESTIMATED_COST_COUNTER.labels(project_id=pid, provider=provider, model=model).inc(cost_usd)


def track_hitl_decision(action_name: str, decision: str):
    """Utility to track human-in-the-loop approvals and rejections."""
    HITL_INTERRUPTS_COUNTER.labels(action_name=action_name, decision=decision).inc()


def track_workflow_duration(service_name: str, duration_seconds: float, status: str = "success"):
    """Records end-to-end multi-agent incident workflow duration."""
    WORKFLOW_DURATION_HISTOGRAM.labels(service_name=service_name, status=status).observe(duration_seconds)


def track_agent_iterations(graph_name: str, iterations: int, status: str = "completed"):
    """Records the turn count / iteration depth of a multi-agent loop."""
    AGENT_RECURSION_HISTOGRAM.labels(graph_name=graph_name, status=status).observe(iterations)


def track_fallback(primary_provider: str, fallback_provider: str, reason: str = "rate_limit"):
    """Records provider fallback events when primary fails."""
    PROVIDER_FALLBACK_COUNTER.labels(primary_provider=primary_provider, fallback_provider=fallback_provider, reason=reason).inc()


def track_ecommerce_cart(cart_value_usd: float, currency: str = "USD"):
    """Records value of ingested abandoned cart."""
    ECOMMERCE_CART_VALUE_COUNTER.labels(currency=currency).inc(cart_value_usd)


def track_ecommerce_recovery(recovered_usd: float, discount_burned_usd: float, strategy: str = "dynamic_bundle"):
    """Records recovered cart revenue and discount dollars spent."""
    ECOMMERCE_RECOVERED_REVENUE_COUNTER.labels(status="projected").inc(recovered_usd)
    ECOMMERCE_DISCOUNT_BURNED_COUNTER.labels(strategy=strategy).inc(discount_burned_usd)


def track_ecommerce_margin(margin_pct: float):
    """Updates the gross margin gauge."""
    ECOMMERCE_GROSS_MARGIN_GAUGE.set(margin_pct)


def track_ecommerce_overstock_cleared(sku: str, category: str, units: int = 1):
    """Tracks warehouse inventory clearance."""
    ECOMMERCE_OVERSTOCK_CLEARED_COUNTER.labels(sku=sku, category=category).inc(units)


def track_ecommerce_hesitation(reason: str):
    """Tracks diagnosed hesitation reason."""
    ECOMMERCE_HESITATION_COUNTER.labels(reason=reason).inc()


def track_ecommerce_linter(status: str):
    """Tracks email/SMS copy linter quality results."""
    ECOMMERCE_LINTER_VALIDATION_COUNTER.labels(status=status).inc()


def track_ecommerce_merchandiser_hitl(decision: str):
    """Tracks merchandiser approval/rejection decisions."""
    ECOMMERCE_MERCHANDISER_HITL_COUNTER.labels(decision=decision).inc()


def track_inventory_stock(sku: str, name: str, category: str, units: int, is_overstock: bool):
    """Sets current real-time inventory stock level for Prometheus & Grafana."""
    ECOMMERCE_INVENTORY_STOCK_GAUGE.labels(
        sku=sku,
        name=name,
        category=category,
        is_overstock="true" if is_overstock else "false"
    ).set(units)


_SERVER_STARTED = False

def start_metrics_server_once(port: int = 8000):
    """Starts Prometheus metrics exporter HTTP server if not already running."""
    global _SERVER_STARTED
    if not _SERVER_STARTED:
        try:
            start_http_server(port)
            _SERVER_STARTED = True
            print(f"[METRICS] Prometheus metrics exporter live at http://localhost:{port}/metrics")
        except OSError as e:
            # Port might already be in use
            print(f"[METRICS] Prometheus metrics server on port {port} (already active or busy: {e})")
