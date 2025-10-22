from __future__ import annotations

import httpx
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAction,
    QLabel,
    QLineEdit,
    QMainWindow,
    QStackedWidget,
    QToolBar,
    QWidget,
)

from .widgets.journal_table import JournalTable


class MainWindow(QMainWindow):
    def __init__(self, api_base_url: str = "http://127.0.0.1:8000") -> None:
        super().__init__()
        self.api_base_url = api_base_url.rstrip("/")
        self.setWindowTitle("Kaikei - Multi-tenant")
        self.resize(1200, 800)

        self.client_key: str | None = None

        self.table = JournalTable()
        self.stacked = QStackedWidget()
        self.stacked.addWidget(self.table)
        self.setCentralWidget(self.stacked)

        self._create_toolbar()
        self._create_statusbar()

    def _create_toolbar(self) -> None:
        tb = QToolBar("Main")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        reload_action = QAction("再読込", self)
        reload_action.triggered.connect(self.reload_journals)
        tb.addAction(reload_action)

        tb.addWidget(QLabel(" Key: "))
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("X-Client-Key")
        self.key_edit.textChanged.connect(self._on_key)
        tb.addWidget(self.key_edit)

    def _create_statusbar(self) -> None:
        self.statusBar().addWidget(QLabel("Ready"))

    def _on_key(self, text: str) -> None:
        self.client_key = text.strip() or None

    def reload_journals(self) -> None:
        headers = {"X-Client-Key": self.client_key} if self.client_key else {}
        try:
            with httpx.Client() as cli:
                r = cli.get(f"{self.api_base_url}/api/journal/", headers=headers, timeout=10)
                r.raise_for_status()
                rows = r.json()
                self.table.load_rows(rows)
        except Exception:
            pass


def create_main_window(api_base_url: str = "http://127.0.0.1:8000") -> QWidget:
    return MainWindow(api_base_url=api_base_url)

