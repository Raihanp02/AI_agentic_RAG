from typing import Literal
from provider.llm.llm import get_openai_llm, get_openrouter_llm
from core.config import settings
from langchain_core.language_models import BaseChatModel

Provider = Literal["openai", "openrouter"]

_FACTORIES = {
    "openai": get_openai_llm,
    "openrouter": get_openrouter_llm,
}

def get_llm(provider: Provider | None = None, **kwargs) -> BaseChatModel:
    provider = provider or settings.LLM_PROVIDER
    try:
        return _FACTORIES[provider](**kwargs)
    except KeyError:
        raise ValueError(f"Unknown provider: {provider}") from None