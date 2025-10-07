# -*- coding: utf-8 -*-
"""
模块数据模型
Module Data Model

定义硬件模块、软件模块、算法模块的数据结构
"""

from typing import Dict, Any, List, Optional
from enum import Enum
try:
    from .base_model import BaseModel, Point, ConnectionPoint
except ImportError:
    from base_model import BaseModel, Point, ConnectionPoint


class ModuleType(Enum):
    """模块类型枚举"""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    ALGORITHM = "algorithm"
    ENVIRONMENT = "environment"


class ModuleTemplate(Enum):
    """模块模板类型"""
    # 硬件模块模板
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    PROCESSOR = "processor"
    MEMORY = "memory"
    COMMUNICATION = "communication"
    
    # 软件模块模板
    OPERATING_SYSTEM = "operating_system"
    MIDDLEWARE = "middleware"
    APPLICATION = "application"
    DATABASE = "database"
    
    # 算法模块模板
    CONTROL_ALGORITHM = "control_algorithm"
    PERCEPTION_ALGORITHM = "perception_algorithm"
    DECISION_ALGORITHM = "decision_algorithm"
    LEARNING_ALGORITHM = "learning_algorithm"
    
    # 环境模块模板
    PHYSICAL_ENVIRONMENT = "physical_environment"
    NETWORK_ENVIRONMENT = "network_environment"
    USER_ENVIRONMENT = "user_environment"


