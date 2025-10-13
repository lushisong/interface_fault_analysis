# -*- coding: utf-8 -*-
"""
系统数据模型
System Data Model

定义智能系统结构、任务剖面、环境模型等数据结构
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
try:
    from .base_model import BaseModel, Point
    from .module_model import Module
    from .interface_model import Interface
    from .task_profile_model import TaskProfile as DetailedTaskProfile
except ImportError:
    from base_model import BaseModel, Point
    from module_model import Module
    from interface_model import Interface
    from task_profile_model import TaskProfile as DetailedTaskProfile


class TaskStatus(Enum):
    """任务状态枚举"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_SUCCESS = "partial_success"
    UNKNOWN = "unknown"


class SuccessCriteria:
    """成功判据"""
    
    def __init__(self, name: str = "", criteria_type: str = "threshold"):
        self.name = name
        self.criteria_type = criteria_type  # threshold, boolean, range, custom
        self.target_module_id = ""  # 目标模块ID
        self.target_parameter = ""  # 目标参数名
        self.threshold_value = 0.0  # 阈值
        self.comparison_operator = ">="  # 比较操作符
        self.python_code = ""  # 自定义判据代码
        self.weight = 1.0  # 权重
        self.enabled = True
    
    def evaluate(self, system_state: Dict[str, Any]) -> bool:
        """评估成功判据"""
        if not self.enabled:
            return True
        
        if self.python_code:
            try:
                local_vars = {
                    'system_state': system_state,
                    'target_module_id': self.target_module_id,
                    'target_parameter': self.target_parameter,
                    'threshold_value': self.threshold_value,
                    'result': False
                }
                exec(self.python_code, {}, local_vars)
                return local_vars.get('result', False)
            except Exception as e:
                print(f"评估成功判据 {self.name} 时出错: {e}")
                return False
        
        # 默认阈值比较
        module_state = system_state.get(self.target_module_id, {})
        actual_value = module_state.get(self.target_parameter, 0)
        
        if self.comparison_operator == ">=":
            return actual_value >= self.threshold_value
        elif self.comparison_operator == "<=":
            return actual_value <= self.threshold_value
        elif self.comparison_operator == "==":
            return actual_value == self.threshold_value
        elif self.comparison_operator == "!=":
            return actual_value != self.threshold_value
        elif self.comparison_operator == ">":
            return actual_value > self.threshold_value
        elif self.comparison_operator == "<":
            return actual_value < self.threshold_value
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'criteria_type': self.criteria_type,
            'target_module_id': self.target_module_id,
            'target_parameter': self.target_parameter,
            'threshold_value': self.threshold_value,
            'comparison_operator': self.comparison_operator,
            'python_code': self.python_code,
            'weight': self.weight,
            'enabled': self.enabled
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.name = data.get('name', '')
        self.criteria_type = data.get('criteria_type', 'threshold')
        self.target_module_id = data.get('target_module_id', '')
        self.target_parameter = data.get('target_parameter', '')
        self.threshold_value = data.get('threshold_value', 0.0)
        self.comparison_operator = data.get('comparison_operator', '>=')
        self.python_code = data.get('python_code', '')
        self.weight = data.get('weight', 1.0)
        self.enabled = data.get('enabled', True)


