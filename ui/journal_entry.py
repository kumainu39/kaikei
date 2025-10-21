"""Journal entry widget mimicking spreadsheet-like bookkeeping entry."""
from __future__ import annotations

import asyncio
from typing import Any, Awaitable, TypeVar

import httpx
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class JournalAPIClient:
    """Async HTTP client used by the UI to communicate with FastAPI."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def list_accounts(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/accounts")
            response.raise_for_status()
            return response.json()

    async def create_journal(self, entry: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/journal", json=entry)
            response.raise_for_status()
            return response.json()


T = TypeVar("T")


class JournalEntryWidget(QWidget):
    COLUMN_HEADERS = ["日付", "借方科目", "貸方科目", "金額", "摘要", "税区分"]

    def __init__(self, api_base_url: str) -> None:
        super().__init__()
        self.api_client = JournalAPIClient(api_base_url)
        self.accounts: list[dict[str, Any]] = []

        self.table = QTableWidget(0, len(self.COLUMN_HEADERS))
        self.table.setHorizontalHeaderLabels(self.COLUMN_HEADERS)
        self.table.verticalHeader().setVisible(False)

        self.add_button = QPushButton("行を追加")
        self.remove_button = QPushButton("選択行を削除")
        self.save_button = QPushButton("保存")

        self.add_button.clicked.connect(self.add_row)
        self.remove_button.clicked.connect(self.remove_selected_rows)
        self.save_button.clicked.connect(self.save_entries)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(buttons_layout)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)

        root_layout = QFormLayout()
        root_layout.addRow(container)
        self.setLayout(root_layout)

        self._run_async(self._load_accounts())
        self.add_row()

    async def _load_accounts(self) -> None:
        try:
            self.accounts = await self.api_client.list_accounts()
        except httpx.HTTPError:
            self.accounts = []

    def _run_async(self, coroutine: Awaitable[T]) -> T:
        try:
            return asyncio.run(coroutine)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coroutine)
            finally:
                loop.close()

    # UI Helpers -----------------------------------------------------------------
    def _create_account_combobox(self) -> QComboBox:
        combo = QComboBox()
        for account in self.accounts:
            combo.addItem(f"{account['code']} {account['name']}", account["id"])
        return combo

    def add_row(self) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)

        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        self.table.setCellWidget(row, 0, date_edit)

        debit_combo = self._create_account_combobox()
        credit_combo = self._create_account_combobox()
        self.table.setCellWidget(row, 1, debit_combo)
        self.table.setCellWidget(row, 2, credit_combo)

        amount_item = QTableWidgetItem("0")
        self.table.setItem(row, 3, amount_item)

        summary_item = QTableWidgetItem("")
        self.table.setItem(row, 4, summary_item)

        tax_item = QTableWidgetItem("対象外")
        self.table.setItem(row, 5, tax_item)

    def remove_selected_rows(self) -> None:
        selected = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)
        for row in selected:
            self.table.removeRow(row)

    def _collect_row_data(self, row: int) -> dict[str, Any] | None:
        date_widget = self.table.cellWidget(row, 0)
        debit_widget = self.table.cellWidget(row, 1)
        credit_widget = self.table.cellWidget(row, 2)
        amount_item = self.table.item(row, 3)
        summary_item = self.table.item(row, 4)
        tax_item = self.table.item(row, 5)

        if not isinstance(date_widget, QDateEdit) or not isinstance(debit_widget, QComboBox) or not isinstance(credit_widget, QComboBox):
            return None

        try:
            amount = float(amount_item.text()) if amount_item else 0
        except ValueError:
            amount = 0

        if amount <= 0:
            return None

        debit_account_id = debit_widget.currentData()
        credit_account_id = credit_widget.currentData()
        if debit_account_id is None or credit_account_id is None:
            return None

        entry = {
            "date": date_widget.date().toPyDate().isoformat(),
            "debit_account_id": debit_account_id,
            "credit_account_id": credit_account_id,
            "amount": amount,
            "summary": summary_item.text() if summary_item else "",
            "tax_type": tax_item.text() if tax_item else None,
        }
        return entry

    def save_entries(self) -> None:
        entries: list[dict[str, Any]] = []
        for row in range(self.table.rowCount()):
            entry = self._collect_row_data(row)
            if entry:
                entries.append(entry)

        if not entries:
            QMessageBox.information(self, "保存", "保存対象の仕訳がありません。")
            return

        try:
            for entry in entries:
                self._run_async(self.api_client.create_journal(entry))
        except httpx.HTTPError as exc:
            QMessageBox.critical(self, "エラー", f"仕訳の保存に失敗しました: {exc}")
            return

        QMessageBox.information(self, "保存", f"{len(entries)}件の仕訳を保存しました。")
