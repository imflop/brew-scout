import typing as t
import uvicorn
from argparse import ArgumentParser
from pydantic import PostgresDsn

from .libs.settings import AppSettings
from .libs.setup_app import setup_app


def init_args_parser() -> ArgumentParser:
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--database_dsn", type=str)
    arg_parser.add_argument("--telegram_api_url", type=str)
    arg_parser.add_argument("--telegram_api_token", type=str)

    return arg_parser


def main(database_dsn: str, telegram_api_url: str, telegram_api_token: str) -> None:
    settings = AppSettings(
        database_dsn=t.cast(PostgresDsn, database_dsn),
        telegram_api_url=telegram_api_url,
        telegram_api_token=telegram_api_token,
    )
    app = setup_app(settings)
    uvicorn.run(app=app, host=settings.host, port=settings.port, http="httptools")


if __name__ == "__main__":
    parser = init_args_parser()
    args = parser.parse_args()

    main(args.database_dsn, args.telegram_api_url, args.telegram_api_token)