class TaskProfile(BaseModel):
    """任务剖面"""
    
    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description)
        self.duration = 0.0  # 任务持续时间(秒)
        self.priority = 1  # 优先级 1-10
        self.success_criteria = []  # 成功判据列表
        self.initial_conditions = {}  # 初始条件
        self.environment_conditions = {}  # 环境条件
        self.expected_outputs = {}  # 期望输出
        self.fault_tree_analysis_results = {}  # 故障树分析结果
        self.analysis_completed = False  # 是否已完成分析
    
    def add_success_criteria(self, criteria: SuccessCriteria):
        """添加成功判据"""
        self.success_criteria.append(criteria)
        self.update_modified_time()
    
    def remove_success_criteria(self, criteria_name: str):
        """移除成功判据"""
        self.success_criteria = [c for c in self.success_criteria if c.name != criteria_name]
        self.update_modified_time()
    
    def evaluate_task_success(self, system_state: Dict[str, Any]) -> Tuple[TaskStatus, float]:
        """评估任务成功状态"""
        if not self.success_criteria:
            return TaskStatus.UNKNOWN, 0.0
        
        total_weight = sum(c.weight for c in self.success_criteria if c.enabled)
        if total_weight == 0:
            return TaskStatus.UNKNOWN, 0.0
        
        success_weight = 0.0
        for criteria in self.success_criteria:
            if criteria.evaluate(system_state):
                success_weight += criteria.weight
        
        success_rate = success_weight / total_weight
        
        if success_rate >= 1.0:
            return TaskStatus.SUCCESS, success_rate
        elif success_rate >= 0.5:
            return TaskStatus.PARTIAL_SUCCESS, success_rate
        else:
            return TaskStatus.FAILURE, success_rate
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'duration': self.duration,
            'priority': self.priority,
            'success_criteria': [sc.to_dict() for sc in self.success_criteria],
            'initial_conditions': self.initial_conditions,
            'environment_conditions': self.environment_conditions,
            'expected_outputs': self.expected_outputs,
            'fault_tree_analysis_results': self.fault_tree_analysis_results,
            'analysis_completed': self.analysis_completed
        })
        return base_dict
    
    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        self.duration = data.get('duration', 0.0)
        self.priority = data.get('priority', 1)
        
        # 加载成功判据
        self.success_criteria = []
        for sc_data in data.get('success_criteria', []):
            sc = SuccessCriteria()
            sc.from_dict(sc_data)
            self.success_criteria.append(sc)
        
        self.initial_conditions = data.get('initial_conditions', {})
        self.environment_conditions = data.get('environment_conditions', {})
        self.expected_outputs = data.get('expected_outputs', {})
        self.fault_tree_analysis_results = data.get('fault_tree_analysis_results', {})
        self.analysis_completed = data.get('analysis_completed', False)


class Connection:
    """模块间连接"""
    
    def __init__(self, id: str = "", source_module_id: str = "", target_module_id: str = "",
                 source_point_id: str = "", target_point_id: str = ""):
        if id:
            self.id = id
        else:
            self.id = f"{source_module_id}_{source_point_id}_{target_module_id}_{target_point_id}"
        self.source_module_id = source_module_id
        self.target_module_id = target_module_id
        self.source_point_id = source_point_id
        self.target_point_id = target_point_id
        self.interface_id = ""  # 关联的接口ID
        self.connection_points = []  # 连线的控制点
        self.enabled = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'source_module_id': self.source_module_id,
            'target_module_id': self.target_module_id,
            'source_point_id': self.source_point_id,
            'target_point_id': self.target_point_id,
            'interface_id': self.interface_id,
            'connection_points': [cp.to_dict() for cp in self.connection_points],
            'enabled': self.enabled
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.source_module_id = data.get('source_module_id', '')
        self.target_module_id = data.get('target_module_id', '')
        self.source_point_id = data.get('source_point_id', '')
        self.target_point_id = data.get('target_point_id', '')
        self.interface_id = data.get('interface_id', '')
        
        # 加载连线控制点
        self.connection_points = []
        for cp_data in data.get('connection_points', []):
            cp = Point()
            cp.from_dict(cp_data)
            self.connection_points.append(cp)
        
        self.enabled = data.get('enabled', True)


