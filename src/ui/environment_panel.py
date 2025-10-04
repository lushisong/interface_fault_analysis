#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境建模面板
Environment Modeling Panel
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QTabWidget,
                             QTableWidget, QTableWidgetItem, QGroupBox,
                             QLabel, QLineEdit, QTextEdit, QComboBox,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
                             QFormLayout, QGridLayout, QHeaderView, QMessageBox,
                             QDialog, QDialogButtonBox, QFrame, QColorDialog,
                             QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor

from ..models.environment_model import (EnvironmentModule, StressFactor, EnvironmentType,
                                      StressType, ENVIRONMENT_TEMPLATES)


class StressFactorDialog(QDialog):
    """应力因子编辑对话框"""
    
    def __init__(self, stress_factor=None, parent=None):
        super().__init__(parent)
        self.stress_factor = stress_factor or StressFactor()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("应力因子编辑")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        
        self.stress_type_combo = QComboBox()
        for stress_type in StressType:
            self.stress_type_combo.addItem(stress_type.value, stress_type)
        
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(True)
        
        basic_layout.addRow("名称:", self.name_edit)
        basic_layout.addRow("描述:", self.description_edit)
        basic_layout.addRow("应力类型:", self.stress_type_combo)
        basic_layout.addRow("启用:", self.enabled_check)
        
        # 数值配置
        value_group = QGroupBox("数值配置")
        value_layout = QFormLayout(value_group)
        
        self.base_value_spin = QDoubleSpinBox()
        self.base_value_spin.setRange(-999999, 999999)
        self.base_value_spin.setDecimals(3)
        
        self.variation_range_spin = QDoubleSpinBox()
        self.variation_range_spin.setRange(0, 999999)
        self.variation_range_spin.setDecimals(3)
        
        self.distribution_combo = QComboBox()
        self.distribution_combo.addItems(["normal", "uniform", "exponential"])
        
        value_layout.addRow("基准值:", self.base_value_spin)
        value_layout.addRow("变化范围:", self.variation_range_spin)
        value_layout.addRow("分布类型:", self.distribution_combo)
        
        # 时间配置
        time_group = QGroupBox("时间配置")
        time_layout = QFormLayout(time_group)
        
        self.time_profile_combo = QComboBox()
        self.time_profile_combo.addItems(["constant", "linear", "sinusoidal", "random"])
        
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(0, 999999)
        self.start_time_spin.setSuffix(" 秒")
        
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0, 999999)
        self.duration_spin.setSuffix(" 秒")
        
        time_layout.addRow("时间剖面:", self.time_profile_combo)
        time_layout.addRow("开始时间:", self.start_time_spin)
        time_layout.addRow("持续时间:", self.duration_spin)
        
        # Python代码
        code_group = QGroupBox("自定义Python代码")
        code_layout = QVBoxLayout(code_group)
        
        self.code_edit = QTextEdit()
        self.code_edit.setPlainText("""# 自定义应力因子代码
# 可用变量: current_time, base_value, variation_range, parameters
# 返回应力值

import random
import math

# 示例: 正弦波变化
# stress_value = base_value + variation_range * math.sin(2 * math.pi * 0.1 * current_time)

stress_value = base_value
""")
        code_layout.addWidget(self.code_edit)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 布局
        layout.addWidget(basic_group)
        layout.addWidget(value_group)
        layout.addWidget(time_group)
        layout.addWidget(code_group)
        layout.addWidget(button_box)
    
    def load_data(self):
        """加载数据"""
        self.name_edit.setText(self.stress_factor.name)
        self.description_edit.setPlainText(self.stress_factor.description)
        
        # 设置应力类型
        for i in range(self.stress_type_combo.count()):
            if self.stress_type_combo.itemData(i) == self.stress_factor.stress_type:
                self.stress_type_combo.setCurrentIndex(i)
                break
        
        self.enabled_check.setChecked(self.stress_factor.enabled)
        self.base_value_spin.setValue(self.stress_factor.base_value)
        self.variation_range_spin.setValue(self.stress_factor.variation_range)
        
        # 设置分布类型
        index = self.distribution_combo.findText(self.stress_factor.distribution)
        if index >= 0:
            self.distribution_combo.setCurrentIndex(index)
        
        # 设置时间剖面
        index = self.time_profile_combo.findText(self.stress_factor.time_profile)
        if index >= 0:
            self.time_profile_combo.setCurrentIndex(index)
        
        self.start_time_spin.setValue(self.stress_factor.start_time)
        self.duration_spin.setValue(self.stress_factor.duration)
        
        if self.stress_factor.python_code:
            self.code_edit.setPlainText(self.stress_factor.python_code)
    
    def save_data(self):
        """保存数据"""
        self.stress_factor.name = self.name_edit.text()
        self.stress_factor.description = self.description_edit.toPlainText()
        self.stress_factor.stress_type = self.stress_type_combo.currentData()
        self.stress_factor.enabled = self.enabled_check.isChecked()
        self.stress_factor.base_value = self.base_value_spin.value()
        self.stress_factor.variation_range = self.variation_range_spin.value()
        self.stress_factor.distribution = self.distribution_combo.currentText()
        self.stress_factor.time_profile = self.time_profile_combo.currentText()
        self.stress_factor.start_time = self.start_time_spin.value()
        self.stress_factor.duration = self.duration_spin.value()
        self.stress_factor.python_code = self.code_edit.toPlainText()
    
    def accept(self):
        """确认"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入应力因子名称")
            return
        
        self.save_data()
        super().accept()


class EnvironmentModuleDialog(QDialog):
    """环境模块编辑对话框"""
    
    def __init__(self, env_module=None, system_modules=None, parent=None):
        super().__init__(parent)
        self.env_module = env_module or EnvironmentModule()
        self.system_modules = system_modules or {}
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("环境模块编辑")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 标签页
        tab_widget = QTabWidget()
        
        # 基本信息标签页
        basic_tab = self.create_basic_tab()
        tab_widget.addTab(basic_tab, "基本信息")
        
        # 应力因子标签页
        stress_tab = self.create_stress_tab()
        tab_widget.addTab(stress_tab, "应力因子")
        
        # 影响模块标签页
        modules_tab = self.create_modules_tab()
        tab_widget.addTab(modules_tab, "影响模块")
        
        # Python代码标签页
        code_tab = self.create_code_tab()
        tab_widget.addTab(code_tab, "Python代码")
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(tab_widget)
        layout.addWidget(button_box)
    
    def create_basic_tab(self):
        """创建基本信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        
        self.env_type_combo = QComboBox()
        for env_type in EnvironmentType:
            self.env_type_combo.addItem(env_type.value, env_type)
        
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(True)
        
        # 颜色选择
        color_layout = QHBoxLayout()
        self.color_label = QLabel()
        self.color_label.setFixedSize(30, 20)
        self.color_label.setStyleSheet("background-color: #FFE4B5; border: 1px solid black;")
        self.color_btn = QPushButton("选择颜色")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_label)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        
        form_layout.addRow("名称:", self.name_edit)
        form_layout.addRow("描述:", self.description_edit)
        form_layout.addRow("环境类型:", self.env_type_combo)
        form_layout.addRow("启用:", self.enabled_check)
        form_layout.addRow("颜色:", color_layout)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        return widget
    
    def create_stress_tab(self):
        """创建应力因子标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_stress_btn = QPushButton("添加应力因子")
        self.add_stress_btn.clicked.connect(self.add_stress_factor)
        
        self.edit_stress_btn = QPushButton("编辑应力因子")
        self.edit_stress_btn.clicked.connect(self.edit_stress_factor)
        self.edit_stress_btn.setEnabled(False)
        
        self.remove_stress_btn = QPushButton("删除应力因子")
        self.remove_stress_btn.clicked.connect(self.remove_stress_factor)
        self.remove_stress_btn.setEnabled(False)
        
        toolbar_layout.addWidget(self.add_stress_btn)
        toolbar_layout.addWidget(self.edit_stress_btn)
        toolbar_layout.addWidget(self.remove_stress_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # 应力因子表格
        self.stress_table = QTableWidget()
        self.stress_table.setColumnCount(5)
        self.stress_table.setHorizontalHeaderLabels([
            "名称", "类型", "基准值", "变化范围", "启用"
        ])
        
        header = self.stress_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.stress_table.itemSelectionChanged.connect(self.on_stress_selected)
        self.stress_table.itemDoubleClicked.connect(self.edit_stress_factor)
        
        layout.addWidget(self.stress_table)
        
        return widget
    
    def create_modules_tab(self):
        """创建影响模块标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("选择受此环境影响的系统模块:")
        layout.addWidget(label)
        
        self.modules_list = QListWidget()
        self.modules_list.setSelectionMode(QListWidget.MultiSelection)
        
        # 添加系统模块到列表
        for module_id, module in self.system_modules.items():
            item = QListWidgetItem(f"{module.name} ({module_id})")
            item.setData(Qt.UserRole, module_id)
            self.modules_list.addItem(item)
        
        layout.addWidget(self.modules_list)
        
        return widget
    
    def create_code_tab(self):
        """创建Python代码标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("自定义环境应力施加代码:")
        layout.addWidget(label)
        
        self.code_edit = QTextEdit()
        self.code_edit.setPlainText("""# 自定义环境应力施加代码
