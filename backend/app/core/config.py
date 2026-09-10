from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/le_bon_coin"
    debug: bool = False
    # Browsers refuse a cross-origin call unless the API says who may make it.
    # The Vite dev server runs on 5173; deployments override this.
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
