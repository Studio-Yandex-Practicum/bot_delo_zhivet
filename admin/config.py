import logging
import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    LOCAL_START = True  # когда запускаем локально фласк True иначе False
    SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", default="SECRET_KEY")
    DEBUG = True
    DB_HOST = (
        os.getenv("DB_HOST_LOCAL") if LOCAL_START else os.getenv("DB_HOST")
    )
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{DB_HOST}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = "development"

    SENTRY_DSN_ADMIN = os.getenv("SENTRY_DSN_ADMIN", default=None)

    # Дополнительные параметры, не участвующие в ините приложения
    BOOTSTRAP_VERSION = "bootstrap4"
    LOG_DEFAULT_LVL = logging.DEBUG
    LOG_EXTENSION = ".log"
    LOG_FORMAT = "%(asctime)s [%(levelname)s]  %(message)s"
    LOG_REL_PATH = "logs"

    # Параметры почтового клиента
    MAIL_SERVER = os.getenv("MAIL_SERVER", default="smtp.yandex.ru")
    MAIL_PORT = os.getenv("MAIL_PORT", default=465)
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", default=True)
    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME", default="test.delo.zhivet@yandex.ru"
    )
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", default="bctlgfnckbtxhgzt")
    MAIL_DEBUG = os.getenv("MAIL_DEBUG", default=1)

    # Параметры генерации токенов сброса пароля
    PASSWORD_RESET_TOKEN_TTL = os.getenv(
        "PASSWORD_RESET_TOKEN_TTL", default=600
    )
    PASSWORD_RESET_TOKEN_ALGORITHM = os.getenv(
        "PASSWORD_RESET_TOKEN_ALGORITHM", default="HS256"
    )
