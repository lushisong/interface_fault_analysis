import math
import os
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.models.interface_model import (
    Interface,
    InterfaceDirection,
    InterfaceFailureMode,
    InterfaceState,
    InterfaceStateType,
    InterfaceType,
    FailureMode,
    TriggerCondition,
)
from src.models.module_model import Module
from src.models.system_model import (
    Connection,
    EnvironmentModel,
    SuccessCriteria as SystemSuccessCriteria,
    SystemStructure,
    TaskProfile as SystemTaskProfile,
    TaskStatus,
)
from src.models.task_profile_model import (
    ComparisonOperator,
    SuccessCriteria,
    TaskProfile,
)
from src.core.fault_tree_generator import FaultTreeGenerator
from src.core.project_manager import ProjectManager
from create_drone_demo import create_drone_system_demo


@pytest.fixture
def interface_with_failure():
    interface = Interface("数据链路", "用于测试的链路", InterfaceType.ALGORITHM_HARDWARE, InterfaceDirection.BIDIRECTIONAL)
    interface.parameters = {"带宽": "20"}

    # 创建失效状态
    failure_state = InterfaceState("通信超时", InterfaceStateType.FAILURE)
    failure_state.outputs["status"] = "timeout"
    failure_state.python_code = "outputs['status'] = 'timeout'"
    failure_state_id = interface.add_state(failure_state)

    # 创建失效模式和触发条件
    failure_mode = InterfaceFailureMode(FailureMode.TIMEOUT, "通信超时")
    failure_mode.associated_state_id = failure_state_id
    failure_mode.id = "failure-mode-timeout"
    failure_mode.enabled = True
    failure_mode.failure_rate = 2e-6

    threshold_condition = TriggerCondition("高延迟", "threshold")
    threshold_condition.parameters = {"variable": "latency", "operator": ">", "value": 50}
    failure_mode.add_trigger_condition(threshold_condition)

    probability_condition = TriggerCondition("随机触发", "probability")
    probability_condition.parameters = {"probability": 0.9}
    failure_mode.add_trigger_condition(probability_condition)

    interface.add_failure_mode(failure_mode)
    interface.reset_runtime_state()
    return interface, failure_mode, failure_state


def test_interface_state_machine_and_instantiation(interface_with_failure):
    interface, failure_mode, failure_state = interface_with_failure

    # 触发状态机转移
    result = interface.step_state_machine({"inputs": {"latency": 80}, "random_generator": None})
    assert result["state_id"] == failure_state.id
    assert interface.current_state_id == failure_state.id
    assert interface.get_active_failure_modes()[0].name == failure_mode.name

    # 验证simulate_interface整合状态输出与Python代码
    outputs = interface.simulate_interface({"latency": 80})
    assert outputs["status"] == "timeout"

    # 验证实例化的独立性
    template_bandwidth = interface.parameters["带宽"]
    instance = interface.instantiate_from_template("实例接口")
    instance.parameters["带宽"] = "40"
    assert interface.parameters["带宽"] == template_bandwidth
    assert instance.current_state_id == instance.normal_state_id
    assert instance.failure_modes[0].name == failure_mode.name
    assert instance.failure_modes[0] is not failure_mode


def test_module_execution_and_serialization(interface_with_failure):
    interface, failure_mode, _ = interface_with_failure

    module = Module("通信模块", "用于测试的模块")
    module.add_interface(interface)
    module.set_parameter("增益", 2)
    module.python_code = "outputs['power'] = inputs.get('signal', 0) * parameters.get('增益', 1)"

    outputs = module.execute_python_code({"signal": 3})
    assert outputs["power"] == 6

    serialized = module.to_dict()
    restored = Module()
    restored.from_dict(serialized)
    assert restored.parameters["增益"] == 2
    assert len(restored.interfaces) == len(module.interfaces)


