from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


SERVER_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = SERVER_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Queue Analysis API")
    app_env: str = Field(default="development")
    debug: bool = Field(default=False)

    api_prefix: str = Field(default="/api/v1")

    cors_origins: str = Field(
        default=(
            "http://localhost:5173,"
            "http://127.0.0.1:5173,"
            "http://localhost:8080,"
            "http://127.0.0.1:8080"
        )
    )
    cors_allow_credentials: bool = Field(default=False)

    log_level: str = Field(default="INFO")

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() in {"development", "develop", "dev", "local"}

    @property
    def is_publish(self) -> bool:
        return self.app_env.lower() in {"publish", "production", "prod", "release"}

    @property
    def cors_origin_list(self) -> list[str]:
        if self.is_development:
            return ["*"]

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def cors_allow_credentials_effective(self) -> bool:
        """
        Browsers do not allow wildcard CORS origins together with credentials.
        In development mode we allow all origins, so credentials must be disabled.
        """
        if "*" in self.cors_origin_list:
            return False

        return self.cors_allow_credentials


@lru_cache
def get_settings() -> Settings:
    return Settings()
