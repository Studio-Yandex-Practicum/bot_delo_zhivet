import os


class Config(object):
    SECRET_KEY = os.getenv('ADMIN_SECRET_KEY', default='SECRET_KEY')
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = 'development'
