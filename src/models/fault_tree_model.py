#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
故障树分析数据模型
Fault Tree Analysis Data Model
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
import uuid
from .base_model import BaseModel


class EventType(Enum):
    """事件类型"""
    TOP_EVENT = "top_event"           # 顶事件
    INTERMEDIATE_EVENT = "intermediate_event"  # 中间事件
    BASIC_EVENT = "basic_event"       # 基本事件
    UNDEVELOPED_EVENT = "undeveloped_event"  # 未展开事件
    EXTERNAL_EVENT = "external_event" # 外部事件
    CONDITIONING_EVENT = "conditioning_event"  # 条件事件


class GateType(Enum):
    """逻辑门类型"""
    AND = "and"                       # 与门
    OR = "or"                         # 或门
    NOT = "not"                       # 非门
    XOR = "xor"                       # 异或门
    NAND = "nand"                     # 与非门
    NOR = "nor"                       # 或非门
    VOTING = "voting"                 # 表决门（k/n门）
    PRIORITY_AND = "priority_and"     # 优先与门
    INHIBIT = "inhibit"               # 禁门
    TRANSFER = "transfer"             # 转移门


class FaultTreeEvent:
    """故障树事件"""
    
    def __init__(self, name: str = "", event_type: EventType = EventType.BASIC_EVENT):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = ""
        self.event_type = event_type
        self.probability = 0.0            # 事件概率
        self.failure_rate = 0.0           # 失效率（λ）
        self.repair_rate = 0.0            # 修复率（μ）
        self.mission_time = 0.0           # 任务时间
        self.unavailability = 0.0         # 不可用度
        
        # 关联信息
        self.module_id = ""               # 关联的模块ID
        self.interface_id = ""            # 关联的接口ID
        self.failure_mode_id = ""         # 关联的失效模式ID
        
        # 图形信息
        self.position = {'x': 0, 'y': 0}  # 在故障树中的位置
        self.size = {'width': 120, 'height': 60}  # 事件框大小
        
        # 分析结果
        self.importance_measures = {}     # 重要度指标
        self.cut_sets = []               # 包含此事件的割集
        
        # 自定义属性
        self.custom_properties = {}
    
    def calculate_probability(self) -> float:
        """计算事件概率"""
        if self.probability > 0:
            return self.probability
        
        if self.failure_rate > 0 and self.mission_time > 0:
            # 指数分布：P(t) = 1 - e^(-λt)
            import math
            self.probability = 1 - math.exp(-self.failure_rate * self.mission_time)
        
        return self.probability
    
    def calculate_unavailability(self) -> float:
        """计算不可用度"""
        if self.unavailability > 0:
            return self.unavailability
        
        if self.failure_rate > 0 and self.repair_rate > 0:
            # 稳态不可用度：Q = λ/(λ+μ)
            self.unavailability = self.failure_rate / (self.failure_rate + self.repair_rate)
        elif self.failure_rate > 0 and self.mission_time > 0:
            # 任务不可用度近似：Q ≈ λt (当λt << 1时)
            self.unavailability = self.failure_rate * self.mission_time
        
        return self.unavailability
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'event_type': self.event_type.value,
            'probability': self.probability,
            'failure_rate': self.failure_rate,
            'repair_rate': self.repair_rate,
            'mission_time': self.mission_time,
            'unavailability': self.unavailability,
            'module_id': self.module_id,
            'interface_id': self.interface_id,
            'failure_mode_id': self.failure_mode_id,
            'position': self.position,
            'size': self.size,
            'importance_measures': self.importance_measures,
            'cut_sets': self.cut_sets,
            'custom_properties': self.custom_properties
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.id = data.get('id', str(uuid.uuid4()))
        self.name = data.get('name', '')
        self.description = data.get('description', '')
        self.event_type = EventType(data.get('event_type', EventType.BASIC_EVENT.value))
        self.probability = data.get('probability', 0.0)
        self.failure_rate = data.get('failure_rate', 0.0)
        self.repair_rate = data.get('repair_rate', 0.0)
        self.mission_time = data.get('mission_time', 0.0)
        self.unavailability = data.get('unavailability', 0.0)
        self.module_id = data.get('module_id', '')
        self.interface_id = data.get('interface_id', '')
        self.failure_mode_id = data.get('failure_mode_id', '')
        self.position = data.get('position', {'x': 0, 'y': 0})
        self.size = data.get('size', {'width': 120, 'height': 60})
        self.importance_measures = data.get('importance_measures', {})
        self.cut_sets = data.get('cut_sets', [])
        self.custom_properties = data.get('custom_properties', {})


