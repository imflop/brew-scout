from pydantic import Field, PostgresDsn, RedisDsn, HttpUrl, field_validator
from pydantic_settings import BaseSettings


SETTINGS_KEY = "settings"


class BaseAppSettings(BaseSettings):
    ...

class AppSettings(BaseAppSettings):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=9090)
    debug: bool = Field(default=True)
    redis_dsn: RedisDsn = Field(...)
    database_dsn: PostgresDsn = Field(...)
    telegram_api_url: str = Field(...)
    telegram_api_token: str = Field(...)
    sentry_dsn: str | None = Field(default=None)
    oauth_app_name: str = Field(...)
    oauth_client_id: str = Field(...)
    oauth_client_secret: str = Field(...)
    oauth_server_metadata_url: HttpUrl = Field(...)
    allowed_users: frozenset[str] | str = Field(...)
    secret_key: str = Field(default="secret")

    @field_validator("allowed_users", mode="before")
    @classmethod
    def parse_allowed_users(cls, data: str) -> frozenset[str] | str:
        if isinstance(data, str):
            return frozenset(user.strip() for user in data.split(","))

        return data
