import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PyQt5.QtWidgets", exc_type=ImportError)
QtCore = pytest.importorskip("PyQt5.QtCore", exc_type=ImportError)

main_window_module = pytest.importorskip("src.ui.main_window", exc_type=ImportError)
MainWindow = main_window_module.MainWindow


def test_main_window_initializes_and_creates_project(qtbot, monkeypatch):
    # Avoid any blocking message boxes during initialization or status updates
    monkeypatch.setattr(
        QtWidgets.QMessageBox, "information", lambda *args, **kwargs: QtWidgets.QMessageBox.Ok
    )

    win = MainWindow()
    qtbot.addWidget(win)
    win.show()
    qtbot.waitExposed(win)

    # On startup, a new project is created and set as current
    assert win.project_manager.current_system is not None
    assert win.tab_widget.count() >= 3  # system canvas, module panel, interface panel, etc.

    # Switch tabs to exercise handlers
    win.tab_widget.setCurrentIndex(1)
    win.tab_widget.setCurrentIndex(2)

    # Ensure project tree can be updated without errors
    win.update_project_tree()

