#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境建模数据模型
Environment Modeling Data Model
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from .base_model import BaseModel


class EnvironmentType(Enum):
    """环境类型"""
    PHYSICAL = "physical"           # 物理环境
    NETWORK = "network"             # 网络环境
    ELECTROMAGNETIC = "electromagnetic"  # 电磁环境
    THERMAL = "thermal"             # 热环境
    VIBRATION = "vibration"         # 振动环境
    RADIATION = "radiation"         # 辐射环境
    WEATHER = "weather"             # 气象环境
    USER_BEHAVIOR = "user_behavior" # 用户行为环境
    CUSTOM = "custom"               # 自定义环境


class StressType(Enum):
    """应力类型"""
    TEMPERATURE = "temperature"     # 温度应力
    HUMIDITY = "humidity"           # 湿度应力
    PRESSURE = "pressure"           # 压力应力
    VIBRATION = "vibration"         # 振动应力
    SHOCK = "shock"                 # 冲击应力
    ELECTROMAGNETIC = "electromagnetic"  # 电磁应力
    RADIATION = "radiation"         # 辐射应力
    CORROSION = "corrosion"         # 腐蚀应力
    FATIGUE = "fatigue"             # 疲劳应力
    WEAR = "wear"                   # 磨损应力
    NETWORK_DELAY = "network_delay" # 网络延迟
    PACKET_LOSS = "packet_loss"     # 丢包
    INTERFERENCE = "interference"   # 干扰
    OVERLOAD = "overload"           # 过载
    CUSTOM = "custom"               # 自定义应力


