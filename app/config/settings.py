import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CACHE_DIR: str = os.getenv("CACHE_DIR", ".cache")
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    PAGE_TIMEOUT_MS: int = int(os.getenv("PAGE_TIMEOUT_MS", "30000"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///news_data_v2.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()