# 可用变量: 
#   system_state - 系统状态字典
#   modified_state - 修改后的系统状态字典
#   current_time - 当前时间
#   parameters - 环境参数
#   stress_factors - 应力因子值字典
#   affected_modules - 受影响的模块ID列表

# 示例: 对受影响的模块施加温度应力
for module_id in affected_modules:
    if module_id in modified_state:
        # 获取温度应力值
        temperature_stress = stress_factors.get('环境温度', 25.0)
        
        # 修改模块状态
        modified_state[module_id]['temperature'] = temperature_stress
        
        # 如果温度过高，降低模块可靠性
        if temperature_stress > 70:
            reliability_factor = max(0.5, 1.0 - (temperature_stress - 70) / 100)
            modified_state[module_id]['reliability'] = modified_state[module_id].get('reliability', 1.0) * reliability_factor
""")
        layout.addWidget(self.code_edit)
        
        return widget
    
    def choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor(QColor(self.env_module.color), self)
        if color.isValid():
            self.env_module.color = color.name()
            self.color_label.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
    
    def load_data(self):
        """加载数据"""
        self.name_edit.setText(self.env_module.name)
        self.description_edit.setPlainText(self.env_module.description)
        
        # 设置环境类型
        for i in range(self.env_type_combo.count()):
            if self.env_type_combo.itemData(i) == self.env_module.environment_type:
                self.env_type_combo.setCurrentIndex(i)
                break
        
        self.enabled_check.setChecked(self.env_module.enabled)
        
        # 设置颜色
        self.color_label.setStyleSheet(f"background-color: {self.env_module.color}; border: 1px solid black;")
        
        # 加载应力因子
        self.refresh_stress_table()
        
        # 选中受影响的模块
        for i in range(self.modules_list.count()):
            item = self.modules_list.item(i)
            module_id = item.data(Qt.UserRole)
            if module_id in self.env_module.affected_modules:
                item.setSelected(True)
        
        # 加载Python代码
        if self.env_module.python_code:
            self.code_edit.setPlainText(self.env_module.python_code)
    
    def refresh_stress_table(self):
        """刷新应力因子表格"""
        self.stress_table.setRowCount(len(self.env_module.stress_factors))
        
        for row, stress_factor in enumerate(self.env_module.stress_factors):
            self.stress_table.setItem(row, 0, QTableWidgetItem(stress_factor.name))
            self.stress_table.setItem(row, 1, QTableWidgetItem(stress_factor.stress_type.value))
            self.stress_table.setItem(row, 2, QTableWidgetItem(str(stress_factor.base_value)))
            self.stress_table.setItem(row, 3, QTableWidgetItem(str(stress_factor.variation_range)))
            self.stress_table.setItem(row, 4, QTableWidgetItem("是" if stress_factor.enabled else "否"))
    
    def add_stress_factor(self):
        """添加应力因子"""
        dialog = StressFactorDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.env_module.add_stress_factor(dialog.stress_factor)
            self.refresh_stress_table()
    
    def edit_stress_factor(self):
        """编辑应力因子"""
        row = self.stress_table.currentRow()
        if row < 0 or row >= len(self.env_module.stress_factors):
            return
        
        stress_factor = self.env_module.stress_factors[row]
        dialog = StressFactorDialog(stress_factor, self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_stress_table()
    
    def remove_stress_factor(self):
        """删除应力因子"""
        row = self.stress_table.currentRow()
        if row < 0 or row >= len(self.env_module.stress_factors):
            return
        
        stress_factor = self.env_module.stress_factors[row]
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除应力因子 '{stress_factor.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.env_module.remove_stress_factor(stress_factor.name)
            self.refresh_stress_table()
    
    def on_stress_selected(self):
        """应力因子选择改变"""
        has_selection = len(self.stress_table.selectedItems()) > 0
        self.edit_stress_btn.setEnabled(has_selection)
        self.remove_stress_btn.setEnabled(has_selection)
    
    def save_data(self):
        """保存数据"""
        self.env_module.name = self.name_edit.text()
        self.env_module.description = self.description_edit.toPlainText()
        self.env_module.environment_type = self.env_type_combo.currentData()
        self.env_module.enabled = self.enabled_check.isChecked()
        
        # 保存受影响的模块
        self.env_module.affected_modules = []
        for i in range(self.modules_list.count()):
            item = self.modules_list.item(i)
            if item.isSelected():
                module_id = item.data(Qt.UserRole)
                self.env_module.affected_modules.append(module_id)
        
        # 保存Python代码
        self.env_module.python_code = self.code_edit.toPlainText()
    
    def accept(self):
        """确认"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入环境模块名称")
            return
        
        self.save_data()
        super().accept()