def test_system_simulation_and_task_success(interface_with_failure):
    interface, failure_mode, _ = interface_with_failure

    system = SystemStructure("无人机系统")

    module = Module("飞行控制", "负责姿态与高度控制")
    module.id = "module_fc"
    module.parameters["偏置"] = 5
    module.python_code = "outputs['altitude'] = parameters.get('偏置', 0)"

    system.add_module(module)
    system.add_interface(interface)

    connection = Connection(
        id="conn_fc",
        source_module_id=module.id,
        target_module_id=module.id,
        source_point_id=interface.id,
        target_point_id=interface.id,
    )
    connection.interface_id = interface.id
    system.add_connection(connection)

    environment = EnvironmentModel("高温环境", "测试环境")
    environment.id = "env_hot"
    environment.parameters = {"altitude_drop": 1}
    environment.python_code = (
        "modified = system_state.copy()\n"
        "module_state = modified.setdefault('module_fc', {})\n"
        "module_state['altitude'] = module_state.get('altitude', 0) - parameters.get('altitude_drop', 0)\n"
        "modified_state = modified\n"
    )
    system.add_environment_model(environment)

    task_profile = SystemTaskProfile("巡航任务", "系统级任务剖面")
    task_profile.id = "system_task"
    criteria = SystemSuccessCriteria("高度判据")
    criteria.target_module_id = module.id
    criteria.target_parameter = "altitude"
    criteria.threshold_value = 4
    criteria.comparison_operator = ">="
    task_profile.add_success_criteria(criteria)
    system.add_task_profile(task_profile)
    system.current_task_profile_id = task_profile.id

    system_state = system.simulate_system()
    status, success_rate = task_profile.evaluate_task_success(system_state)
    assert status == TaskStatus.SUCCESS
    assert math.isclose(success_rate, 1.0)


def test_fault_tree_generation_with_interface_failures(interface_with_failure):
    interface, failure_mode, _ = interface_with_failure

    system = SystemStructure("故障树系统")
    module = Module("导航模块", "负责航迹导航")
    module.id = "module_nav"
    system.add_module(module)

    system.add_interface(interface)

    connection = Connection(
        id="conn_nav",
        source_module_id=module.id,
        target_module_id=module.id,
        source_point_id=interface.id,
        target_point_id=interface.id,
    )
    connection.interface_id = interface.id
    system.add_connection(connection)

    task_profile = TaskProfile("导航任务", "任务剖面")
    criteria = SuccessCriteria("航迹误差")
    criteria.module_id = module.id
    criteria.parameter_name = "track_error"
    criteria.operator = ComparisonOperator.LESS_EQUAL
    criteria.target_value = 5.0
    task_profile.add_success_criteria(criteria)

    generator = FaultTreeGenerator()
    fault_tree = generator.generate_fault_tree(system, task_profile)

    top_event = fault_tree.get_top_event()
    assert top_event is not None
    assert "失败" in top_event.name
    assert any(event.interface_id == interface.id for event in fault_tree.events.values())
    assert fault_tree.top_event_id == top_event.id


def test_demo_project_persists_task_profiles_and_environments(tmp_path):
    system, _ = create_drone_system_demo()

    manager = ProjectManager()
    manager.set_current_system(system)
    project_path = tmp_path / "drone_demo.json"

    assert manager.save_project_as(str(project_path))

    reloaded = manager.load_project(str(project_path))

    assert len(reloaded.task_profiles) == 2
    task_names = {profile.name for profile in reloaded.task_profiles.values()}
    assert {"抵近侦察任务", "物资投放任务"} <= task_names
    for profile in reloaded.task_profiles.values():
        assert hasattr(profile, "total_duration")
        assert profile.total_duration > 0

    assert len(reloaded.environment_models) == 3
    environment_names = {model.name for model in reloaded.environment_models.values()}
    expected_env = {"恶劣天气环境", "电磁干扰环境", "高温环境"}
    assert expected_env <= environment_names


def test_fault_tree_generator_handles_duration_only_task_profile():
    system = SystemStructure("遗留任务剖面系统")

    module = Module("导航模块", "负责航迹导航")
    module.id = "module_nav"
    system.add_module(module)

    legacy_profile = SystemTaskProfile("遗留任务", "仅包含持续时间字段")
    legacy_profile.id = "legacy_task"
    legacy_profile.duration = 1800.0
    assert not hasattr(legacy_profile, "total_duration")

    criteria = SystemSuccessCriteria("航迹误差阈值")
    criteria.target_module_id = module.id
    criteria.target_parameter = "track_error"
    criteria.threshold_value = 10.0
    criteria.comparison_operator = "<="
    # 模拟旧版任务剖面字段
    criteria.module_id = module.id
    criteria.parameter_name = "track_error"
    criteria.operator = "<="
    criteria.target_value = 10.0
    legacy_profile.add_success_criteria(criteria)

    generator = FaultTreeGenerator()
    fault_tree = generator.generate_fault_tree(system, legacy_profile)

    assert math.isclose(fault_tree.mission_time, legacy_profile.duration / 3600.0)
    assert fault_tree.get_top_event() is not None
