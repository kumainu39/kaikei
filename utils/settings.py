"""Application settings loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    database_url: str = "sqlite:///" + str(BASE_DIR / "kaikei.db")
    scheduler_timezone: str = "Asia/Tokyo"
    bank_api_key: str | None = None
    card_api_key: str | None = None
    ai_model_path: str = str(BASE_DIR / "models" / "model.pkl")
    ai_vectorizer_path: str = str(BASE_DIR / "models" / "vectorizer.pkl")

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
