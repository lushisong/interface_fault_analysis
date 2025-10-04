#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务剖面面板
Task Profile Panel
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QTabWidget,
                             QTableWidget, QTableWidgetItem, QGroupBox,
                             QLabel, QLineEdit, QTextEdit, QComboBox,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
                             QFormLayout, QGridLayout, QHeaderView, QMessageBox,
                             QDialog, QDialogButtonBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from ..models.task_profile_model import (TaskProfile, SuccessCriteria, TaskPhase,
                                       SuccessCriteriaType, ComparisonOperator,
                                       TASK_PROFILE_TEMPLATES)


class SuccessCriteriaDialog(QDialog):
    """成功判据编辑对话框"""
    
    def __init__(self, criteria=None, modules=None, parent=None):
        super().__init__(parent)
        self.criteria = criteria or SuccessCriteria()
        self.modules = modules or {}
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("成功判据编辑")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        
        basic_layout.addRow("名称:", self.name_edit)
        basic_layout.addRow("描述:", self.description_edit)
        
        # 判据配置
        config_group = QGroupBox("判据配置")
        config_layout = QFormLayout(config_group)
        
        self.type_combo = QComboBox()
        for criteria_type in SuccessCriteriaType:
            self.type_combo.addItem(criteria_type.value, criteria_type)
        
        self.module_combo = QComboBox()
        self.module_combo.addItem("请选择模块", "")
        for module_id, module in self.modules.items():
            self.module_combo.addItem(f"{module.name} ({module_id})", module_id)
        
        self.parameter_edit = QLineEdit()
        
        self.operator_combo = QComboBox()
        for op in ComparisonOperator:
            self.operator_combo.addItem(op.value, op)
        
        self.target_spin = QDoubleSpinBox()
        self.target_spin.setRange(-999999, 999999)
        self.target_spin.setDecimals(3)
        
        self.range_min_spin = QDoubleSpinBox()
        self.range_min_spin.setRange(-999999, 999999)
        self.range_min_spin.setDecimals(3)
        
        self.range_max_spin = QDoubleSpinBox()
        self.range_max_spin.setRange(-999999, 999999)
        self.range_max_spin.setDecimals(3)
        
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.1, 10.0)
        self.weight_spin.setValue(1.0)
        self.weight_spin.setDecimals(1)
        
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(True)
        
        config_layout.addRow("类型:", self.type_combo)
        config_layout.addRow("关联模块:", self.module_combo)
        config_layout.addRow("参数名称:", self.parameter_edit)
        config_layout.addRow("比较操作:", self.operator_combo)
        config_layout.addRow("目标值:", self.target_spin)
        config_layout.addRow("范围最小值:", self.range_min_spin)
        config_layout.addRow("范围最大值:", self.range_max_spin)
        config_layout.addRow("权重:", self.weight_spin)
        config_layout.addRow("启用:", self.enabled_check)
        
        # Python代码
        code_group = QGroupBox("自定义Python代码")
        code_layout = QVBoxLayout(code_group)
        
        self.code_edit = QTextEdit()
        self.code_edit.setPlainText("""# 自定义成功判据评估代码
# 可用变量: system_state (系统状态字典)
# 设置 result = True/False 表示判据是否满足

# 示例:
# if system_state.get('module_id', {}).get('parameter') > threshold:
#     result = True
# else:
#     result = False

result = False
""")
        code_layout.addWidget(self.code_edit)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 布局
        layout.addWidget(basic_group)
        layout.addWidget(config_group)
        layout.addWidget(code_group)
        layout.addWidget(button_box)
        
        # 连接信号
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        self.operator_combo.currentTextChanged.connect(self.on_operator_changed)
    
    def on_type_changed(self):
        """类型改变时的处理"""
        criteria_type = self.type_combo.currentData()
        is_custom = criteria_type == SuccessCriteriaType.CUSTOM_CONDITION
        
        self.module_combo.setEnabled(not is_custom)
        self.parameter_edit.setEnabled(not is_custom)
        self.operator_combo.setEnabled(not is_custom)
        self.target_spin.setEnabled(not is_custom)
        self.code_edit.setEnabled(is_custom)
    
    def on_operator_changed(self):
        """操作符改变时的处理"""
        operator = self.operator_combo.currentData()
        is_range = operator in [ComparisonOperator.IN_RANGE, ComparisonOperator.OUT_RANGE]
        
        self.range_min_spin.setEnabled(is_range)
        self.range_max_spin.setEnabled(is_range)
        self.target_spin.setEnabled(not is_range)
    
    def load_data(self):
        """加载数据"""
        self.name_edit.setText(self.criteria.name)
        self.description_edit.setPlainText(self.criteria.description)
        
        # 设置类型
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == self.criteria.criteria_type:
                self.type_combo.setCurrentIndex(i)
                break
        
        # 设置模块
        for i in range(self.module_combo.count()):
            if self.module_combo.itemData(i) == self.criteria.module_id:
                self.module_combo.setCurrentIndex(i)
                break
        
        self.parameter_edit.setText(self.criteria.parameter_name)
        
        # 设置操作符
        for i in range(self.operator_combo.count()):
            if self.operator_combo.itemData(i) == self.criteria.operator:
                self.operator_combo.setCurrentIndex(i)
                break
        
        self.target_spin.setValue(self.criteria.target_value)
        self.range_min_spin.setValue(self.criteria.range_min)
        self.range_max_spin.setValue(self.criteria.range_max)
        self.weight_spin.setValue(self.criteria.weight)
        self.enabled_check.setChecked(self.criteria.enabled)
        
        if self.criteria.python_code:
            self.code_edit.setPlainText(self.criteria.python_code)
        
        # 触发类型和操作符变化处理
        self.on_type_changed()
        self.on_operator_changed()
    
    def save_data(self):
        """保存数据"""
        self.criteria.name = self.name_edit.text()
        self.criteria.description = self.description_edit.toPlainText()
        self.criteria.criteria_type = self.type_combo.currentData()
        self.criteria.module_id = self.module_combo.currentData()
        self.criteria.parameter_name = self.parameter_edit.text()
        self.criteria.operator = self.operator_combo.currentData()
        self.criteria.target_value = self.target_spin.value()
        self.criteria.range_min = self.range_min_spin.value()
        self.criteria.range_max = self.range_max_spin.value()
        self.criteria.weight = self.weight_spin.value()
        self.criteria.enabled = self.enabled_check.isChecked()
        self.criteria.python_code = self.code_edit.toPlainText()
    
    def accept(self):
        """确认"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入成功判据名称")
            return
        
        self.save_data()
        super().accept()


class TaskPhaseDialog(QDialog):
    """任务阶段编辑对话框"""
    
    def __init__(self, phase=None, parent=None):
        super().__init__(parent)
        self.phase = phase or TaskPhase()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("任务阶段编辑")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 基本信息
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(0, 999999)
        self.start_time_spin.setSuffix(" 秒")
        
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(1, 999999)
        self.duration_spin.setSuffix(" 秒")
        self.duration_spin.setValue(60)
        
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(True)
        
        form_layout.addRow("名称:", self.name_edit)
        form_layout.addRow("描述:", self.description_edit)
        form_layout.addRow("开始时间:", self.start_time_spin)
        form_layout.addRow("持续时间:", self.duration_spin)
        form_layout.addRow("启用:", self.enabled_check)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
    
    def load_data(self):
        """加载数据"""
        self.name_edit.setText(self.phase.name)
        self.description_edit.setPlainText(self.phase.description)
        self.start_time_spin.setValue(self.phase.start_time)
        self.duration_spin.setValue(self.phase.duration)
        self.enabled_check.setChecked(self.phase.enabled)
    
    def save_data(self):
        """保存数据"""
        self.phase.name = self.name_edit.text()
        self.phase.description = self.description_edit.toPlainText()
        self.phase.start_time = self.start_time_spin.value()
        self.phase.duration = self.duration_spin.value()
        self.phase.enabled = self.enabled_check.isChecked()
    
    def accept(self):
        """确认"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入任务阶段名称")
            return
        
        self.save_data()
        super().accept()


