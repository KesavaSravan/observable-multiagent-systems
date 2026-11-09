"""
Shared utilities for LangGraph + LangSmith + Grafana Observability Module.
"""

import sys

# Ensure stdout and stderr handle UTF-8 cleanly on Windows across all modules
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
