import os
from functools import lru_cache

from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    DB_USERNAME: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    TELEGRAM_BOT_TOKEN: SecretStr

    TESTING = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 테스트 코스용
class TestSettings(BaseSettings):
    DB_USERNAME = "admin"
    DB_PASSWORD: SecretStr = "1234"
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_NAME = "testing"

    TELEGRAM_BOT_TOKEN: SecretStr = "secret"

    TESTING = True


@lru_cache
def get_settings():
    # 조건절 추가, 환경에 "dev" 추가
    # if os.environ["APP_ENV", "dev"].lower() == "test":
    if os.getenv("APP_ENV", "dev").lower() == "test":
        return TestSettings()
    return Settings()


settings = get_settings()
