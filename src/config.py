"""Application configuration management."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str
    whisper_model: str = "whisper-1"
    tts_model: str = "tts-1"
    tts_voice: str = "alloy"
    gpt_model: str = "gpt-4-turbo-preview"

    # Twilio Configuration
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str

    # Database Configuration
    database_url: str
    redis_url: str

    # Application Settings
    environment: str = "development"
    secret_key: str
    encryption_key: str

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # HIPAA Compliance
    enable_audit_log: bool = True
    log_level: str = "INFO"

    # Voice Processing
    max_audio_duration: int = 300  # 5 minutes max
    response_timeout: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
