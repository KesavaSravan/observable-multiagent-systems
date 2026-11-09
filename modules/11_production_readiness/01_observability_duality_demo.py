"""
Module 11 - Script 01: Observability Duality Demonstration

Demonstrates:
1. The operational duality between Grafana (Aggregate Telemetry) and LangSmith (Distributed Traces)
2. Simulating a Grafana Alert trigger
3. Correlating the alert to a specific LangSmith Trace ID for root-cause diagnosis
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def simulate_incident_workflow():
    print("=" * 70)
    print("  MODULE 11: OBSERVABILITY DUALITY (GRAFANA + LANGSMITH)")
    print("=" * 70)

    # 1. Prometheus / Grafana Layer
    print("\n🚨 [STEP 1: GRAFANA ALERT FIRES]")
    print("   • Metric Alert : 'HighAgentFailureRate'")
    print("   • Expression   : sum(rate(langgraph_node_errors_total[5m])) by (node_name) > 0.1")
    print("   • Affected Node: 'remediation_coder'")
    print("   • Severity     : P1 - Critical")
    print("   • Action       : Grafana notifies on-call engineer via PagerDuty / Slack.")

    # 2. Correlation
    print("\n🔗 [STEP 2: CORRELATION & PIVOT]")
    print("   • On-call opens Grafana Dashboard Panel: 'Agent Failure Breakdown'")
    print("   • Discovers 15 consecutive exceptions in 'remediation_coder'")
    print("   • Grabs the correlated Run / Trace ID: 'run_88a91cf2-0012'")

    # 3. LangSmith Trace Inspection Layer
    print("\n🔍 [STEP 3: LANGSMITH DEEP TRACE INVESTIGATION]")
    print("   • Engineer opens LangSmith URL: https://smith.langchain.com/.../run_88a91cf2-0012")
    print("   • Inspects Child Span: 'remediation_coder'")
    print("   • Exact Stack Trace: JSONDecodeError: Expecting value: line 1 column 1 (char 0)")
    print("   • Prompt Inspection: Discovers LLM output wrapped in invalid markdown backticks ```json ...")

    # 4. Resolution
    print("\n🛠️ [STEP 4: ROOT CAUSE MITIGATION]")
    print("   • Engineer applies output parser sanitizer to strip markdown backticks.")
    print("   • Deploys fix, error rate drops to 0.0% in Grafana within 30 seconds.")

    print("\n" + "=" * 70)
    print("💡 Key Takeaway: Grafana answers 'IS THE SYSTEM HEALTHY AND WITHIN SLA?'")
    print("   LangSmith answers 'WHY EXACTLY DID THIS INDIVIDUAL AGENT CALL FAIL?'")
    print("=" * 70)
    print("✅ Completed Script 01 successfully!\n")


if __name__ == "__main__":
    simulate_incident_workflow()
