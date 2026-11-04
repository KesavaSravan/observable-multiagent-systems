"""
Multi-Provider LLM Factory for LangGraph Observability.

Supports:
- OpenAI (gpt-4o, gpt-4o-mini, o1, etc.)
- Anthropic Claude (claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022, etc.)
- Google Gemini (gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash, etc.)
- Groq (llama-3.3-70b-versatile, mixtral-8x7b-32768, etc.)
- Ollama (llama3, mistral, qwen2.5, etc.)
- Mock fallback for dry-run / offline testing without API keys

Allows switching via:
1. Environment variables (.env)
2. Function arguments in Python code
3. Interactive selection at runtime
"""

import os
import sys
import re
from typing import Optional, Any, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from shared.config import settings

# Default recommended models per provider
RECOMMENDED_MODELS = {
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
    "anthropic": ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"],
    "google": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
    "groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
    "ollama": ["llama3:latest", "mistral:latest", "qwen2.5:latest"],
}


from langchain_core.callbacks import BaseCallbackHandler
from shared.metrics import track_tokens

# Pricing matrix per 1 Million tokens (USD)
PRICING_PER_MILLION = {
    # OpenAI
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    # Anthropic
    "claude-3-5-sonnet-20241022": {"prompt": 3.00, "completion": 15.00},
    "claude-3-5-haiku-20241022": {"prompt": 0.80, "completion": 4.00},
    # Google
    "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    "gemini-1.5-pro": {"prompt": 1.25, "completion": 5.00},
    "gemini-2.0-flash": {"prompt": 0.10, "completion": 0.40},
    # Groq
    "llama-3.3-70b-versatile": {"prompt": 0.59, "completion": 0.79},
    "llama-3.1-8b-instant": {"prompt": 0.05, "completion": 0.08},
    "openai/gpt-oss-120b": {"prompt": 0.60, "completion": 0.90},
}


class UnauthorizedModelPolicyError(ValueError):
    """Raised when an unapproved model is requested outside the project allowlist."""
    pass


def get_allowed_models_list(project_id: Optional[str] = None) -> List[str]:
    """Retrieves the list of authorized models configured in .env for a specific project.
    
    Resolution order:
    1. PROJECT_<PROJECT_ID_UPPER>_MODELS (e.g. PROJECT_ECOMMERCE_RECOVERY_MODELS)
    2. Global ALLOWED_MODELS fallback
    """
    pid = (project_id or os.getenv("PROJECT_ID", getattr(settings, "PROJECT_ID", "default_project"))).strip()
    sanitized = re.sub(r"[^A-Za-z0-9_]", "_", pid).upper()
    
    # 1. Project-specific env lookup
    project_env_var = f"PROJECT_{sanitized}_MODELS"
    raw = os.getenv(project_env_var)
    
    # 2. Fall back to global allowlist
    if not raw:
        raw = os.getenv("ALLOWED_MODELS", getattr(settings, "ALLOWED_MODELS", ""))
        
    return [m.strip() for m in raw.split(",") if m.strip()]


class TokenAndCostTrackingCallback(BaseCallbackHandler):
    """Automatically records token usage and calculates USD cost per model into Prometheus."""
    def __init__(self, provider: str, model_name: str, project_id: Optional[str] = None):
        self.provider = provider
        self.model_name = model_name
        self.project_id = (project_id or os.getenv("PROJECT_ID", getattr(settings, "PROJECT_ID", "default_project"))).strip()

    def on_llm_end(self, response, **kwargs):
        prompt_tokens = 0
        completion_tokens = 0

        # Method A: Extract from standard usage_metadata (langchain-core)
        if hasattr(response, "generations") and response.generations:
            for gen_list in response.generations:
                for gen in gen_list:
                    msg = getattr(gen, "message", None)
                    if msg and hasattr(msg, "usage_metadata") and msg.usage_metadata:
                        prompt_tokens += msg.usage_metadata.get("input_tokens", 0)
                        completion_tokens += msg.usage_metadata.get("output_tokens", 0)

        # Method B: Fallback to llm_output dict
        if not prompt_tokens and hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            prompt_tokens = token_usage.get("prompt_tokens", 0)
            completion_tokens = token_usage.get("completion_tokens", 0)

        rates = PRICING_PER_MILLION.get(self.model_name, {"prompt": 0.50, "completion": 1.50})
        cost_usd = ((prompt_tokens / 1_000_000) * rates["prompt"]) + \
                   ((completion_tokens / 1_000_000) * rates["completion"])

        if prompt_tokens or completion_tokens:
            track_tokens(
                provider=self.provider,
                model=self.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost_usd=cost_usd,
                project_id=self.project_id
            )


