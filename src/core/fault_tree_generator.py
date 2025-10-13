#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
故障树生成器
Fault Tree Generator
"""

from typing import Dict, List, Any, Optional, Set
from ..models.fault_tree_model import (FaultTree, FaultTreeEvent, FaultTreeGate,
                                     EventType, GateType)
from ..models.system_model import SystemStructure
from ..models.task_profile_model import TaskProfile
from ..models.interface_model import Interface, FailureMode


class FaultTreeGenerator:
    """故障树生成器"""
    
    def __init__(self):
        self.system = None
        self.task_profile = None
        self.fault_tree = None
        self.generation_config = {
            'include_interface_failures': True,
            'include_module_failures': True,
            'include_environment_effects': True,
            'max_depth': 5,
            'min_probability_threshold': 1e-6
        }
    
    def generate_fault_tree(self, system: SystemStructure, task_profile: TaskProfile,
                          config: Dict[str, Any] = None) -> FaultTree:
        """生成故障树"""
        self.system = system
        self.task_profile = task_profile
        if config:
            self.generation_config.update(config)
        
        # 创建故障树
        self.fault_tree = FaultTree(
            name=f"{task_profile.name}_故障树",
            description=f"基于任务剖面 '{task_profile.name}' 生成的故障树"
        )

        self.fault_tree.task_profile_id = task_profile.id
        self.fault_tree.system_structure_id = system.id
        mission_seconds = getattr(task_profile, 'total_duration', None)
        if mission_seconds is None:
            mission_seconds = getattr(task_profile, 'duration', 0.0)
        try:
            mission_seconds = float(mission_seconds)
        except (TypeError, ValueError):
            mission_seconds = 0.0

        self.fault_tree.mission_time = mission_seconds / 3600.0  # 转换为小时
        self.fault_tree.generation_config = self.generation_config.copy()
        
        # 创建顶事件
        top_event = self._create_top_event()
        self.fault_tree.add_event(top_event)
        self.fault_tree.top_event_id = top_event.id
        
        # 生成故障树结构
        self._generate_fault_tree_structure(top_event)
        
        # 设置事件概率
        self._set_event_probabilities()
        
        # 布局故障树
        self._layout_fault_tree()
        
        return self.fault_tree
    
    def _create_top_event(self) -> FaultTreeEvent:
        """创建顶事件"""
        top_event = FaultTreeEvent(
            name=f"{self.task_profile.name}失败",
            event_type=EventType.TOP_EVENT
        )
        top_event.description = f"任务 '{self.task_profile.name}' 执行失败"
        return top_event
    
    def _generate_fault_tree_structure(self, top_event: FaultTreeEvent):
        """生成故障树结构"""
        # 基于任务成功判据生成第一层分解
        if self.task_profile.success_criteria:
            self._generate_success_criteria_failures(top_event)
        else:
            # 如果没有成功判据，基于系统结构生成
            self._generate_system_structure_failures(top_event)
    
    def _generate_success_criteria_failures(self, top_event: FaultTreeEvent):
        """基于成功判据生成失效事件"""
        if len(self.task_profile.success_criteria) == 1:
            # 只有一个成功判据，直接连接
            criteria = self.task_profile.success_criteria[0]
            criteria_failure_event = self._create_criteria_failure_event(criteria)
            self.fault_tree.add_event(criteria_failure_event)
            
            # 进一步分解判据失效
            self._decompose_criteria_failure(criteria_failure_event, criteria)
        
        else:
            # 多个成功判据，创建或门（任一判据失效导致任务失败）
            or_gate = FaultTreeGate(
                name="成功判据失效",
                gate_type=GateType.OR
            )
            or_gate.output_event_id = top_event.id
            self.fault_tree.add_gate(or_gate)
            
            for criteria in self.task_profile.success_criteria:
                criteria_failure_event = self._create_criteria_failure_event(criteria)
                self.fault_tree.add_event(criteria_failure_event)
                or_gate.input_events.append(criteria_failure_event.id)
                
                # 进一步分解判据失效
                self._decompose_criteria_failure(criteria_failure_event, criteria)
    
    def _create_criteria_failure_event(self, criteria) -> FaultTreeEvent:
        """创建成功判据失效事件"""
        event = FaultTreeEvent(
            name=f"{criteria.name}失效",
            event_type=EventType.INTERMEDIATE_EVENT
        )
        event.description = f"成功判据 '{criteria.name}' 不满足"
        return event
    
    def _decompose_criteria_failure(self, criteria_event: FaultTreeEvent, criteria):
        """分解成功判据失效"""
        # 如果判据关联了模块，分解为模块失效
        if criteria.module_id and criteria.module_id in self.system.modules:
            module = self.system.modules[criteria.module_id]
            
            # 创建模块失效事件
            module_failure_event = FaultTreeEvent(
                name=f"{module.name}失效",
                event_type=EventType.INTERMEDIATE_EVENT
            )
            module_failure_event.description = f"模块 '{module.name}' 失效导致判据不满足"
            module_failure_event.module_id = criteria.module_id
            self.fault_tree.add_event(module_failure_event)
            
            # 连接到判据失效事件
            gate = FaultTreeGate(
                name=f"{criteria.name}失效门",
                gate_type=GateType.OR
            )
            gate.output_event_id = criteria_event.id
            gate.input_events.append(module_failure_event.id)
            self.fault_tree.add_gate(gate)
            
            # 进一步分解模块失效
            self._decompose_module_failure(module_failure_event, module)
    
    def _decompose_module_failure(self, module_event: FaultTreeEvent, module):
        """分解模块失效"""
        failure_events = []
        
        # 1. 模块内部失效
        if self.generation_config.get('include_module_failures', True):
            internal_failure_event = FaultTreeEvent(
                name=f"{module.name}内部失效",
                event_type=EventType.BASIC_EVENT
            )
            internal_failure_event.description = f"模块 '{module.name}' 内部组件失效"
            internal_failure_event.module_id = module.id
            internal_failure_event.failure_rate = getattr(module, 'failure_rate', 1e-5)  # 默认失效率
            self.fault_tree.add_event(internal_failure_event)
            failure_events.append(internal_failure_event.id)
        
        # 2. 接口失效
        if self.generation_config.get('include_interface_failures', True):
            interface_failures = self._get_module_interface_failures(module)
            failure_events.extend(interface_failures)
        
        # 3. 环境影响
        if self.generation_config.get('include_environment_effects', True):
            env_failures = self._get_module_environment_failures(module)
            failure_events.extend(env_failures)
        
        # 创建逻辑门连接失效事件
        if failure_events:
            if len(failure_events) == 1:
                # 只有一个失效原因，直接连接
                gate = FaultTreeGate(
                    name=f"{module.name}失效门",
                    gate_type=GateType.OR
                )
                gate.output_event_id = module_event.id
                gate.input_events = failure_events
                self.fault_tree.add_gate(gate)
            else:
                # 多个失效原因，使用或门
                gate = FaultTreeGate(
                    name=f"{module.name}失效门",
                    gate_type=GateType.OR
                )
                gate.output_event_id = module_event.id
                gate.input_events = failure_events
                self.fault_tree.add_gate(gate)
    
    def _get_module_interface_failures(self, module) -> List[str]:
        """获取模块相关的接口失效事件"""
        interface_failure_events = []
        
        # 查找与该模块相关的连接
        for connection in self.system.connections.values():
            if connection.source_module_id == module.id or connection.target_module_id == module.id:
                # 查找连接使用的接口
                if connection.interface_id and connection.interface_id in self.system.interfaces:
                    interface = self.system.interfaces[connection.interface_id]
                    
                    # 为接口的每个失效模式创建事件
                    for failure_mode in interface.failure_modes:
                        if failure_mode.enabled:
                            failure_event = FaultTreeEvent(
                                name=f"{interface.name}_{failure_mode.name}",
                                event_type=EventType.BASIC_EVENT
                            )
                            failure_event.description = f"接口 '{interface.name}' 发生 '{failure_mode.name}' 失效"
                            failure_event.interface_id = interface.id
                            failure_event.failure_mode_id = failure_mode.id
                            failure_event.failure_rate = failure_mode.failure_rate
                            
                            self.fault_tree.add_event(failure_event)
                            interface_failure_events.append(failure_event.id)
        
        return interface_failure_events
    
    def _get_module_environment_failures(self, module) -> List[str]:
        """获取模块相关的环境失效事件"""
        env_failure_events = []
        
        # 查找影响该模块的环境
        if hasattr(self.system, 'environment_models'):
            for env_id, env_module in self.system.environment_models.items():
                if module.id in env_module.affected_modules:
                    # 为每个应力因子创建失效事件
                    for stress_factor in env_module.stress_factors:
                        if stress_factor.enabled:
                            failure_event = FaultTreeEvent(
                                name=f"{module.name}_{stress_factor.name}失效",
                                event_type=EventType.BASIC_EVENT
                            )
                            failure_event.description = f"模块 '{module.name}' 因 '{stress_factor.name}' 应力失效"
                            failure_event.module_id = module.id
                            
                            # 根据应力类型估算失效率
                            base_failure_rate = 1e-6  # 基础失效率
                            stress_multiplier = 1.0
                            
                            if stress_factor.base_value > 0:
                                # 简化的应力-失效率关系
                                if stress_factor.stress_type.value == "temperature":
                                    # 温度每升高10度，失效率增加一倍（阿伦尼乌斯模型简化）
                                    if stress_factor.base_value > 25:  # 假设25度为基准温度
                                        stress_multiplier = 2 ** ((stress_factor.base_value - 25) / 10)
                                elif stress_factor.stress_type.value == "vibration":
                                    # 振动应力线性关系
                                    stress_multiplier = 1 + stress_factor.base_value * 0.1
                            
                            failure_event.failure_rate = base_failure_rate * stress_multiplier
                            
                            self.fault_tree.add_event(failure_event)
                            env_failure_events.append(failure_event.id)
        
        return env_failure_events
    
    def _generate_system_structure_failures(self, top_event: FaultTreeEvent):
        """基于系统结构生成失效事件"""
        # 如果没有成功判据，为每个模块创建失效事件
        module_failure_events = []
        
        for module_id, module in self.system.modules.items():
            module_failure_event = FaultTreeEvent(
                name=f"{module.name}失效",
                event_type=EventType.INTERMEDIATE_EVENT
            )
            module_failure_event.description = f"模块 '{module.name}' 失效"
            module_failure_event.module_id = module_id
            self.fault_tree.add_event(module_failure_event)
            module_failure_events.append(module_failure_event.id)
            
            # 分解模块失效
            self._decompose_module_failure(module_failure_event, module)
        
        # 创建顶层逻辑门（假设任一模块失效导致系统失效）
        if module_failure_events:
            top_gate = FaultTreeGate(
                name="系统失效门",
                gate_type=GateType.OR
            )
            top_gate.output_event_id = top_event.id
            top_gate.input_events = module_failure_events
            self.fault_tree.add_gate(top_gate)
    
    def _set_event_probabilities(self):
        """设置事件概率"""
        mission_time_hours = self.fault_tree.mission_time
        
        for event in self.fault_tree.events.values():
            if event.event_type == EventType.BASIC_EVENT:
                if event.failure_rate > 0:
                    event.mission_time = mission_time_hours
                    event.calculate_probability()
                elif event.probability == 0.0:
                    # 设置默认概率
                    event.probability = 1e-4  # 默认概率
    
    def _layout_fault_tree(self):
        """布局故障树"""
        # 简单的层次布局算法
        if not self.fault_tree.top_event_id:
            return
        
        # 计算每个事件的层级
        event_levels = self._calculate_event_levels()
        
        # 按层级布局
        level_width = 200  # 层级间距
        node_width = 150   # 节点间距
        start_x = 100
        start_y = 100
        
        # 按层级分组
        levels = {}
        for event_id, level in event_levels.items():
            if level not in levels:
                levels[level] = []
            levels[level].append(event_id)
        
        # 布局每一层
        for level, event_ids in levels.items():
            y = start_y + level * level_width
            total_width = len(event_ids) * node_width
            start_x_level = start_x - total_width // 2
            
            for i, event_id in enumerate(event_ids):
                x = start_x_level + i * node_width
                
                if event_id in self.fault_tree.events:
                    self.fault_tree.events[event_id].position = {'x': x, 'y': y}
        
        # 布局逻辑门（放在输入输出事件之间）
        for gate in self.fault_tree.gates.values():
            if gate.output_event_id in self.fault_tree.events and gate.input_events:
                output_event = self.fault_tree.events[gate.output_event_id]
                
                # 计算输入事件的平均位置
                avg_x = 0
                avg_y = 0
                valid_inputs = 0
                
                for input_event_id in gate.input_events:
                    if input_event_id in self.fault_tree.events:
                        input_event = self.fault_tree.events[input_event_id]
                        avg_x += input_event.position['x']
                        avg_y += input_event.position['y']
                        valid_inputs += 1
                
                if valid_inputs > 0:
                    avg_x //= valid_inputs
                    avg_y //= valid_inputs
                    
                    # 逻辑门位置在输出事件和输入事件平均位置之间
                    gate.position = {
                        'x': (output_event.position['x'] + avg_x) // 2,
                        'y': (output_event.position['y'] + avg_y) // 2
                    }
    
    def _calculate_event_levels(self) -> Dict[str, int]:
        """计算事件层级"""
        event_levels = {}
        
        if not self.fault_tree.top_event_id:
            return event_levels
        
        # 从顶事件开始，广度优先搜索
        queue = [(self.fault_tree.top_event_id, 0)]
        visited = set()
        
        while queue:
            event_id, level = queue.pop(0)
            
            if event_id in visited:
                continue
            
            visited.add(event_id)
            event_levels[event_id] = level
            
            # 查找输入到该事件的逻辑门
            for gate in self.fault_tree.gates.values():
                if gate.output_event_id == event_id:
                    for input_event_id in gate.input_events:
                        if input_event_id not in visited:
                            queue.append((input_event_id, level + 1))
        
        return event_levels