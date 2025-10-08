#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务剖面数据模型
Task Profile Data Model
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from .base_model import BaseModel


class SuccessCriteriaType(Enum):
    """成功判据类型"""
    MODULE_OUTPUT = "module_output"  # 模块输出参数
    MODULE_STATE = "module_state"    # 模块状态量
    SYSTEM_PERFORMANCE = "system_performance"  # 系统性能指标
    CUSTOM_CONDITION = "custom_condition"      # 自定义条件


class ComparisonOperator(Enum):
    """比较操作符"""
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="
    IN_RANGE = "in_range"
    OUT_RANGE = "out_range"


class SuccessCriteria:
    """成功判据"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.description = ""
        self.criteria_type = SuccessCriteriaType.MODULE_OUTPUT
        self.module_id = ""  # 关联的模块ID
        self.parameter_name = ""  # 参数名称
        self.operator = ComparisonOperator.GREATER_EQUAL
        self.target_value = 0.0  # 目标值
        self.range_min = 0.0  # 范围最小值
        self.range_max = 100.0  # 范围最大值
        self.weight = 1.0  # 权重
        self.enabled = True  # 是否启用
        self.python_code = ""  # 自定义Python代码
    
    def evaluate(self, system_state: Dict[str, Any]) -> bool:
        """评估成功判据"""
        try:
            if self.criteria_type == SuccessCriteriaType.CUSTOM_CONDITION:
                # 执行自定义Python代码
                if self.python_code:
                    local_vars = {
                        'system_state': system_state,
                        'result': False
                    }
                    exec(self.python_code, {}, local_vars)
                    return local_vars.get('result', False)
                return False
            
            # 获取参数值
            if self.module_id not in system_state:
                return False
            
            module_state = system_state[self.module_id]
            if self.parameter_name not in module_state:
                return False
            
            current_value = module_state[self.parameter_name]
            
            # 执行比较操作
            if self.operator == ComparisonOperator.EQUAL:
                return current_value == self.target_value
            elif self.operator == ComparisonOperator.NOT_EQUAL:
                return current_value != self.target_value
            elif self.operator == ComparisonOperator.GREATER:
                return current_value > self.target_value
            elif self.operator == ComparisonOperator.GREATER_EQUAL:
                return current_value >= self.target_value
            elif self.operator == ComparisonOperator.LESS:
                return current_value < self.target_value
            elif self.operator == ComparisonOperator.LESS_EQUAL:
                return current_value <= self.target_value
            elif self.operator == ComparisonOperator.IN_RANGE:
                return self.range_min <= current_value <= self.range_max
            elif self.operator == ComparisonOperator.OUT_RANGE:
                return not (self.range_min <= current_value <= self.range_max)
            
            return False
            
        except Exception as e:
            print(f"评估成功判据 {self.name} 时出错: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'criteria_type': self.criteria_type.value,
            'module_id': self.module_id,
            'parameter_name': self.parameter_name,
            'operator': self.operator.value,
            'target_value': self.target_value,
            'range_min': self.range_min,
            'range_max': self.range_max,
            'weight': self.weight,
            'enabled': self.enabled,
            'python_code': self.python_code
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.name = data.get('name', '')
        self.description = data.get('description', '')
        self.criteria_type = SuccessCriteriaType(data.get('criteria_type', SuccessCriteriaType.MODULE_OUTPUT.value))
        self.module_id = data.get('module_id', '')
        self.parameter_name = data.get('parameter_name', '')
        self.operator = ComparisonOperator(data.get('operator', ComparisonOperator.GREATER_EQUAL.value))
        self.target_value = data.get('target_value', 0.0)
        self.range_min = data.get('range_min', 0.0)
        self.range_max = data.get('range_max', 100.0)
        self.weight = data.get('weight', 1.0)
        self.enabled = data.get('enabled', True)
        self.python_code = data.get('python_code', '')


class TaskPhase:
    """任务阶段"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.description = ""
        self.start_time = 0.0  # 开始时间（秒）
        self.duration = 60.0   # 持续时间（秒）
        self.conditions = []   # 阶段条件
        self.parameters = {}   # 阶段参数
        self.enabled = True    # 是否启用
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'start_time': self.start_time,
            'duration': self.duration,
            'conditions': self.conditions,
            'parameters': self.parameters,
            'enabled': self.enabled
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.name = data.get('name', '')
        self.description = data.get('description', '')
        self.start_time = data.get('start_time', 0.0)
        self.duration = data.get('duration', 60.0)
        self.conditions = data.get('conditions', [])
        self.parameters = data.get('parameters', {})
        self.enabled = data.get('enabled', True)


