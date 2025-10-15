import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

QtWidgets = pytest.importorskip("PyQt5.QtWidgets", exc_type=ImportError)

from src.ui.system_canvas import SystemCanvas
from src.models.system_model import SystemStructure, Connection
from src.models.module_model import Module, ModuleType
from src.models.interface_model import Interface, InterfaceDirection
from src.models.base_model import Point


class DummyProjectManager:
    def __init__(self):
        self.modified = False

    def mark_modified(self):
        self.modified = True


@pytest.fixture
def canvas_with_system(qtbot):
    system = SystemStructure("测试系统")

    source_module = Module("源模块", module_type=ModuleType.HARDWARE)
    source_module.position = Point(100, 120)
    source_module.size = Point(140, 80)
    source_interface = Interface(
        "输出", "", direction=InterfaceDirection.OUTPUT
    )
    source_module.add_interface(source_interface)
    system.modules[source_module.id] = source_module

    target_module = Module("目标模块", module_type=ModuleType.HARDWARE)
    target_module.position = Point(420, 220)
    target_module.size = Point(140, 80)
    target_interface = Interface(
        "输入", "", direction=InterfaceDirection.INPUT
    )
    target_module.add_interface(target_interface)
    system.modules[target_module.id] = target_module

    canvas = SystemCanvas()
    canvas.set_project_manager(DummyProjectManager())
    canvas.set_system(system)
    qtbot.addWidget(canvas)
    canvas.show()
    qtbot.waitExposed(canvas)

    return canvas, system, source_module, source_interface, target_module, target_interface


def _interface_positions(canvas, source_module, source_interface, target_module, target_interface):
    source_item = canvas.graphics_items[source_module.id]
    target_item = canvas.graphics_items[target_module.id]
    source_pos = source_item.get_interface_position(source_interface.id)
    target_pos = target_item.get_interface_position(target_interface.id)
    return source_pos, target_pos


def test_connection_style_combo_defaults(canvas_with_system):
    canvas, *_ = canvas_with_system
    assert canvas.connection_style_combo.currentData() == "curved"
    assert canvas.connection_line_style == "curved"

    canvas.connection_style_combo.setCurrentIndex(1)
    assert canvas.connection_style_combo.currentData() == "straight"
    assert canvas.connection_line_style == "straight"

    canvas.connection_style_combo.setCurrentIndex(2)
    assert canvas.connection_style_combo.currentData() == "orthogonal"
    assert canvas.connection_line_style == "orthogonal"


@pytest.mark.parametrize(
    "style, expected_elements",
    [
        ("curved", 4),
        ("straight", 2),
        ("orthogonal", 4),
    ],
)
def test_draw_connection_respects_style(canvas_with_system, style, expected_elements):
    canvas, system, source_module, source_interface, target_module, target_interface = canvas_with_system

    connection = Connection(
        id=f"conn_{style}",
        source_module_id=source_module.id,
        target_module_id=target_module.id,
        source_point_id=source_interface.id,
        target_point_id=target_interface.id,
        line_style=style,
    )
    system.connections[connection.id] = connection

    canvas.draw_connection(connection)

    item = canvas.connection_items[connection.id]
    path = item.path()

    assert path.elementCount() == expected_elements
    assert connection.line_style == style

    source_pos, target_pos = _interface_positions(
        canvas, source_module, source_interface, target_module, target_interface
    )

    first_element = path.elementAt(0)
    last_element_index = path.elementCount() - 1
    last_element = path.elementAt(last_element_index)

    assert first_element.x == pytest.approx(source_pos.x())
    assert first_element.y == pytest.approx(source_pos.y())
    assert last_element.x == pytest.approx(target_pos.x())
    assert last_element.y == pytest.approx(target_pos.y())

    if style == "curved":
        assert len(item.control_point_items) == 2
    else:
        assert len(item.control_point_items) == 0

    if style == "straight":
        assert path.elementCount() == 2
        straight_endpoint = path.elementAt(1)
        assert straight_endpoint.x == pytest.approx(target_pos.x())
        assert straight_endpoint.y == pytest.approx(target_pos.y())
    elif style == "orthogonal":
        assert path.elementCount() == 4
        mid1 = path.elementAt(1)
        mid2 = path.elementAt(2)

        dx = target_pos.x() - source_pos.x()
        dy = target_pos.y() - source_pos.y()

        if abs(dx) >= abs(dy):
            expected_mid_x = source_pos.x() + dx / 2
            assert mid1.y == pytest.approx(source_pos.y())
            assert mid1.x == pytest.approx(expected_mid_x)
            assert mid2.x == pytest.approx(expected_mid_x)
            assert mid2.y == pytest.approx(target_pos.y())
        else:
            expected_mid_y = source_pos.y() + dy / 2
            assert mid1.x == pytest.approx(source_pos.x())
            assert mid1.y == pytest.approx(expected_mid_y)
            assert mid2.x == pytest.approx(target_pos.x())
            assert mid2.y == pytest.approx(expected_mid_y)
