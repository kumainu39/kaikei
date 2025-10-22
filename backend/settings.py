"""Backend settings for multi-tenant build (separate from legacy utils.settings)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


class Settings:
    # Master DB for client registry
    master_database_url: str = os.getenv("MASTER_DATABASE_URL", f"sqlite:///{(BASE_DIR / 'data' / 'master.db')}")

    # LLM
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
    llm_model: str = os.getenv("LLM_MODEL", "llama3.1:8b")
    llm_api_key: Optional[str] = os.getenv("LLM_API_KEY")

    # Confidence threshold
    ai_autopost_threshold: float = float(os.getenv("AI_AUTOPOST_THRESHOLD", "0.7"))

    # Scheduler
    scansnap_poll_minutes: int = int(os.getenv("SCANSNAP_POLL_MINUTES", "3"))

    # Clients
    clients: List[str]
    scansnap_folders: Dict[str, str]

    def __init__(self) -> None:
        raw = os.getenv("CLIENTS", "").strip()
        self.clients = [c.strip() for c in raw.split(",") if c.strip()] if raw else []
        folders: Dict[str, str] = {}
        for code in self.clients:
            val = os.getenv(f"SCANSNAP_FOLDER_{code}")
            if val:
                folders[code] = val
        single = os.getenv("SCANSNAP_FOLDER")
        if single and not folders:
            folders["default"] = single
        self.scansnap_folders = folders


settings = Settings()

