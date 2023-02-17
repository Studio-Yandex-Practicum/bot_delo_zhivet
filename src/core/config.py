from pydantic import BaseSettings


class Settings(BaseSettings):
    app_title: str = "Сервис Дело Живет"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    POSTGRES_DB: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
