from __future__ import annotations

from pathlib import Path
from typing import Dict, Set

from apscheduler.schedulers.background import BackgroundScheduler

from .auto_journal_scan import process_scansnap_xml
from .db_manager import get_master_session
from .models_client import Client
from .settings import settings


scheduler = BackgroundScheduler()
_processed: Set[str] = set()


def _iter_client_folders() -> Dict[str, str]:
    # Prefer explicit mapping from settings
    if settings.scansnap_folders:
        return dict(settings.scansnap_folders)
    # Fallback to folders in master DB
    folders: Dict[str, str] = {}
    with get_master_session() as s:
        for c in s.query(Client).all():
            if c.base_folder:
                folders[c.code] = c.base_folder
    return folders


def watch_scansnap_folders() -> None:
    for client_code, folder in _iter_client_folders().items():
        p = Path(folder)
        if not p.exists():
            continue
        for xml_file in p.glob("*.xml"):
            key = f"{client_code}|{xml_file.resolve()}"
            if key in _processed:
                continue
            try:
                result = process_scansnap_xml(xml_file, client_code=client_code)
                if result.get("saved"):
                    _processed.add(key)
            except Exception:
                pass


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.add_job(watch_scansnap_folders, "interval", minutes=settings.scansnap_poll_minutes, id="watch_scansnap")
        scheduler.start()


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()

