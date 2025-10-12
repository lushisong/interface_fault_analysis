import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

QtWidgets = pytest.importorskip("PyQt5.QtWidgets", exc_type=ImportError)
QtCore = pytest.importorskip("PyQt5.QtCore", exc_type=ImportError)

QMessageBox = QtWidgets.QMessageBox
Qt = QtCore.Qt

interface_panel_module = pytest.importorskip("src.ui.interface_panel", exc_type=ImportError)
InterfacePanel = interface_panel_module.InterfacePanel

interface_model_module = pytest.importorskip("src.models.interface_model", exc_type=ImportError)
InterfaceType = interface_model_module.InterfaceType
InterfaceDirection = interface_model_module.InterfaceDirection


class DummyProjectManager:
    def __init__(self):
        self.modified = False

    def mark_modified(self):
        self.modified = True


class DummySystem:
    def __init__(self):
        self.interfaces = {}


@pytest.fixture
def interface_panel(qtbot):
    panel = InterfacePanel()
    qtbot.addWidget(panel)
    panel.show()
    qtbot.waitExposed(panel)
    return panel


def test_template_selection_populates_fields(interface_panel, qtbot):
    panel = interface_panel

    root = panel.interface_tree.invisibleRootItem()
    first_category = root.child(0)
    template_item = first_category.child(0)

    panel.interface_tree.setCurrentItem(template_item)
    qtbot.waitUntil(lambda: panel.name_edit.text() == template_item.text(0))

    assert panel.name_edit.text() == template_item.text(0)
    assert panel.type_combo.currentText() == first_category.text(0)
    assert template_item.text(0) in panel.description_edit.toPlainText()
    assert panel.failure_list.count() > 0
    assert panel.subtype_combo.count() > 0


def test_save_interface_creates_instance(qtbot, monkeypatch):
    panel = InterfacePanel()
    qtbot.addWidget(panel)
    panel.set_project_manager(DummyProjectManager())
    system = DummySystem()
    panel.set_current_system(system)
    panel.show()
    qtbot.waitExposed(panel)

    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "critical", lambda *args, **kwargs: QMessageBox.Ok)

    root = panel.interface_tree.invisibleRootItem()
    first_category = root.child(0)
    template_item = first_category.child(0)
    panel.interface_tree.setCurrentItem(template_item)
    qtbot.waitUntil(lambda: panel.name_edit.text() == template_item.text(0))

    panel.name_edit.setText("测试接口")
    panel.description_edit.setPlainText("自定义描述")
    panel.type_combo.setCurrentText("算法-硬件设备接口")
    panel.direction_combo.setCurrentText("输出")

    panel.param_name_edit.setText("带宽")
    panel.param_value_edit.setText("10")
    panel.param_type_combo.setCurrentText("int")
    panel.add_parameter()

    panel.code_edit.setPlainText("print('hello')")

    panel.save_interface()

    assert len(panel.interfaces) == 1
    interface = next(iter(panel.interfaces.values()))
    assert interface.name == "测试接口"
    assert interface.description == "自定义描述"
    assert interface.interface_type == InterfaceType.ALGORITHM_HARDWARE
    assert interface.direction == InterfaceDirection.OUTPUT
    assert interface.parameters == {"带宽": "10"}
    assert interface.python_code == "print('hello')"

    assert interface.id in system.interfaces
    assert panel.project_manager.modified

    current_item = panel.interface_tree.currentItem()
    assert current_item is not None
    data = current_item.data(0, Qt.UserRole)
    assert data["type"] == "interface_instance"
    assert data["interface_id"] == interface.id