class EnvironmentModel(BaseModel):
    """环境模型"""
    
    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description)
        self.environment_type = "physical"  # physical, network, user, electromagnetic
        self.parameters = {}  # 环境参数
        self.stress_factors = {}  # 应力因子
        self.python_code = ""  # Python建模代码
        self.position = Point()  # 在图形界面中的位置
        self.size = Point(120, 80)  # 环境模块大小
        self.icon_path = ""  # 图标路径
    
    def apply_stress(self, system_state: Dict[str, Any]) -> Dict[str, Any]:
        """施加环境应力"""
        if not self.python_code:
            return system_state
        
        # 准备执行环境
        local_vars = {
            'system_state': system_state,
            'parameters': self.parameters,
            'stress_factors': self.stress_factors,
            'modified_state': system_state.copy()
        }
        
        try:
            # 执行用户定义的Python代码
            exec(self.python_code, {}, local_vars)
            return local_vars.get('modified_state', system_state)
        except Exception as e:
            print(f"执行环境模型 {self.name} 的Python代码时出错: {e}")
            return system_state
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'environment_type': self.environment_type,
            'parameters': self.parameters,
            'stress_factors': self.stress_factors,
            'python_code': self.python_code,
            'position': self.position.to_dict(),
            'size': self.size.to_dict(),
            'icon_path': self.icon_path
        })
        return base_dict
    
    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        self.environment_type = data.get('environment_type', 'physical')
        self.parameters = data.get('parameters', {})
        self.stress_factors = data.get('stress_factors', {})
        self.python_code = data.get('python_code', '')
        
        self.position = Point()
        self.position.from_dict(data.get('position', {}))
        
        self.size = Point()
        self.size.from_dict(data.get('size', {'x': 120, 'y': 80}))
        
        self.icon_path = data.get('icon_path', '')


