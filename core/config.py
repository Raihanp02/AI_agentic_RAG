from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_ASYNC_URL: str
    DATABASE_SYNC_URL: str
    QUERY_SCHEMA_NAME: str
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str
    OPENROUTER_MODEL: str
    class Config:
        env_file = ".env" 

@lru_cache # Caches the settings object to ensure it's loaded only once
def get_settings():
    return Settings()

settings = get_settings()