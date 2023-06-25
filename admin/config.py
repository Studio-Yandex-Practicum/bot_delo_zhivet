import os
from logging import INFO

from pydantic import BaseSettings


class Settings(BaseSettings):
    DEBUG = True
    FLASK_ENV: str
    SECRET_KEY: str = "SECRET_KEY"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: str = None

    # First SuperUser
    SUPER_USER_EMAIL: str
    SUPER_USER_LOGIN: str
    SUPER_USER_PASSWORD: str

    SENTRY_DSN_ADMIN: str = None

    # Logging
    LOG_NAME: str = "admin"
    LOG_DEFAULT_LVL: int | None = INFO

    # Параметры почтового клиента
    MAIL_DEBUG: int = 1
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.yandex.ru"
    MAIL_USE_SSL: bool = True
    MAIL_USERNAME: str = "test.delo.zhivet@yandex.ru"
    MAIL_PASSWORD: str = "bctlgfnckbtxhgzt"

    # Параметры генерации токенов сброса пароля
    PASSWORD_RESET_TOKEN_ALGORITHM: str = "HS256"
    PASSWORD_RESET_TOKEN_TTL: int = 600

    # Дополнительные параметры, не участвующие в ините приложения
    BOOTSTRAP_VERSION = "bootstrap4"

    class Config:
        env_file_encoding = "utf-8"
        env_files_names = (
            ".env.flask",
            ".env.s3",
            ".env.mail",
            ".env.sentry",
            ".env.db.local",
        )
        env_file = ("./infrastructure/.env_files/" + file_name for file_name in env_files_names)


class DevSettings(Settings):
    pass


class LocalSettings(Settings):
    pass


def get_settings():
    PG_DOCKER_ENV = os.getenv("PG_DOCKER_ENV", "local")
    if PG_DOCKER_ENV == "dev":
        return DevSettings()
    else:
        return LocalSettings()


settings = get_settings()
settings.SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/"
    f"{settings.POSTGRES_DB}"
)
