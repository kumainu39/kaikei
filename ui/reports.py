"""Placeholder widget for reports and statements."""
from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ReportsWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("帳簿・集計機能は今後実装予定です。"))
        layout.addStretch()
        self.setLayout(layout)
