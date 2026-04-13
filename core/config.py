from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str
    OPENROUTER_MODEL: str
    class Config:
        env_file = ".env" 

@lru_cache # Caches the settings object to ensure it's loaded only once
def get_settings():
    return Settings()

settings = get_settings()