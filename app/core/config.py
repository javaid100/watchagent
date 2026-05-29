from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    API_PORT: int = 8000
    POLL_INTERVAL_SECONDS: int = 300

    class Config:
        env_file = ".env"

settings = Settings()