class Module(BaseModel):
    """模块基类"""
    
    def __init__(self, name: str = "", description: str = "", 
                 module_type: ModuleType = ModuleType.HARDWARE):
        super().__init__(name, description)
        self.module_type = module_type
        self.template = None  # 使用的模板类型
        self.position = Point()  # 在图形界面中的位置
        self.size = Point(100, 60)  # 模块大小
        self.icon_path = ""  # 图标路径
        self.connection_points = []  # 接口列表
        self.parameters = {}  # 模块参数
        self.state_variables = {}  # 状态变量
        self.python_code = ""  # Python建模代码
        self.is_template = False  # 是否为模板
        self.id = f"module_{id(self)}"  # 确保每个模块都有唯一ID
        
    def add_connection_point(self, point: ConnectionPoint):
        """添加接口"""
        self.connection_points.append(point)
        self.update_modified_time()
    
    def remove_connection_point(self, point_id: str):
        """移除接口"""
        self.connection_points = [p for p in self.connection_points if p.id != point_id]
        self.update_modified_time()
    
    def get_connection_point(self, point_id: str) -> Optional[ConnectionPoint]:
        """获取接口"""
        for point in self.connection_points:
            if point.id == point_id:
                return point
        return None
    
    def set_parameter(self, key: str, value: Any):
        """设置参数"""
        self.parameters[key] = value
        self.update_modified_time()
    
    def get_parameter(self, key: str, default_value: Any = None) -> Any:
        """获取参数"""
        return self.parameters.get(key, default_value)
    
    def set_state_variable(self, key: str, value: Any):
        """设置状态变量"""
        self.state_variables[key] = value
        self.update_modified_time()
    
    def get_state_variable(self, key: str, default_value: Any = None) -> Any:
        """获取状态变量"""
        return self.state_variables.get(key, default_value)
    
    def execute_python_code(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行Python建模代码"""
        if not self.python_code:
            return {}
        
        # 准备执行环境
        local_vars = {
            'inputs': inputs or {},
            'parameters': self.parameters,
            'state_variables': self.state_variables,
            'outputs': {}
        }
        
        try:
            # 执行用户定义的Python代码
            exec(self.python_code, {}, local_vars)
            return local_vars.get('outputs', {})
        except Exception as e:
            print(f"执行模块 {self.name} 的Python代码时出错: {e}")
            return {}
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'module_type': self.module_type.value if hasattr(self.module_type, 'value') else self.module_type,
            'template': self.template.value if self.template and hasattr(self.template, 'value') else self.template,
            'position': self.position.to_dict() if hasattr(self.position, 'to_dict') else self.position,
            'size': self.size.to_dict() if hasattr(self.size, 'to_dict') else self.size,
            'icon_path': self.icon_path,
            'connection_points': [cp.to_dict() for cp in self.connection_points],
            'parameters': self.parameters,
            'state_variables': self.state_variables,
            'python_code': self.python_code,
            'is_template': self.is_template
        })
        return base_dict
    
    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        self.module_type = ModuleType(data.get('module_type', ModuleType.HARDWARE.value))
        template_value = data.get('template')
        self.template = ModuleTemplate(template_value) if template_value else None
        
        self.position = Point()
        self.position.from_dict(data.get('position', {}))
        
        self.size = Point()
        self.size.from_dict(data.get('size', {'x': 100, 'y': 60}))
        
        self.icon_path = data.get('icon_path', '')
        
        # 加载接口
        self.connection_points = []
        for cp_data in data.get('connection_points', []):
            cp = ConnectionPoint()
            cp.from_dict(cp_data)
            self.connection_points.append(cp)
        
        self.parameters = data.get('parameters', {})
        self.state_variables = data.get('state_variables', {})
        self.python_code = data.get('python_code', '')
        self.is_template = data.get('is_template', False)


class HardwareModule(Module):
    """硬件模块"""
    
    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description, ModuleType.HARDWARE)
        self.manufacturer = ""  # 制造商
        self.model = ""  # 型号
        self.specifications = {}  # 技术规格
        self.power_consumption = 0.0  # 功耗
        self.operating_temperature = (-40, 85)  # 工作温度范围
        self.reliability_data = {}  # 可靠性数据
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'manufacturer': self.manufacturer,
            'model': self.model,
            'specifications': self.specifications,
            'power_consumption': self.power_consumption,
            'operating_temperature': self.operating_temperature,
            'reliability_data': self.reliability_data
        })
        return base_dict
    
    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        self.manufacturer = data.get('manufacturer', '')
        self.model = data.get('model', '')
        self.specifications = data.get('specifications', {})
        self.power_consumption = data.get('power_consumption', 0.0)
        self.operating_temperature = data.get('operating_temperature', (-40, 85))
        self.reliability_data = data.get('reliability_data', {})


class SoftwareModule(Module):
    """软件模块"""
    
    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description, ModuleType.SOFTWARE)
        self.software_version = "1.0"  # 软件版本
        self.programming_language = "Python"  # 编程语言
        self.dependencies = []  # 依赖项
        self.memory_usage = 0  # 内存使用量(MB)
        self.cpu_usage = 0.0  # CPU使用率(%)
        self.execution_time = 0.0  # 执行时间(ms)
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'software_version': self.software_version,
            'programming_language': self.programming_language,
            'dependencies': self.dependencies,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'execution_time': self.execution_time
        })
        return base_dict
    
    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        self.software_version = data.get('software_version', '1.0')
        self.programming_language = data.get('programming_language', 'Python')
        self.dependencies = data.get('dependencies', [])
        self.memory_usage = data.get('memory_usage', 0)
        self.cpu_usage = data.get('cpu_usage', 0.0)
        self.execution_time = data.get('execution_time', 0.0)


class AlgorithmModule(Module):
    """算法模块"""
    
    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description, ModuleType.ALGORITHM)
        self.algorithm_type = ""  # 算法类型
        self.complexity = ""  # 算法复杂度
        self.accuracy = 0.0  # 准确率
        self.performance_metrics = {}  # 性能指标
        self.training_data = ""  # 训练数据描述
        self.model_parameters = {}  # 模型参数
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'algorithm_type': self.algorithm_type,
            'complexity': self.complexity,
            'accuracy': self.accuracy,
            'performance_metrics': self.performance_metrics,
            'training_data': self.training_data,
            'model_parameters': self.model_parameters
        })
        return base_dict
    
    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        self.algorithm_type = data.get('algorithm_type', '')
        self.complexity = data.get('complexity', '')
        self.accuracy = data.get('accuracy', 0.0)
        self.performance_metrics = data.get('performance_metrics', {})
        self.training_data = data.get('training_data', '')
        self.model_parameters = data.get('model_parameters', {})
