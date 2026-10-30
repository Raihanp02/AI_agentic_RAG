from langchain_openai import ChatOpenAI
from core.config import settings
from langchain_core.language_models import BaseChatModel
from functools import lru_cache


@lru_cache
def get_openai_llm(
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.7,
) -> BaseChatModel:
    return ChatOpenAI(model=model_name, temperature=temperature)


@lru_cache
def get_openrouter_llm(
    model_name: str | None = None,
    temperature: float = 0.7,
) -> BaseChatModel:
    return ChatOpenAI(
        model=model_name or settings.OPENROUTER_MODEL,
        base_url=settings.OPENROUTER_BASE_URL,
        api_key=settings.OPENROUTER_API_KEY,
        temperature=temperature,
    )
