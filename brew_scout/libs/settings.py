from pydantic import BaseSettings, Field, PostgresDsn, RedisDsn


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

    class Config:
        validate_assigment = True
