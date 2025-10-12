# -*- coding: utf-8 -*-
"""
接口数据模型
Interface Data Model

定义各种接口类型和失效模式的数据结构
"""

from datetime import datetime
import copy
import random
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid

STATE_HISTORY_LIMIT = 200
try:
    from .base_model import BaseModel
except ImportError:
    from base_model import BaseModel


class InterfaceType(Enum):
    """接口类型枚举"""
    ALGORITHM_OS = "algorithm_os"  # 算法-操作系统接口
    ALGORITHM_FRAMEWORK = "algorithm_framework"  # 算法-智能框架接口
    ALGORITHM_APPLICATION = "algorithm_application"  # 算法-应用接口
    ALGORITHM_DATA_PLATFORM = "algorithm_data_platform"  # 算法-数据平台接口
    ALGORITHM_HARDWARE = "algorithm_hardware"  # 算法-硬件设备接口
    SOFTWARE_HARDWARE = "software_hardware"  # 软件-硬件接口
    HARDWARE_HARDWARE = "hardware_hardware"  # 硬件-硬件接口
    SOFTWARE_SOFTWARE = "software_software"  # 软件-软件接口


class HardwareInterfaceSubtype(Enum):
    """硬件接口子类型"""
    SENSOR = "sensor"  # 传感器接口
    ACTUATOR = "actuator"  # 执行器接口
    COMPUTING_HARDWARE = "computing_hardware"  # 专用计算硬件接口


class FailureMode(Enum):
    """失效模式枚举"""
    COMMUNICATION_FAILURE = "communication_failure"  # 通信失效
    DATA_CORRUPTION = "data_corruption"  # 数据损坏
    TIMEOUT = "timeout"  # 超时
    PROTOCOL_MISMATCH = "protocol_mismatch"  # 协议不匹配
    RESOURCE_EXHAUSTION = "resource_exhaustion"  # 资源耗尽
    AUTHENTICATION_FAILURE = "authentication_failure"  # 认证失败
    PERMISSION_DENIED = "permission_denied"  # 权限拒绝
    VERSION_INCOMPATIBILITY = "version_incompatibility"  # 版本不兼容
    HARDWARE_FAULT = "hardware_fault"  # 硬件故障
    SOFTWARE_BUG = "software_bug"  # 软件缺陷
    CONFIGURATION_ERROR = "configuration_error"  # 配置错误
    ENVIRONMENTAL_STRESS = "environmental_stress"  # 环境应力


