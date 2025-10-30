import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PyQt5.QtWidgets", exc_type=ImportError)

from src.ui.interface_editor_widget import InterfaceEditorWidget
from src.models.interface_model import Interface, FailureMode, InterfaceFailureMode


def test_add_and_edit_failure_mode(qtbot, monkeypatch):
    widget = InterfaceEditorWidget()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)

    iface = Interface("链路", "测试接口")
    widget.load_interface(iface)

    class StubDlg:
        def __init__(self, *args, **kwargs):
            self._fm = InterfaceFailureMode(FailureMode.TIMEOUT, "超时")
            self._fm.description = "触发超时"
            self._fm.severity = 7
            self._fm.failure_rate = 1e-5
            self._fm.detection_rate = 0.3

        def exec_(self):
            return QtWidgets.QDialog.Accepted

        def get_failure_mode(self):
            return self._fm

    # Add failure mode via dialog stub
    monkeypatch.setattr("src.ui.interface_editor_widget.FailureModeDialog", StubDlg)
    widget.add_failure_mode()

    assert iface.failure_modes
    assert iface.failure_modes[0].name == "超时"

    # Edit failure mode (use stub again with different content)
    class StubDlg2(StubDlg):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._fm = InterfaceFailureMode(FailureMode.DATA_CORRUPTION, "数据损坏")
            self._fm.description = "CRC错误"
            self._fm.severity = 6
            self._fm.failure_rate = 2e-5
            self._fm.detection_rate = 0.4

    monkeypatch.setattr("src.ui.interface_editor_widget.FailureModeDialog", StubDlg2)
    # select first and edit
    widget.failure_list.setCurrentRow(0)
    widget.edit_failure_mode()

    assert iface.failure_modes[0].name == "数据损坏"
    assert iface.failure_modes[0].failure_rate == pytest.approx(2e-5)
