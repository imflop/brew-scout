import typing as t
import uvicorn
from argparse import ArgumentParser
from pydantic import PostgresDsn, RedisDsn, HttpUrl

from .libs.settings import AppSettings
from .libs.setup_app import setup_app


def init_args_parser() -> ArgumentParser:
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--database_dsn", type=str)
    arg_parser.add_argument("--redis_dsn", type=str)
    arg_parser.add_argument("--sentry_dsn", type=str)
    arg_parser.add_argument("--telegram_api_url", type=str)
    arg_parser.add_argument("--telegram_api_token", type=str)
    arg_parser.add_argument("--oauth_app_name", type=str)
    arg_parser.add_argument("--oauth_client_id", type=str)
    arg_parser.add_argument("--oauth_client_secret", type=str)
    arg_parser.add_argument("--oauth_server_metadata_url", type=str)
    arg_parser.add_argument("--allowed_users", type=str)
    arg_parser.add_argument("--secret_key", type=str)

    return arg_parser


def main(
    database_dsn: str,
    redis_dsn: str,
    sentry_dsn: str,
    telegram_api_url: str,
    telegram_api_token: str,
    oauth_app_name: str,
    oauth_client_id: str,
    oauth_client_secret: str,
    oauth_server_metadata_url: str,
    allowed_users: str,
    secret_key: str,
) -> None:
    settings = AppSettings(
        database_dsn=t.cast(PostgresDsn, database_dsn),
        redis_dsn=t.cast(RedisDsn, redis_dsn),
        sentry_dsn=sentry_dsn,
        telegram_api_url=telegram_api_url,
        telegram_api_token=telegram_api_token,
        oauth_app_name=oauth_app_name,
        oauth_client_id=oauth_client_id,
        oauth_client_secret=oauth_client_secret,
        oauth_server_metadata_url=t.cast(HttpUrl, oauth_server_metadata_url),
        allowed_users=allowed_users,
        secret_key=secret_key,
    )
    app = setup_app(settings)
    uvicorn.run(app=app, host=settings.host, port=settings.port, http="httptools")


if __name__ == "__main__":
    parser = init_args_parser()
    args = parser.parse_args()

    main(
        args.database_dsn,
        args.redis_dsn,
        args.sentry_dsn,
        args.telegram_api_url,
        args.telegram_api_token,
        args.oauth_app_name,
        args.oauth_client_id,
        args.oauth_client_secret,
        args.oauth_server_metadata_url,
        args.allowed_users,
        args.secret_key,
    )
