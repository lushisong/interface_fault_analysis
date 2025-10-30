from src.templates import (
    build_interface_from_template,
    create_module_from_template,
    get_interface_templates_by_category,
)
from src.models.module_model import ModuleTemplate
from src.models.interface_model import InterfaceDirection
from src.models.system_model import SystemStructure, Connection


def test_sensor_template_produces_measurement_and_interfaces():
    module = create_module_from_template(ModuleTemplate.SENSOR)
    outputs = module.execute_python_code({"environment": {"stress": 0.2}})

    assert "measurement" in outputs
    assert "health" in outputs
    assert 0.0 <= outputs["health"] <= 1.0
    assert module.interfaces  # 模板应提供接口

    sensor_in = None
    sensor_out = None
    for interface in module.interfaces.values():
        if interface.direction == InterfaceDirection.INPUT:
            sensor_in = interface
        elif interface.direction == InterfaceDirection.OUTPUT:
            sensor_out = interface
        assert interface.failure_modes, "模板接口应包含默认失效模式"
    assert sensor_in is not None and sensor_out is not None


def test_category_interface_template_has_failure_modes_and_code():
    catalog = get_interface_templates_by_category()
    application_templates = catalog["算法-应用接口"]
    assert application_templates, "应用接口模板应已注册"

    definition = application_templates[0]
    instance = build_interface_from_template(definition)

    assert instance.failure_modes
    assert "interface_function" in instance.python_code or "outputs" in instance.python_code


def test_system_simulation_flow_uses_template_interfaces():
    system = SystemStructure("模板系统")

    sensor = create_module_from_template(ModuleTemplate.SENSOR)
    actuator = create_module_from_template(ModuleTemplate.ACTUATOR)

    system.add_module(sensor)
    system.add_module(actuator)

    sensor_out = next(
        iface for iface in sensor.interfaces.values() if iface.direction == InterfaceDirection.OUTPUT
    )
    actuator_in = next(
        iface for iface in actuator.interfaces.values() if iface.direction == InterfaceDirection.INPUT
    )

    # 建立简单的连线关系
    sensor_out.target_module_id = actuator.id
    actuator_in.source_module_id = sensor.id

    connection = Connection(
        id="sensor_to_actuator",
        source_module_id=sensor.id,
        target_module_id=actuator.id,
        source_point_id=sensor_out.id,
        target_point_id=actuator_in.id,
    )
    connection.interface_id = sensor_out.id
    system.add_connection(connection)

    state = system.simulate_system()

    assert sensor.id in state and actuator.id in state
    actuator_state = state[actuator.id]
    assert "interface_inputs" in actuator_state
    assert actuator_in.name in actuator_state["interface_inputs"]