class FaultTreeGate:
    """故障树逻辑门"""
    
    def __init__(self, name: str = "", gate_type: GateType = GateType.OR):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = ""
        self.gate_type = gate_type
        
        # 表决门参数
        self.k_value = 1                  # k/n门的k值
        self.n_value = 1                  # k/n门的n值
        
        # 输入输出
        self.input_events = []            # 输入事件ID列表
        self.output_event_id = ""         # 输出事件ID
        
        # 图形信息
        self.position = {'x': 0, 'y': 0}  # 在故障树中的位置
        self.size = {'width': 80, 'height': 60}  # 逻辑门大小
        
        # 分析结果
        self.probability = 0.0            # 门输出概率
        self.importance_measures = {}     # 重要度指标
        
        # 自定义属性
        self.custom_properties = {}
    
    def calculate_probability(self, input_probabilities: List[float]) -> float:
        """计算逻辑门输出概率"""
        if not input_probabilities:
            return 0.0
        
        if self.gate_type == GateType.AND:
            # 与门：所有输入都发生
            self.probability = 1.0
            for p in input_probabilities:
                self.probability *= p
        
        elif self.gate_type == GateType.OR:
            # 或门：至少一个输入发生
            self.probability = 1.0
            for p in input_probabilities:
                self.probability *= (1 - p)
            self.probability = 1 - self.probability
        
        elif self.gate_type == GateType.NOT:
            # 非门：输入不发生
            if input_probabilities:
                self.probability = 1 - input_probabilities[0]
        
        elif self.gate_type == GateType.XOR:
            # 异或门：恰好一个输入发生
            if len(input_probabilities) == 2:
                p1, p2 = input_probabilities[0], input_probabilities[1]
                self.probability = p1 * (1 - p2) + p2 * (1 - p1)
        
        elif self.gate_type == GateType.NAND:
            # 与非门：不是所有输入都发生
            prob_and = 1.0
            for p in input_probabilities:
                prob_and *= p
            self.probability = 1 - prob_and
        
        elif self.gate_type == GateType.NOR:
            # 或非门：没有输入发生
            prob_or = 1.0
            for p in input_probabilities:
                prob_or *= (1 - p)
            self.probability = prob_or
        
        elif self.gate_type == GateType.VOTING:
            # 表决门：至少k个输入发生
            self.probability = self._calculate_voting_probability(input_probabilities)
        
        return self.probability
    
    def _calculate_voting_probability(self, input_probabilities: List[float]) -> float:
        """计算表决门概率"""
        from itertools import combinations
        import math
        
        n = len(input_probabilities)
        k = min(self.k_value, n)
        
        total_prob = 0.0
        
        # 计算所有可能的k个或更多输入发生的概率
        for r in range(k, n + 1):
            for combo in combinations(range(n), r):
                # 计算这个组合的概率
                combo_prob = 1.0
                for i in range(n):
                    if i in combo:
                        combo_prob *= input_probabilities[i]
                    else:
                        combo_prob *= (1 - input_probabilities[i])
                total_prob += combo_prob
        
        return total_prob
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'gate_type': self.gate_type.value,
            'k_value': self.k_value,
            'n_value': self.n_value,
            'input_events': self.input_events,
            'output_event_id': self.output_event_id,
            'position': self.position,
            'size': self.size,
            'probability': self.probability,
            'importance_measures': self.importance_measures,
            'custom_properties': self.custom_properties
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.id = data.get('id', str(uuid.uuid4()))
        self.name = data.get('name', '')
        self.description = data.get('description', '')
        self.gate_type = GateType(data.get('gate_type', GateType.OR.value))
        self.k_value = data.get('k_value', 1)
        self.n_value = data.get('n_value', 1)
        self.input_events = data.get('input_events', [])
        self.output_event_id = data.get('output_event_id', '')
        self.position = data.get('position', {'x': 0, 'y': 0})
        self.size = data.get('size', {'width': 80, 'height': 60})
        self.probability = data.get('probability', 0.0)
        self.importance_measures = data.get('importance_measures', {})
        self.custom_properties = data.get('custom_properties', {})


