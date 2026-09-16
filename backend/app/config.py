from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Job Application Tracker API"
    database_url: str = "sqlite:///./job_tracker.db"
    backend_cors_origins: str = "http://localhost:5173,http://localhost:4173"
    seed_demo_data: bool = True
    secret_key: str = "development-only-secret-key-change-me"
    access_token_expire_minutes: int = 60 * 24 * 7
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
