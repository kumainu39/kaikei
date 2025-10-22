"""Scheduler setup using APScheduler."""
from __future__ import annotations

from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler

from utils.settings import settings
from backend.auto_journal_scan import process_scansnap_xml


scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)
_processed_scansnap: set[str] = set()


def watch_scansnap_folders() -> None:
    folders = getattr(settings, "scansnap_folders", None)
    if not folders:
        # Backward-compat single folder
        folder = Path(getattr(settings, "scansnap_folder", "")).expanduser()
        if not folder or not folder.exists():
            return
        for xml_file in folder.glob("*.xml"):
            key = str(xml_file.resolve())
            if key in _processed_scansnap:
                continue
            try:
                result = process_scansnap_xml(xml_file)
                if result.get("saved"):
                    _processed_scansnap.add(key)
            except Exception:
                pass
        return

    for client_code, path in folders.items():
        if not path:
            continue
        folder = Path(path).expanduser()
        if not folder.exists():
            continue
        for xml_file in folder.glob("*.xml"):
            key = f"{client_code}|{str(xml_file.resolve())}"
            if key in _processed_scansnap:
                continue
            try:
                result = process_scansnap_xml(xml_file, client_code=client_code)
                if result.get("saved"):
                    _processed_scansnap.add(key)
            except Exception:
                # Best-effort; try again next tick
                pass


def start_scheduler() -> None:
    if not scheduler.running:
        # Add job if not present
        if not scheduler.get_job("watch_scansnap"):
            minutes = getattr(settings, "scansnap_poll_minutes", 3)
            scheduler.add_job(watch_scansnap_folders, "interval", minutes=minutes, id="watch_scansnap")
        scheduler.start()


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
