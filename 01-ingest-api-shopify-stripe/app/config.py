from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://de_user:de_pass@localhost:5433/de_db"
    API_KEY: str = "sk-client-12345"
    class Config:
        env_file = ".env"

settings = Settings()
