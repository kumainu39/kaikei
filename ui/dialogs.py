"""Dialog definitions for settings screens."""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)


class AccountDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("科目設定")
        self.code_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.type_edit = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow("科目コード", self.code_edit)
        form_layout.addRow("科目名", self.name_edit)
        form_layout.addRow("区分", self.type_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self) -> dict[str, str]:
        return {
            "code": self.code_edit.text(),
            "name": self.name_edit.text(),
            "type": self.type_edit.text(),
        }
