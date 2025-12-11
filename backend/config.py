from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # OpenAI
    openai_api_key: str

    # ElevenLabs
    elevenlabs_api_key: str
    elevenlabs_voice_id: str

    # Anam AI
    anam_api_key: str

    # Redis
    redis_url: Optional[str] = "redis://localhost:6379"

    # App Config
    environment: str = "development"
    log_level: str = "INFO"

    # API Settings
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
