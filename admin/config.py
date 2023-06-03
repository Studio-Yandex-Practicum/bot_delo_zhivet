import logging
import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(".env.db"))
load_dotenv(find_dotenv(".env.flask"))
load_dotenv(find_dotenv(".env.mail"))
load_dotenv(find_dotenv(".env.sentry"))


class Config(object):
    DEBUG = True
    FLASK_ENV = os.getenv("FLASK_ENV")
    SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", default="SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://{os.getenv("POSTGRES_USER")}:'
        f'{os.getenv("POSTGRES_PASSWORD")}@'
        f'{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/'
        f'{os.getenv("POSTGRES_DB")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SENTRY_DSN_ADMIN = os.getenv("SENTRY_DSN_ADMIN", default=None)

    # Дополнительные параметры, не участвующие в ините приложения
    BOOTSTRAP_VERSION = "bootstrap4"
    LOG_DEFAULT_LVL = logging.DEBUG
    LOG_EXTENSION = ".log"
    LOG_FORMAT = "%(asctime)s [%(levelname)s]  %(message)s"
    LOG_REL_PATH = "logs"

    # Параметры почтового клиента
    MAIL_DEBUG = os.getenv("MAIL_DEBUG", default=1)
    MAIL_PORT = os.getenv("MAIL_PORT", default=465)
    MAIL_SERVER = os.getenv("MAIL_SERVER", default="smtp.yandex.ru")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", default=True)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", default="test.delo.zhivet@yandex.ru")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", default="bctlgfnckbtxhgzt")

    # Параметры генерации токенов сброса пароля
    PASSWORD_RESET_TOKEN_ALGORITHM = os.getenv("PASSWORD_RESET_TOKEN_ALGORITHM", default="HS256")
    PASSWORD_RESET_TOKEN_TTL = os.getenv("PASSWORD_RESET_TOKEN_TTL", default=600)
