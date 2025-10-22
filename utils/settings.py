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
    # AI/LLM configuration
    ai_mode: str = "ml"  # "ml" (joblib model) or "llm"
    llm_base_url: str = "http://127.0.0.1:11434/v1"
    llm_model: str = "llama3.1:8b"
    llm_api_key: str | None = None
    # ScanSnap integration
    scansnap_folder: str | None = None  # e.g., r"C:/Users/USER/Documents/ScanSnap Home/"
    scansnap_poll_minutes: int = 3
    # AI auto-posting confidence threshold
    ai_autopost_threshold: float = 0.7
    # Multi-client support
    clients: list[str] = []  # e.g., ["A001","B002"]
    scansnap_folders: dict[str, str] | None = None

    def __init__(self, **data):
        super().__init__(**data)
        # Build scansnap_folders from env like SCANSNAP_FOLDER_<CODE>
        import os
        if not self.clients:
            raw = os.getenv("CLIENTS", "").strip()
            if raw:
                self.clients = [c.strip() for c in raw.split(",") if c.strip()]
        if not self.scansnap_folders:
            folders: dict[str, str] = {}
            for code in self.clients:
                val = os.getenv(f"SCANSNAP_FOLDER_{code}")
                if val:
                    folders[code] = val
            if not folders and os.getenv("SCANSNAP_FOLDER"):
                folders["default"] = os.getenv("SCANSNAP_FOLDER", "")
            self.scansnap_folders = folders or None

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
