from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "calistrength"

    # App
    APP_SECRET_KEY: str = "change_me"
    ENVIRONMENT: str = "development"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_PATH: str = "./firebase-service-account.json"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
