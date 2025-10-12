"""Pytest-Qt suite for verifying the six primary module templates.

The suite exercises the ModulePanel UI to instantiate SENSOR, ACTUATOR,
PROCESSOR, OPERATING_SYSTEM, APPLICATION, and CONTROL_ALGORITHM templates.
Each test validates the resulting module metadata, interface definitions,
and the automatic initialization of interface state machines. The suite is
marked with ``diamante`` for selective execution via ``pytest -m diamante``.
"""

import os
from typing import Dict

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:  # pragma: no cover - guard for environments lacking GUI dependencies
    from PyQt5.QtCore import Qt
    from src.ui.module_panel import ModulePanel
    from src.models.interface_model import InterfaceDirection
    from src.models.module_model import (
        AlgorithmModule,
        HardwareModule,
        ModuleTemplate,
        ModuleType,
        SoftwareModule,
    )
except ImportError as exc:  # pragma: no cover - skip when PyQt cannot load (e.g., missing libGL)
    pytest.skip(
        f"PyQt5 dependencies unavailable, skipping UI template tests: {exc}",
        allow_module_level=True,
    )


TEMPLATE_EXPECTATIONS = [
    (
        ModuleTemplate.SENSOR,
        HardwareModule,
        ModuleType.HARDWARE,
        {
            "传感器数据输入": {
                "direction": InterfaceDirection.INPUT,
                "data_format": "signal",
            },
            "传感器数据输出": {
                "direction": InterfaceDirection.OUTPUT,
                "data_format": "data",
            },
        },
    ),
    (
        ModuleTemplate.ACTUATOR,
        HardwareModule,
        ModuleType.HARDWARE,
        {
            "控制信号输入": {
                "direction": InterfaceDirection.INPUT,
                "data_format": "control",
            },
            "状态反馈输出": {
                "direction": InterfaceDirection.OUTPUT,
                "data_format": "signal",
            },
        },
    ),
    (
        ModuleTemplate.PROCESSOR,
        HardwareModule,
        ModuleType.HARDWARE,
        {
            "通用输入": {
                "direction": InterfaceDirection.INPUT,
                "data_format": "data",
            },
            "通用输出": {
                "direction": InterfaceDirection.OUTPUT,
                "data_format": "data",
            },
        },
    ),
    (
        ModuleTemplate.OPERATING_SYSTEM,
        SoftwareModule,
        ModuleType.SOFTWARE,
        {
            "通用输入": {
                "direction": InterfaceDirection.INPUT,
                "data_format": "data",
            },
            "通用输出": {
                "direction": InterfaceDirection.OUTPUT,
                "data_format": "data",
            },
        },
    ),
    (
        ModuleTemplate.APPLICATION,
        SoftwareModule,
        ModuleType.SOFTWARE,
        {
            "通用输入": {
                "direction": InterfaceDirection.INPUT,
                "data_format": "data",
            },
            "通用输出": {
                "direction": InterfaceDirection.OUTPUT,
                "data_format": "data",
            },
        },
    ),
    (
        ModuleTemplate.CONTROL_ALGORITHM,
        AlgorithmModule,
        ModuleType.ALGORITHM,
        {
            "通用输入": {
                "direction": InterfaceDirection.INPUT,
                "data_format": "data",
            },
            "通用输出": {
                "direction": InterfaceDirection.OUTPUT,
                "data_format": "data",
            },
        },
    ),
]


def _find_template_item(panel: ModulePanel, template: ModuleTemplate):
    """Locate the QListWidgetItem that stores the requested template."""
    for index in range(panel.template_list.count()):
        item = panel.template_list.item(index)
        if item.data(Qt.UserRole) == template:
            return item
    return None


@pytest.mark.diamante
@pytest.mark.parametrize(
    "template,expected_class,expected_type,expected_interfaces",
    TEMPLATE_EXPECTATIONS,
    ids=[
        "sensor",
        "actuator",
        "processor",
        "operating-system",
        "application",
        "control-algorithm",
    ],
)
def test_module_template_creation_workflow(
    qtbot,
    template: ModuleTemplate,
    expected_class,
    expected_type: ModuleType,
    expected_interfaces: Dict[str, Dict[str, object]],
):
    """Ensure double-clicking a template yields a fully configured module."""

    panel = ModulePanel()
    qtbot.addWidget(panel)
    panel.show()
    qtbot.waitForWindowShown(panel)

    template_item = _find_template_item(panel, template)
    assert template_item is not None, f"Template {template} not present in list"

    item_rect = panel.template_list.visualItemRect(template_item)
    item_center = item_rect.center()

    with qtbot.waitSignal(panel.module_created, timeout=2000) as blocker:
        qtbot.mouseClick(
            panel.template_list.viewport(),
            Qt.LeftButton,
            pos=item_center,
        )
        qtbot.mouseDClick(
            panel.template_list.viewport(),
            Qt.LeftButton,
            pos=item_center,
        )

    created_module = blocker.args[0]
    assert isinstance(created_module, expected_class)

    # The panel should make the created module current and persist it internally.
    assert panel.current_module is created_module
    assert created_module.id in panel.modules

    # Template metadata should be preserved.
    assert created_module.template == template
    assert created_module.module_type == expected_type

    # The module tree view should contain a single entry pointing to the module.
    assert panel.module_tree.topLevelItemCount() == 1
    tree_item = panel.module_tree.topLevelItem(0)
    assert tree_item.data(0, Qt.UserRole) == created_module.id
    assert tree_item.text(0) == created_module.name

    # Validate interface definitions for the selected template.
    interfaces = {iface.name: iface for iface in created_module.interfaces.values()}
    assert set(interfaces.keys()) == set(expected_interfaces.keys())

    for name, expectations in expected_interfaces.items():
        interface = interfaces[name]
        assert interface.direction == expectations["direction"]
        assert interface.data_format == expectations["data_format"]

    # Ensure that the default state machine is initialized for each interface.
    for interface in interfaces.values():
        assert interface.current_state_id is not None
        assert interface.normal_state_id == interface.current_state_id
        assert interface.states  # At least the normal state should be present.