class TaskProfilePanel(QWidget):
    """任务剖面面板"""
    
    task_profile_changed = pyqtSignal(object)  # 任务剖面改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_profile = None
        self.project_manager = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：任务剖面列表
        left_widget = self.create_profile_list()
        left_widget.setMaximumWidth(300)
        
        # 右侧：任务剖面编辑器
        right_widget = self.create_profile_editor()
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
    
    def create_profile_list(self):
        """创建任务剖面列表"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题
        title_label = QLabel("任务剖面列表")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.new_profile_btn = QPushButton("新建")
        self.new_profile_btn.clicked.connect(self.new_profile)
        
        self.template_btn = QPushButton("从模板创建")
        self.template_btn.clicked.connect(self.create_from_template)
        
        self.delete_profile_btn = QPushButton("删除")
        self.delete_profile_btn.clicked.connect(self.delete_profile)
        self.delete_profile_btn.setEnabled(False)
        
        toolbar_layout.addWidget(self.new_profile_btn)
        toolbar_layout.addWidget(self.template_btn)
        toolbar_layout.addWidget(self.delete_profile_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # 任务剖面树
        self.profile_tree = QTreeWidget()
        self.profile_tree.setHeaderLabel("任务剖面")
        self.profile_tree.itemSelectionChanged.connect(self.on_profile_selected)
        layout.addWidget(self.profile_tree)
        
        return widget
    
    def create_profile_editor(self):
        """创建任务剖面编辑器"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题栏
        title_layout = QHBoxLayout()
        self.profile_title_label = QLabel("请选择任务剖面")
        self.profile_title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_layout.addWidget(self.profile_title_label)
        title_layout.addStretch()
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_profile)
        self.save_btn.setEnabled(False)
        title_layout.addWidget(self.save_btn)
        
        layout.addLayout(title_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 基本信息标签页
        self.basic_tab = self.create_basic_tab()
        self.tab_widget.addTab(self.basic_tab, "基本信息")
        
        # 成功判据标签页
        self.criteria_tab = self.create_criteria_tab()
        self.tab_widget.addTab(self.criteria_tab, "成功判据")
        
        # 任务阶段标签页
        self.phases_tab = self.create_phases_tab()
        self.tab_widget.addTab(self.phases_tab, "任务阶段")
        
        # 分析结果标签页
        self.results_tab = self.create_results_tab()
        self.tab_widget.addTab(self.results_tab, "分析结果")
        
        self.tab_widget.setEnabled(False)
        layout.addWidget(self.tab_widget)
        
        return widget
    
    def create_basic_tab(self):
        """创建基本信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 基本信息表单
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        
        self.mission_type_edit = QLineEdit()
        
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(1, 999999)
        self.duration_spin.setSuffix(" 秒")
        self.duration_spin.setValue(3600)
        
        form_layout.addRow("名称:", self.name_edit)
        form_layout.addRow("描述:", self.description_edit)
        form_layout.addRow("任务类型:", self.mission_type_edit)
        form_layout.addRow("总持续时间:", self.duration_spin)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        return widget
    
    def create_criteria_tab(self):
        """创建成功判据标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_criteria_btn = QPushButton("添加判据")
        self.add_criteria_btn.clicked.connect(self.add_success_criteria)
        
        self.edit_criteria_btn = QPushButton("编辑判据")
        self.edit_criteria_btn.clicked.connect(self.edit_success_criteria)
        self.edit_criteria_btn.setEnabled(False)
        
        self.remove_criteria_btn = QPushButton("删除判据")
        self.remove_criteria_btn.clicked.connect(self.remove_success_criteria)
        self.remove_criteria_btn.setEnabled(False)
        
        toolbar_layout.addWidget(self.add_criteria_btn)
        toolbar_layout.addWidget(self.edit_criteria_btn)
        toolbar_layout.addWidget(self.remove_criteria_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # 成功判据表格
        self.criteria_table = QTableWidget()
        self.criteria_table.setColumnCount(6)
        self.criteria_table.setHorizontalHeaderLabels([
            "名称", "类型", "模块", "参数", "条件", "权重"
        ])
        
        header = self.criteria_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.criteria_table.itemSelectionChanged.connect(self.on_criteria_selected)
        self.criteria_table.itemDoubleClicked.connect(self.edit_success_criteria)
        
        layout.addWidget(self.criteria_table)
        
        return widget
    
    def create_phases_tab(self):
        """创建任务阶段标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_phase_btn = QPushButton("添加阶段")
        self.add_phase_btn.clicked.connect(self.add_task_phase)
        
        self.edit_phase_btn = QPushButton("编辑阶段")
        self.edit_phase_btn.clicked.connect(self.edit_task_phase)
        self.edit_phase_btn.setEnabled(False)
        
        self.remove_phase_btn = QPushButton("删除阶段")
        self.remove_phase_btn.clicked.connect(self.remove_task_phase)
        self.remove_phase_btn.setEnabled(False)
        
        toolbar_layout.addWidget(self.add_phase_btn)
        toolbar_layout.addWidget(self.edit_phase_btn)
        toolbar_layout.addWidget(self.remove_phase_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # 任务阶段表格
        self.phases_table = QTableWidget()
        self.phases_table.setColumnCount(4)
        self.phases_table.setHorizontalHeaderLabels([
            "名称", "开始时间(秒)", "持续时间(秒)", "启用"
        ])
        
        header = self.phases_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.phases_table.itemSelectionChanged.connect(self.on_phase_selected)
        self.phases_table.itemDoubleClicked.connect(self.edit_task_phase)
        
        layout.addWidget(self.phases_table)
        
        return widget
    
    def create_results_tab(self):
        """创建分析结果标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 故障树状态
        status_group = QGroupBox("故障树状态")
        status_layout = QVBoxLayout(status_group)
        
        self.fault_tree_status_label = QLabel("未生成故障树")
        self.generate_fault_tree_btn = QPushButton("生成故障树")
        self.generate_fault_tree_btn.clicked.connect(self.generate_fault_tree)
        
        status_layout.addWidget(self.fault_tree_status_label)
        status_layout.addWidget(self.generate_fault_tree_btn)
        
        # 分析结果
        results_group = QGroupBox("分析结果")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(status_group)
        layout.addWidget(results_group)
        
        return widget
    
    def set_project_manager(self, project_manager):
        """设置项目管理器"""
        self.project_manager = project_manager
        self.refresh_profile_list()
    
    def refresh_profile_list(self):
        """刷新任务剖面列表"""
        self.profile_tree.clear()
        
        if not self.project_manager or not self.project_manager.current_system:
            return
        
        # 添加任务剖面到树中
        system = self.project_manager.current_system
        if hasattr(system, 'task_profiles'):
            for profile_id, profile in system.task_profiles.items():
                item = QTreeWidgetItem([profile.name])
                item.setData(0, Qt.UserRole, profile_id)
                self.profile_tree.addTopLevelItem(item)
    
    def on_profile_selected(self):
        """任务剖面选择改变"""
        items = self.profile_tree.selectedItems()
        if not items:
            self.current_profile = None
            self.profile_title_label.setText("请选择任务剖面")
            self.tab_widget.setEnabled(False)
            self.save_btn.setEnabled(False)
            self.delete_profile_btn.setEnabled(False)
            return
        
        profile_id = items[0].data(0, Qt.UserRole)
        if self.project_manager and self.project_manager.current_system:
            system = self.project_manager.current_system
            if hasattr(system, 'task_profiles') and profile_id in system.task_profiles:
                self.current_profile = system.task_profiles[profile_id]
                self.load_profile_data()
                self.tab_widget.setEnabled(True)
                self.save_btn.setEnabled(True)
                self.delete_profile_btn.setEnabled(True)
    
    def load_profile_data(self):
        """加载任务剖面数据"""
        if not self.current_profile:
            return
        
        self.profile_title_label.setText(f"任务剖面: {self.current_profile.name}")
        
        # 加载基本信息
        self.name_edit.setText(self.current_profile.name)
        self.description_edit.setPlainText(self.current_profile.description)
        self.mission_type_edit.setText(self.current_profile.mission_type)
        self.duration_spin.setValue(self.current_profile.total_duration)
        
        # 加载成功判据
        self.refresh_criteria_table()
        
        # 加载任务阶段
        self.refresh_phases_table()
        
        # 加载分析结果
        self.refresh_results()
    
    def refresh_criteria_table(self):
        """刷新成功判据表格"""
        if not self.current_profile:
            return
        
        self.criteria_table.setRowCount(len(self.current_profile.success_criteria))
        
        for row, criteria in enumerate(self.current_profile.success_criteria):
            self.criteria_table.setItem(row, 0, QTableWidgetItem(criteria.name))
            self.criteria_table.setItem(row, 1, QTableWidgetItem(criteria.criteria_type.value))
            self.criteria_table.setItem(row, 2, QTableWidgetItem(criteria.module_id))
            self.criteria_table.setItem(row, 3, QTableWidgetItem(criteria.parameter_name))
            
            # 构建条件字符串
            if criteria.operator in [ComparisonOperator.IN_RANGE, ComparisonOperator.OUT_RANGE]:
                condition = f"{criteria.operator.value} [{criteria.range_min}, {criteria.range_max}]"
            else:
                condition = f"{criteria.operator.value} {criteria.target_value}"
            
            self.criteria_table.setItem(row, 4, QTableWidgetItem(condition))
            self.criteria_table.setItem(row, 5, QTableWidgetItem(str(criteria.weight)))
    
    def refresh_phases_table(self):
        """刷新任务阶段表格"""
        if not self.current_profile:
            return
        
        self.phases_table.setRowCount(len(self.current_profile.task_phases))
        
        for row, phase in enumerate(self.current_profile.task_phases):
            self.phases_table.setItem(row, 0, QTableWidgetItem(phase.name))
            self.phases_table.setItem(row, 1, QTableWidgetItem(str(phase.start_time)))
            self.phases_table.setItem(row, 2, QTableWidgetItem(str(phase.duration)))
            
            enabled_item = QTableWidgetItem("是" if phase.enabled else "否")
            self.phases_table.setItem(row, 3, enabled_item)
    
    def refresh_results(self):
        """刷新分析结果"""
        if not self.current_profile:
            return
        
        # 更新故障树状态
        if self.current_profile.fault_tree_generated:
            self.fault_tree_status_label.setText("已生成故障树")
            self.generate_fault_tree_btn.setText("重新生成故障树")
        else:
            self.fault_tree_status_label.setText("未生成故障树")
            self.generate_fault_tree_btn.setText("生成故障树")
        
        # 显示分析结果
        if self.current_profile.analysis_results:
            results_text = "分析结果:\n\n"
            for key, value in self.current_profile.analysis_results.items():
                results_text += f"{key}: {value}\n"
            self.results_text.setPlainText(results_text)
        else:
            self.results_text.setPlainText("暂无分析结果")
    
    def new_profile(self):
        """新建任务剖面"""
        if not self.project_manager or not self.project_manager.current_system:
            QMessageBox.warning(self, "警告", "请先创建或打开一个系统")
            return
        
        profile = TaskProfile("新任务剖面", "新建的任务剖面")
        
        # 添加到系统中
        system = self.project_manager.current_system
        if not hasattr(system, 'task_profiles'):
            system.task_profiles = {}
        
        system.task_profiles[profile.id] = profile
        
        # 刷新列表并选中新建的剖面
        self.refresh_profile_list()
        
        # 选中新建的项目
        for i in range(self.profile_tree.topLevelItemCount()):
            item = self.profile_tree.topLevelItem(i)
            if item.data(0, Qt.UserRole) == profile.id:
                self.profile_tree.setCurrentItem(item)
                break
    
    def create_from_template(self):
        """从模板创建任务剖面"""
        if not self.project_manager or not self.project_manager.current_system:
            QMessageBox.warning(self, "警告", "请先创建或打开一个系统")
            return
        
        # 显示模板选择对话框
        from PyQt5.QtWidgets import QInputDialog
        
        templates = list(TASK_PROFILE_TEMPLATES.keys())
        template_name, ok = QInputDialog.getItem(
            self, "选择模板", "请选择任务剖面模板:", templates, 0, False
        )
        
        if not ok or not template_name:
            return
        
        # 从模板创建任务剖面
        template_data = TASK_PROFILE_TEMPLATES[template_name]
        profile = TaskProfile()
        profile.from_dict(template_data)
        
        # 添加到系统中
        system = self.project_manager.current_system
        if not hasattr(system, 'task_profiles'):
            system.task_profiles = {}
        
        system.task_profiles[profile.id] = profile
        
        # 刷新列表并选中新建的剖面
        self.refresh_profile_list()
        
        # 选中新建的项目
        for i in range(self.profile_tree.topLevelItemCount()):
            item = self.profile_tree.topLevelItem(i)
            if item.data(0, Qt.UserRole) == profile.id:
                self.profile_tree.setCurrentItem(item)
                break
    
    def delete_profile(self):
        """删除任务剖面"""
        if not self.current_profile:
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除任务剖面 '{self.current_profile.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            system = self.project_manager.current_system
            if hasattr(system, 'task_profiles') and self.current_profile.id in system.task_profiles:
                del system.task_profiles[self.current_profile.id]
            
            self.current_profile = None
            self.refresh_profile_list()
    
    def save_profile(self):
        """保存任务剖面"""
        if not self.current_profile:
            return
        
        # 保存基本信息
        self.current_profile.name = self.name_edit.text()
        self.current_profile.description = self.description_edit.toPlainText()
        self.current_profile.mission_type = self.mission_type_edit.text()
        self.current_profile.total_duration = self.duration_spin.value()
        
        # 更新修改时间
        self.current_profile.update_modified_time()
        
        # 刷新列表
        self.refresh_profile_list()
        
        # 发送信号
        self.task_profile_changed.emit(self.current_profile)
        
        QMessageBox.information(self, "保存成功", "任务剖面已保存")
    
    def add_success_criteria(self):
        """添加成功判据"""
        if not self.current_profile:
            return
        
        # 获取系统模块列表
        modules = {}
        if self.project_manager and self.project_manager.current_system:
            modules = self.project_manager.current_system.modules
        
        dialog = SuccessCriteriaDialog(modules=modules, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.current_profile.add_success_criteria(dialog.criteria)
            self.refresh_criteria_table()
    
    def edit_success_criteria(self):
        """编辑成功判据"""
        if not self.current_profile:
            return
        
        row = self.criteria_table.currentRow()
        if row < 0 or row >= len(self.current_profile.success_criteria):
            return
        
        criteria = self.current_profile.success_criteria[row]
        
        # 获取系统模块列表
        modules = {}
        if self.project_manager and self.project_manager.current_system:
            modules = self.project_manager.current_system.modules
        
        dialog = SuccessCriteriaDialog(criteria, modules, self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_criteria_table()
    
    def remove_success_criteria(self):
        """删除成功判据"""
        if not self.current_profile:
            return
        
        row = self.criteria_table.currentRow()
        if row < 0 or row >= len(self.current_profile.success_criteria):
            return
        
        criteria = self.current_profile.success_criteria[row]
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除成功判据 '{criteria.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_profile.remove_success_criteria(criteria.name)
            self.refresh_criteria_table()
    
    def on_criteria_selected(self):
        """成功判据选择改变"""
        has_selection = len(self.criteria_table.selectedItems()) > 0
        self.edit_criteria_btn.setEnabled(has_selection)
        self.remove_criteria_btn.setEnabled(has_selection)
    
    def add_task_phase(self):
        """添加任务阶段"""
        if not self.current_profile:
            return
        
        dialog = TaskPhaseDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.current_profile.add_task_phase(dialog.phase)
            self.refresh_phases_table()
    
    def edit_task_phase(self):
        """编辑任务阶段"""
        if not self.current_profile:
            return
        
        row = self.phases_table.currentRow()
        if row < 0 or row >= len(self.current_profile.task_phases):
            return
        
        phase = self.current_profile.task_phases[row]
        
        dialog = TaskPhaseDialog(phase, self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_phases_table()
    
    def remove_task_phase(self):
        """删除任务阶段"""
        if not self.current_profile:
            return
        
        row = self.phases_table.currentRow()
        if row < 0 or row >= len(self.current_profile.task_phases):
            return
        
        phase = self.current_profile.task_phases[row]
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除任务阶段 '{phase.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_profile.remove_task_phase(phase.name)
            self.refresh_phases_table()
    
    def on_phase_selected(self):
        """任务阶段选择改变"""
        has_selection = len(self.phases_table.selectedItems()) > 0
        self.edit_phase_btn.setEnabled(has_selection)
        self.remove_phase_btn.setEnabled(has_selection)
    
    def generate_fault_tree(self):
        """生成故障树"""
        if not self.current_profile:
            return
        
        # 这里应该调用故障树生成算法
        # 目前只是模拟
        self.current_profile.fault_tree_generated = True
        self.current_profile.fault_tree_data = {
            "root_event": "任务失败",
            "nodes": [],
            "edges": []
        }
        
        # 模拟分析结果
        self.current_profile.analysis_results = {
            "故障树节点数": 15,
            "最小割集数": 8,
            "系统可靠性": 0.95,
            "关键路径": "传感器失效 -> 导航失效 -> 任务失败"
        }
        
        self.refresh_results()
        QMessageBox.information(self, "生成完成", "故障树已生成并完成分析")