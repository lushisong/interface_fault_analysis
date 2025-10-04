# -*- coding: utf-8 -*-
"""
属性面板
Property Panel

显示和编辑选中对象的属性
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal


class PropertyPanel(QWidget):
    """属性面板组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("属性面板"))
        self.setLayout(layout)
    
    def show_item_properties(self, item_type, item_id, system):
        """显示项目属性"""
        print(f"显示 {item_type} {item_id} 的属性")