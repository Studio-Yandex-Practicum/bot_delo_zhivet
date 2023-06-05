from logging import INFO

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_title: str = "Сервис Дело Живет"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    POSTGRES_DB: str
    TELEGRAM_BOT_TOKEN: str = None
    WEBHOOK_DOMAIN: str = None
    WEBHOOK_PORT: int = None
    WEBHOOK_PATH: str = None
    HOST: str = None
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_SERVICE_NAME: str
    AWS_ENDPOINT_URL: str
    AWS_BUCKET_NAME: str
    SENTRY_DSN_BOT: str = None

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
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
