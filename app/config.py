from datetime import timedelta

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore', env_file_encoding='utf-8')

    DEBUG: bool = True

    # Postgres
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    # SMTP
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    # Auth
    SECRET_KEY: str
    ALGORITHM: str
    # Token
    TOKEN_NAME: str = "task_tracker_token"
    TOKEN_TIMER: timedelta = timedelta(minutes=30)

    @property
    def db_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB
        )


settings = Settings()
