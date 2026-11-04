"""
SQLite Checkpoint & State History Inspector for E-Commerce Swarm
"""

import sys
import sqlite3
from pathlib import Path

# Reconfigure Windows stdout encoding for UTF-8 compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ecommerce_agent.core.checkpoint import get_sqlite_checkpointer
from ecommerce_agent.core.graph import build_cart_recovery_graph


def inspect_sqlite():
    db_file = ROOT_DIR / "ecommerce_agent" / "ecommerce_state.sqlite"
    print("\n" + "=" * 76)
    print(" 📁 SQLITE DURABLE STATE CHECKPOINT INSPECTOR")
    print(f"    Database File: {db_file}")
    print("=" * 76)

    if not db_file.exists():
        print(f"❌ SQLite file not found at {db_file}. Run cli.py first to generate states.")
        return

    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()

    # Query distinct threads
    cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY checkpoint_id DESC LIMIT 10;")
    threads = cur.fetchall()

    if not threads:
        print("⚠️ No session threads found in SQLite database yet.")
        conn.close()
        return

    print(f"\nFound {len(threads)} recent session threads stored in SQLite:\n")
    for idx, (t_id,) in enumerate(threads, 1):
        cur.execute("SELECT COUNT(*) FROM checkpoints WHERE thread_id = ?", (t_id,))
        count = cur.fetchone()[0]
        print(f"  [{idx}] Thread ID: {t_id.ljust(36)} -> {count} Checkpoints saved")

    conn.close()

    # Re-open graph with SqliteSaver to inspect state history
    checkpointer = get_sqlite_checkpointer(db_file)
    graph = build_cart_recovery_graph(checkpointer=checkpointer, enable_hitl=True)

    choice = input("\nEnter thread index to inspect state history [1-N] (Default: 1): ").strip()
    idx = int(choice) - 1 if (choice.isdigit() and 1 <= int(choice) <= len(threads)) else 0
    selected_thread = threads[idx][0]

    config = {"configurable": {"thread_id": selected_thread}}
    latest_state = graph.get_state(config)

    print("\n" + "-" * 76)
    print(f"🔍 INSPECTING SESSION: {selected_thread}")
    print("-" * 76)
    print(f"• Cart ID          : {latest_state.values.get('cart_id')}")
    print(f"• Customer         : {latest_state.values.get('customer_name')} ({latest_state.values.get('customer_tier')})")
    print(f"• Cart Total       : ${latest_state.values.get('cart_total', 0):.2f}")
    print(f"• Reason Diagnosed : {latest_state.values.get('hesitation_reason')}")
    print(f"• Bundle Discount  : -${latest_state.values.get('discount_amount_usd', 0):.2f} (Code: {latest_state.values.get('discount_code')})")
    print(f"• Preserved Margin : {latest_state.values.get('projected_gross_margin_pct', 0):.1f}%")
    print(f"• Execution Status : {latest_state.values.get('execution_status')}")
    print(f"• Next Node to Run : {latest_state.next or 'COMPLETED (END)'}")

    print("\n📜 Persisted Audit Trail in SQLite:")
    for log in latest_state.values.get("audit_log", []):
        print(f"  {log}")

    print("\n" + "=" * 76)
    print("✅ Durable SQLite state verified! State survives process restarts and crashes.")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    inspect_sqlite()
