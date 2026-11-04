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

# Load environment variables from .env file located at root
ROOT_DIR = Path(__file__).parent.parent
ENV_PATH = ROOT_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    load_dotenv(override=True)


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
