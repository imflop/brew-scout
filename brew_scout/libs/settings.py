from pydantic import BaseSettings, Field, PostgresDsn


SETTINGS_KEY = "settings"


class BaseAppSettings(BaseSettings):
    class Config:
        env_file = ".env"


class AppSettings(BaseAppSettings):
    host: str = Field(default="0.0.0.0", env="host")
    port: int = Field(default=9090, env="port")
    debug: bool = Field(default=True, env="debug")
    database_dsn: PostgresDsn = Field(..., env="database_dsn")

    class Config:
        validate_assigment = True