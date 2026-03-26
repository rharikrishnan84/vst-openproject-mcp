from pathlib import Path
from pydantic import AnyHttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OPENPROJECT_",
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: AnyHttpUrl
    api_token: SecretStr
    timeout: float = 30.0
    verify_ssl: bool = True


def get_settings() -> Settings:
    return Settings()