class StressFactor:
    """应力因子"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.stress_type = StressType.TEMPERATURE
        self.description = ""
        self.base_value = 0.0       # 基准值
        self.variation_range = 0.0  # 变化范围
        self.distribution = "normal"  # 分布类型: normal, uniform, exponential
        self.time_profile = "constant"  # 时间剖面: constant, linear, sinusoidal, random
        self.duration = 0.0         # 持续时间
        self.start_time = 0.0       # 开始时间
        self.enabled = True         # 是否启用
        self.parameters = {}        # 额外参数
        self.python_code = ""       # 自定义Python代码
    
    def generate_stress_value(self, current_time: float) -> float:
        """生成应力值"""
        import random
        import math
        
        if not self.enabled:
            return self.base_value
        
        # 检查时间范围
        if current_time < self.start_time or (self.duration > 0 and current_time > self.start_time + self.duration):
            return self.base_value
        
        # 计算时间相关的变化
        time_factor = 1.0
        if self.time_profile == "linear":
            progress = (current_time - self.start_time) / max(self.duration, 1.0)
            time_factor = progress
        elif self.time_profile == "sinusoidal":
            frequency = self.parameters.get('frequency', 1.0)
            time_factor = math.sin(2 * math.pi * frequency * (current_time - self.start_time))
        elif self.time_profile == "random":
            time_factor = random.uniform(-1, 1)
        
        # 计算分布相关的变化
        if self.distribution == "normal":
            variation = random.gauss(0, self.variation_range / 3)  # 3σ规则
        elif self.distribution == "uniform":
            variation = random.uniform(-self.variation_range, self.variation_range)
        elif self.distribution == "exponential":
            variation = random.expovariate(1.0 / max(self.variation_range, 0.1))
        else:
            variation = 0.0
        
        return self.base_value + variation * time_factor
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'stress_type': self.stress_type.value,
            'description': self.description,
            'base_value': self.base_value,
            'variation_range': self.variation_range,
            'distribution': self.distribution,
            'time_profile': self.time_profile,
            'duration': self.duration,
            'start_time': self.start_time,
            'enabled': self.enabled,
            'parameters': self.parameters,
            'python_code': self.python_code
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.name = data.get('name', '')
        self.stress_type = StressType(data.get('stress_type', StressType.TEMPERATURE.value))
        self.description = data.get('description', '')
        self.base_value = data.get('base_value', 0.0)
        self.variation_range = data.get('variation_range', 0.0)
        self.distribution = data.get('distribution', 'normal')
        self.time_profile = data.get('time_profile', 'constant')
        self.duration = data.get('duration', 0.0)
        self.start_time = data.get('start_time', 0.0)
        self.enabled = data.get('enabled', True)
        self.parameters = data.get('parameters', {})
        self.python_code = data.get('python_code', '')


class EnvironmentModule(BaseModel):
    """环境模块"""
    
    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description)
        self.environment_type = EnvironmentType.PHYSICAL
        self.stress_factors = []  # 应力因子列表
        self.parameters = {}      # 环境参数
        self.python_code = ""     # Python建模代码
        self.position = {'x': 0, 'y': 0}  # 在图形界面中的位置
        self.size = {'width': 120, 'height': 80}  # 环境模块大小
        self.icon_path = ""       # 图标路径
        self.color = "#FFE4B5"    # 模块颜色
        self.affected_modules = []  # 受影响的模块ID列表
        self.enabled = True       # 是否启用
    
    def add_stress_factor(self, stress_factor: StressFactor):
        """添加应力因子"""
        self.stress_factors.append(stress_factor)
        self.update_modified_time()
    
    def remove_stress_factor(self, factor_name: str):
        """移除应力因子"""
        self.stress_factors = [sf for sf in self.stress_factors if sf.name != factor_name]
        self.update_modified_time()
    
    def get_stress_factor(self, factor_name: str) -> Optional[StressFactor]:
        """获取应力因子"""
        for sf in self.stress_factors:
            if sf.name == factor_name:
                return sf
        return None
    
    def apply_environment_stress(self, system_state: Dict[str, Any], current_time: float = 0.0) -> Dict[str, Any]:
        """施加环境应力"""
        if not self.enabled:
            return system_state
        
        modified_state = system_state.copy()
        
        # 应用应力因子
        for stress_factor in self.stress_factors:
            if not stress_factor.enabled:
                continue
            
            stress_value = stress_factor.generate_stress_value(current_time)
            
            # 对受影响的模块施加应力
            for module_id in self.affected_modules:
                if module_id in modified_state:
                    module_state = modified_state[module_id]
                    
                    # 根据应力类型修改模块状态
                    if stress_factor.stress_type == StressType.TEMPERATURE:
                        module_state['temperature'] = stress_value
                    elif stress_factor.stress_type == StressType.VIBRATION:
                        module_state['vibration_level'] = stress_value
                    elif stress_factor.stress_type == StressType.NETWORK_DELAY:
                        module_state['network_delay'] = stress_value
                    elif stress_factor.stress_type == StressType.PACKET_LOSS:
                        module_state['packet_loss_rate'] = stress_value
                    # 可以根据需要添加更多应力类型的处理
        
        # 执行自定义Python代码
        if self.python_code:
            try:
                local_vars = {
                    'system_state': system_state,
                    'modified_state': modified_state,
                    'current_time': current_time,
                    'parameters': self.parameters,
                    'stress_factors': {sf.name: sf.generate_stress_value(current_time) for sf in self.stress_factors},
                    'affected_modules': self.affected_modules
                }
                exec(self.python_code, {}, local_vars)
                modified_state = local_vars.get('modified_state', modified_state)
            except Exception as e:
                print(f"执行环境模块 {self.name} 的Python代码时出错: {e}")
        
        return modified_state
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            'environment_type': self.environment_type.value,
            'stress_factors': [sf.to_dict() for sf in self.stress_factors],
            'parameters': self.parameters,
            'python_code': self.python_code,
            'position': self.position,
            'size': self.size,
            'icon_path': self.icon_path,
            'color': self.color,
            'affected_modules': self.affected_modules,
            'enabled': self.enabled
        })
        return base_dict
    
    def from_dict(self, data: Dict[str, Any]):
        super().from_dict(data)
        self.environment_type = EnvironmentType(data.get('environment_type', EnvironmentType.PHYSICAL.value))
        
        # 加载应力因子
        self.stress_factors = []
        for sf_data in data.get('stress_factors', []):
            sf = StressFactor()
            sf.from_dict(sf_data)
            self.stress_factors.append(sf)
        
        self.parameters = data.get('parameters', {})
        self.python_code = data.get('python_code', '')
        self.position = data.get('position', {'x': 0, 'y': 0})
        self.size = data.get('size', {'width': 120, 'height': 80})
        self.icon_path = data.get('icon_path', '')
        self.color = data.get('color', '#FFE4B5')
        self.affected_modules = data.get('affected_modules', [])
        self.enabled = data.get('enabled', True)


# 预定义环境模块模板
ENVIRONMENT_TEMPLATES = {
    "高温环境": {
        "name": "高温环境",
        "description": "高温工作环境，可能导致设备过热",
        "environment_type": "thermal",
        "stress_factors": [
            {
                "name": "环境温度",
                "stress_type": "temperature",
                "description": "环境温度变化",
                "base_value": 60.0,
                "variation_range": 20.0,
                "distribution": "normal",
                "time_profile": "sinusoidal",
                "parameters": {"frequency": 0.1}
            }
        ],
        "parameters": {
            "max_temperature": 80.0,
            "min_temperature": 40.0
        },
        "color": "#FF6B6B"
    },
    
    "振动环境": {
        "name": "振动环境",
        "description": "机械振动环境，可能影响精密设备",
        "environment_type": "vibration",
        "stress_factors": [
            {
                "name": "振动加速度",
                "stress_type": "vibration",
                "description": "振动加速度变化",
                "base_value": 2.0,
                "variation_range": 1.0,
                "distribution": "uniform",
                "time_profile": "random"
            }
        ],
        "parameters": {
            "frequency_range": "10-1000Hz",
            "amplitude": "±2g"
        },
        "color": "#4ECDC4"
    },
    
    "网络延迟环境": {
        "name": "网络延迟环境",
        "description": "网络通信延迟环境",
        "environment_type": "network",
        "stress_factors": [
            {
                "name": "网络延迟",
                "stress_type": "network_delay",
                "description": "网络通信延迟",
                "base_value": 50.0,
                "variation_range": 30.0,
                "distribution": "exponential",
                "time_profile": "random"
            },
            {
                "name": "丢包率",
                "stress_type": "packet_loss",
                "description": "网络丢包率",
                "base_value": 0.01,
                "variation_range": 0.02,
                "distribution": "uniform",
                "time_profile": "constant"
            }
        ],
        "parameters": {
            "bandwidth": "100Mbps",
            "protocol": "TCP/IP"
        },
        "color": "#45B7D1"
    },
    
    "电磁干扰环境": {
        "name": "电磁干扰环境",
        "description": "电磁干扰环境，可能影响电子设备",
        "environment_type": "electromagnetic",
        "stress_factors": [
            {
                "name": "电磁场强度",
                "stress_type": "electromagnetic",
                "description": "电磁场强度变化",
                "base_value": 10.0,
                "variation_range": 5.0,
                "distribution": "normal",
                "time_profile": "sinusoidal",
                "parameters": {"frequency": 0.5}
            }
        ],
        "parameters": {
            "frequency_band": "1-10GHz",
            "polarization": "vertical"
        },
        "color": "#F7DC6F"
    },
    
    "恶劣天气环境": {
        "name": "恶劣天气环境",
        "description": "恶劣天气条件，包括风雨雪等",
        "environment_type": "weather",
        "stress_factors": [
            {
                "name": "风速",
                "stress_type": "custom",
                "description": "风速变化",
                "base_value": 15.0,
                "variation_range": 10.0,
                "distribution": "normal",
                "time_profile": "random"
            },
            {
                "name": "降雨量",
                "stress_type": "custom",
                "description": "降雨量",
                "base_value": 5.0,
                "variation_range": 8.0,
                "distribution": "exponential",
                "time_profile": "linear"
            }
        ],
        "parameters": {
            "visibility": "low",
            "humidity": "high"
        },
        "color": "#85C1E9"
    }
}