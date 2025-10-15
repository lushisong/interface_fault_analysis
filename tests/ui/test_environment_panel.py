import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PyQt5.QtWidgets", exc_type=ImportError)
QtCore = pytest.importorskip("PyQt5.QtCore", exc_type=ImportError)

environment_panel_module = pytest.importorskip("src.ui.environment_panel", exc_type=ImportError)
EnvironmentPanel = environment_panel_module.EnvironmentPanel

system_model = pytest.importorskip("src.models.system_model", exc_type=ImportError)
SystemStructure = system_model.SystemStructure

env_model = pytest.importorskip("src.models.environment_model", exc_type=ImportError)
ENVIRONMENT_TEMPLATES = env_model.ENVIRONMENT_TEMPLATES


class DummyProjectManager:
    def __init__(self, system):
        self.current_system = system
        self.modified = False

    def mark_modified(self):
        self.modified = True


@pytest.fixture
def env_panel(qtbot, monkeypatch):
    system = SystemStructure("测试系统")
    pm = DummyProjectManager(system)

    panel = EnvironmentPanel()
    panel.set_project_manager(pm)
    panel.set_current_system(system)
    qtbot.addWidget(panel)
    panel.show()
    qtbot.waitExposed(panel)

    # Avoid blocking dialogs
    monkeypatch.setattr(
        QtWidgets.QMessageBox, "information", lambda *args, **kwargs: QtWidgets.QMessageBox.Ok
    )
    monkeypatch.setattr(
        QtWidgets.QMessageBox, "warning", lambda *args, **kwargs: QtWidgets.QMessageBox.Ok
    )
    monkeypatch.setattr(
        QtWidgets.QMessageBox, "question", lambda *args, **kwargs: QtWidgets.QMessageBox.Yes
    )

    return panel, pm, system


def test_new_environment_workflow(env_panel, qtbot, monkeypatch):
    panel, pm, system = env_panel

    class StubEnvDialog:
        def __init__(self, env_module=None, system_modules=None, parent=None):
            self._env = env_module

        def exec_(self):
            # Pretend user accepted dialog
            # Also tweak the name to verify persistence
            self._env.name = "新建环境A"
            return QtWidgets.QDialog.Accepted

    monkeypatch.setattr(environment_panel_module, "EnvironmentModuleDialog", StubEnvDialog)

    # Trigger creation via button
    panel.new_env_btn.click()

    # One environment should be present and selected in tree
    qtbot.waitUntil(lambda: panel.env_tree.topLevelItemCount() == 1)
    assert len(system.environment_models) == 1

    env_obj = next(iter(system.environment_models.values()))
    assert env_obj.name == "新建环境A"

    # Details area should reflect selection
    items = panel.env_tree.selectedItems()
    assert items, "New environment should be selected"
    assert panel.save_btn.isEnabled() and panel.edit_btn.isEnabled()


def test_create_environment_from_template(env_panel, qtbot, monkeypatch):
    panel, pm, system = env_panel

    # Choose a real template key
    template_key = next(iter(ENVIRONMENT_TEMPLATES.keys()))

    # Stub the QInputDialog.getItem to return our choice and Accepted
    def fake_get_item(parent, title, label, items, current, editable):
        return template_key, True

    monkeypatch.setattr(QtWidgets.QInputDialog, "getItem", staticmethod(fake_get_item))

    # Trigger template creation
    panel.template_btn.click()
    qtbot.waitUntil(lambda: panel.env_tree.topLevelItemCount() >= 1)

    # Verify environment added and visible
    assert len(system.environment_models) >= 1
    names = [item.text(0) for item in (panel.env_tree.topLevelItem(i) for i in range(panel.env_tree.topLevelItemCount()))]
    assert template_key in names

