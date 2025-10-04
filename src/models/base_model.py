# -*- coding: utf-8 -*-
"""
基础数据模型
Base Data Model

定义系统中所有数据模型的基类和通用接口
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


class BaseModel(ABC):
    """基础模型类，所有数据模型的父类"""
    
    def __init__(self, name: str = "", description: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_time = datetime.now()
        self.modified_time = datetime.now()
        self.version = "1.0"
        
    def update_modified_time(self):
        """更新修改时间"""
        self.modified_time = datetime.now()
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_time': self.created_time.isoformat(),
            'modified_time': self.modified_time.isoformat(),
            'version': self.version
        }
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]):
        """从字典格式加载数据"""
        self.id = data.get('id', str(uuid.uuid4()))
        self.name = data.get('name', '')
        self.description = data.get('description', '')
        self.created_time = datetime.fromisoformat(data.get('created_time', datetime.now().isoformat()))
        self.modified_time = datetime.fromisoformat(data.get('modified_time', datetime.now().isoformat()))
        self.version = data.get('version', '1.0')
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def from_json(self, json_str: str):
        """从JSON字符串加载数据"""
        data = json.loads(json_str)
        self.from_dict(data)
    
    def clone(self):
        """克隆对象"""
        data = self.to_dict()
        data['id'] = str(uuid.uuid4())  # 生成新的ID
        new_obj = self.__class__()
        new_obj.from_dict(data)
        return new_obj
    
    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
    
    def __repr__(self):
        return self.__str__()


class Point:
    """二维坐标点"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y
    
    def to_dict(self) -> Dict[str, float]:
        return {'x': self.x, 'y': self.y}
    
    def from_dict(self, data: Dict[str, float]):
        self.x = data.get('x', 0.0)
        self.y = data.get('y', 0.0)
    
    def distance_to(self, other: 'Point') -> float:
        """计算到另一个点的距离"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"


class ConnectionPoint:
    """连接点/接口点"""
    
    def __init__(self, name: str = "", position: Point = None, 
                 connection_type: str = "input", data_type: str = "signal"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.position = position or Point()
        self.connection_type = connection_type  # input, output, bidirectional
        self.data_type = data_type  # signal, data, power, control
        self.variables = []  # 关联的变量列表
        self.connected_to = []  # 连接到的其他连接点ID列表
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position.to_dict(),
            'connection_type': self.connection_type,
            'data_type': self.data_type,
            'variables': self.variables,
            'connected_to': self.connected_to
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.id = data.get('id', str(uuid.uuid4()))
        self.name = data.get('name', '')
        self.position = Point()
        self.position.from_dict(data.get('position', {}))
        self.connection_type = data.get('connection_type', 'input')
        self.data_type = data.get('data_type', 'signal')
        self.variables = data.get('variables', [])
        self.connected_to = data.get('connected_to', [])
    
    def add_variable(self, variable_name: str):
        """添加关联变量"""
        if variable_name not in self.variables:
            self.variables.append(variable_name)
    
    def remove_variable(self, variable_name: str):
        """移除关联变量"""
        if variable_name in self.variables:
            self.variables.remove(variable_name)
    
    def connect_to(self, other_point_id: str):
        """连接到另一个连接点"""
        if other_point_id not in self.connected_to:
            self.connected_to.append(other_point_id)
    
    def disconnect_from(self, other_point_id: str):
        """断开与另一个连接点的连接"""
        if other_point_id in self.connected_to:
            self.connected_to.remove(other_point_id)