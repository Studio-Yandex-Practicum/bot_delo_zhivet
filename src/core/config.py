import os
from logging import INFO

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_title: str = "Сервис Дело Живет"
    # database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    POSTGRES_DB: str

    # telegram
    TELEGRAM_BOT_TOKEN: str = None
    WEBHOOK_DOMAIN: str = None
    WEBHOOK_PORT: int = None
    WEBHOOK_PATH: str = None
    HOST: str = None
    # aws
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_SERVICE_NAME: str
    AWS_ENDPOINT_URL: str
    AWS_BUCKET_NAME: str
    # sentry
    SENTRY_DSN_BOT: str = None

    # Dadata
    DADATA_TOKEN: str
    DADATA_SECRET: str

    # GEOCODER
    GEOCODER_BASE_URL: str = None
    GEOCODER_APIKEY: str = None
    MAXIMUM_OBJECTS_FROM_GEOCODER: int = 10

    # YaTracker
    OAUTH_TOKEN: str
    ORG_ID: str

    # Celery
    redis_host: str | None = "redis"
    redis_port: str | None = "6379"
    celery_connect_string = "redis://{}:{}/0"

    # Logging
    logger_name: str = "bot"
    log_file: str | None = "bot.log"
    log_level: int | None = INFO
    log_encoding: str | None = "utf-8"

    # порядок сортировки тегов в боте по убыванию (по мере убывания важности поля)
    sort_tags_in_bot = ["priority", "name"]

    class Config:
        env_file_encoding = "utf-8"
        env_file_dir = "./infrastructure/.env_files/"
        env_files_names = (
            ".env.telegram",
            ".env.s3",
            ".env.sentry",
            ".env.dadata",
            ".env.geocoder",
            ".env.yatracker",
        )

        @classmethod
        def get_env_file(cls, env_db_file) -> set:
            all_env_file_names = [file_name for file_name in cls.env_files_names]
            all_env_file_names.append(env_db_file)
            env_file = (cls.env_file_dir + file_name for file_name in all_env_file_names)
            return env_file


class DevSettings(Settings):
    class Config(Settings.Config):
        env_db_file = ".env.db"
        env_file = Settings.Config.get_env_file(env_db_file)


class LocalSettings(Settings):
    class Config(Settings.Config):
        env_db_file = ".env.db.local"
        env_file = Settings.Config.get_env_file(env_db_file)


def get_settings():
    PG_DOCKER_ENV = os.getenv("PG_DOCKER_ENV", "local")
    if PG_DOCKER_ENV == "dev":
        return DevSettings()
    else:
        return LocalSettings()


settings = get_settings()
