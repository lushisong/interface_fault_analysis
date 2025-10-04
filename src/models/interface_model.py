# -*- coding: utf-8 -*-
"""
接口数据模型
Interface Data Model

定义各种接口类型和失效模式的数据结构
"""

from typing import Dict, Any, List, Optional
from enum import Enum
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
        self.name = name
        self.condition_type = condition_type  # threshold, event, time, probability
        self.parameters = {}  # 条件参数
        self.python_code = ""  # Python条件判断代码
        self.probability = 0.0  # 触发概率
        self.enabled = True
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估触发条件是否满足"""
        if not self.enabled:
            return False
        
        if self.python_code:
            try:
                local_vars = {
                    'context': context,
                    'parameters': self.parameters,
                    'result': False
                }
                exec(self.python_code, {}, local_vars)
                return local_vars.get('result', False)
            except Exception as e:
                print(f"评估触发条件 {self.name} 时出错: {e}")
                return False
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'condition_type': self.condition_type,
            'parameters': self.parameters,
            'python_code': self.python_code,
            'probability': self.probability,
            'enabled': self.enabled
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.name = data.get('name', '')
        self.condition_type = data.get('condition_type', 'threshold')
        self.parameters = data.get('parameters', {})
        self.python_code = data.get('python_code', '')
        self.probability = data.get('probability', 0.0)
        self.enabled = data.get('enabled', True)


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
            'python_code': self.python_code
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


class Interface(BaseModel):
    """接口基类"""
    
    def __init__(self, name: str = "", description: str = "", 
                 interface_type: InterfaceType = InterfaceType.SOFTWARE_HARDWARE):
        super().__init__(name, description)
        self.interface_type = interface_type
        self.subtype = None  # 子类型（如硬件接口的传感器、执行器等）
        self.source_module_id = ""  # 源模块ID
        self.target_module_id = ""  # 目标模块ID
        self.protocol = ""  # 通信协议
        self.data_format = ""  # 数据格式
        self.bandwidth = 0.0  # 带宽
        self.latency = 0.0  # 延迟
        self.reliability = 0.99  # 可靠性
        self.failure_modes = []  # 失效模式列表
        self.python_code = ""  # Python建模代码
        self.parameters = {}  # 接口参数
    
    def add_failure_mode(self, failure_mode: InterfaceFailureMode):
        """添加失效模式"""
        self.failure_modes.append(failure_mode)
        self.update_modified_time()
    
    def remove_failure_mode(self, failure_mode_name: str):
        """移除失效模式"""
        self.failure_modes = [fm for fm in self.failure_modes if fm.name != failure_mode_name]
        self.update_modified_time()
    
    def get_failure_mode(self, failure_mode_name: str) -> Optional[InterfaceFailureMode]:
        """获取失效模式"""
        for fm in self.failure_modes:
            if fm.name == failure_mode_name:
                return fm
        return None
    
    def simulate_interface(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """模拟接口行为"""
        if not self.python_code:
            return inputs  # 如果没有自定义代码，直接传递输入
        
        # 准备执行环境
        local_vars = {
            'inputs': inputs,
            'parameters': self.parameters,
            'outputs': inputs.copy(),
            'interface': self
        }
        
        try:
            # 执行用户定义的Python代码
            exec(self.python_code, {}, local_vars)
            return local_vars.get('outputs', inputs)
        except Exception as e:
            print(f"执行接口 {self.name} 的Python代码时出错: {e}")
            return inputs
    
    def check_failure_conditions(self, context: Dict[str, Any]) -> List[InterfaceFailureMode]:
        """检查失效条件，返回触发的失效模式"""
        triggered_failures = []
        for failure_mode in self.failure_modes:
            if failure_mode.check_triggers(context):
                triggered_failures.append(failure_mode)
        return triggered_failures
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'interface_type': self.interface_type.value if hasattr(self.interface_type, 'value') else self.interface_type,
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
            'parameters': self.parameters
        })
        return base_dict
    
    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        self.interface_type = InterfaceType(data.get('interface_type', InterfaceType.SOFTWARE_HARDWARE.value))
        
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
        
        # 加载失效模式
        self.failure_modes = []
        for fm_data in data.get('failure_modes', []):
            fm = InterfaceFailureMode(FailureMode.COMMUNICATION_FAILURE)
            fm.from_dict(fm_data)
            self.failure_modes.append(fm)
        
        self.python_code = data.get('python_code', '')
        self.parameters = data.get('parameters', {})