class MockChatModel(BaseChatModel):
    """Fallback mock chat model for offline testing and dry-run execution."""

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Any = None, **kwargs: Any) -> Any:
        from langchain_core.outputs import ChatResult, ChatGeneration
        last_msg = messages[-1].content if messages else ""
        text_resp = f"[MOCK MODEL RESPONSE] Processed prompt: '{last_msg[:80]}...'. Simulated completion generated successfully."
        # Provide simulated token usage metadata
        p_tokens = max(len(last_msg.split()) * 2, 80)
        c_tokens = 45
        msg = AIMessage(
            content=text_resp,
            usage_metadata={"input_tokens": p_tokens, "output_tokens": c_tokens, "total_tokens": p_tokens + c_tokens}
        )
        generation = ChatGeneration(message=msg)
        target_pid = os.getenv("PROJECT_ID", getattr(settings, "PROJECT_ID", "default_project"))
        track_tokens(provider="mock", model="mock-model", prompt_tokens=p_tokens, completion_tokens=c_tokens, cost_usd=0.0001, project_id=target_pid)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "mock-chat-model"

    def bind_tools(self, tools: Any, **kwargs: Any) -> Any:
        return self


def get_chat_model(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    project_id: Optional[str] = None,
    allow_mock_fallback: bool = True,
    **kwargs: Any
) -> BaseChatModel:
    """
    Factory function to instantiate any chat model from any provider.

    Args:
        provider: 'openai' | 'anthropic' | 'google' | 'groq' | 'ollama' (defaults to LLM_PROVIDER in .env)
        model: Model name string (defaults to LLM_MODEL in .env or provider default)
        temperature: Sampling temperature (defaults to LLM_TEMPERATURE in .env)
        project_id: Project identifier for FinOps cost isolation (defaults to PROJECT_ID in .env)
        allow_mock_fallback: If True, falls back to MockChatModel when API key is missing instead of crashing.
    """
    target_pid = (project_id or os.getenv("PROJECT_ID", getattr(settings, "PROJECT_ID", "default_project"))).strip()
    sanitized_pid = re.sub(r"[^A-Za-z0-9_]", "_", target_pid).upper()
    target_provider = (provider or os.getenv("LLM_PROVIDER") or settings.LLM_PROVIDER).lower().strip()
    target_temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
    
    # Priority: 1. Passed model arg, 2. Project-specific default model, 3. Global LLM_MODEL
    target_model = model or os.getenv(f"PROJECT_{sanitized_pid}_DEFAULT_MODEL") or os.getenv("LLM_MODEL")

    # Set default model if none specified
    if not target_model:
        if target_provider == "openai":
            target_model = "gpt-4o-mini"
        elif target_provider in ("anthropic", "claude"):
            target_model = "claude-3-5-haiku-20241022"
        elif target_provider in ("google", "gemini"):
            target_model = "gemini-1.5-flash"
        elif target_provider == "groq":
            target_model = "llama-3.3-70b-versatile"
        elif target_provider == "ollama":
            target_model = "llama3"
        else:
            target_model = "default-model"

    # 🛡️ POLICY ENFORCEMENT GATE: Check allowed models whitelist for this specific project
    allowed_models = get_allowed_models_list(target_pid)
    if allowed_models and target_model not in allowed_models and target_provider != "mock":
        raise UnauthorizedModelPolicyError(
            f"❌ Model '{target_model}' is NOT authorized for project '{target_pid}'. "
            f"Allowed models for '{target_pid}' (from .env): {allowed_models}"
        )

    tracker = TokenAndCostTrackingCallback(target_provider, target_model, project_id=target_pid)
    existing_callbacks = kwargs.pop("callbacks", [])
    if isinstance(existing_callbacks, list):
        callbacks = existing_callbacks + [tracker]
    else:
        callbacks = [existing_callbacks, tracker]

    if target_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        if not api_key or api_key.startswith("sk-..."):
            if allow_mock_fallback:
                print(f"[WARN] OPENAI_API_KEY not set. Using MockChatModel for offline execution.")
                return MockChatModel()
            raise ValueError("OPENAI_API_KEY environment variable is missing or placeholder.")
        from langchain_openai import ChatOpenAI
        chat = ChatOpenAI(model=target_model, temperature=target_temperature, api_key=api_key, callbacks=callbacks, **kwargs)

    elif target_provider in ("anthropic", "claude"):
        api_key = os.getenv("ANTHROPIC_API_KEY") or settings.ANTHROPIC_API_KEY
        if not api_key or api_key.startswith("sk-ant-..."):
            if allow_mock_fallback:
                print(f"[WARN] ANTHROPIC_API_KEY not set. Using MockChatModel for offline execution.")
                return MockChatModel()
            raise ValueError("ANTHROPIC_API_KEY environment variable is missing or placeholder.")
        from langchain_anthropic import ChatAnthropic
        chat = ChatAnthropic(model=target_model, temperature=target_temperature, api_key=api_key, callbacks=callbacks, **kwargs)

    elif target_provider in ("google", "gemini"):
        api_key = os.getenv("GOOGLE_API_KEY") or settings.GOOGLE_API_KEY
        if not api_key or api_key.startswith("AIzaSy..."):
            if allow_mock_fallback:
                print(f"[WARN] GOOGLE_API_KEY not set. Using MockChatModel for offline execution.")
                return MockChatModel()
            raise ValueError("GOOGLE_API_KEY environment variable is missing or placeholder.")
        from langchain_google_genai import ChatGoogleGenerativeAI
        chat = ChatGoogleGenerativeAI(model=target_model, temperature=target_temperature, google_api_key=api_key, callbacks=callbacks, **kwargs)

    elif target_provider == "groq":
        api_key = os.getenv("GROQ_API_KEY") or settings.GROQ_API_KEY
        if not api_key or api_key.startswith("gsk_..."):
            if allow_mock_fallback:
                print(f"[WARN] GROQ_API_KEY not set. Using MockChatModel for offline execution.")
                return MockChatModel()
            raise ValueError("GROQ_API_KEY environment variable is missing or placeholder.")
        from langchain_groq import ChatGroq
        chat = ChatGroq(model_name=target_model, temperature=target_temperature, groq_api_key=api_key, callbacks=callbacks, **kwargs)

    elif target_provider == "ollama":
        try:
            from langchain_community.chat_models import ChatOllama
            chat = ChatOllama(model=target_model, temperature=target_temperature, callbacks=callbacks, **kwargs)
        except Exception as e:
            if allow_mock_fallback:
                print(f"[WARN] ChatOllama failed ({e}). Falling back to MockChatModel.")
                return MockChatModel()
            raise e

    elif target_provider == "mock":
        return MockChatModel()

    else:
        # Fallback to OpenAI-compatible generic or mock
        if allow_mock_fallback:
            print(f"[WARN] Unknown provider '{target_provider}'. Falling back to MockChatModel.")
            return MockChatModel()
        chat = MockChatModel()

    if allow_mock_fallback:
        return chat.with_fallbacks([MockChatModel()])
    return chat


