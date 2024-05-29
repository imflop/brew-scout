import typing as t

from pydantic import BaseSettings, Field, PostgresDsn, RedisDsn, HttpUrl, validator


SETTINGS_KEY = "settings"


class BaseAppSettings(BaseSettings):
    class Config:
        env_file = ".env"


class AppSettings(BaseAppSettings):
    host: str = Field(default="0.0.0.0", env="host")
    port: int = Field(default=9090, env="port")
    debug: bool = Field(default=True, env="debug")
    redis_dsn: RedisDsn = Field(..., env="redis_dsn")
    database_dsn: PostgresDsn = Field(..., env="database_dsn")
    telegram_api_url: str = Field(..., env="telegram_api_url")
    telegram_api_token: str = Field(..., env="telegram_api_token")
    sentry_dsn: str | None = Field(None, env="sentry_dsn")
    oauth_app_name: str = Field(..., env="oauth_app_name")
    oauth_client_id: str = Field(..., env="oauth_client_id")
    oauth_client_secret: str = Field(..., env="oauth_client_secret")
    oauth_server_metadata_url: HttpUrl = Field(..., env="oauth_server_metadata_url")
    allowed_users: frozenset[str] | str = Field(..., env="allowed_users")
    secret_key: str = Field(default="secret", env="secret_key")

    class Config:
        validate_assigment = True

    @validator("allowed_users", pre=True)
    def parse_allowed_users(cls, data: str) -> frozenset[str] | str:
        if isinstance(data, str):
            return frozenset(user.strip() for user in data.split(","))

        return data
