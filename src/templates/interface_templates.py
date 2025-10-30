"""
Interface template library.

Provides reusable interface definitions with pre-populated behaviour
scripts, default state machines, and representative failure modes so
that modules created from templates include immediately executable
models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from textwrap import dedent
from typing import Any, Dict, List, Optional

from ..models.interface_model import (
    FailureMode,
    HardwareInterfaceSubtype,
    Interface,
    InterfaceDirection,
    InterfaceFailureMode,
    InterfaceState,
    InterfaceStateType,
    InterfaceType,
    TriggerCondition,
)


@dataclass(frozen=True)
class TriggerSpec:
    """Declarative description of a trigger condition."""

    name: str
    condition_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    python_code: str = ""


@dataclass(frozen=True)
class FailureModeSpec:
    """Declarative description of an interface failure mode."""

    failure_mode: FailureMode
    name: str
    description: str
    severity: int = 5
    failure_rate: float = 1e-5
    detection_rate: float = 0.5
    occurrence_rate: float = 0.0
    triggers: List[TriggerSpec] = field(default_factory=list)
    state_outputs: Dict[str, Any] = field(default_factory=dict)
    python_code: str = ""


@dataclass(frozen=True)
class InterfaceTemplateDefinition:
    """Structured template metadata for generating Interface instances."""

    key: str
    name: str
    category: str
    description: str
    direction: InterfaceDirection
    interface_type: InterfaceType
    data_format: str = "data"
    subtype: Optional[HardwareInterfaceSubtype] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    python_code: str = ""
    normal_state_outputs: Dict[str, Any] = field(default_factory=dict)
    failure_modes: List[FailureModeSpec] = field(default_factory=list)
    latency: float = 5.0
    bandwidth: float = 0.0


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _apply_failure_modes(interface: Interface, definition: InterfaceTemplateDefinition) -> None:
    for fm_spec in definition.failure_modes:
        failure = InterfaceFailureMode(fm_spec.failure_mode, fm_spec.name)
        failure.description = fm_spec.description
        failure.severity = fm_spec.severity
        failure.failure_rate = fm_spec.failure_rate
        if fm_spec.occurrence_rate:
            failure.occurrence_rate = fm_spec.occurrence_rate
        failure.detection_rate = fm_spec.detection_rate
        failure.python_code = fm_spec.python_code

        for trig in fm_spec.triggers:
            condition = TriggerCondition(trig.name, trig.condition_type)
            condition.parameters = dict(trig.parameters)
            condition.python_code = trig.python_code

            # Preserve backwards compatibility for direct probability usage.
            if trig.condition_type == "probability":
                if "probability" in trig.parameters:
                    condition.probability = _coerce_float(trig.parameters["probability"], 0.0)
                elif "p" in trig.parameters:
                    condition.probability = _coerce_float(trig.parameters["p"], 0.0)
            failure.add_trigger_condition(condition)

        interface.add_failure_mode(failure)

        # Update associated failure state outputs when provided.
        if fm_spec.state_outputs:
            state_id = failure.associated_state_id or interface.failure_state_map.get(failure.name)
            if state_id and state_id in interface.states:
                failure_state = interface.states[state_id]
                failure_state.outputs.update(fm_spec.state_outputs)


def build_interface_from_template(definition: InterfaceTemplateDefinition) -> Interface:
    """Instantiate a concrete Interface from a template definition."""

    interface = Interface(
        definition.name,
        definition.description,
        definition.interface_type,
        definition.direction,
    )
    interface.data_format = definition.data_format
    interface.subtype = definition.subtype
    interface.latency = definition.latency
    interface.bandwidth = definition.bandwidth
    interface.parameters = dict(definition.parameters)
    interface.python_code = definition.python_code or dedent(
        """\
        # 默认接口行为模板
        outputs.setdefault('link_status', state_outputs.get('link_status', 'normal'))
        outputs.setdefault('latency_ms', parameters.get('latency_ms', 5.0))
        outputs.setdefault('payload', inputs)
        """
    )

    # Annotate the instance to ease UI inspection.
    interface.category = definition.category  # type: ignore[attr-defined]
    interface.template_key = definition.key  # type: ignore[attr-defined]

    # Populate the nominal state with template outputs.
    if definition.normal_state_outputs:
        normal_state = interface.get_state(interface.normal_state_id)
        normal_state.outputs.update(definition.normal_state_outputs)

    _apply_failure_modes(interface, definition)
    interface.reset_runtime_state()
    return interface


def _base_interface_code(payload_key: str, health_key: str = "quality") -> str:
    """Generate a deterministic interface behaviour snippet."""
    return dedent(
        f"""\
        # 自动生成的接口行为代码
        def _safe_float(value, default=0.0):
            try:
                return float(value)
            except Exception:
                return default

        outputs.setdefault('{payload_key}', inputs)
        health = _safe_float(inputs.get('{health_key}', parameters.get('{health_key}', 1.0)), 1.0)
        outputs['health_score'] = max(0.0, min(1.0, health))
        outputs['link_status'] = 'normal' if health >= 0.7 else ('degraded' if health >= 0.4 else 'failed')
        outputs['latency_ms'] = parameters.get('latency_ms', 5.0)
        """
    )


# ---------------------------------------------------------------------------
# Template catalog
# ---------------------------------------------------------------------------

INTERFACE_TEMPLATE_LIBRARY: Dict[str, InterfaceTemplateDefinition] = {}


def _register_template(definition: InterfaceTemplateDefinition) -> None:
    INTERFACE_TEMPLATE_LIBRARY[definition.key] = definition


def _sensor_templates() -> None:
    normal_outputs = {"link_status": "normal", "data_valid": True}

    sensor_output = InterfaceTemplateDefinition(
        key="sensor_data_output",
        name="传感器数据输出",
        category="算法-硬件设备接口",
        description="将传感器原始量测发布给上游算法或控制器。",
        direction=InterfaceDirection.OUTPUT,
        interface_type=InterfaceType.ALGORITHM_HARDWARE,
        data_format="data",
        subtype=HardwareInterfaceSubtype.SENSOR,
        parameters={
            "latency_ms": 8.0,
            "update_rate_hz": 100.0,
        },
        python_code=_base_interface_code("payload", "health"),
        normal_state_outputs=normal_outputs,
        failure_modes=[
            FailureModeSpec(
                failure_mode=FailureMode.DATA_CORRUPTION,
                name="传感器数据损坏",
                description="环境应力或链路噪声导致传感器样本失真。",
                severity=7,
                failure_rate=2.5e-5,
                detection_rate=0.5,
                triggers=[
                    TriggerSpec(
                        name="健康度低",
                        condition_type="threshold",
                        parameters={"variable": "health", "operator": "<", "value": 0.6},
                    ),
                    TriggerSpec(
                        name="随机扰动",
                        condition_type="probability",
                        parameters={"lambda_per_hour": 2e-5, "dt": 1.0},
                    ),
                ],
                state_outputs={"link_status": "degraded", "data_valid": False},
            ),
            FailureModeSpec(
                failure_mode=FailureMode.TIMEOUT,
                name="传感器超时",
                description="采样或总线拥塞导致数据长时间未更新。",
                severity=6,
                failure_rate=1.5e-5,
                detection_rate=0.6,
                triggers=[
                    TriggerSpec(
                        name="刷新率过低",
                        condition_type="threshold",
                        parameters={"variable": "update_rate_hz", "operator": "<", "value": 5.0},
                    ),
                ],
                state_outputs={"link_status": "timeout", "data_valid": False},
            ),
        ],
    )

    sensor_input = InterfaceTemplateDefinition(
        key="sensor_power_input",
        name="传感器数据输入",
        category="算法-硬件设备接口",
        description="为传感器提供外部校准或环境基准。",
        direction=InterfaceDirection.INPUT,
        interface_type=InterfaceType.ALGORITHM_HARDWARE,
        data_format="signal",
        subtype=HardwareInterfaceSubtype.SENSOR,
        parameters={
            "latency_ms": 2.0,
            "expected_variables": ["environment"],
        },
        python_code=dedent(
            """\
            # 传感器辅助输入，维护传感器健康评估
            environment = inputs.get('environment', {})
            outputs['environment_snapshot'] = environment
            outputs['link_status'] = 'normal'
            """
        ),
        normal_state_outputs={"link_status": "normal"},
        failure_modes=[
            FailureModeSpec(
                failure_mode=FailureMode.COMMUNICATION_FAILURE,
                name="输入信号中断",
                description="校准/供电信号中断，导致传感器健康度下降。",
                severity=6,
                failure_rate=1.0e-5,
                detection_rate=0.4,
                triggers=[
                    TriggerSpec(
                        name="环境信号缺失",
                        condition_type="threshold",
                        parameters={"variable": "signal_strength", "operator": "<", "value": 0.1},
                    )
                ],
                state_outputs={"link_status": "failed"},
            )
        ],
    )

    _register_template(sensor_input)
    _register_template(sensor_output)


def _actuator_templates() -> None:
    actuator_input = InterfaceTemplateDefinition(
        key="actuator_command_input",
        name="控制信号输入",
        category="算法-硬件设备接口",
        description="接收来自控制算法的指令并在执行前做边界检查。",
        direction=InterfaceDirection.INPUT,
        interface_type=InterfaceType.ALGORITHM_HARDWARE,
        data_format="control",
        subtype=HardwareInterfaceSubtype.ACTUATOR,
        parameters={
            "latency_ms": 4.0,
            "command_min": -1.0,
            "command_max": 1.0,
        },
        python_code=dedent(
            """\
            # 控制指令接收与约束
            cmd = inputs.get('command', 0.0)

            def _to_float(val, fallback=0.0):
                try:
                    return float(val)
                except Exception:
                    return fallback

            cmin = _to_float(parameters.get('command_min', -1.0), -1.0)
            cmax = _to_float(parameters.get('command_max', 1.0), 1.0)
            value = max(cmin, min(cmax, _to_float(cmd, 0.0)))
            outputs['bounded_command'] = value
            outputs['saturated'] = value == cmin or value == cmax
            outputs['link_status'] = 'normal' if not outputs['saturated'] else 'saturated'
            """
        ),
        normal_state_outputs={"link_status": "normal"},
        failure_modes=[
            FailureModeSpec(
                failure_mode=FailureMode.RESOURCE_EXHAUSTION,
                name="执行器命令队列溢出",
                description="持续高频命令导致缓冲区耗尽。",
                severity=7,
                failure_rate=1.2e-5,
                detection_rate=0.5,
                triggers=[
                    TriggerSpec(
                        name="频率过高",
                        condition_type="threshold",
                        parameters={"variable": "command_rate_hz", "operator": ">", "value": 150.0},
                    )
                ],
                state_outputs={"link_status": "backlogged"},
            )
        ],
    )

    actuator_output = InterfaceTemplateDefinition(
        key="actuator_feedback_output",
        name="状态反馈输出",
        category="算法-硬件设备接口",
        description="反馈执行器的当前状态、闭环误差与健康信息。",
        direction=InterfaceDirection.OUTPUT,
        interface_type=InterfaceType.ALGORITHM_HARDWARE,
        data_format="signal",
        subtype=HardwareInterfaceSubtype.ACTUATOR,
        parameters={"latency_ms": 6.0},
        python_code=_base_interface_code("feedback", "health"),
        normal_state_outputs={"link_status": "normal"},
        failure_modes=[
            FailureModeSpec(
                failure_mode=FailureMode.TIMEOUT,
                name="反馈超时",
                description="执行器长时间未上报状态。",
                severity=8,
                failure_rate=1.6e-5,
                detection_rate=0.6,
                triggers=[
                    TriggerSpec(
                        name="反馈间隔过长",
                        condition_type="threshold",
                        parameters={"variable": "feedback_age", "operator": ">", "value": 0.5},
                    )
                ],
                state_outputs={"link_status": "timeout"},
            ),
            FailureModeSpec(
                failure_mode=FailureMode.DATA_CORRUPTION,
                name="反馈数据异常",
                description="反馈信号噪声或传输损坏。",
                severity=6,
                failure_rate=9.0e-6,
                detection_rate=0.5,
                triggers=[
                    TriggerSpec(
                        name="健康度低",
                        condition_type="threshold",
                        parameters={"variable": "health", "operator": "<", "value": 0.5},
                    )
                ],
                state_outputs={"link_status": "degraded"},
            ),
        ],
    )

    _register_template(actuator_input)
    _register_template(actuator_output)


def _generic_io_templates() -> None:
    categories = [
        ("通用输入", "general_input_interface", InterfaceDirection.INPUT),
        ("通用输出", "general_output_interface", InterfaceDirection.OUTPUT),
    ]

    for name, key, direction in categories:
        definition = InterfaceTemplateDefinition(
            key=key,
            name=name,
            category="一般接口",
            description="在模块之间传递结构化数据的通用接口。",
            direction=direction,
            interface_type=InterfaceType.SOFTWARE_HARDWARE,
            data_format="data",
            parameters={
                "latency_ms": 5.0,
                "schema": "generic",
            },
            python_code=_base_interface_code("payload"),
            normal_state_outputs={"link_status": "normal"},
            failure_modes=[
                FailureModeSpec(
                    failure_mode=FailureMode.COMMUNICATION_FAILURE,
                    name="通信中断",
                    description="链路失效或协议错误导致数据无法传输。",
                    severity=6,
                    failure_rate=1.0e-5,
                    detection_rate=0.4,
                    triggers=[
                        TriggerSpec(
                            name="随机中断",
                            condition_type="probability",
                            parameters={"lambda_per_hour": 8e-6, "dt": 1.0},
                        )
                    ],
                    state_outputs={"link_status": "failed"},
                ),
                FailureModeSpec(
                    failure_mode=FailureMode.CONFIGURATION_ERROR,
                    name="配置错误",
                    description="接口配置与对端不一致导致数据丢弃。",
                    severity=5,
                    failure_rate=7.5e-6,
                    detection_rate=0.6,
                    triggers=[
                        TriggerSpec(
                            name="配置变更",
                            condition_type="event",
                            parameters={"event": "configuration_changed"},
                        )
                    ],
                    state_outputs={"link_status": "degraded"},
                ),
            ],
        )
        _register_template(definition)


def _default_failure_modes(category: str) -> List[FailureModeSpec]:
    """Generate a common pair of failure modes for higher-level templates."""
    return [
        FailureModeSpec(
            failure_mode=FailureMode.COMMUNICATION_FAILURE,
            name=f"{category}通信异常",
            description=f"{category}链路暂时不可用或会话被重置。",
            severity=6,
            failure_rate=1.0e-5,
            detection_rate=0.5,
            triggers=[
                TriggerSpec(
                    name="链路抖动",
                    condition_type="probability",
                    parameters={"lambda_per_hour": 6e-6, "dt": 1.0},
                )
            ],
            state_outputs={"link_status": "failed"},
        ),
        FailureModeSpec(
            failure_mode=FailureMode.TIMEOUT,
            name=f"{category}处理超时",
            description=f"{category}在规定时间内未完成任务。",
            severity=5,
            failure_rate=8.0e-6,
            detection_rate=0.6,
            triggers=[
                TriggerSpec(
                    name="队列过长",
                    condition_type="threshold",
                    parameters={"variable": "queue_length", "operator": ">", "value": 128},
                )
            ],
            state_outputs={"link_status": "timeout"},
        ),
    ]


def _slugify(name: str) -> str:
    return "".join(ch for ch in name if ch.isascii() and ch.isalnum()).lower()


def _category_templates() -> None:
    mappings = {
        "算法-操作系统接口": (
            InterfaceType.ALGORITHM_OS,
            [
                ("进程调度接口", "负责任务优先级与调度周期协调。"),
                ("内存管理接口", "提供页表与内存池访问能力。"),
                ("文件系统接口", "面向算法组件的持久化访问能力。"),
                ("网络接口", "与操作系统网络栈交换数据的接口。"),
                ("设备驱动接口", "暴露底层驱动能力的抽象接口。"),
            ],
        ),
        "算法-智能框架接口": (
            InterfaceType.ALGORITHM_FRAMEWORK,
            [
                ("模型加载接口", "负责模型权重与配置的加载。"),
                ("推理执行接口", "对深度学习推理服务进行调用。"),
                ("数据预处理接口", "对输入数据进行归一化与裁剪。"),
                ("后处理接口", "对推理结果做多目标融合处理。"),
                ("GPU加速接口", "管理GPU算力资源与kernel调用。"),
            ],
        ),
        "算法-应用接口": (
            InterfaceType.ALGORITHM_APPLICATION,
            [
                ("API调用接口", "向上层应用暴露的服务调用接口。"),
                ("数据交换接口", "负责算法与应用间的数据交换。"),
                ("配置管理接口", "实现运行期参数配置下发。"),
                ("状态监控接口", "向应用提供算法状态诊断。"),
                ("事件通知接口", "算法异常事件的通知通道。"),
            ],
        ),
        "算法-数据平台接口": (
            InterfaceType.ALGORITHM_DATA_PLATFORM,
            [
                ("数据读取接口", "从数据平台拉取训练/验证数据。"),
                ("数据写入接口", "向数据平台写入处理结果。"),
                ("数据查询接口", "面向指标与元数据的查询接口。"),
                ("数据同步接口", "在多节点之间同步数据。"),
                ("缓存接口", "访问高速缓存或流式数据。"),
            ],
        ),
        "算法-硬件设备接口": (
            InterfaceType.ALGORITHM_HARDWARE,
            [
                ("传感器接口", "与外设传感器的抽象交互接口。"),
                ("执行器接口", "统一控制执行器的命令通道。"),
                ("专用计算硬件接口", "与FPGA/ASIC的计算资源交互。"),
                ("通信硬件接口", "与通信基带或射频模块交互。"),
                ("存储硬件接口", "高可靠存储硬件的读写接口。"),
            ],
        ),
        "一般接口": (
            InterfaceType.SOFTWARE_HARDWARE,
            [
                ("软件-硬件接口", "传统软硬件交互的通用接口。"),
                ("软件-软件接口", "不同软件子系统之间的接口。"),
                ("硬件-硬件接口", "硬件组件之间的桥接接口。"),
                ("用户接口", "供运维或用户交互的数据接口。"),
                ("网络接口", "通用的网络交换接口。"),
            ],
        ),
    }

    for category, (iface_type, entries) in mappings.items():
        for name, description in entries:
            key = f"{_slugify(category)}_{_slugify(name)}"
            definition = InterfaceTemplateDefinition(
                key=key,
                name=name,
                category=category,
                description=f"{name}：{description}",
                direction=InterfaceDirection.BIDIRECTIONAL,
                interface_type=iface_type,
                data_format="data",
                parameters={},
                python_code=_base_interface_code("payload"),
                normal_state_outputs={"link_status": "normal"},
                failure_modes=_default_failure_modes(category),
            )
            _register_template(definition)


def initialise_interface_templates() -> None:
    """Populate the global template registry if it is empty."""
    if INTERFACE_TEMPLATE_LIBRARY:
        return

    _sensor_templates()
    _actuator_templates()
    _generic_io_templates()
    _category_templates()


def get_interface_template(key: str) -> InterfaceTemplateDefinition:
    initialise_interface_templates()
    return INTERFACE_TEMPLATE_LIBRARY[key]


def list_interface_templates() -> Dict[str, InterfaceTemplateDefinition]:
    initialise_interface_templates()
    return dict(INTERFACE_TEMPLATE_LIBRARY)


def get_interface_templates_by_category() -> Dict[str, List[InterfaceTemplateDefinition]]:
    initialise_interface_templates()
    categories: Dict[str, List[InterfaceTemplateDefinition]] = {}
    for definition in INTERFACE_TEMPLATE_LIBRARY.values():
        categories.setdefault(definition.category, []).append(definition)
    # Stable ordering by template name for UI predictability.
    for defs in categories.values():
        defs.sort(key=lambda item: item.name)
    return categories
