from __future__ import annotations

import pytest


def test_main_window_importable():
    pytest.importorskip("PyQt6")
    from ui.main_window import MainWindow

    assert MainWindow.__name__ == "MainWindow"