class EnvironmentPanel(QWidget):
    """环境建模面板"""
    
    environment_changed = pyqtSignal(object)  # 环境改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_environment = None
        self.project_manager = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：环境模块列表
        left_widget = self.create_environment_list()
        left_widget.setMaximumWidth(300)
        
        # 右侧：环境模块编辑器
        right_widget = self.create_environment_editor()
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
    
    def create_environment_list(self):
        """创建环境模块列表"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题
        title_label = QLabel("环境模块列表")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.new_env_btn = QPushButton("新建")
        self.new_env_btn.clicked.connect(self.new_environment)
        
        self.template_btn = QPushButton("从模板创建")
        self.template_btn.clicked.connect(self.create_from_template)
        
        self.delete_env_btn = QPushButton("删除")
        self.delete_env_btn.clicked.connect(self.delete_environment)
        self.delete_env_btn.setEnabled(False)
        
        toolbar_layout.addWidget(self.new_env_btn)
        toolbar_layout.addWidget(self.template_btn)
        toolbar_layout.addWidget(self.delete_env_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # 环境模块树
        self.env_tree = QTreeWidget()
        self.env_tree.setHeaderLabel("环境模块")
        self.env_tree.itemSelectionChanged.connect(self.on_environment_selected)
        layout.addWidget(self.env_tree)
        
        return widget
    
    def create_environment_editor(self):
        """创建环境模块编辑器"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题栏
        title_layout = QHBoxLayout()
        self.env_title_label = QLabel("请选择环境模块")
        self.env_title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_layout.addWidget(self.env_title_label)
        title_layout.addStretch()
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_environment)
        self.save_btn.setEnabled(False)
        
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.clicked.connect(self.edit_environment)
        self.edit_btn.setEnabled(False)
        
        title_layout.addWidget(self.save_btn)
        title_layout.addWidget(self.edit_btn)
        
        layout.addLayout(title_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 环境信息显示
        self.info_widget = self.create_info_widget()
        layout.addWidget(self.info_widget)
        
        return widget
    
    def create_info_widget(self):
        """创建信息显示组件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.name_label = QLabel("-")
        self.description_label = QLabel("-")
        self.type_label = QLabel("-")
        self.enabled_label = QLabel("-")
        
        basic_layout.addRow("名称:", self.name_label)
        basic_layout.addRow("描述:", self.description_label)
        basic_layout.addRow("类型:", self.type_label)
        basic_layout.addRow("启用:", self.enabled_label)
        
        # 应力因子
        stress_group = QGroupBox("应力因子")
        stress_layout = QVBoxLayout(stress_group)
        
        self.stress_table = QTableWidget()
        self.stress_table.setColumnCount(4)
        self.stress_table.setHorizontalHeaderLabels([
            "名称", "类型", "基准值", "变化范围"
        ])
        
        header = self.stress_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        stress_layout.addWidget(self.stress_table)
        
        # 影响模块
        modules_group = QGroupBox("影响模块")
        modules_layout = QVBoxLayout(modules_group)
        
        self.modules_list = QListWidget()
        modules_layout.addWidget(self.modules_list)
        
        layout.addWidget(basic_group)
        layout.addWidget(stress_group)
        layout.addWidget(modules_group)
        
        return widget
    
    def set_project_manager(self, project_manager):
        """设置项目管理器"""
        self.project_manager = project_manager
        self.refresh_environment_list()
    
    def refresh_environment_list(self):
        """刷新环境模块列表"""
        self.env_tree.clear()
        
        if not self.project_manager or not self.project_manager.current_system:
            return
        
        # 添加环境模块到树中
        system = self.project_manager.current_system
        if hasattr(system, 'environment_models'):
            for env_id, env_module in system.environment_models.items():
                item = QTreeWidgetItem([env_module.name])
                item.setData(0, Qt.UserRole, env_id)
                self.env_tree.addTopLevelItem(item)
    
    def on_environment_selected(self):
        """环境模块选择改变"""
        items = self.env_tree.selectedItems()
        if not items:
            self.current_environment = None
            self.env_title_label.setText("请选择环境模块")
            self.save_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_env_btn.setEnabled(False)
            self.clear_info_display()
            return
        
        env_id = items[0].data(0, Qt.UserRole)
        if self.project_manager and self.project_manager.current_system:
            system = self.project_manager.current_system
            if hasattr(system, 'environment_models') and env_id in system.environment_models:
                self.current_environment = system.environment_models[env_id]
                self.load_environment_info()
                self.save_btn.setEnabled(True)
                self.edit_btn.setEnabled(True)
                self.delete_env_btn.setEnabled(True)
    
    def load_environment_info(self):
        """加载环境模块信息"""
        if not self.current_environment:
            return
        
        self.env_title_label.setText(f"环境模块: {self.current_environment.name}")
        
        # 显示基本信息
        self.name_label.setText(self.current_environment.name)
        self.description_label.setText(self.current_environment.description or "-")
        self.type_label.setText(self.current_environment.environment_type.value)
        self.enabled_label.setText("是" if self.current_environment.enabled else "否")
        
        # 显示应力因子
        self.stress_table.setRowCount(len(self.current_environment.stress_factors))
        for row, stress_factor in enumerate(self.current_environment.stress_factors):
            self.stress_table.setItem(row, 0, QTableWidgetItem(stress_factor.name))
            self.stress_table.setItem(row, 1, QTableWidgetItem(stress_factor.stress_type.value))
            self.stress_table.setItem(row, 2, QTableWidgetItem(str(stress_factor.base_value)))
            self.stress_table.setItem(row, 3, QTableWidgetItem(str(stress_factor.variation_range)))
        
        # 显示影响模块
        self.modules_list.clear()
        if self.project_manager and self.project_manager.current_system:
            system = self.project_manager.current_system
            for module_id in self.current_environment.affected_modules:
                if module_id in system.modules:
                    module = system.modules[module_id]
                    self.modules_list.addItem(f"{module.name} ({module_id})")
    
    def clear_info_display(self):
        """清空信息显示"""
        self.name_label.setText("-")
        self.description_label.setText("-")
        self.type_label.setText("-")
        self.enabled_label.setText("-")
        self.stress_table.setRowCount(0)
        self.modules_list.clear()
    
    def new_environment(self):
        """新建环境模块"""
        if not self.project_manager or not self.project_manager.current_system:
            QMessageBox.warning(self, "警告", "请先创建或打开一个系统")
            return
        
        # 获取系统模块列表
        system_modules = {}
        if self.project_manager.current_system:
            system_modules = self.project_manager.current_system.modules
        
        env_module = EnvironmentModule("新环境模块", "新建的环境模块")
        
        dialog = EnvironmentModuleDialog(env_module, system_modules, self)
        if dialog.exec_() == QDialog.Accepted:
            # 添加到系统中
            system = self.project_manager.current_system
            if not hasattr(system, 'environment_models'):
                system.environment_models = {}
            
            system.environment_models[env_module.id] = env_module
            
            # 刷新列表并选中新建的环境模块
            self.refresh_environment_list()
            
            # 选中新建的项目
            for i in range(self.env_tree.topLevelItemCount()):
                item = self.env_tree.topLevelItem(i)
                if item.data(0, Qt.UserRole) == env_module.id:
                    self.env_tree.setCurrentItem(item)
                    break
    
    def create_from_template(self):
        """从模板创建环境模块"""
        if not self.project_manager or not self.project_manager.current_system:
            QMessageBox.warning(self, "警告", "请先创建或打开一个系统")
            return
        
        # 显示模板选择对话框
        from PyQt5.QtWidgets import QInputDialog
        
        templates = list(ENVIRONMENT_TEMPLATES.keys())
        template_name, ok = QInputDialog.getItem(
            self, "选择模板", "请选择环境模块模板:", templates, 0, False
        )
        
        if not ok or not template_name:
            return
        
        # 从模板创建环境模块
        template_data = ENVIRONMENT_TEMPLATES[template_name]
        env_module = EnvironmentModule()
        env_module.from_dict(template_data)
        
        # 添加到系统中
        system = self.project_manager.current_system
        if not hasattr(system, 'environment_models'):
            system.environment_models = {}
        
        system.environment_models[env_module.id] = env_module
        
        # 刷新列表并选中新建的环境模块
        self.refresh_environment_list()
        
        # 选中新建的项目
        for i in range(self.env_tree.topLevelItemCount()):
            item = self.env_tree.topLevelItem(i)
            if item.data(0, Qt.UserRole) == env_module.id:
                self.env_tree.setCurrentItem(item)
                break
    
    def edit_environment(self):
        """编辑环境模块"""
        if not self.current_environment:
            return
        
        # 获取系统模块列表
        system_modules = {}
        if self.project_manager and self.project_manager.current_system:
            system_modules = self.project_manager.current_system.modules
        
        dialog = EnvironmentModuleDialog(self.current_environment, system_modules, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_environment_info()
            self.refresh_environment_list()
    
    def delete_environment(self):
        """删除环境模块"""
        if not self.current_environment:
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除环境模块 '{self.current_environment.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            system = self.project_manager.current_system
            if hasattr(system, 'environment_models') and self.current_environment.id in system.environment_models:
                del system.environment_models[self.current_environment.id]
            
            self.current_environment = None
            self.refresh_environment_list()
    
    def save_environment(self):
        """保存环境模块"""
        if not self.current_environment:
            return
        
        # 更新修改时间
        self.current_environment.update_modified_time()
        
        # 刷新列表
        self.refresh_environment_list()
        
        # 发送信号
        self.environment_changed.emit(self.current_environment)
        
        QMessageBox.information(self, "保存成功", "环境模块已保存")