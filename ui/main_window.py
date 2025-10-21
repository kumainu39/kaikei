"""PyQt6 main window containing navigation and central views."""
from __future__ import annotations

import asyncio

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAction,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QToolBar,
    QWidget,
)

from ui.journal_entry import JournalEntryWidget
from ui.reports import ReportsWidget


class MainWindow(QMainWindow):
    """Main window with a stacked widget replicating an accounting menu structure."""

    def __init__(self, api_base_url: str = "http://127.0.0.1:8000") -> None:
        super().__init__()
        self.api_base_url = api_base_url
        self.setWindowTitle("Kaikei - Accounting")
        self.resize(1200, 800)

        self.stacked_widget = QStackedWidget()
        self.journal_widget = JournalEntryWidget(api_base_url=self.api_base_url)
        self.reports_widget = ReportsWidget()

        self.stacked_widget.addWidget(self.journal_widget)
        self.stacked_widget.addWidget(self.reports_widget)
        self.setCentralWidget(self.stacked_widget)

        self._create_toolbar()
        self._create_status_bar()

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Main toolbar")
        toolbar.setIconSize(toolbar.iconSize())
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        journal_action = QAction("仕訳入力", self)
        journal_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.journal_widget))
        toolbar.addAction(journal_action)

        reports_action = QAction("帳簿・レポート", self)
        reports_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.reports_widget))
        toolbar.addAction(reports_action)

    def _create_status_bar(self) -> None:
        status_label = QLabel("Ready")
        self.statusBar().addWidget(status_label)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        # Ensure pending asyncio tasks used by the API client are closed gracefully
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            loop.stop()
        return super().closeEvent(event)


def create_main_window(api_base_url: str = "http://127.0.0.1:8000") -> QWidget:
    return MainWindow(api_base_url=api_base_url)
