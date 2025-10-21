"""Scheduler setup using APScheduler."""
from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from utils.settings import settings


scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
