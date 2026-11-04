"""
Production SQLite Persistent Checkpointer Helper for E-Commerce Swarm
"""

import sqlite3
from pathlib import Path
from langgraph.checkpoint.sqlite import SqliteSaver

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = ROOT_DIR / "ecommerce_state.sqlite"


def get_sqlite_checkpointer(db_path: Path = DEFAULT_DB_PATH) -> SqliteSaver:
    """
    Initializes a production-grade durable SQLite checkpointer.
    Enables WAL (Write-Ahead Logging) mode for concurrent high-throughput access,
    and automatically executes checkpointer.setup() to provision tables.
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    # Enable Write-Ahead Logging for high performance & safe concurrency
    conn.execute("PRAGMA journal_mode=WAL;")
    
    checkpointer = SqliteSaver(conn)
    checkpointer.setup()
    return checkpointer
