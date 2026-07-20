from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    google_api_key: str
    supabase_url: str
    supabase_service_key: str

    class Config:
        env_file = ".env"


settings = Settings()
