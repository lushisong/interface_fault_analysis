import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest

QtWidgets = pytest.importorskip("PyQt5.QtWidgets", exc_type=ImportError)

panel_module = pytest.importorskip("src.ui.task_profile_panel", exc_type=ImportError)
TaskProfilePanel = panel_module.TaskProfilePanel

system_model = pytest.importorskip("src.models.system_model", exc_type=ImportError)
SystemStructure = system_model.SystemStructure

profile_model = pytest.importorskip("src.models.task_profile_model", exc_type=ImportError)
SuccessCriteria = profile_model.SuccessCriteria
TaskPhase = profile_model.TaskPhase
ComparisonOperator = profile_model.ComparisonOperator
SuccessCriteriaType = profile_model.SuccessCriteriaType


class DummyProjectManager:
    def __init__(self, system):
        self.current_system = system
        self.modified = False

    def mark_modified(self):
        self.modified = True


@pytest.fixture
def task_profile_panel(qtbot, monkeypatch):
    system = SystemStructure("测试系统")
    project_manager = DummyProjectManager(system)

    panel = TaskProfilePanel()
    panel.set_project_manager(project_manager)
    qtbot.addWidget(panel)
    panel.show()
    qtbot.waitExposed(panel)

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
        "question",
        lambda *args, **kwargs: QtWidgets.QMessageBox.Yes,
    )

    return panel, project_manager, system


def test_task_profile_creation_and_save(task_profile_panel, qtbot):
    panel, project_manager, system = task_profile_panel

    # Create a new profile via the toolbar button
    panel.new_profile_btn.click()
    qtbot.waitUntil(lambda: panel.profile_tree.topLevelItemCount() == 1)

    item = panel.profile_tree.topLevelItem(0)
    panel.profile_tree.setCurrentItem(item)
    qtbot.waitUntil(lambda: panel.current_profile is not None)

    panel.name_edit.setText("巡航任务")
    panel.description_edit.setPlainText("无人机巡航监视任务")
    panel.mission_type_edit.setText("surveillance")
    panel.duration_spin.setValue(1800)

    # Inject success criteria and phases to exercise table updates
    criteria = SuccessCriteria("高度维持")
    criteria.criteria_type = SuccessCriteriaType.MODULE_OUTPUT
    criteria.module_id = "flight_controller"
    criteria.parameter_name = "altitude"
    criteria.operator = ComparisonOperator.GREATER_EQUAL
    criteria.target_value = 1000.0
    panel.current_profile.add_success_criteria(criteria)
    panel.refresh_criteria_table()
    assert panel.criteria_table.rowCount() == 1

    phase = TaskPhase("巡航阶段")
    phase.start_time = 0.0
    phase.duration = 1200.0
    panel.current_profile.add_task_phase(phase)
    panel.refresh_phases_table()
    assert panel.phases_table.rowCount() == 1

    panel.save_btn.click()

    saved_profile = panel.current_profile
    assert saved_profile.name == "巡航任务"
    assert saved_profile.description == "无人机巡航监视任务"
    assert saved_profile.total_duration == 1800
    assert saved_profile.success_criteria[0].parameter_name == "altitude"
    assert saved_profile.task_phases[0].duration == 1200.0
    assert saved_profile.id in system.task_profiles
