import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

QtWidgets = pytest.importorskip("PyQt5.QtWidgets", exc_type=ImportError)

from src.models.system_model import SystemStructure, Connection
from src.models.module_model import ModuleTemplate
from src.ui.module_panel import ModulePanel
from src.models.task_profile_model import TaskProfile
from src.core.fault_tree_generator import FaultTreeGenerator


def _build_template_module(panel: ModulePanel, template: ModuleTemplate):
    module = panel.create_module_from_template(template)
    panel.modules[module.id] = module
    return module


def test_fault_tree_generation_from_templates(qtbot):
    panel = ModulePanel()
    qtbot.addWidget(panel)
    panel.show()
    qtbot.waitExposed(panel)

    system = SystemStructure("FT 集成测试")

    # Create a simple sensor -> actuator chain
    sensor = _build_template_module(panel, ModuleTemplate.SENSOR)
    actuator = _build_template_module(panel, ModuleTemplate.ACTUATOR)

    system.modules[sensor.id] = sensor
    system.modules[actuator.id] = actuator

    # Persist one interface template as a reusable interface in system, then connect via Connection
    interface = next(iter(sensor.interfaces.values()))
    system.interfaces[interface.id] = interface

    connection = Connection(
        id="c1",
        source_module_id=sensor.id,
        target_module_id=actuator.id,
        source_point_id=next(iter(sensor.interfaces.keys())),
        target_point_id=next(iter(actuator.interfaces.keys())),
    )
    connection.interface_id = interface.id
    system.connections[connection.id] = connection

    # Create a minimal task profile (30 minutes)
    task = TaskProfile("演示任务")
    task.duration = 1800.0

    ft = FaultTreeGenerator().generate_fault_tree(system, task)

    # We should have top + intermediate + several basic events (from module + interface failure modes)
    basic_events = [e for e in ft.events.values() if e.event_type.name == 'BASIC_EVENT']
    assert len(basic_events) >= 2  # At least one module internal + one interface failure mode
    # Probabilities should be set for basic events
    assert all(getattr(be, 'probability', 0.0) >= 0.0 for be in basic_events)

    # Names should include module and failure mode hints for interface events
    any_named = any(('[' in e.name and ']' in e.name) for e in basic_events)
    assert any_named


def test_interface_failure_modes_populated_in_templates(qtbot):
    panel = ModulePanel()
    qtbot.addWidget(panel)
    panel.show()
    qtbot.waitExposed(panel)

    mod = _build_template_module(panel, ModuleTemplate.SENSOR)
    # All interfaces created by templates should carry default failure modes
    assert mod.interfaces
    for iface in mod.interfaces.values():
        assert iface.failure_modes, "Template interface should have default failure modes"
        # Each failure mode should provide a sensible RPN value
        assert all(fm.rpn() > 0 for fm in iface.failure_modes)


def test_fault_tree_module_summary(qtbot):
    panel = ModulePanel()
    qtbot.addWidget(panel)
    panel.show()
    qtbot.waitExposed(panel)

    system = SystemStructure("FT 模块统计")
    a = panel.create_module_from_template(ModuleTemplate.SENSOR)
    b = panel.create_module_from_template(ModuleTemplate.ACTUATOR)
    system.modules[a.id] = a
    system.modules[b.id] = b
    iface = next(iter(a.interfaces.values()))
    system.interfaces[iface.id] = iface
    conn = Connection(
        id="c2",
        source_module_id=a.id,
        target_module_id=b.id,
        source_point_id=next(iter(a.interfaces.keys())),
        target_point_id=next(iter(b.interfaces.keys())),
    )
    conn.interface_id = iface.id
    system.connections[conn.id] = conn

    task = TaskProfile("T")
    task.duration = 600
    ft = FaultTreeGenerator().generate_fault_tree(system, task)
    summary = ft.analysis_results.get('module_summary')
    assert isinstance(summary, dict) and summary
    # Each module should appear with basic_event_count
    for mid, item in summary.items():
        assert item['basic_event_count'] >= 1
        assert isinstance(item['top_events'], list)
