from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    telegram_bot_token: str = None
    webhook_domain: str = None
    webhook_port: int = None
    webhook_path: str = None
    host: str = None

    class Config:
        env_file = ".env"


settings = Settings()
