# -*- coding: utf-8 -*-
"""
项目管理器
Project Manager

负责项目的创建、保存、加载等操作
"""

import os
import json
from typing import Optional
from ..models.system_model import SystemStructure


class ProjectManager:
    """项目管理器"""
    
    def __init__(self):
        self.current_system: Optional[SystemStructure] = None
        self.current_file_path: Optional[str] = None
        self.is_modified = False
    
    def set_current_system(self, system: SystemStructure):
        """设置当前系统"""
        self.current_system = system
        self.is_modified = True
    
    def create_new_project(self, name: str = "新项目", description: str = "") -> SystemStructure:
        """创建新项目"""
        system = SystemStructure(name, description)
        self.set_current_system(system)
        self.current_file_path = None
        return system
    
    def save_project(self) -> bool:
        """保存项目"""
        if not self.current_file_path:
            raise ValueError("没有指定保存路径，请使用 save_project_as")
        
        return self.save_project_as(self.current_file_path)
    
    def save_project_as(self, file_path: str) -> bool:
        """另存为项目"""
        if not self.current_system:
            raise ValueError("没有当前项目可保存")
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存为JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_system.to_dict(), f, 
                         ensure_ascii=False, indent=2)
            
            self.current_file_path = file_path
            self.is_modified = False
            return True
            
        except Exception as e:
            print(f"保存项目失败: {e}")
            return False
    
    def load_project(self, file_path: str) -> SystemStructure:
        """加载项目"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"项目文件不存在: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            system = SystemStructure()
            system.from_dict(data)
            
            self.current_system = system
            self.current_file_path = file_path
            self.is_modified = False
            
            return system
            
        except Exception as e:
            raise Exception(f"加载项目失败: {e}")
    
    def has_unsaved_changes(self) -> bool:
        """检查是否有未保存的更改"""
        return self.is_modified
    
    def mark_modified(self):
        """标记为已修改"""
        self.is_modified = True
    
    def get_current_system(self) -> Optional[SystemStructure]:
        """获取当前系统"""
        return self.current_system
    
    def get_current_file_path(self) -> Optional[str]:
        """获取当前文件路径"""
        return self.current_file_path