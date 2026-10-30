from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Annotated, Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # ignore unknown vars in .env
    )

    DATABASE_ASYNC_URL: str
    DATABASE_SYNC_URL: str
    QUERY_SCHEMA_NAME: str
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str
    OPENROUTER_MODEL: str
    # Auth
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    QUERY_LLM_URL: Literal["openrouter", "anthropic", "openai"] = "openrouter"  # default value for QUERY_LLM_URL

@lru_cache # Caches the settings object to ensure it's loaded only once
def get_settings():
    return Settings()

settings = get_settings()