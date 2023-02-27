import logging
import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", default="SECRET_KEY")
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = "development"

    # Дополнительные параметры, не участвующие в ините приложения
    BOOTSTRAP_VERSION = "bootstrap4"
    LOG_DEFAULT_LVL = logging.DEBUG
    LOG_EXTENSION = ".log"
    LOG_FORMAT = "%(asctime)s [%(levelname)s]  %(message)s"
    LOG_REL_PATH = "logs"

    # Требуются настройки аккаунта из веб-интерфейса
    # Шестеренка -> Все настройки -> Безопасность >
    # в тексте найти "Пароли приложений" ->
    # Создать пароль приложения
    MAIL_SERVER = "smtp.yandex.ru"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = "test.delo.zhivet@yandex.ru"
    MAIL_PASSWORD = "bctlgfnckbtxhgzt"
