from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ARGOS"
    environment: str = "development"
    database_url: str = "sqlite:///./argos.db"
    api_v1_prefix: str = "/api/v1"
    frontend_url: str = "http://localhost:5175"
    cors_origins: str = "http://localhost:5175,http://127.0.0.1:5175"
    auto_create_lite_tables: bool = True
    llm_provider: str = "openrouter"
    llm_fallback_provider: str = ""
    llm_timeout_seconds: float = 45.0
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_default_model: str = "openrouter/auto"
    openrouter_http_referer: str = ""
    openrouter_x_title: str = "ARGOS"
    openai_api_key: str = ""
    openai_default_model: str = "gpt-4o-mini"
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 45.0
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    redis_url: str = "redis://localhost:6379/0"
    storage_path: str = "storage"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = "noreply@argos.local"
    admin_email: str = "admin@argos.gov.br"
    admin_password: str = "argos123"
    celery_enabled: bool = True

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.environment.lower() != "production":
            return self

        insecure_values = {
            "SECRET_KEY": self.secret_key == "change-me-in-production",
            "ADMIN_PASSWORD": self.admin_password == "argos123",
        }
        missing_or_insecure = [
            name for name, is_insecure in insecure_values.items() if is_insecure
        ]
        if missing_or_insecure:
            fields = ", ".join(missing_or_insecure)
            raise ValueError(f"Configuracao insegura para producao: {fields}")

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
