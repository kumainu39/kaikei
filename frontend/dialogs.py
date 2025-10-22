from __future__ import annotations

import requests
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QLineEdit, QTextEdit
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView


class CorrectionDialog(QDialog):
    def __init__(self, api_base_url: str, client_key: str, entry: dict):
        super().__init__()
        self.api_base_url = api_base_url.rstrip("/")
        self.client_key = client_key
        self.entry = entry
        self.setWindowTitle("仕訳修正")
        layout = QVBoxLayout(self)

        # PDFビュー
        self.pdf_doc = QPdfDocument()
        self.pdf_view = QPdfView()
        pdf_path = entry.get("pdf_path") or ""
        if pdf_path:
            self.pdf_doc.load(pdf_path)
        self.pdf_view.setDocument(self.pdf_doc)
        layout.addWidget(self.pdf_view)

        # 修正入力欄
        self.debit_edit = QLineEdit(entry.get("debit_account") or "")
        self.credit_edit = QLineEdit(entry.get("credit_account") or "")
        self.reason_box = QTextEdit()
        self.save_btn = QPushButton("修正を保存")

        layout.addWidget(QLabel("借方科目:"))
        layout.addWidget(self.debit_edit)
        layout.addWidget(QLabel("貸方科目:"))
        layout.addWidget(self.credit_edit)
        layout.addWidget(QLabel("修正理由:"))
        layout.addWidget(self.reason_box)
        layout.addWidget(self.save_btn)

        self.save_btn.clicked.connect(self.on_save)

    def on_save(self):
        payload = {
            "entry_id": self.entry.get("id"),
            "new_debit": self.debit_edit.text(),
            "new_credit": self.credit_edit.text(),
            "reason": self.reason_box.toPlainText(),
        }
        headers = {"X-Client-Key": self.client_key} if self.client_key else {}
        requests.post(f"{self.api_base_url}/api/journal/correct", json=payload, headers=headers, timeout=10)
        self.accept()

