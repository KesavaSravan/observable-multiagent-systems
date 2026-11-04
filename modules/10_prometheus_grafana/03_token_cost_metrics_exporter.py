"""
Module 10 - Script 03: Live Prometheus Metrics HTTP Server Exporter

Demonstrates:
1. Launching a background Prometheus metrics server on port 8000
2. Updating token counters and estimated cost gauges
3. Validating the live HTTP /metrics endpoint via requests
"""

import sys
import time
import requests
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared.metrics import start_metrics_server_once, track_tokens
from shared.config import settings


def main():
    print("=" * 70)
    print("  MODULE 10: LIVE PROMETHEUS METRICS HTTP EXPORTER")
    print("=" * 70)

    port = settings.PROMETHEUS_PORT
    print(f"\n🚀 Starting Prometheus metrics server on port {port}...")
    start_metrics_server_once(port)

    # Simulate token and cost updates across providers
    print("📊 Emitting token and cost metrics...")
    track_tokens(provider="openai", model="gpt-4o-mini", prompt_tokens=1400, completion_tokens=320, cost_usd=0.0004)
    track_tokens(provider="anthropic", model="claude-3-5-sonnet", prompt_tokens=3200, completion_tokens=850, cost_usd=0.0223)
    track_tokens(provider="google", model="gemini-1.5-flash", prompt_tokens=4800, completion_tokens=900, cost_usd=0.0006)

    time.sleep(0.5)

    # Test reading the endpoint via HTTP
    url = f"http://localhost:{port}/metrics"
    print(f"\n📡 Testing HTTP GET {url}...")
    try:
        resp = requests.get(url, timeout=3.0)
        print(f"✅ Response Status: {resp.status_code} OK")
        print("📄 Metrics Sample:")
        sample_lines = [l for l in resp.text.split("\n") if "langgraph_" in l and not l.startswith("#")]
        for line in sample_lines[:6]:
            print(f"   {line}")
    except Exception as exc:
        print(f"⚠️ Error reaching exporter: {exc}")

    print("\n" + "=" * 70)
    print("💡 Prometheus Scraper Configuration:")
    print("   Prometheus can now scrape 'http://localhost:8000/metrics' every 5 seconds.")
    print("🎉 Script 03 completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
