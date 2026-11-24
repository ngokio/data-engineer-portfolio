from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://de_user:de_pass@localhost:5433/de_db")
    API_KEY: str = os.getenv("API_KEY", "dev-key-change-me")

    class Config:
        env_file = ".env"

settings = Settings()