class TaskProfile(BaseModel):
    """任务剖面"""
    
    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description)
        self.mission_type = ""  # 任务类型
        self.total_duration = 3600.0  # 总持续时间（秒）
        self.success_criteria = []  # 成功判据列表
        self.task_phases = []  # 任务阶段列表
        self.environment_conditions = {}  # 环境条件
        self.initial_conditions = {}  # 初始条件
        self.fault_tree_generated = False  # 是否已生成故障树
        self.fault_tree_data = {}  # 故障树数据
        self.analysis_results = {}  # 分析结果
    
    def add_success_criteria(self, criteria: SuccessCriteria):
        """添加成功判据"""
        self.success_criteria.append(criteria)
        self.update_modified_time()
    
    def remove_success_criteria(self, criteria_name: str):
        """移除成功判据"""
        self.success_criteria = [sc for sc in self.success_criteria if sc.name != criteria_name]
        self.update_modified_time()
    
    def get_success_criteria(self, criteria_name: str) -> Optional[SuccessCriteria]:
        """获取成功判据"""
        for sc in self.success_criteria:
            if sc.name == criteria_name:
                return sc
        return None
    
    def add_task_phase(self, phase: TaskPhase):
        """添加任务阶段"""
        self.task_phases.append(phase)
        self.update_modified_time()
    
    def remove_task_phase(self, phase_name: str):
        """移除任务阶段"""
        self.task_phases = [tp for tp in self.task_phases if tp.name != phase_name]
        self.update_modified_time()
    
    def get_task_phase(self, phase_name: str) -> Optional[TaskPhase]:
        """获取任务阶段"""
        for tp in self.task_phases:
            if tp.name == phase_name:
                return tp
        return None
    
    def evaluate_success(self, system_state: Dict[str, Any]) -> Dict[str, Any]:
        """评估任务成功"""
        results = {
            'overall_success': True,
            'criteria_results': {},
            'success_score': 0.0,
            'total_weight': 0.0,
            'success_rate': 0.0
        }
        
        enabled_criteria = [sc for sc in self.success_criteria if sc.enabled]
        
        for criteria in enabled_criteria:
            try:
                success = criteria.evaluate(system_state)
                results['criteria_results'][criteria.name] = {
                    'success': success,
                    'weight': criteria.weight,
                    'message': '评估成功' if success else '评估失败'
                }
                
                if success:
                    results['success_score'] += criteria.weight
                else:
                    results['overall_success'] = False
                
                results['total_weight'] += criteria.weight
                
            except Exception as e:
                # 单个判据评估失败不影响其他判据
                results['criteria_results'][criteria.name] = {
                    'success': False,
                    'weight': criteria.weight,
                    'message': f'评估出错: {str(e)}'
                }
                results['overall_success'] = False
        
        # 计算成功率（加权平均）
        if results['total_weight'] > 0:
            results['success_rate'] = results['success_score'] / results['total_weight']
        else:
            results['success_rate'] = 0.0
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'mission_type': self.mission_type,
            'total_duration': self.total_duration,
            'success_criteria': [sc.to_dict() for sc in self.success_criteria],
            'task_phases': [tp.to_dict() for tp in self.task_phases],
            'environment_conditions': self.environment_conditions,
            'initial_conditions': self.initial_conditions,
            'fault_tree_generated': self.fault_tree_generated,
            'fault_tree_data': self.fault_tree_data,
            'analysis_results': self.analysis_results
        })
        return base_dict
    
    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        self.mission_type = data.get('mission_type', '')
        self.total_duration = data.get('total_duration', 3600.0)
        
        # 加载成功判据
        self.success_criteria = []
        for sc_data in data.get('success_criteria', []):
            sc = SuccessCriteria()
            sc.from_dict(sc_data)
            self.success_criteria.append(sc)
        
        # 加载任务阶段
        self.task_phases = []
        for tp_data in data.get('task_phases', []):
            tp = TaskPhase()
            tp.from_dict(tp_data)
            self.task_phases.append(tp)
        
        self.environment_conditions = data.get('environment_conditions', {})
        self.initial_conditions = data.get('initial_conditions', {})
        self.fault_tree_generated = data.get('fault_tree_generated', False)
        self.fault_tree_data = data.get('fault_tree_data', {})
        self.analysis_results = data.get('analysis_results', {})


# 预定义任务剖面模板
TASK_PROFILE_TEMPLATES = {
    "无人机巡航任务": {
        "name": "无人机巡航任务",
        "description": "无人机执行巡航监控任务",
        "mission_type": "surveillance",
        "total_duration": 1800.0,  # 30分钟
        "success_criteria": [
            {
                "name": "飞行高度维持",
                "description": "维持指定飞行高度",
                "criteria_type": "module_output",
                "module_id": "flight_controller",
                "parameter_name": "altitude",
                "operator": "in_range",
                "range_min": 95.0,
                "range_max": 105.0,
                "weight": 2.0
            },
            {
                "name": "航线跟踪精度",
                "description": "航线跟踪误差小于5米",
                "criteria_type": "module_output",
                "module_id": "navigation",
                "parameter_name": "track_error",
                "operator": "<=",
                "target_value": 5.0,
                "weight": 3.0
            }
        ],
        "task_phases": [
            {
                "name": "起飞阶段",
                "description": "无人机起飞到指定高度",
                "start_time": 0.0,
                "duration": 120.0
            },
            {
                "name": "巡航阶段",
                "description": "按预定航线巡航",
                "start_time": 120.0,
                "duration": 1500.0
            },
            {
                "name": "返航降落",
                "description": "返回起飞点并降落",
                "start_time": 1620.0,
                "duration": 180.0
            }
        ]
    },
    
    "机器人搬运任务": {
        "name": "机器人搬运任务",
        "description": "机器人执行物品搬运任务",
        "mission_type": "transportation",
        "total_duration": 600.0,  # 10分钟
        "success_criteria": [
            {
                "name": "搬运精度",
                "description": "物品放置位置误差小于2cm",
                "criteria_type": "module_output",
                "module_id": "manipulator",
                "parameter_name": "position_error",
                "operator": "<=",
                "target_value": 0.02,
                "weight": 3.0
            },
            {
                "name": "任务完成时间",
                "description": "在规定时间内完成任务",
                "criteria_type": "system_performance",
                "parameter_name": "completion_time",
                "operator": "<=",
                "target_value": 600.0,
                "weight": 2.0
            }
        ]
    }
}