class SystemStructure(BaseModel):
    """系统结构模型"""
    
    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description)
        self.modules = {}  # 模块字典 {module_id: Module}
        self.interfaces = {}  # 接口字典 {interface_id: Interface}
        self.connections = {}  # 连接字典 {connection_id: Connection}
        self.environment_models = {}  # 环境模型字典 {env_id: EnvironmentModel}
        self.task_profiles = {}  # 任务剖面字典 {task_id: TaskProfile}
        self.current_task_profile_id = ""  # 当前选中的任务剖面ID
        self.canvas_size = Point(1200, 800)  # 画布大小
        self.zoom_level = 1.0  # 缩放级别
        self.view_offset = Point(0, 0)  # 视图偏移
    
    def add_module(self, module: Module):
        """添加模块"""
        self.modules[module.id] = module
        self.update_modified_time()
    
    def remove_module(self, module_id: str):
        """移除模块"""
        if module_id in self.modules:
            # 移除相关的连接
            connections_to_remove = []
            for conn_id, conn in self.connections.items():
                if conn.source_module_id == module_id or conn.target_module_id == module_id:
                    connections_to_remove.append(conn_id)
            
            for conn_id in connections_to_remove:
                del self.connections[conn_id]
            
            # 移除模块
            del self.modules[module_id]
            self.update_modified_time()
    
    def add_interface(self, interface: Interface):
        """添加接口"""
        self.interfaces[interface.id] = interface
        self.update_modified_time()
    
    def remove_interface(self, interface_id: str):
        """移除接口"""
        if interface_id in self.interfaces:
            del self.interfaces[interface_id]
            self.update_modified_time()
    
    def add_connection(self, connection: Connection):
        """添加连接"""
        self.connections[connection.id] = connection
        self.update_modified_time()
    
    def remove_connection(self, connection_id: str):
        """移除连接"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            self.update_modified_time()
    
    def add_environment_model(self, env_model: EnvironmentModel):
        """添加环境模型"""
        self.environment_models[env_model.id] = env_model
        self.update_modified_time()
    
    def remove_environment_model(self, env_id: str):
        """移除环境模型"""
        if env_id in self.environment_models:
            del self.environment_models[env_id]
            self.update_modified_time()
    
    def add_task_profile(self, task_profile: TaskProfile):
        """添加任务剖面"""
        self.task_profiles[task_profile.id] = task_profile
        if not self.current_task_profile_id:
            self.current_task_profile_id = task_profile.id
        self.update_modified_time()
    
    def remove_task_profile(self, task_id: str):
        """移除任务剖面"""
        if task_id in self.task_profiles:
            del self.task_profiles[task_id]
            if self.current_task_profile_id == task_id:
                # 选择另一个任务剖面作为当前任务
                if self.task_profiles:
                    self.current_task_profile_id = next(iter(self.task_profiles.keys()))
                else:
                    self.current_task_profile_id = ""
            self.update_modified_time()
    
    def get_current_task_profile(self) -> Optional[TaskProfile]:
        """获取当前任务剖面"""
        if self.current_task_profile_id in self.task_profiles:
            return self.task_profiles[self.current_task_profile_id]
        return None
    
    def simulate_system(self, duration: float = 1.0) -> Dict[str, Any]:
        """模拟系统运行"""
        # 这里实现系统仿真逻辑
        # 返回系统状态
        system_state = {}
        
        # 执行模块仿真
        for module_id, module in self.modules.items():
            module_inputs = {}  # 从连接获取输入
            module_outputs = module.execute_python_code(module_inputs)
            system_state[module_id] = module_outputs
        
        # 应用环境应力
        for env_model in self.environment_models.values():
            system_state = env_model.apply_stress(system_state)
        
        return system_state
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'modules': {k: v.to_dict() for k, v in self.modules.items()},
            'interfaces': {k: v.to_dict() for k, v in self.interfaces.items()},
            'connections': {k: v.to_dict() for k, v in self.connections.items()},
            'environment_models': {k: v.to_dict() for k, v in self.environment_models.items()},
            'task_profiles': {k: v.to_dict() for k, v in self.task_profiles.items()},
            'current_task_profile_id': self.current_task_profile_id,
            'canvas_size': self.canvas_size.to_dict(),
            'zoom_level': self.zoom_level,
            'view_offset': self.view_offset.to_dict()
        })
        return base_dict
    
    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        
        # 加载模块（这里需要根据实际的模块类型创建对应的对象）
        self.modules = {}
        for module_id, module_data in data.get('modules', {}).items():
            # 根据module_type创建对应的模块类型
            module_type_str = module_data.get('module_type', 'hardware')
            if module_type_str == 'hardware':
                from .module_model import HardwareModule as ModuleClass
            elif module_type_str == 'software':
                from .module_model import SoftwareModule as ModuleClass
            elif module_type_str == 'algorithm':
                from .module_model import AlgorithmModule as ModuleClass
            else:
                from .module_model import Module as ModuleClass
                
            module = ModuleClass()
            module.from_dict(module_data)
            # 确保模块ID正确设置
            module.id = module_id
            self.modules[module_id] = module
        
        # 加载接口
        self.interfaces = {}
        for interface_id, interface_data in data.get('interfaces', {}).items():
            interface = Interface()
            interface.from_dict(interface_data)
            self.interfaces[interface_id] = interface
        
        # 加载连接
        self.connections = {}
        for connection_id, connection_data in data.get('connections', {}).items():
            try:
                connection = Connection()
                connection.from_dict(connection_data)
                # 确保连接有有效的ID
                if not connection.id:
                    connection.id = connection_id
                self.connections[connection_id] = connection
            except Exception as e:
                print(f"加载连接 {connection_id} 时出错: {e}")
        
        # 加载环境模型
        self.environment_models = {}
        for env_id, env_data in data.get('environment_models', {}).items():
            env_model = EnvironmentModel()
            env_model.from_dict(env_data)
            self.environment_models[env_id] = env_model
        
        # 加载任务剖面
        self.task_profiles = {}
        for task_id, task_data in data.get('task_profiles', {}).items():
            if 'mission_type' in task_data or 'task_phases' in task_data or 'total_duration' in task_data:
                task_profile = DetailedTaskProfile()
            else:
                task_profile = TaskProfile()
            task_profile.from_dict(task_data)
            self.task_profiles[task_id] = task_profile
        
        self.current_task_profile_id = data.get('current_task_profile_id', '')
        
        self.canvas_size = Point()
        self.canvas_size.from_dict(data.get('canvas_size', {'x': 1200, 'y': 800}))
        
        self.zoom_level = data.get('zoom_level', 1.0)
        
        self.view_offset = Point()
        self.view_offset.from_dict(data.get('view_offset', {'x': 0, 'y': 0}))
