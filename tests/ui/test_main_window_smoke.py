import json
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PyQt5.QtWidgets", exc_type=ImportError)
QtCore = pytest.importorskip("PyQt5.QtCore", exc_type=ImportError)

main_window_module = pytest.importorskip("src.ui.main_window", exc_type=ImportError)
system_model_module = pytest.importorskip("src.models.system_model", exc_type=ImportError)

MainWindow = main_window_module.MainWindow
SystemStructure = system_model_module.SystemStructure


def _create_settings(tmp_path):
    settings = QtCore.QSettings(str(tmp_path / "ifa_test.ini"), QtCore.QSettings.IniFormat)
    settings.clear()
    return settings


def _suppress_message_boxes(monkeypatch):
    # Avoid any blocking message boxes during initialization or status updates
    monkeypatch.setattr(
        QtWidgets.QMessageBox, "information", lambda *args, **kwargs: QtWidgets.QMessageBox.Ok
    )
    # Avoid blocking closeEvent dialog during teardown
    monkeypatch.setattr(
        QtWidgets.QMessageBox, "question", lambda *args, **kwargs: QtWidgets.QMessageBox.Discard
    )


def test_main_window_initializes_and_creates_project(qtbot, tmp_path, monkeypatch):
    settings = _create_settings(tmp_path)
    _suppress_message_boxes(monkeypatch)

    win = MainWindow(settings=settings)
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


def test_main_window_auto_loads_last_project(qtbot, tmp_path, monkeypatch):
    settings = _create_settings(tmp_path)
    _suppress_message_boxes(monkeypatch)

    project_path = tmp_path / "auto_project.json"
    system = SystemStructure("自动加载测试项目")
    with project_path.open("w", encoding="utf-8") as fh:
        json.dump(system.to_dict(), fh, ensure_ascii=False, indent=2)

    settings.setValue("last_project_path", str(project_path))

    win = MainWindow(settings=settings)
    qtbot.addWidget(win)
    win.show()
    qtbot.waitExposed(win)

    assert win.project_manager.current_file_path == str(project_path)
    assert win.project_manager.current_system is not None
    assert win.project_manager.current_system.name == "自动加载测试项目"
    assert win.project_label.text() == project_path.name
