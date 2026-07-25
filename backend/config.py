from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    # anthropic_api_key: Optional[str] = None  # disabled — using GitHub Models instead
    google_api_key: Optional[str] = None
    github_token: Optional[str] = None
    github_model: str = "gpt-4o-mini"
    supabase_url: str
    supabase_service_key: str
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    class Config:
        env_file = _ENV_FILE
        extra = "ignore"


settings = Settings()