class TriggerCondition:
    """触发条件"""

    def __init__(self, name: str = "", condition_type: str = "threshold"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.condition_type = condition_type  # threshold, event, time, probability
        self.parameters: Dict[str, Any] = {}  # 条件参数
        self.python_code = ""  # Python条件判断代码
        self.probability = 0.0  # 触发概率
        self.enabled = True

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估触发条件是否满足"""
        if not self.enabled:
            return False

        # 优先执行自定义Python代码
        if self.python_code:
            try:
                local_vars = {
                    'context': context,
                    'parameters': self.parameters,
                    'result': False
                }
                exec(self.python_code, {}, local_vars)
                return bool(local_vars.get('result', False))
            except Exception as e:
                print(f"评估触发条件 {self.name} 时出错: {e}")
                return False

        condition_type = self.condition_type.lower()
        inputs = context.get('inputs', {})
        state_variables = context.get('state_variables', {})
        environment = context.get('environment', {})

        # 简单阈值判断
        if condition_type == 'threshold':
            variable = self.parameters.get('variable')
            operator = self.parameters.get('operator', '>=')
            threshold = self.parameters.get('value')

            if variable is None or threshold is None:
                return False

            actual_value = inputs.get(variable)
            if actual_value is None:
                actual_value = state_variables.get(variable)
            if actual_value is None:
                actual_value = environment.get(variable)

            if actual_value is None:
                return False

            try:
                if operator == '>=':
                    return actual_value >= threshold
                if operator == '>':
                    return actual_value > threshold
                if operator == '<=':
                    return actual_value <= threshold
                if operator == '<':
                    return actual_value < threshold
                if operator == '==':
                    return actual_value == threshold
                if operator == '!=':
                    return actual_value != threshold
            except Exception as exc:
                print(f"阈值条件计算失败: {exc}")
                return False

        # 事件触发：根据上下文的事件集合判断
        elif condition_type == 'event':
            event_name = self.parameters.get('event')
            events = context.get('events', set())
            return event_name in events if event_name else False

        # 时间触发：比较当前时间或任务阶段时间
        elif condition_type == 'time':
            current_time = context.get('time', 0.0)
            trigger_time = self.parameters.get('time', None)
            if trigger_time is None:
                return False
            comparison = self.parameters.get('comparison', '>=')
            if comparison == '>=':
                return current_time >= trigger_time
            if comparison == '>':
                return current_time > trigger_time
            if comparison == '<=':
                return current_time <= trigger_time
            if comparison == '<':
                return current_time < trigger_time
            if comparison == '==':
                return current_time == trigger_time

        # 概率触发：使用设定概率判断
        elif condition_type == 'probability':
            probability = float(self.parameters.get('probability', self.probability))
            if probability <= 0:
                return False
            rng = context.get('random_generator')
            if rng is None:
                rng = random.Random()
            return rng.random() < probability

        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'condition_type': self.condition_type,
            'parameters': self.parameters,
            'python_code': self.python_code,
            'probability': self.probability,
            'enabled': self.enabled
        }

    def from_dict(self, data: Dict[str, Any]):
        self.id = data.get('id', str(uuid.uuid4()))
        self.name = data.get('name', '')
        self.condition_type = data.get('condition_type', 'threshold')
        self.parameters = data.get('parameters', {})
        self.python_code = data.get('python_code', '')
        self.probability = data.get('probability', 0.0)
        self.enabled = data.get('enabled', True)

    def clone(self) -> 'TriggerCondition':
        """克隆触发条件，生成独立实例"""
        new_condition = TriggerCondition(self.name, self.condition_type)
        new_condition.parameters = copy.deepcopy(self.parameters)
        new_condition.python_code = self.python_code
        new_condition.probability = self.probability
        new_condition.enabled = self.enabled
        return new_condition


class InterfaceFailureMode:
    """接口失效模式"""

    def __init__(self, failure_mode: FailureMode, name: str = ""):
        self.failure_mode = failure_mode
        self.name = name or failure_mode.value
        self.description = ""
        self.severity = 1  # 严重程度 1-10
        self.occurrence_rate = 0.0  # 发生率
        self.detection_rate = 0.0  # 检测率
        self.trigger_conditions = []  # 触发条件列表
        self.effects = []  # 失效影响
        self.mitigation_measures = []  # 缓解措施
        self.python_code = ""  # Python建模代码
        self.associated_state_id: Optional[str] = None  # 关联的状态机状态

    def add_trigger_condition(self, condition: TriggerCondition):
        """添加触发条件"""
        self.trigger_conditions.append(condition)

    def remove_trigger_condition(self, condition_name: str):
        """移除触发条件"""
        self.trigger_conditions = [c for c in self.trigger_conditions if c.name != condition_name]
    
    def check_triggers(self, context: Dict[str, Any]) -> bool:
        """检查是否有触发条件满足"""
        for condition in self.trigger_conditions:
            if condition.evaluate(context):
                return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'failure_mode': self.failure_mode.value,
            'name': self.name,
            'description': self.description,
            'severity': self.severity,
            'occurrence_rate': self.occurrence_rate,
            'detection_rate': self.detection_rate,
            'trigger_conditions': [tc.to_dict() for tc in self.trigger_conditions],
            'effects': self.effects,
            'mitigation_measures': self.mitigation_measures,
            'python_code': self.python_code,
            'associated_state_id': self.associated_state_id
        }

    def from_dict(self, data: Dict[str, Any]):
        self.failure_mode = FailureMode(data.get('failure_mode', FailureMode.COMMUNICATION_FAILURE.value))
        self.name = data.get('name', '')
        self.description = data.get('description', '')
        self.severity = data.get('severity', 1)
        self.occurrence_rate = data.get('occurrence_rate', 0.0)
        self.detection_rate = data.get('detection_rate', 0.0)
        
        # 加载触发条件
        self.trigger_conditions = []
        for tc_data in data.get('trigger_conditions', []):
            tc = TriggerCondition()
            tc.from_dict(tc_data)
            self.trigger_conditions.append(tc)
        
        self.effects = data.get('effects', [])
        self.mitigation_measures = data.get('mitigation_measures', [])
        self.python_code = data.get('python_code', '')
        self.associated_state_id = data.get('associated_state_id')

    def clone(self) -> 'InterfaceFailureMode':
        """克隆失效模式，确保触发条件独立"""
        new_failure = InterfaceFailureMode(self.failure_mode, self.name)
        new_failure.description = self.description
        new_failure.severity = self.severity
        new_failure.occurrence_rate = self.occurrence_rate
        new_failure.detection_rate = self.detection_rate
        new_failure.trigger_conditions = [tc.clone() for tc in self.trigger_conditions]
        new_failure.effects = copy.deepcopy(self.effects)
        new_failure.mitigation_measures = copy.deepcopy(self.mitigation_measures)
        new_failure.python_code = self.python_code
        new_failure.associated_state_id = self.associated_state_id
        return new_failure


class InterfaceStateType(Enum):
    """接口状态类型"""
    NORMAL = "normal"
    FAILURE = "failure"


class InterfaceState:
    """接口状态"""

    def __init__(self, name: str = "正常状态", state_type: InterfaceStateType = InterfaceStateType.NORMAL):
        self.id = str(uuid.uuid4())
        self.name = name
        self.state_type = state_type
        self.description = ""
        self.python_code = ""  # 状态下的执行代码
        self.outputs: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    def execute(self, context: Dict[str, Any], interface: 'Interface') -> Dict[str, Any]:
        """执行状态下的代码"""
        base_outputs = copy.deepcopy(self.outputs)

        if self.python_code:
            try:
                local_vars = {
                    'context': context,
                    'interface': interface,
                    'parameters': interface.parameters,
                    'state_outputs': copy.deepcopy(base_outputs),
                    'outputs': copy.deepcopy(base_outputs)
                }
                exec(self.python_code, {}, local_vars)
                return local_vars.get('outputs', base_outputs)
            except Exception as exc:
                print(f"执行接口状态 {self.name} 的Python代码时出错: {exc}")
                return base_outputs

        return base_outputs

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'state_type': self.state_type.value,
            'description': self.description,
            'python_code': self.python_code,
            'outputs': self.outputs,
            'metadata': self.metadata
        }

    def from_dict(self, data: Dict[str, Any]):
        self.id = data.get('id', str(uuid.uuid4()))
        self.name = data.get('name', '正常状态')
        state_type_value = data.get('state_type', InterfaceStateType.NORMAL.value)
        try:
            self.state_type = InterfaceStateType(state_type_value)
        except ValueError:
            self.state_type = InterfaceStateType.NORMAL
        self.description = data.get('description', '')
        self.python_code = data.get('python_code', '')
        self.outputs = data.get('outputs', {})
        self.metadata = data.get('metadata', {})

    def clone(self) -> 'InterfaceState':
        cloned = InterfaceState(self.name, self.state_type)
        cloned.description = self.description
        cloned.python_code = self.python_code
        cloned.outputs = copy.deepcopy(self.outputs)
        cloned.metadata = copy.deepcopy(self.metadata)
        return cloned


class InterfaceTransition:
    """接口状态转换"""

    def __init__(self, source_state_id: str, target_state_id: str,
                 condition: Optional[TriggerCondition] = None, name: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name or f"{source_state_id}->{target_state_id}"
        self.source_state_id = source_state_id
        self.target_state_id = target_state_id
        self.condition = condition or TriggerCondition("默认条件")
        self.priority = 0  # 用于冲突时的选择
        self.is_recovery = False  # 是否为恢复转换
        self.metadata: Dict[str, Any] = {}

    def evaluate(self, context: Dict[str, Any]) -> bool:
        return self.condition.evaluate(context)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'source_state_id': self.source_state_id,
            'target_state_id': self.target_state_id,
            'condition': self.condition.to_dict(),
            'priority': self.priority,
            'is_recovery': self.is_recovery,
            'metadata': self.metadata
        }

    def from_dict(self, data: Dict[str, Any]):
        self.id = data.get('id', str(uuid.uuid4()))
        self.name = data.get('name', '')
        self.source_state_id = data.get('source_state_id', '')
        self.target_state_id = data.get('target_state_id', '')
        self.condition = TriggerCondition()
        self.condition.from_dict(data.get('condition', {}))
        self.priority = data.get('priority', 0)
        self.is_recovery = data.get('is_recovery', False)
        self.metadata = data.get('metadata', {})

    def clone(self) -> 'InterfaceTransition':
        cloned = InterfaceTransition(self.source_state_id, self.target_state_id, self.condition.clone(), self.name)
        cloned.priority = self.priority
        cloned.is_recovery = self.is_recovery
        cloned.metadata = copy.deepcopy(self.metadata)
        return cloned


class InterfaceDirection(Enum):
    """接口方向枚举"""
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"


class Interface(BaseModel):
    """接口基类，支持状态机、失效模式与Python行为建模"""

    def __init__(self, name: str = "", description: str = "",
                 interface_type: InterfaceType = InterfaceType.SOFTWARE_HARDWARE,
                 direction: InterfaceDirection = InterfaceDirection.BIDIRECTIONAL):
        super().__init__(name, description)
        self.interface_type = interface_type
        self.direction = direction
        self.subtype = None  # 子类型（如硬件接口的传感器、执行器等）
        self.source_module_id = ""  # 源模块ID
        self.target_module_id = ""  # 目标模块ID
        self.protocol = ""  # 通信协议
        self.data_format = ""  # 数据格式
        self.bandwidth = 0.0  # 带宽
        self.latency = 0.0  # 延迟
        self.reliability = 0.99  # 可靠性
        self.failure_modes: List[InterfaceFailureMode] = []  # 失效模式列表
        self.python_code = ""  # Python建模代码
        self.parameters: Dict[str, Any] = {}  # 接口参数

        # 状态机相关
        self.state_machine_enabled = True
        self.states: Dict[str, InterfaceState] = {}
        self.transitions: List[InterfaceTransition] = []
        self.normal_state_id: Optional[str] = None
        self.current_state_id: Optional[str] = None
        self.state_history: List[Dict[str, Any]] = []
        self.failure_state_map: Dict[str, str] = {}  # 失效模式名称 -> 状态ID

        self._initialize_default_state()

    # ------------------------------------------------------------------
    # 状态机管理
    # ------------------------------------------------------------------
    def _initialize_default_state(self):
        """创建默认的正常状态"""
        if self.states:
            return

        normal_state = InterfaceState("正常状态", InterfaceStateType.NORMAL)
        normal_state.description = "接口正常工作的默认状态"
        self.add_state(normal_state, make_default=True)
        self.reset_runtime_state()

    def add_state(self, state: InterfaceState, make_default: bool = False) -> str:
        """添加状态并返回状态ID"""
        if state.id in self.states:
            # 生成新的ID避免冲突
            state = state.clone()
            state.id = str(uuid.uuid4())

        self.states[state.id] = state

        if make_default or (state.state_type == InterfaceStateType.NORMAL and not self.normal_state_id):
            self.normal_state_id = state.id

        if not self.current_state_id:
            self.current_state_id = self.normal_state_id or state.id

        self.update_modified_time()
        return state.id

    def remove_state(self, state_id: str):
        """移除状态并清理相关转换"""
        if state_id not in self.states:
            return

        del self.states[state_id]

        # 移除相关转换
        self.transitions = [
            t for t in self.transitions
            if t.source_state_id != state_id and t.target_state_id != state_id
        ]

        # 更新映射
        for failure_name, mapped_state in list(self.failure_state_map.items()):
            if mapped_state == state_id:
                del self.failure_state_map[failure_name]

        if self.normal_state_id == state_id:
            self.normal_state_id = None

        if self.current_state_id == state_id:
            self.reset_runtime_state()

        self.update_modified_time()

    def get_state(self, state_id: str) -> Optional[InterfaceState]:
        return self.states.get(state_id)

    def add_transition(self, transition: InterfaceTransition) -> str:
        """添加状态转换，避免重复"""
        for existing in self.transitions:
            template_id = existing.metadata.get('trigger_condition_template_id')
            if (existing.source_state_id == transition.source_state_id and
                    existing.target_state_id == transition.target_state_id and
                    (template_id and template_id == transition.metadata.get('trigger_condition_template_id'))):
                return existing.id

        self.transitions.append(transition)
        self.update_modified_time()
        return transition.id

    def remove_transition(self, transition_id: str):
        self.transitions = [t for t in self.transitions if t.id != transition_id]
        self.update_modified_time()

    def get_transitions_from_state(self, state_id: str) -> List[InterfaceTransition]:
        return [t for t in self.transitions if t.source_state_id == state_id]

    def _ensure_state_for_failure_mode(self, failure_mode: InterfaceFailureMode) -> str:
        if failure_mode.associated_state_id and failure_mode.associated_state_id in self.states:
            return failure_mode.associated_state_id

        if failure_mode.name in self.failure_state_map:
            mapped_state_id = self.failure_state_map[failure_mode.name]
            if mapped_state_id in self.states:
                failure_mode.associated_state_id = mapped_state_id
                return mapped_state_id

        failure_state = InterfaceState(failure_mode.name, InterfaceStateType.FAILURE)
        failure_state.description = failure_mode.description or f"故障状态: {failure_mode.name}"
        failure_state.metadata['failure_mode'] = failure_mode.failure_mode.value
        state_id = self.add_state(failure_state)
        self.failure_state_map[failure_mode.name] = state_id
        failure_mode.associated_state_id = state_id
        return state_id

    def _ensure_transitions_for_failure_mode(self, failure_mode: InterfaceFailureMode, failure_state_id: str):
        normal_state_id = self.normal_state_id or self.current_state_id
        if not normal_state_id:
            return

        for condition in failure_mode.trigger_conditions:
            existing = False
            for transition in self.transitions:
                template_id = transition.metadata.get('trigger_condition_template_id')
                if (transition.source_state_id == normal_state_id and
                        transition.target_state_id == failure_state_id and
                        template_id == condition.id):
                    existing = True
                    break

            if existing:
                continue

            transition = InterfaceTransition(normal_state_id, failure_state_id, condition.clone(), failure_mode.name)
            transition.metadata['failure_mode'] = failure_mode.name
            transition.metadata['trigger_condition_template_id'] = condition.id
            self.add_transition(transition)

    def _sync_state_machine_with_failure_modes(self):
        for failure_mode in self.failure_modes:
            state_id = self._ensure_state_for_failure_mode(failure_mode)
            self._ensure_transitions_for_failure_mode(failure_mode, state_id)

    def reset_runtime_state(self, to_normal: bool = True):
        """重置状态机运行状态"""
        if to_normal and self.normal_state_id and self.normal_state_id in self.states:
            self.current_state_id = self.normal_state_id
        elif self.states:
            # 任意选择一个状态作为当前状态
            self.current_state_id = next(iter(self.states.keys()))
        else:
            self.current_state_id = None

        self.state_history = []

    def step_state_machine(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行一次状态机评估并返回状态信息"""
        if not self.state_machine_enabled:
            return {
                'state_id': self.current_state_id,
                'state_name': self.get_state(self.current_state_id).name if self.current_state_id in self.states else '',
                'outputs': {},
                'transition': None
            }

        context = context.copy() if context else {}
        context.setdefault('parameters', self.parameters)
        context.setdefault('state_variables', {})
        context.setdefault('environment', {})

        if self.current_state_id not in self.states:
            self.reset_runtime_state()

        current_state = self.get_state(self.current_state_id)
        triggered_transition = None

        # 根据优先级排序（数值越小优先级越高）
        transitions = sorted(self.get_transitions_from_state(self.current_state_id), key=lambda t: t.priority)
        for transition in transitions:
            if transition.evaluate(context):
                triggered_transition = transition
                break

        if triggered_transition:
            previous_state_id = self.current_state_id
            self.current_state_id = triggered_transition.target_state_id
            current_state = self.get_state(self.current_state_id)

            history_record = {
                'from': previous_state_id,
                'to': self.current_state_id,
                'transition_id': triggered_transition.id,
                'timestamp': datetime.now().isoformat()
            }
            if 'failure_mode' in triggered_transition.metadata:
                history_record['failure_mode'] = triggered_transition.metadata['failure_mode']

            self.state_history.append(history_record)
            if len(self.state_history) > STATE_HISTORY_LIMIT:
                self.state_history = self.state_history[-STATE_HISTORY_LIMIT:]

        outputs = current_state.execute(context, self) if current_state else {}

        return {
            'state_id': self.current_state_id,
            'state_name': current_state.name if current_state else '',
            'outputs': outputs,
            'transition': triggered_transition.to_dict() if triggered_transition else None
        }

    # ------------------------------------------------------------------
    # 失效模式与行为建模
    # ------------------------------------------------------------------
    def add_failure_mode(self, failure_mode: InterfaceFailureMode):
        if failure_mode not in self.failure_modes:
            self.failure_modes.append(failure_mode)

        state_id = self._ensure_state_for_failure_mode(failure_mode)
        self._ensure_transitions_for_failure_mode(failure_mode, state_id)
        self.update_modified_time()

    def remove_failure_mode(self, failure_mode_name: str):
        removed_modes = [fm for fm in self.failure_modes if fm.name == failure_mode_name]
        self.failure_modes = [fm for fm in self.failure_modes if fm.name != failure_mode_name]

        for failure_mode in removed_modes:
            state_id = failure_mode.associated_state_id or self.failure_state_map.get(failure_mode.name)
            if state_id:
                self.remove_state(state_id)

        self.update_modified_time()

    def get_failure_mode(self, failure_mode_name: str) -> Optional[InterfaceFailureMode]:
        for fm in self.failure_modes:
            if fm.name == failure_mode_name:
                return fm
        return None

    def get_active_failure_modes(self) -> List[InterfaceFailureMode]:
        active_modes = []
        for failure_mode in self.failure_modes:
            if failure_mode.associated_state_id and failure_mode.associated_state_id == self.current_state_id:
                active_modes.append(failure_mode)
        return active_modes

    def check_failure_conditions(self, context: Dict[str, Any]) -> List[InterfaceFailureMode]:
        triggered_failures = []
        for failure_mode in self.failure_modes:
            if failure_mode.check_triggers(context):
                triggered_failures.append(failure_mode)
        return triggered_failures

    def simulate_interface(self, inputs: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        runtime_context = context.copy() if context else {}
        runtime_context['inputs'] = inputs
        runtime_context.setdefault('parameters', self.parameters)

        state_result = self.step_state_machine(runtime_context)
        outputs = copy.deepcopy(inputs)
        state_outputs = state_result.get('outputs', {}) or {}
        outputs.update(state_outputs)

        if self.python_code:
            local_vars = {
                'inputs': copy.deepcopy(inputs),
                'parameters': self.parameters,
                'state_outputs': state_outputs,
                'context': runtime_context,
                'outputs': copy.deepcopy(outputs),
                'interface': self
            }
            try:
                exec(self.python_code, {}, local_vars)
                outputs = local_vars.get('outputs', outputs)
            except Exception as e:
                print(f"执行接口 {self.name} 的Python代码时出错: {e}")

        return outputs

    def instantiate_from_template(self, name: Optional[str] = None) -> 'Interface':
        """基于当前接口模板创建实例"""
        instance = Interface(name or f"{self.name}_实例", self.description,
                             self.interface_type, self.direction)
        instance.subtype = self.subtype
        instance.protocol = self.protocol
        instance.data_format = self.data_format
        instance.bandwidth = self.bandwidth
        instance.latency = self.latency
        instance.reliability = self.reliability
        instance.python_code = self.python_code
        instance.parameters = copy.deepcopy(self.parameters)

        # 克隆状态
        instance.states = {}
        state_id_map = {}
        for state in self.states.values():
            cloned_state = state.clone()
            old_id = state.id
            cloned_state.id = str(uuid.uuid4())
            instance.states[cloned_state.id] = cloned_state
            state_id_map[old_id] = cloned_state.id

        if self.normal_state_id:
            instance.normal_state_id = state_id_map.get(self.normal_state_id)
        instance.current_state_id = instance.normal_state_id

        # 克隆转换
        instance.transitions = []
        for transition in self.transitions:
            cloned_transition = transition.clone()
            cloned_transition.id = str(uuid.uuid4())
            cloned_transition.source_state_id = state_id_map.get(transition.source_state_id, transition.source_state_id)
            cloned_transition.target_state_id = state_id_map.get(transition.target_state_id, transition.target_state_id)
            cloned_transition.condition = transition.condition.clone()
            template_id = transition.metadata.get('trigger_condition_template_id')
            if template_id:
                cloned_transition.metadata['trigger_condition_template_id'] = template_id
            instance.transitions.append(cloned_transition)

        # 克隆失效模式
        instance.failure_modes = []
        instance.failure_state_map = {}
        for failure_mode in self.failure_modes:
            cloned_failure = failure_mode.clone()
            if failure_mode.associated_state_id:
                cloned_failure.associated_state_id = state_id_map.get(failure_mode.associated_state_id)
            instance.failure_modes.append(cloned_failure)
            if failure_mode.name in self.failure_state_map:
                instance.failure_state_map[failure_mode.name] = state_id_map.get(
                    self.failure_state_map[failure_mode.name], cloned_failure.associated_state_id
                )

        instance.reset_runtime_state()
        return instance

    # ------------------------------------------------------------------
    # 序列化与反序列化
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'interface_type': self.interface_type.value if hasattr(self.interface_type, 'value') else self.interface_type,
            'direction': self.direction.value if hasattr(self.direction, 'value') else self.direction,
            'subtype': self.subtype.value if self.subtype and hasattr(self.subtype, 'value') else self.subtype,
            'source_module_id': self.source_module_id,
            'target_module_id': self.target_module_id,
            'protocol': self.protocol,
            'data_format': self.data_format,
            'bandwidth': self.bandwidth,
            'latency': self.latency,
            'reliability': self.reliability,
            'failure_modes': [fm.to_dict() for fm in self.failure_modes],
            'python_code': self.python_code,
            'parameters': self.parameters,
            'state_machine': {
                'enabled': self.state_machine_enabled,
                'states': {state_id: state.to_dict() for state_id, state in self.states.items()},
                'transitions': [transition.to_dict() for transition in self.transitions],
                'normal_state_id': self.normal_state_id,
                'current_state_id': self.current_state_id,
                'failure_state_map': self.failure_state_map,
                'state_history': self.state_history
            }
        })
        return base_dict

    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        self.interface_type = InterfaceType(data.get('interface_type', InterfaceType.SOFTWARE_HARDWARE.value))

        # 加载方向
        direction_value = data.get('direction', 'bidirectional')
        try:
            self.direction = InterfaceDirection(direction_value)
        except ValueError:
            self.direction = InterfaceDirection.BIDIRECTIONAL

        subtype_value = data.get('subtype')
        if subtype_value and self.interface_type == InterfaceType.ALGORITHM_HARDWARE:
            self.subtype = HardwareInterfaceSubtype(subtype_value)
        else:
            self.subtype = None

        self.source_module_id = data.get('source_module_id', '')
        self.target_module_id = data.get('target_module_id', '')
        self.protocol = data.get('protocol', '')
        self.data_format = data.get('data_format', '')
        self.bandwidth = data.get('bandwidth', 0.0)
        self.latency = data.get('latency', 0.0)
        self.reliability = data.get('reliability', 0.99)

        # 失效模式
        self.failure_modes = []
        for fm_data in data.get('failure_modes', []):
            fm = InterfaceFailureMode(FailureMode.COMMUNICATION_FAILURE)
            fm.from_dict(fm_data)
            self.failure_modes.append(fm)

        self.python_code = data.get('python_code', '')
        self.parameters = data.get('parameters', {})

        # 状态机
        state_machine_data = data.get('state_machine', {})
        self.state_machine_enabled = state_machine_data.get('enabled', True)

        self.states = {}
        for state_id, state_data in state_machine_data.get('states', {}).items():
            state = InterfaceState()
            state.from_dict(state_data)
            self.states[state.id] = state

        self.transitions = []
        for transition_data in state_machine_data.get('transitions', []):
            transition = InterfaceTransition('', '')
            transition.from_dict(transition_data)
            self.transitions.append(transition)

        self.normal_state_id = state_machine_data.get('normal_state_id')
        self.current_state_id = state_machine_data.get('current_state_id')
        self.failure_state_map = state_machine_data.get('failure_state_map', {})
        self.state_history = state_machine_data.get('state_history', [])

        if not self.states:
            self._initialize_default_state()
        else:
            if self.normal_state_id not in self.states:
                self.normal_state_id = next((sid for sid, state in self.states.items()
                                             if state.state_type == InterfaceStateType.NORMAL), None)
            if not self.normal_state_id:
                # 确保存在正常状态
                self._initialize_default_state()

        if self.current_state_id not in self.states:
            self.reset_runtime_state(to_normal=False)

        # 同步状态机与失效模式
        self._sync_state_machine_with_failure_modes()
