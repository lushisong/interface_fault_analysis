import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest

QtWidgets = pytest.importorskip("PyQt5.QtWidgets", exc_type=ImportError)
QtCore = pytest.importorskip("PyQt5.QtCore", exc_type=ImportError)

module_panel_module = pytest.importorskip("src.ui.module_panel", exc_type=ImportError)
ModulePanel = module_panel_module.ModulePanel

interface_model = pytest.importorskip("src.models.interface_model", exc_type=ImportError)
Interface = interface_model.Interface
InterfaceType = interface_model.InterfaceType
InterfaceDirection = interface_model.InterfaceDirection


class DummyProjectManager:
    def __init__(self):
        self.modified = False
        self.current_system = None

    def mark_modified(self):
        self.modified = True


class DummySystem:
    def __init__(self):
        self.modules = {}
        self.interfaces = {}


@pytest.fixture
def module_panel(qtbot, monkeypatch):
    panel = ModulePanel()
    qtbot.addWidget(panel)

    project_manager = DummyProjectManager()
    system = DummySystem()
    project_manager.current_system = system

    panel.set_project_manager(project_manager)
    panel.set_current_system(system)

    qtbot.waitExposed(panel)

    # Patch message boxes to avoid blocking dialogs during tests
    monkeypatch.setattr(
        QtWidgets.QMessageBox,
        "information",
        lambda *args, **kwargs: QtWidgets.QMessageBox.Ok,
    )
    monkeypatch.setattr(
        QtWidgets.QMessageBox,
        "warning",
        lambda *args, **kwargs: QtWidgets.QMessageBox.Ok,
    )
    monkeypatch.setattr(
        QtWidgets.QMessageBox,
        "critical",
        lambda *args, **kwargs: QtWidgets.QMessageBox.Ok,
    )
    monkeypatch.setattr(
        QtWidgets.QMessageBox,
        "question",
        lambda *args, **kwargs: QtWidgets.QMessageBox.Yes,
    )

    return panel, project_manager, system


def test_module_creation_and_save_workflow(module_panel, qtbot, monkeypatch):
    panel, project_manager, system = module_panel

    # Prepare an interface template for instantiation via the selector dialog
    template_interface = Interface(
        "测试模板接口",
        "用于模块连线的模板",
        InterfaceType.ALGORITHM_HARDWARE,
        InterfaceDirection.BIDIRECTIONAL,
    )
    template_interface.parameters = {"默认参数": "1"}
    system.interfaces[template_interface.id] = template_interface

    class StubInterfaceDialog:
        def __init__(self, interfaces_dict, parent=None):
            self.interfaces = interfaces_dict

        def exec_(self):
            return QtWidgets.QDialog.Accepted

        def get_selected_interface(self):
            return template_interface

    monkeypatch.setattr(module_panel_module, "InterfaceTemplateDialog", StubInterfaceDialog)

    panel.show()

    # Create a new module via the toolbar button
    panel.new_module_btn.click()
    qtbot.waitUntil(lambda: panel.module_tree.topLevelItemCount() == 1)

    module_item = panel.module_tree.topLevelItem(0)
    panel.module_tree.setCurrentItem(module_item)

    # Fill in basic information
    panel.name_edit.setText("执行单元")
    panel.description_edit.setPlainText("负责执行控制命令的模块")
    panel.module_type_combo.setCurrentText("hardware")
    panel.pos_x_spin.setValue(12.5)
    panel.pos_y_spin.setValue(34.0)
    panel.size_width_spin.setValue(180)
    panel.size_height_spin.setValue(90)

    # Add module parameters through the UI
    panel.param_name_edit.setText("增益")
    panel.param_value_edit.setText("2.5")
    panel.add_param_btn.click()
    qtbot.waitUntil(lambda: panel.parameter_list.count() == 1)

    # Attach an interface from the template library
    panel.add_connection_btn.click()
    qtbot.waitUntil(lambda: panel.connection_list.count() == 1)

    # Provide Python modeling code
    panel.code_edit.setPlainText(
        "outputs['thrust'] = float(inputs.get('command', 0)) * float(parameters.get('增益', 1))"
    )

    panel.save_btn.click()

    assert len(system.modules) == 1
    saved_module = next(iter(system.modules.values()))
    assert saved_module.name == "执行单元"
    assert saved_module.description == "负责执行控制命令的模块"
    assert saved_module.parameters == {"增益": "2.5"}
    assert len(saved_module.interfaces) == 1
    assert isinstance(next(iter(saved_module.interfaces.values())), Interface)
    assert project_manager.modified is True
