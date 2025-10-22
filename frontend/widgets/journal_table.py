from __future__ import annotations

from typing import List, Dict, Any

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem


class JournalTable(QTableWidget):
    HEADERS = ["日付", "摘要", "金額", "借方", "貸方", "信頼度", "確認"]

    def __init__(self) -> None:
        super().__init__(0, len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.verticalHeader().setVisible(False)

    def load_rows(self, rows: List[Dict[str, Any]]) -> None:
        self.setRowCount(0)
        for r in rows:
            i = self.rowCount()
            self.insertRow(i)
            self.setItem(i, 0, QTableWidgetItem(str(r.get("date", ""))))
            self.setItem(i, 1, QTableWidgetItem(str(r.get("summary", ""))))
            self.setItem(i, 2, QTableWidgetItem(str(r.get("amount", ""))))
            self.setItem(i, 3, QTableWidgetItem(str(r.get("debit_account", ""))))
            self.setItem(i, 4, QTableWidgetItem(str(r.get("credit_account", ""))))
            self.setItem(i, 5, QTableWidgetItem(str(r.get("confidence", ""))))
            self.setItem(i, 6, QTableWidgetItem("済" if r.get("reviewed") else "要確認"))

