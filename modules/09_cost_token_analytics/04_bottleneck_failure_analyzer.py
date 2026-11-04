"""
Module 09 - Script 04: SRE Bottleneck and Node Failure Analyzer

Demonstrates:
1. Programmatic analysis of historical run spans
2. Ranking nodes by latency P95 and error rates
3. Flagging critical graph bottlenecks automatically
"""

import sys
from typing import List, Dict, Any
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def analyze_graph_bottlenecks(historical_spans: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates average latency, error counts, and failure rate per node."""
    node_stats = {}

    for span in historical_spans:
        name = span["node_name"]
        lat = span["latency_seconds"]
        err = span.get("error", False)

        if name not in node_stats:
            node_stats[name] = {"latencies": [], "errors": 0, "total": 0}

        node_stats[name]["latencies"].append(lat)
        if err:
            node_stats[name]["errors"] += 1
        node_stats[name]["total"] += 1

    ranked = []
    for name, s in node_stats.items():
        avg_lat = sum(s["latencies"]) / s["total"]
        max_lat = max(s["latencies"])
        err_rate = (s["errors"] / s["total"]) * 100
        ranked.append({
            "node": name,
            "avg_latency": avg_lat,
            "max_latency": max_lat,
            "error_rate": err_rate,
            "total_runs": s["total"]
        })

    # Sort primarily by error rate, then by avg latency
    ranked.sort(key=lambda x: (x["error_rate"], x["avg_latency"]), reverse=True)
    return {"analysis": ranked}


def main():
    print("=" * 70)
    print("  MODULE 09: SRE BOTTLENECK AND NODE FAILURE ANALYZER")
    print("=" * 70)

    # Simulated historical span logs across 20 incident runs
    mock_spans = [
        {"node_name": "triage_router", "latency_seconds": 0.42, "error": False},
        {"node_name": "triage_router", "latency_seconds": 0.51, "error": False},
        {"node_name": "k8s_log_fetcher", "latency_seconds": 3.80, "error": True},  # Failure
        {"node_name": "k8s_log_fetcher", "latency_seconds": 2.90, "error": False},
        {"node_name": "k8s_log_fetcher", "latency_seconds": 4.10, "error": True},  # Failure
        {"node_name": "code_patch_generator", "latency_seconds": 5.40, "error": False},
        {"node_name": "code_patch_generator", "latency_seconds": 6.10, "error": False},
        {"node_name": "final_summary_node", "latency_seconds": 0.85, "error": False},
    ]

    report = analyze_graph_bottlenecks(mock_spans)

    print("\n🔍 Node Health & Bottleneck Ranking:")
    print(f"{'Node Name':<24} | {'Avg Latency (s)':<16} | {'Max Latency (s)':<16} | {'Error Rate (%)':<16}")
    print("-" * 80)

    for item in report["analysis"]:
        flag = " ⚠️ [CRITICAL ALERT]" if item["error_rate"] > 20 or item["avg_latency"] > 5.0 else ""
        print(f"{item['node']:<24} | {item['avg_latency']:>14.2f}s | {item['max_latency']:>14.2f}s | {item['error_rate']:>14.1f}%{flag}")

    print("-" * 80)
    print("\n💡 SRE Diagnostic Recommendations:")
    print("  1. 'k8s_log_fetcher' has a 66.7% error rate -> Implement retry policy with exponential backoff.")
    print("  2. 'code_patch_generator' is the highest latency bottleneck (avg 5.75s) -> Consider faster model or streaming.")
    print("\n" + "=" * 70)
    print("🎉 Module 09 completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
