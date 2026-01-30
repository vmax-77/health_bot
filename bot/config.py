from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    BOT_TOKEN: str
    OPENWEATHER_API_KEY: str
    OPENFOODFACTS_APP_KEY: Optional[str] = None
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./fitness.db"
    
    class Config:
        env_file = ".env"

settings = Settings()