def prompt_model_selection() -> tuple[str, str]:
    """Interactive prompt for switching provider and model at runtime."""
    print("\n--- Select LLM Provider ---")
    providers = list(RECOMMENDED_MODELS.keys())
    for idx, p in enumerate(providers, 1):
        print(f"  [{idx}] {p.upper()}")
    choice = input(f"Choose provider [1-{len(providers)}] (Default: {settings.LLM_PROVIDER}): ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(providers):
        selected_provider = providers[int(choice) - 1]
    else:
        selected_provider = settings.LLM_PROVIDER

    models = RECOMMENDED_MODELS.get(selected_provider, ["default"])
    print(f"\n--- Recommended Models for {selected_provider.upper()} ---")
    for idx, m in enumerate(models, 1):
        print(f"  [{idx}] {m}")
    print(f"  [C] Custom model name")
    m_choice = input(f"Choose model [1-{len(models)}/C] (Default: {models[0]}): ").strip()

    if m_choice.lower() == "c":
        selected_model = input("Enter custom model string: ").strip()
    elif m_choice.isdigit() and 1 <= int(m_choice) <= len(models):
        selected_model = models[int(m_choice) - 1]
    else:
        selected_model = models[0]

    os.environ["LLM_PROVIDER"] = selected_provider
    os.environ["LLM_MODEL"] = selected_model
    print(f"\n Active Model set to: [{selected_provider.upper()}] -> {selected_model}\n")
    return selected_provider, selected_model
