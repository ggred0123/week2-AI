from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI App"
    DEBUG_MODE: bool = False
    API_VERSION: str = "v1"
    DATABASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()