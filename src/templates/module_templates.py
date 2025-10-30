"""
Module template library.

Provides deterministic module behaviour scripts together with rich
interface compositions so that users can instantiate ready-to-run module
models directly from the template gallery.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from textwrap import dedent
from typing import Dict, List, Optional, Type

from ..models.module_model import (
    AlgorithmModule,
    HardwareModule,
    Module,
    ModuleTemplate,
    ModuleType,
    SoftwareModule,
)
from ..models.base_model import Point
from ..templates.interface_templates import (
    build_interface_from_template,
    get_interface_template,
    initialise_interface_templates,
)
from ..models.interface_model import InterfaceDirection


@dataclass(frozen=True)
class ModuleTemplateDefinition:
    """Structural description of a module template."""

    template: ModuleTemplate
    display_name: str
    description: str
    module_cls: Type[Module]
    module_type: ModuleType
    python_code: str
    parameters: Dict[str, object] = field(default_factory=dict)
    state_variables: Dict[str, object] = field(default_factory=dict)
    interface_keys: List[str] = field(default_factory=list)
    icon_path: str = ""
    size: Point = field(default_factory=lambda: Point(120.0, 80.0))
    failure_rate: float = 1.0e-5


MODULE_TEMPLATE_LIBRARY: Dict[ModuleTemplate, ModuleTemplateDefinition] = {}


def _safe_float_expression(name: str, default: float) -> str:
    return f"_to_float(parameters.get('{name}', {default}))"


COMMON_HELPERS = dedent(
    """\
    def _to_float(value, default=0.0):
        try:
            return float(value)
        except Exception:
            return default

    def _to_int(value, default=0):
        try:
            return int(value)
        except Exception:
            return default
    """
)


SENSOR_CODE = COMMON_HELPERS + dedent(
    """\
    environment = inputs.get('environment', {})
    stress = _to_float(environment.get('vibration_level', environment.get('stress', 0.0)))
    drift = _to_float(state_variables.get('drift', 0.0))
    drift += _to_float(parameters.get('drift_rate', 0.0002))
    state_variables['drift'] = drift

    baseline = _to_float(parameters.get('baseline', 1.0))
    sensitivity = _to_float(parameters.get('sensitivity', 1.0))
    measurement = baseline * sensitivity + drift + stress * _to_float(parameters.get('stress_gain', 0.05))

    outputs['measurement'] = measurement
    outputs['health'] = max(0.0, 1.0 - abs(stress) * _to_float(parameters.get('stress_penalty', 0.02)))
    outputs['status'] = 'nominal' if outputs['health'] >= 0.7 else ('degraded' if outputs['health'] >= 0.4 else 'critical')
    outputs['update_rate_hz'] = _to_float(parameters.get('update_rate_hz', 100.0))
    outputs['noise_floor'] = _to_float(parameters.get('noise_floor', 0.01))
    """
)


ACTUATOR_CODE = COMMON_HELPERS + dedent(
    """\
    command = _to_float(inputs.get('command', parameters.get('default_command', 0.0)))
    cmin = _to_float(parameters.get('command_min', -1.0))
    cmax = _to_float(parameters.get('command_max', 1.0))
    applied = max(cmin, min(cmax, command * _to_float(parameters.get('gain', 1.0))))

    state_variables['command_history'] = state_variables.get('command_history', [])
    history = state_variables['command_history']
    history.append(applied)
    if len(history) > 20:
        del history[0]

    setpoint = _to_float(inputs.get('setpoint', applied))
    tracking_error = setpoint - applied
    outputs['response'] = applied
    outputs['tracking_error'] = tracking_error
    outputs['health'] = max(0.0, 1.0 - abs(tracking_error) * _to_float(parameters.get('error_penalty', 0.02)))
    outputs['feedback'] = {
        'response': applied,
        'tracking_error': tracking_error,
        'saturated': applied == cmin or applied == cmax,
    }
    """
)


PROCESSOR_CODE = COMMON_HELPERS + dedent(
    """\
    workload = _to_float(inputs.get('workload', parameters.get('baseline_load', 0.35)))
    workload = max(0.0, min(1.5, workload))
    cores = _to_int(parameters.get('cpu_cores', 4))
    clock = _to_float(parameters.get('clock_rate_ghz', 2.0))
    outputs['cpu_usage'] = workload
    outputs['thermal_margin'] = max(0.0, 1.0 - workload * _to_float(parameters.get('thermal_sensitivity', 0.4)))
    outputs['compute_capacity_gflops'] = cores * clock * _to_float(parameters.get('ipc', 4.0))
    outputs['health'] = max(0.0, 1.0 - workload * 0.5)
    """
)


MEMORY_CODE = COMMON_HELPERS + dedent(
    """\
    total = _to_float(parameters.get('capacity_gb', 8.0))
    used = _to_float(inputs.get('used_gb', parameters.get('baseline_used_gb', 2.0)))
    used = max(0.0, min(total, used))
    state_variables['peak_used_gb'] = max(used, _to_float(state_variables.get('peak_used_gb', used)))
    outputs['used_gb'] = used
    outputs['available_gb'] = max(0.0, total - used)
    outputs['health'] = max(0.0, 1.0 - used / max(total, 0.1))
    """
)


COMMUNICATION_CODE = COMMON_HELPERS + dedent(
    """\
    traffic = _to_float(inputs.get('traffic_mbps', parameters.get('baseline_traffic_mbps', 10.0)))
    bandwidth = _to_float(parameters.get('bandwidth_mbps', 100.0))
    utilisation = min(1.5, traffic / max(bandwidth, 1.0))
    outputs['throughput_mbps'] = traffic
    outputs['latency_ms'] = _to_float(parameters.get('base_latency_ms', 5.0)) * (1.0 + utilisation)
    outputs['health'] = max(0.0, 1.0 - max(0.0, utilisation - 1.0) * 0.5)
    """
)


OPERATING_SYSTEM_CODE = COMMON_HELPERS + dedent(
    """\
    tasks = _to_int(inputs.get('active_tasks', parameters.get('baseline_tasks', 12)))
    sched_capacity = _to_int(parameters.get('scheduler_capacity', 32))
    io_wait = _to_float(inputs.get('io_wait_fraction', parameters.get('io_wait_fraction', 0.1)))
    cpu_usage = min(1.2, tasks / max(sched_capacity, 1))
    latency = _to_float(parameters.get('base_latency_ms', 12.0)) * (1.0 + io_wait + cpu_usage * 0.5)
    outputs['cpu_usage'] = cpu_usage
    outputs['syscall_latency_ms'] = latency
    outputs['health'] = max(0.0, 1.0 - io_wait - max(0.0, cpu_usage - 1.0))
    """
)


MIDDLEWARE_CODE = COMMON_HELPERS + dedent(
    """\
    queue_depth = _to_int(inputs.get('queue_depth', parameters.get('baseline_queue_depth', 5)))
    max_queue = _to_int(parameters.get('max_queue_depth', 20))
    drop_rate = max(0.0, (queue_depth - max_queue) / max(max_queue, 1))
    outputs['queue_depth'] = queue_depth
    outputs['drop_rate'] = drop_rate
    outputs['health'] = max(0.0, 1.0 - drop_rate * 1.5)
    """
)


APPLICATION_CODE = COMMON_HELPERS + dedent(
    """\
    requests = _to_float(inputs.get('requests_per_second', parameters.get('baseline_rps', 50.0)))
    capacity = _to_float(parameters.get('service_capacity_rps', 120.0))
    load = requests / max(capacity, 1.0)
    outputs['throughput_rps'] = min(requests, capacity)
    outputs['response_time_ms'] = _to_float(parameters.get('base_latency_ms', 20.0)) * (1.0 + load)
    outputs['health'] = max(0.0, 1.0 - max(0.0, load - 1.0))
    """
)


DATABASE_CODE = COMMON_HELPERS + dedent(
    """\
    queries = _to_float(inputs.get('queries_per_second', parameters.get('baseline_qps', 30.0)))
    capacity = _to_float(parameters.get('capacity_qps', 200.0))
    utilisation = queries / max(capacity, 1.0)
    outputs['latency_ms'] = _to_float(parameters.get('base_latency_ms', 15.0)) * (1.0 + utilisation)
    outputs['cache_hit_ratio'] = _to_float(parameters.get('cache_hit_ratio', 0.92))
    outputs['health'] = max(0.0, 1.0 - max(0.0, utilisation - 1.0) * 0.6)
    """
)


ALGORITHM_BASE_CODE = COMMON_HELPERS + dedent(
    """\
    input_quality = _to_float(inputs.get('input_quality', parameters.get('input_quality', 0.85)))
    load_factor = _to_float(inputs.get('load_factor', 0.5))
    state_variables['iterations'] = _to_int(state_variables.get('iterations', 0)) + 1
    outputs['confidence'] = max(0.0, min(1.0, 0.6 * input_quality + 0.4 * _to_float(parameters.get('algorithm_quality', 0.9))))
    outputs['latency_ms'] = _to_float(parameters.get('base_latency_ms', 25.0)) * (1.0 + load_factor)
    outputs['health'] = max(0.0, 1.0 - load_factor * 0.4)
    """
)


CONTROL_ALGORITHM_CODE = ALGORITHM_BASE_CODE + dedent(
    """\
    setpoint = _to_float(inputs.get('setpoint', parameters.get('default_setpoint', 0.0)))
    measurement = _to_float(inputs.get('measurement', setpoint))
    kp = _to_float(parameters.get('kp', 1.2))
    ki = _to_float(parameters.get('ki', 0.05))
    kd = _to_float(parameters.get('kd', 0.01))

    state_variables['integral'] = state_variables.get('integral', 0.0) + (setpoint - measurement) * ki
    derivative = (setpoint - measurement) - state_variables.get('previous_error', 0.0)
    control = kp * (setpoint - measurement) + state_variables['integral'] + kd * derivative
    state_variables['previous_error'] = setpoint - measurement
    outputs['control_command'] = control
    outputs['tracking_error'] = setpoint - measurement
    """
)


PERCEPTION_ALGORITHM_CODE = ALGORITHM_BASE_CODE + dedent(
    """\
    features = _to_int(inputs.get('features_tracked', parameters.get('features_tracked', 120)))
    outputs['perception_score'] = max(0.0, min(1.0, features / max(_to_float(parameters.get('max_features', 200)), 1.0)))
    outputs['data_freshness_ms'] = _to_float(parameters.get('base_latency_ms', 35.0))
    """
)


DECISION_ALGORITHM_CODE = ALGORITHM_BASE_CODE + dedent(
    """\
    alternatives = _to_int(inputs.get('alternatives', parameters.get('alternatives', 5)))
    outputs['decision_quality'] = max(0.0, min(1.0, outputs['confidence'] * (1.0 - 0.02 * alternatives)))
    outputs['selected_option'] = int(alternatives > 0)
    """
)


LEARNING_ALGORITHM_CODE = ALGORITHM_BASE_CODE + dedent(
    """\
    learning_rate = _to_float(parameters.get('learning_rate', 0.001))
    loss = _to_float(inputs.get('loss', parameters.get('baseline_loss', 0.15)))
    state_variables['loss_history'] = state_variables.get('loss_history', [])
    history = state_variables['loss_history']
    history.append(loss)
    if len(history) > 50:
        del history[0]
    outputs['updated_loss'] = loss * (1.0 - learning_rate)
    outputs['convergence'] = max(0.0, 1.0 - outputs['updated_loss'])
    """
)


def _register(definition: ModuleTemplateDefinition) -> None:
    MODULE_TEMPLATE_LIBRARY[definition.template] = definition


def initialise_module_templates() -> None:
    """Populate the module template registry."""
    if MODULE_TEMPLATE_LIBRARY:
        return

    initialise_interface_templates()

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.SENSOR,
            display_name="传感器模块",
            description="典型的物理传感器建模模板，提供连续量测与健康评估。",
            module_cls=HardwareModule,
            module_type=ModuleType.HARDWARE,
            python_code=SENSOR_CODE,
            parameters={
                "baseline": 1.0,
                "sensitivity": 0.95,
                "drift_rate": 0.0002,
                "stress_gain": 0.05,
                "stress_penalty": 0.02,
                "update_rate_hz": 100.0,
                "noise_floor": 0.01,
            },
            state_variables={"drift": 0.0},
            interface_keys=["sensor_power_input", "sensor_data_output"],
            failure_rate=2.5e-5,
        )
    )

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.ACTUATOR,
            display_name="执行器模块",
            description="执行命令并反馈运行状态的致动器模型。",
            module_cls=HardwareModule,
            module_type=ModuleType.HARDWARE,
            python_code=ACTUATOR_CODE,
            parameters={
                "gain": 1.0,
                "command_min": -1.0,
                "command_max": 1.0,
                "error_penalty": 0.02,
            },
            interface_keys=["actuator_command_input", "actuator_feedback_output"],
            failure_rate=1.3e-5,
        )
    )

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.PROCESSOR,
            display_name="处理器模块",
            description="处理负载、功耗与热裕度的处理器模板。",
            module_cls=HardwareModule,
            module_type=ModuleType.HARDWARE,
            python_code=PROCESSOR_CODE,
            parameters={
                "cpu_cores": 4,
                "clock_rate_ghz": 2.4,
                "ipc": 4.0,
                "thermal_sensitivity": 0.4,
                "baseline_load": 0.35,
            },
            interface_keys=["general_input_interface", "general_output_interface"],
            failure_rate=1.0e-4,
        )
    )

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.MEMORY,
            display_name="存储器模块",
            description="建模存储资源使用与可用容量。",
            module_cls=HardwareModule,
            module_type=ModuleType.HARDWARE,
            python_code=MEMORY_CODE,
            parameters={
                "capacity_gb": 16.0,
                "baseline_used_gb": 4.0,
            },
            interface_keys=["general_input_interface", "general_output_interface"],
            failure_rate=8.0e-6,
        )
    )

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.COMMUNICATION,
            display_name="通信模块",
            description="建模链路带宽、时延与健康度的通信单元。",
            module_cls=HardwareModule,
            module_type=ModuleType.HARDWARE,
            python_code=COMMUNICATION_CODE,
            parameters={
                "bandwidth_mbps": 100.0,
                "baseline_traffic_mbps": 10.0,
                "base_latency_ms": 5.0,
            },
            interface_keys=["general_input_interface", "general_output_interface"],
            failure_rate=1.6e-5,
        )
    )

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.OPERATING_SYSTEM,
            display_name="操作系统模块",
            description="仿真调度、系统调用时延与资源使用状况。",
            module_cls=SoftwareModule,
            module_type=ModuleType.SOFTWARE,
            python_code=OPERATING_SYSTEM_CODE,
            parameters={
                "scheduler_capacity": 32,
                "baseline_tasks": 12,
                "base_latency_ms": 12.0,
                "io_wait_fraction": 0.1,
            },
            interface_keys=["general_input_interface", "general_output_interface"],
            failure_rate=9.0e-5,
        )
    )

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.MIDDLEWARE,
            display_name="中间件模块",
            description="聚焦消息队列与缓冲策略的中间件模板。",
            module_cls=SoftwareModule,
            module_type=ModuleType.SOFTWARE,
            python_code=MIDDLEWARE_CODE,
            parameters={
                "max_queue_depth": 20,
                "baseline_queue_depth": 5,
            },
            interface_keys=["general_input_interface", "general_output_interface"],
            failure_rate=7.5e-5,
        )
    )

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.APPLICATION,
            display_name="应用程序模块",
            description="面向任务服务的应用组件模板。",
            module_cls=SoftwareModule,
            module_type=ModuleType.SOFTWARE,
            python_code=APPLICATION_CODE,
            parameters={
                "service_capacity_rps": 120.0,
                "baseline_rps": 50.0,
                "base_latency_ms": 20.0,
            },
            interface_keys=["general_input_interface", "general_output_interface"],
            failure_rate=1.1e-4,
        )
    )

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.DATABASE,
            display_name="数据库模块",
            description="以查询吞吐与缓存命中率为核心的数据库模板。",
            module_cls=SoftwareModule,
            module_type=ModuleType.SOFTWARE,
            python_code=DATABASE_CODE,
            parameters={
                "capacity_qps": 200.0,
                "baseline_qps": 30.0,
                "cache_hit_ratio": 0.92,
                "base_latency_ms": 15.0,
            },
            interface_keys=["general_input_interface", "general_output_interface"],
            failure_rate=8.0e-5,
        )
    )

    algorithm_base = ModuleTemplateDefinition(
        template=ModuleTemplate.ALGORITHM,
        display_name="算法模块",
        description="通用算法建模模板，输出置信度与时延指标。",
        module_cls=AlgorithmModule,
        module_type=ModuleType.ALGORITHM,
        python_code=ALGORITHM_BASE_CODE,
        parameters={
            "algorithm_quality": 0.9,
            "base_latency_ms": 25.0,
        },
        interface_keys=["general_input_interface", "general_output_interface"],
        failure_rate=6.5e-5,
    )
    _register(algorithm_base)

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.CONTROL_ALGORITHM,
            display_name="控制算法模块",
            description="具备PID控制回路计算能力的控制算法模板。",
            module_cls=AlgorithmModule,
            module_type=ModuleType.ALGORITHM,
            python_code=CONTROL_ALGORITHM_CODE,
            parameters={
                "kp": 1.2,
                "ki": 0.05,
                "kd": 0.01,
                "default_setpoint": 0.0,
                "base_latency_ms": 18.0,
            },
            interface_keys=["general_input_interface", "general_output_interface"],
            failure_rate=7.5e-5,
        )
    )

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.PERCEPTION_ALGORITHM,
            display_name="感知算法模块",
            description="融合多源传感信息的感知算法模板。",
            module_cls=AlgorithmModule,
            module_type=ModuleType.ALGORITHM,
            python_code=PERCEPTION_ALGORITHM_CODE,
            parameters={
                "max_features": 200,
                "features_tracked": 120,
                "base_latency_ms": 35.0,
            },
            interface_keys=["general_input_interface", "general_output_interface"],
            failure_rate=8.0e-5,
        )
    )

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.DECISION_ALGORITHM,
            display_name="决策算法模块",
            description="基于多方案评估的智能决策模板。",
            module_cls=AlgorithmModule,
            module_type=ModuleType.ALGORITHM,
            python_code=DECISION_ALGORITHM_CODE,
            parameters={
                "alternatives": 5,
                "base_latency_ms": 40.0,
            },
            interface_keys=["general_input_interface", "general_output_interface"],
            failure_rate=8.5e-5,
        )
    )

    _register(
        ModuleTemplateDefinition(
            template=ModuleTemplate.LEARNING_ALGORITHM,
            display_name="学习算法模块",
            description="包含在线更新能力的学习算法模板。",
            module_cls=AlgorithmModule,
            module_type=ModuleType.ALGORITHM,
            python_code=LEARNING_ALGORITHM_CODE,
            parameters={
                "learning_rate": 0.001,
                "baseline_loss": 0.15,
                "base_latency_ms": 60.0,
            },
            interface_keys=["general_input_interface", "general_output_interface"],
            failure_rate=9.0e-5,
        )
    )


def create_module_from_template(template: ModuleTemplate, *, name: Optional[str] = None, description: Optional[str] = None) -> Module:
    """Create a fully configured module based on the given template."""
    initialise_module_templates()

    if template not in MODULE_TEMPLATE_LIBRARY:
        raise KeyError(f"模板 {template} 未在模板库中注册")

    definition = MODULE_TEMPLATE_LIBRARY[template]
    module = definition.module_cls(
        name or definition.display_name,
        description or definition.description,
    )
    module.module_type = definition.module_type
    module.template = template
    module.icon_path = definition.icon_path
    module.size = Point(definition.size.x, definition.size.y)
    module.parameters.update(definition.parameters)
    module.state_variables.update(definition.state_variables)
    module.python_code = definition.python_code
    module.failure_rate = definition.failure_rate

    for key in definition.interface_keys:
        interface_def = get_interface_template(key)
        interface = build_interface_from_template(interface_def)
        if interface.direction == InterfaceDirection.INPUT:
            interface.target_module_id = module.id
        elif interface.direction == InterfaceDirection.OUTPUT:
            interface.source_module_id = module.id
        else:
            interface.source_module_id = module.id
            interface.target_module_id = module.id
        module.add_interface(interface)

    return module


def list_module_templates() -> Dict[ModuleTemplate, ModuleTemplateDefinition]:
    initialise_module_templates()
    return dict(MODULE_TEMPLATE_LIBRARY)
