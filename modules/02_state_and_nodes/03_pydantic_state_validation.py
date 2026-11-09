"""
Module 02 - Script 03: Pydantic v2 State Validation & Strict Schema Enforcement

Demonstrates:
1. Defining a Pydantic BaseModel state schema
2. Enforcing field validation rules (e.g. valid severity levels, non-empty IDs)
3. Catching runtime validation errors within node boundaries
"""

import sys
from enum import Enum
from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel, Field, field_validator

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from langgraph.graph import StateGraph, START, END


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# 1. Pydantic State Schema
class ValidatedIncidentState(BaseModel):
    incident_id: str = Field(..., description="Unique ticket identifier like INC-1234")
    service_name: str = Field(..., description="Affected microservice name")
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Error rate percentage (0.0 to 1.0)")
    severity: SeverityLevel = SeverityLevel.MEDIUM
    tags: List[str] = Field(default_factory=list)
    remediation_required: bool = False

    @field_validator("incident_id")
    @classmethod
    def validate_ticket_format(cls, v: str) -> str:
        if not v.startswith("INC-"):
            raise ValueError(f"Incident ID must start with 'INC-', received: '{v}'")
        return v


# 2. Node with typed state manipulation
def evaluate_risk_node(state: ValidatedIncidentState) -> dict:
    print(f" [Node: evaluate_risk] Validating service '{state.service_name}' with error rate {state.error_rate * 100:.1f}%")
    
    # Logic based on validated schema
    is_critical = state.error_rate > 0.05
    new_severity = SeverityLevel.CRITICAL if is_critical else SeverityLevel.LOW
    
    return {
        "severity": new_severity,
        "remediation_required": is_critical,
        "tags": state.tags + ["evaluated", f"tier:{new_severity.value.lower()}"]
    }


def main():
    print("=" * 70)
    print("  MODULE 02: PYDANTIC V2 STATE VALIDATION")
    print("=" * 70)

    # Build Graph with Pydantic State Schema
    builder = StateGraph(ValidatedIncidentState)
    builder.add_node("evaluate_risk", evaluate_risk_node)
    builder.add_edge(START, "evaluate_risk")
    builder.add_edge("evaluate_risk", END)

    graph = builder.compile()

    # Valid Test Case
    print("\n▶️ Case 1: Valid State Execution")
    valid_input = {
        "incident_id": "INC-4450",
        "service_name": "payment-gateway",
        "error_rate": 0.082,
        "tags": ["env:production", "pci-compliant"]
    }

    res1 = graph.invoke(valid_input, config={"run_name": "pydantic-valid-run"})
    print(f"✅ Success! Evaluated Severity: {res1['severity']} | Remediation: {res1['remediation_required']}")
    print(f"   Tags: {res1['tags']}")

    # Invalid Test Case (Testing Schema Enforcement)
    print("\n▶️ Case 2: Triggering Schema Validation Error (Bad Ticket Prefix)")
    invalid_input = {
        "incident_id": "INVALID-TICKET-99",  # Does not start with INC-
        "service_name": "auth-service",
        "error_rate": 0.01
    }

    try:
        graph.invoke(invalid_input)
    except Exception as exc:
        print(f"🛡️ Caught Expected Validation Exception:\n   {exc}")

    print("\n" + "=" * 70)
    print("✅ Completed Script 03 successfully!\n")


if __name__ == "__main__":
    main()
