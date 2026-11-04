"""
Module 06 - Script 03: Peer Agent Handoffs and Consensus Loop

Demonstrates:
1. Direct peer-to-peer agent handoffs (Triager -> Coder -> Reviewer)
2. Reviewer rejecting code and looping back to Coder for revisions
3. Consensus termination when Reviewer approves
"""

import sys
from typing import TypedDict, Literal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langgraph.graph import StateGraph, START, END


class PeerReviewState(TypedDict):
    issue: str
    proposed_code: str
    review_status: Literal["approved", "needs_revision"]
    revision_count: int


def coder_agent(state: PeerReviewState) -> dict:
    rev = state.get("revision_count", 0) + 1
    print(f" 💻 [Agent: Coder] Drafting patch (Attempt {rev})...")
    
    if rev == 1:
        code = "def fix(): pass # Preliminary quick draft"
    else:
        code = "def fix(): # Full fix with error handling\n    try:\n        db.reconnect()\n    except Exception as e:\n        log.error(e)"
        
    return {"proposed_code": code, "revision_count": rev}


def reviewer_agent(state: PeerReviewState) -> dict:
    print(f" 🕵️ [Agent: Reviewer] Reviewing code draft: '{state['proposed_code'][:30]}...'")
    if "try:" in state["proposed_code"]:
        print("   ↳ Review Decision: [APPROVED] Code meets production standards.")
        return {"review_status": "approved"}
    else:
        print("   ↳ Review Decision: [REJECTED] Missing exception handling, requesting revision.")
        return {"review_status": "needs_revision"}


def main():
    print("=" * 70)
    print("  MODULE 06: PEER AGENT HANDOFFS & CONSENSUS LOOP")
    print("=" * 70)

    builder = StateGraph(PeerReviewState)
    builder.add_node("coder", coder_agent)
    builder.add_node("reviewer", reviewer_agent)

    builder.add_edge(START, "coder")
    builder.add_edge("coder", "reviewer")

    # Conditional feedback loop
    builder.add_conditional_edges(
        "reviewer",
        lambda s: s["review_status"],
        {
            "needs_revision": "coder",
            "approved": END
        }
    )

    graph = builder.compile()

    print("\n▶️ Starting Peer Consensus Graph...")
    final = graph.invoke({
        "issue": "Database reconnect loop bug",
        "proposed_code": "",
        "review_status": "needs_revision",
        "revision_count": 0
    })

    print("\n" + "-" * 70)
    print(f"🎉 Consensus Reached after {final['revision_count']} revisions!")
    print(f"Approved Code:\n{final['proposed_code']}")
    print("-" * 70)
    print("✅ Completed Script 03 successfully!\n")


if __name__ == "__main__":
    main()