class MinimalCutSet:
    """最小割集"""
    
    def __init__(self, events: List[str] = None):
        self.id = str(uuid.uuid4())
        self.events = events or []        # 基本事件ID列表
        self.probability = 0.0            # 割集概率
        self.importance = 0.0             # 割集重要度
        self.order = len(self.events)     # 割集阶数
    
    def calculate_probability(self, event_probabilities: Dict[str, float]) -> float:
        """计算割集概率"""
        self.probability = 1.0
        for event_id in self.events:
            if event_id in event_probabilities:
                self.probability *= event_probabilities[event_id]
        return self.probability
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'events': self.events,
            'probability': self.probability,
            'importance': self.importance,
            'order': self.order
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.id = data.get('id', str(uuid.uuid4()))
        self.events = data.get('events', [])
        self.probability = data.get('probability', 0.0)
        self.importance = data.get('importance', 0.0)
        self.order = data.get('order', len(self.events))


class FaultTree(BaseModel):
    """故障树模型"""
    
    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description)
        self.top_event_id = ""            # 顶事件ID
        self.events = {}                  # 事件字典 {event_id: FaultTreeEvent}
        self.gates = {}                   # 逻辑门字典 {gate_id: FaultTreeGate}
        self.minimal_cut_sets = []        # 最小割集列表
        
        # 分析参数
        self.mission_time = 8760.0        # 任务时间（小时）
        self.confidence_level = 0.95      # 置信水平
        
        # 分析结果
        self.system_probability = 0.0     # 系统失效概率
        self.system_unavailability = 0.0  # 系统不可用度
        self.mean_time_to_failure = 0.0   # 平均故障时间
        self.analysis_results = {}        # 详细分析结果
        
        # 关联信息
        self.task_profile_id = ""         # 关联的任务剖面ID
        self.system_structure_id = ""     # 关联的系统结构ID
        
        # 生成参数
        self.generation_config = {
            'include_interface_failures': True,
            'include_module_failures': True,
            'include_environment_effects': True,
            'max_depth': 5,
            'min_probability_threshold': 1e-6
        }
    
    def add_event(self, event: FaultTreeEvent):
        """添加事件"""
        self.events[event.id] = event
        self.update_modified_time()
    
    def remove_event(self, event_id: str):
        """移除事件"""
        if event_id in self.events:
            # 移除相关的逻辑门连接
            for gate in self.gates.values():
                if event_id in gate.input_events:
                    gate.input_events.remove(event_id)
                if gate.output_event_id == event_id:
                    gate.output_event_id = ""
            
            del self.events[event_id]
            self.update_modified_time()
    
    def add_gate(self, gate: FaultTreeGate):
        """添加逻辑门"""
        self.gates[gate.id] = gate
        self.update_modified_time()
    
    def remove_gate(self, gate_id: str):
        """移除逻辑门"""
        if gate_id in self.gates:
            del self.gates[gate_id]
            self.update_modified_time()
    
    def get_top_event(self) -> Optional[FaultTreeEvent]:
        """获取顶事件"""
        if self.top_event_id and self.top_event_id in self.events:
            return self.events[self.top_event_id]
        return None
    
    def get_basic_events(self) -> List[FaultTreeEvent]:
        """获取所有基本事件"""
        return [event for event in self.events.values() 
                if event.event_type == EventType.BASIC_EVENT]
    
    def calculate_system_probability(self) -> float:
        """计算系统失效概率"""
        if not self.minimal_cut_sets:
            return 0.0
        
        # 使用最小割集计算系统概率
        # 近似公式：P_sys ≈ Σ P_i - Σ P_i * P_j + ...
        # 这里使用一阶近似
        self.system_probability = 0.0
        
        event_probabilities = {}
        for event in self.events.values():
            event_probabilities[event.id] = event.calculate_probability()
        
        for cut_set in self.minimal_cut_sets:
            cut_set.calculate_probability(event_probabilities)
            self.system_probability += cut_set.probability
        
        # 确保概率不超过1
        self.system_probability = min(self.system_probability, 1.0)
        
        return self.system_probability
    
    def find_minimal_cut_sets(self) -> List[MinimalCutSet]:
        """查找最小割集"""
        if not self.top_event_id or self.top_event_id not in self.events:
            return []
        
        # 使用递归算法查找最小割集
        cut_sets = self._find_cut_sets_recursive(self.top_event_id, set())
        
        # 转换为最小割集对象并去重
        minimal_cut_sets = []
        unique_cut_sets = set()
        
        for cut_set in cut_sets:
            cut_set_tuple = tuple(sorted(cut_set))
            if cut_set_tuple not in unique_cut_sets:
                unique_cut_sets.add(cut_set_tuple)
                mcs = MinimalCutSet(list(cut_set))
                minimal_cut_sets.append(mcs)
        
        # 移除非最小割集
        self.minimal_cut_sets = self._remove_non_minimal(minimal_cut_sets)
        
        return self.minimal_cut_sets
    
    def _find_cut_sets_recursive(self, event_id: str, current_path: Set[str]) -> List[Set[str]]:
        """递归查找割集"""
        if event_id in current_path:  # 避免循环
            return []
        
        if event_id not in self.events:
            return []
        
        event = self.events[event_id]
        
        # 如果是基本事件，返回包含该事件的割集
        if event.event_type == EventType.BASIC_EVENT:
            return [{event_id}]
        
        # 查找输入到该事件的逻辑门
        input_gate = None
        for gate in self.gates.values():
            if gate.output_event_id == event_id:
                input_gate = gate
                break
        
        if not input_gate:
            return [{event_id}]  # 如果没有输入门，当作基本事件处理
        
        # 根据逻辑门类型处理
        new_path = current_path | {event_id}
        
        if input_gate.gate_type == GateType.OR:
            # 或门：每个输入都是一个割集
            cut_sets = []
            for input_event_id in input_gate.input_events:
                input_cut_sets = self._find_cut_sets_recursive(input_event_id, new_path)
                cut_sets.extend(input_cut_sets)
            return cut_sets
        
        elif input_gate.gate_type == GateType.AND:
            # 与门：所有输入的笛卡尔积
            all_input_cut_sets = []
            for input_event_id in input_gate.input_events:
                input_cut_sets = self._find_cut_sets_recursive(input_event_id, new_path)
                if input_cut_sets:
                    all_input_cut_sets.append(input_cut_sets)
            
            # 计算笛卡尔积
            if not all_input_cut_sets:
                return []
            
            result = all_input_cut_sets[0]
            for i in range(1, len(all_input_cut_sets)):
                new_result = []
                for cut_set1 in result:
                    for cut_set2 in all_input_cut_sets[i]:
                        new_result.append(cut_set1 | cut_set2)
                result = new_result
            
            return result
        
        else:
            # 其他类型的门暂时简化处理
            return [{event_id}]
    
    def _remove_non_minimal(self, cut_sets: List[MinimalCutSet]) -> List[MinimalCutSet]:
        """移除非最小割集"""
        minimal_cut_sets = []
        
        for i, cut_set1 in enumerate(cut_sets):
            is_minimal = True
            for j, cut_set2 in enumerate(cut_sets):
                if i != j and set(cut_set2.events).issubset(set(cut_set1.events)):
                    is_minimal = False
                    break
            
            if is_minimal:
                minimal_cut_sets.append(cut_set1)
        
        return minimal_cut_sets
    
    def calculate_importance_measures(self):
        """计算重要度指标"""
        if not self.minimal_cut_sets:
            return
        
        event_probabilities = {}
        for event in self.events.values():
            event_probabilities[event.id] = event.calculate_probability()
        
        system_prob = self.calculate_system_probability()
        
        for event in self.events.values():
            if event.event_type != EventType.BASIC_EVENT:
                continue
            
            # 结构重要度（Structure Importance）
            # 这里简化计算：事件出现在多少个最小割集中
            appearance_count = sum(1 for mcs in self.minimal_cut_sets if event.id in mcs.events)
            structure_importance = appearance_count / len(self.minimal_cut_sets) if self.minimal_cut_sets else 0
            
            # 概率重要度（Probability Importance）
            # ∂P_sys / ∂P_i
            prob_importance = 0.0
            for mcs in self.minimal_cut_sets:
                if event.id in mcs.events:
                    # 简化计算：假设其他事件概率不变
                    other_prob = 1.0
                    for other_event_id in mcs.events:
                        if other_event_id != event.id:
                            other_prob *= event_probabilities.get(other_event_id, 0.0)
                    prob_importance += other_prob
            
            # 关键重要度（Critical Importance）
            event_prob = event_probabilities.get(event.id, 0.0)
            critical_importance = (prob_importance * event_prob / system_prob) if system_prob > 0 else 0
            
            event.importance_measures = {
                'structure_importance': structure_importance,
                'probability_importance': prob_importance,
                'critical_importance': critical_importance
            }
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'top_event_id': self.top_event_id,
            'events': {eid: event.to_dict() for eid, event in self.events.items()},
            'gates': {gid: gate.to_dict() for gid, gate in self.gates.items()},
            'minimal_cut_sets': [mcs.to_dict() for mcs in self.minimal_cut_sets],
            'mission_time': self.mission_time,
            'confidence_level': self.confidence_level,
            'system_probability': self.system_probability,
            'system_unavailability': self.system_unavailability,
            'mean_time_to_failure': self.mean_time_to_failure,
            'analysis_results': self.analysis_results,
            'task_profile_id': self.task_profile_id,
            'system_structure_id': self.system_structure_id,
            'generation_config': self.generation_config
        })
        return base_dict
    
    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        self.top_event_id = data.get('top_event_id', '')
        
        # 加载事件
        self.events = {}
        for eid, event_data in data.get('events', {}).items():
            event = FaultTreeEvent()
            event.from_dict(event_data)
            self.events[eid] = event
        
        # 加载逻辑门
        self.gates = {}
        for gid, gate_data in data.get('gates', {}).items():
            gate = FaultTreeGate()
            gate.from_dict(gate_data)
            self.gates[gid] = gate
        
        # 加载最小割集
        self.minimal_cut_sets = []
        for mcs_data in data.get('minimal_cut_sets', []):
            mcs = MinimalCutSet()
            mcs.from_dict(mcs_data)
            self.minimal_cut_sets.append(mcs)
        
        self.mission_time = data.get('mission_time', 8760.0)
        self.confidence_level = data.get('confidence_level', 0.95)
        self.system_probability = data.get('system_probability', 0.0)
        self.system_unavailability = data.get('system_unavailability', 0.0)
        self.mean_time_to_failure = data.get('mean_time_to_failure', 0.0)
        self.analysis_results = data.get('analysis_results', {})
        self.task_profile_id = data.get('task_profile_id', '')
        self.system_structure_id = data.get('system_structure_id', '')
        self.generation_config = data.get('generation_config', {
            'include_interface_failures': True,
            'include_module_failures': True,
            'include_environment_effects': True,
            'max_depth': 5,
            'min_probability_threshold': 1e-6
        })