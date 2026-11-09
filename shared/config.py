"""
Configuration & Environment Validator for LangGraph + LangSmith + Grafana.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure stdout and stderr handle UTF-8 cleanly on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import re

# Load environment variables from .env file located at root (override=False to preserve runtime overrides)
ROOT_DIR = Path(__file__).parent.parent
ENV_PATH = ROOT_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=False)
else:
    load_dotenv(override=False)


def update_env_file(key_values: dict[str, str]):
    """Persists updated environment variables directly to .env file and updates os.environ."""
    for key, val in key_values.items():
        os.environ[key] = str(val)

    if not ENV_PATH.exists():
        return
    try:
        content = ENV_PATH.read_text(encoding="utf-8")
        for key, val in key_values.items():
            pattern = re.compile(rf"^{re.escape(key)}\s*=.*$", re.MULTILINE)
            if pattern.search(content):
                content = pattern.sub(f"{key}={val}", content)
            else:
                content += f"\n{key}={val}"
        ENV_PATH.write_text(content, encoding="utf-8")
    except Exception as e:
        print(f"[WARN] Could not update .env: {e}")


class Settings:
    """Central settings and status inspector."""
    
    # Project Identity & FinOps
    PROJECT_ID: str = os.getenv("PROJECT_ID", "ecommerce_recovery")
    ALLOWED_MODELS: str = os.getenv("ALLOWED_MODELS", "gemini-1.5-flash,gpt-4o-mini,mock-model")

    # LangSmith Tracing
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() in ("true", "1", "yes")
    LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "langgraph-observability-course")

    # Multi-Provider Defaults
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai").lower()
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))

    # Provider API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Monitoring
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "8000"))
    PROMETHEUS_METRICS_PATH: str = os.getenv("PROMETHEUS_METRICS_PATH", "/metrics")

    @classmethod
    def get_status_dict(cls) -> dict:
        """Returns a formatted status dictionary of all environment variables and keys."""
        return {
            "Active Project ID": cls.PROJECT_ID,
            "Allowed Models Allowlist": cls.ALLOWED_MODELS,
            "LangSmith Tracing Enabled": cls.LANGCHAIN_TRACING_V2,
            "LangSmith Project": cls.LANGCHAIN_PROJECT,
            "LangSmith Key Present": bool(cls.LANGCHAIN_API_KEY and not cls.LANGCHAIN_API_KEY.startswith("lsv2_pt_your")),
            "Current Provider": cls.LLM_PROVIDER,
            "Current Model": cls.LLM_MODEL,
            "OpenAI Key Present": bool(cls.OPENAI_API_KEY and not cls.OPENAI_API_KEY.startswith("sk-...")),
            "Anthropic Key Present": bool(cls.ANTHROPIC_API_KEY and not cls.ANTHROPIC_API_KEY.startswith("sk-ant-...")),
            "Google Gemini Key Present": bool(cls.GOOGLE_API_KEY and not cls.GOOGLE_API_KEY.startswith("AIzaSy...")),
            "Groq Key Present": bool(cls.GROQ_API_KEY and not cls.GROQ_API_KEY.startswith("gsk_...")),
            "Prometheus Port": cls.PROMETHEUS_PORT,
        }

    @classmethod
    def print_diagnostics(cls):
        """Prints a human-readable diagnostics check."""
        print("=" * 60)
        print("  LANGGRAPH + LANGSMITH + GRAFANA DIAGNOSTICS")
        print("=" * 60)
        for k, v in cls.get_status_dict().items():
            status = " [OK]" if v is True else (" [MISSING/DISABLED]" if v is False else f": {v}")
            print(f"• {k.ljust(30)}{status}")
        print("=" * 60)


settings = Settings()
