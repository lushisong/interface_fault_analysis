# -*- coding: utf-8 -*-
"""
模块面板
Module Panel

模块建模功能界面，支持创建、编辑硬件/软件/算法模块
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QTabWidget,
                             QFormLayout, QLineEdit, QTextEdit, QComboBox,
                             QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QListWidget, QListWidgetItem,
                             QMessageBox, QFileDialog, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from ..models.module_model import Module, ModuleType, ModuleTemplate, HardwareModule, SoftwareModule, AlgorithmModule
from ..models.base_model import ConnectionPoint, Point
from ..models.interface_model import Interface, InterfaceDirection
from .interface_editor_widget import InterfaceEditorWidget


class ModulePanel(QWidget):
    """模块面板组件"""
    
    # 信号定义
    module_created = pyqtSignal(object)  # 模块被创建
    module_modified = pyqtSignal(object)  # 模块被修改
    
    def __init__(self):
        super().__init__()
        self.current_module = None
        self.modules = {}  # 模块字典
        self.project_manager = None  # 项目管理器
        self.current_system = None  # 当前系统
        
        self.init_ui()
        self.init_connections()
    
    def set_project_manager(self, project_manager):
        """设置项目管理器"""
        self.project_manager = project_manager
        self.load_modules_from_system()
    
    def set_current_system(self, system):
        """设置当前系统"""
        self.current_system = system
        self.load_modules_from_system()
    
    def load_modules_from_system(self):
        """从系统中加载模块"""
        if self.current_system:
            self.modules = self.current_system.modules.copy()
            self.update_module_tree()
    
    def save_modules_to_system(self):
        """保存模块到系统"""
        if self.current_system:
            self.current_system.modules = self.modules.copy()
            if self.project_manager:
                self.project_manager.mark_modified()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QHBoxLayout()
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：模块列表和模板库
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧：模块编辑器
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([300, 600])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def create_left_panel(self):
        """创建左侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 模块列表
        self.module_tree = QTreeWidget()
        self.module_tree.setHeaderLabel("模块列表")
        layout.addWidget(QLabel("模块列表"))
        layout.addWidget(self.module_tree)
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.new_module_btn = QPushButton("新建模块")
        self.delete_module_btn = QPushButton("删除模块")
        self.clone_module_btn = QPushButton("克隆模块")
        
        button_layout.addWidget(self.new_module_btn)
        button_layout.addWidget(self.delete_module_btn)
        button_layout.addWidget(self.clone_module_btn)
        
        layout.addLayout(button_layout)
        
        # 模板库
        layout.addWidget(QLabel("模块模板"))
        self.template_list = QListWidget()
        self.populate_template_list()
        layout.addWidget(self.template_list)
        
        widget.setLayout(layout)
        return widget
    
    def create_right_panel(self):
        """创建右侧面板"""
        # 主部件
        right_widget = QWidget()
        layout = QVBoxLayout()
        
        # 标签页控件
        self.tab_widget = QTabWidget()
        
        # 基本信息标签页
        self.basic_tab = self.create_basic_tab()
        self.tab_widget.addTab(self.basic_tab, "基本信息")
        
        # 接口标签页
        self.connections_tab = self.create_connections_tab()
        self.tab_widget.addTab(self.connections_tab, "接口")
        
        # 参数标签页
        self.parameters_tab = self.create_parameters_tab()
        self.tab_widget.addTab(self.parameters_tab, "参数配置")
        
        # Python代码标签页
        self.code_tab = self.create_code_tab()
        self.tab_widget.addTab(self.code_tab, "Python建模")
        
        # 专用属性标签页（根据模块类型动态显示）
        self.specific_tab = self.create_specific_tab()
        self.tab_widget.addTab(self.specific_tab, "专用属性")
        
        layout.addWidget(self.tab_widget)
        
        # 添加保存按钮
        self.save_btn = QPushButton("保存模块")
        self.save_btn.setMinimumHeight(40)
        layout.addWidget(self.save_btn)
        
        right_widget.setLayout(layout)
        return right_widget
    
    def create_basic_tab(self):
        """创建基本信息标签页"""
        widget = QWidget()
        layout = QFormLayout()
        
        # 基本信息
        self.name_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        
        self.module_type_combo = QComboBox()
        for module_type in ModuleType:
            self.module_type_combo.addItem(module_type.value, module_type)
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("无模板", None)
        for template in ModuleTemplate:
            self.template_combo.addItem(template.value, template)
        
        # 位置和大小
        self.pos_x_spin = QDoubleSpinBox()
        self.pos_x_spin.setRange(-9999, 9999)
        self.pos_y_spin = QDoubleSpinBox()
        self.pos_y_spin.setRange(-9999, 9999)
        
        self.size_width_spin = QDoubleSpinBox()
        self.size_width_spin.setRange(50, 500)
        self.size_width_spin.setValue(100)
        self.size_height_spin = QDoubleSpinBox()
        self.size_height_spin.setRange(30, 300)
        self.size_height_spin.setValue(60)
        
        # 图标
        self.icon_path_edit = QLineEdit()
        self.icon_browse_btn = QPushButton("浏览...")
        
        # 添加到布局
        layout.addRow("名称:", self.name_edit)
        layout.addRow("描述:", self.description_edit)
        layout.addRow("模块类型:", self.module_type_combo)
        layout.addRow("模板:", self.template_combo)
        
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("X:"))
        pos_layout.addWidget(self.pos_x_spin)
        pos_layout.addWidget(QLabel("Y:"))
        pos_layout.addWidget(self.pos_y_spin)
        layout.addRow("位置:", pos_layout)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("宽:"))
        size_layout.addWidget(self.size_width_spin)
        size_layout.addWidget(QLabel("高:"))
        size_layout.addWidget(self.size_height_spin)
        layout.addRow("大小:", size_layout)
        
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(self.icon_path_edit)
        icon_layout.addWidget(self.icon_browse_btn)
        layout.addRow("图标:", icon_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_connections_tab(self):
        """创建接口标签页"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # 左侧：接口列表和操作
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # 接口列表
        self.connection_list = QListWidget()
        left_layout.addWidget(QLabel("接口列表"))
        left_layout.addWidget(self.connection_list)
        
        # 按钮组
        button_layout = QHBoxLayout()
        self.add_connection_btn = QPushButton("添加接口")
        self.edit_connection_btn = QPushButton("编辑接口")
        self.remove_connection_btn = QPushButton("删除接口")
        
        button_layout.addWidget(self.add_connection_btn)
        button_layout.addWidget(self.edit_connection_btn)
        button_layout.addWidget(self.remove_connection_btn)
        left_layout.addLayout(button_layout)
        
        # 接口位置设置
        position_group = QGroupBox("接口位置")
        position_layout = QFormLayout()
        
        self.conn_pos_x_spin = QDoubleSpinBox()
        self.conn_pos_x_spin.setRange(0, 500)
        self.conn_pos_y_spin = QDoubleSpinBox()
        self.conn_pos_y_spin.setRange(0, 300)
        
        position_layout.addRow("X坐标:", self.conn_pos_x_spin)
        position_layout.addRow("Y坐标:", self.conn_pos_y_spin)
        
        position_group.setLayout(position_layout)
        left_layout.addWidget(position_group)
        
        # 接口与模块变量映射
        mapping_group = QGroupBox("变量映射")
        mapping_layout = QVBoxLayout()
        
        self.variable_mapping_list = QListWidget()
        mapping_layout.addWidget(QLabel("接口变量与模块变量的映射关系:"))
        mapping_layout.addWidget(self.variable_mapping_list)
        
        mapping_btn_layout = QHBoxLayout()
        self.add_mapping_btn = QPushButton("添加映射")
        self.remove_mapping_btn = QPushButton("删除映射")
        mapping_btn_layout.addWidget(self.add_mapping_btn)
        mapping_btn_layout.addWidget(self.remove_mapping_btn)
        mapping_btn_layout.addStretch()
        mapping_layout.addLayout(mapping_btn_layout)
        
        mapping_group.setLayout(mapping_layout)
        left_layout.addWidget(mapping_group)
        
        left_panel.setLayout(left_layout)
        layout.addWidget(left_panel)
        
        # 右侧：接口编辑器
        self.interface_editor = InterfaceEditorWidget()
        self.interface_editor.interface_changed.connect(self.on_interface_changed)
        layout.addWidget(self.interface_editor)
        
        # 设置分割比例
        layout.setStretch(0, 1)  # 左侧占1/3
        layout.setStretch(1, 2)  # 右侧占2/3
        
        widget.setLayout(layout)
        return widget
    
    def create_parameters_tab(self):
        """创建参数标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 参数列表
        self.parameter_list = QListWidget()
        layout.addWidget(QLabel("参数列表"))
        layout.addWidget(self.parameter_list)
        
        # 按钮组
        button_layout = QHBoxLayout()
        self.add_param_btn = QPushButton("添加参数")
        self.edit_param_btn = QPushButton("编辑参数")
        self.remove_param_btn = QPushButton("删除参数")
        
        button_layout.addWidget(self.add_param_btn)
        button_layout.addWidget(self.edit_param_btn)
        button_layout.addWidget(self.remove_param_btn)
        layout.addLayout(button_layout)
        
        # 参数编辑
        param_group = QGroupBox("参数编辑")
        param_layout = QFormLayout()
        
        self.param_name_edit = QLineEdit()
        self.param_value_edit = QLineEdit()
        self.param_type_combo = QComboBox()
        self.param_type_combo.addItems(["string", "int", "float", "bool", "list", "dict"])
        
        param_layout.addRow("参数名:", self.param_name_edit)
        param_layout.addRow("参数值:", self.param_value_edit)
        param_layout.addRow("参数类型:", self.param_type_combo)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_code_tab(self):
        """创建Python代码标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 代码编辑器
        layout.addWidget(QLabel("Python建模代码:"))
        self.code_edit = QTextEdit()
        self.code_edit.setFont(self.get_monospace_font())
        
        # 设置默认代码模板
        default_code = '''# 模块行为建模代码
# 可用变量：
# - inputs: 输入数据字典
# - parameters: 模块参数字典
# - state_variables: 状态变量字典
# - outputs: 输出数据字典（需要设置）

# 示例代码：
# outputs['result'] = inputs.get('input1', 0) * parameters.get('gain', 1.0)
# state_variables['counter'] = state_variables.get('counter', 0) + 1

'''
        self.code_edit.setPlainText(default_code)
        layout.addWidget(self.code_edit)
        
        # 按钮组
        button_layout = QHBoxLayout()
        self.test_code_btn = QPushButton("测试代码")
        self.load_code_btn = QPushButton("加载文件")
        self.save_code_btn = QPushButton("保存文件")
        
        button_layout.addWidget(self.test_code_btn)
        button_layout.addWidget(self.load_code_btn)
        button_layout.addWidget(self.save_code_btn)
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_specific_tab(self):
        """创建专用属性标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 这里会根据模块类型动态创建不同的属性编辑界面
        self.specific_layout = layout
        
        widget.setLayout(layout)
        return widget
    
    def populate_template_list(self):
        """填充模板列表"""
        templates = {
            "硬件模块": [
                ("传感器", ModuleTemplate.SENSOR),
                ("执行器", ModuleTemplate.ACTUATOR),
                ("处理器", ModuleTemplate.PROCESSOR),
                ("存储器", ModuleTemplate.MEMORY),
                ("通信模块", ModuleTemplate.COMMUNICATION)
            ],
            "软件模块": [
                ("操作系统", ModuleTemplate.OPERATING_SYSTEM),
                ("中间件", ModuleTemplate.MIDDLEWARE),
                ("应用程序", ModuleTemplate.APPLICATION),
                ("数据库", ModuleTemplate.DATABASE)
            ],
            "算法模块": [
                ("控制算法", ModuleTemplate.CONTROL_ALGORITHM),
                ("感知算法", ModuleTemplate.PERCEPTION_ALGORITHM),
                ("决策算法", ModuleTemplate.DECISION_ALGORITHM),
                ("学习算法", ModuleTemplate.LEARNING_ALGORITHM)
            ]
        }
        
        for category, items in templates.items():
            category_item = QListWidgetItem(category)
            category_item.setFlags(Qt.ItemIsEnabled)  # 不可选择
            self.template_list.addItem(category_item)
            
            for name, template in items:
                item = QListWidgetItem(f"  {name}")
                item.setData(Qt.UserRole, template)
                self.template_list.addItem(item)
    
    def init_connections(self):
        """初始化信号连接"""
        # 模块列表选择
        self.module_tree.itemSelectionChanged.connect(self.on_module_selected)
        
        # 按钮连接
        self.new_module_btn.clicked.connect(self.create_new_module)
        self.delete_module_btn.clicked.connect(self.delete_module)
        self.clone_module_btn.clicked.connect(self.clone_module)
        
        # 图标浏览
        self.icon_browse_btn.clicked.connect(self.browse_icon)
        
        # 接口操作
        self.add_connection_btn.clicked.connect(self.add_connection_point)
        self.edit_connection_btn.clicked.connect(self.edit_connection_point)
        self.remove_connection_btn.clicked.connect(self.remove_connection_point)
        self.connection_list.currentItemChanged.connect(self.on_interface_selected)
        
        # 变量映射操作
        self.add_mapping_btn.clicked.connect(self.add_variable_mapping)
        self.remove_mapping_btn.clicked.connect(self.remove_variable_mapping)
        
        # 参数操作
        self.add_param_btn.clicked.connect(self.add_parameter)
        self.edit_param_btn.clicked.connect(self.edit_parameter)
        self.remove_param_btn.clicked.connect(self.remove_parameter)
        
        # 代码操作
        self.test_code_btn.clicked.connect(self.test_code)
        self.load_code_btn.clicked.connect(self.load_code)
        self.save_code_btn.clicked.connect(self.save_code)
        
        # 模板双击
        self.template_list.itemDoubleClicked.connect(self.create_from_template)
        
        # 模块类型变化
        self.module_type_combo.currentTextChanged.connect(self.on_module_type_changed)
        
        # 保存按钮
        self.save_btn.clicked.connect(self.save_current_module)
    
    def get_monospace_font(self):
        """获取等宽字体"""
        from PyQt5.QtGui import QFont
        font = QFont("Consolas")
        if not font.exactMatch():
            font = QFont("Monaco")
        if not font.exactMatch():
            font = QFont("Courier New")
        font.setPointSize(10)
        return font
    
    def create_new_module(self):
        """创建新模块"""
        module = Module("新模块", "新创建的模块")
        self.modules[module.id] = module
        self.save_modules_to_system()
        self.update_module_tree()
        self.select_module(module)
        self.module_created.emit(module)
    
    def delete_module(self):
        """删除模块"""
        if self.current_module:
            reply = QMessageBox.question(self, "确认删除", 
                                       f"确定要删除模块 '{self.current_module.name}' 吗？")
            if reply == QMessageBox.Yes:
                del self.modules[self.current_module.id]
                self.current_module = None
                self.save_modules_to_system()
                self.update_module_tree()
                self.clear_editor()
    
    def clone_module(self):
        """克隆模块"""
        if self.current_module:
            cloned = self.current_module.clone()
            cloned.name += "_副本"
            self.modules[cloned.id] = cloned
            self.save_modules_to_system()
            self.update_module_tree()
            self.select_module(cloned)
    
    def create_from_template(self, item):
        """从模板创建模块"""
        template = item.data(Qt.UserRole)
        if template:
            # 根据模板创建模块
            module = self.create_module_from_template(template)
            self.modules[module.id] = module
            self.save_modules_to_system()
            self.update_module_tree()
            self.select_module(module)
            self.module_created.emit(module)
    
    def create_module_from_template(self, template):
        """根据模板创建模块"""
        # 这里实现模板到模块的转换逻辑
        if template in [ModuleTemplate.SENSOR, ModuleTemplate.ACTUATOR, 
                       ModuleTemplate.PROCESSOR, ModuleTemplate.MEMORY, 
                       ModuleTemplate.COMMUNICATION]:
            module = HardwareModule(template.value, f"基于{template.value}模板创建的硬件模块")
        elif template in [ModuleTemplate.OPERATING_SYSTEM, ModuleTemplate.MIDDLEWARE,
                         ModuleTemplate.APPLICATION, ModuleTemplate.DATABASE]:
            module = SoftwareModule(template.value, f"基于{template.value}模板创建的软件模块")
        else:
            module = AlgorithmModule(template.value, f"基于{template.value}模板创建的算法模块")
        
        module.template = template
        
        # 为模块模板添加相应的接口
        self.add_template_interfaces(module, template)
        
        return module
    
    def create_interface(self, name, description, direction, interface_type, data_format="data"):
        """创建接口的辅助方法"""
        from ..models.interface_model import Interface
        interface = Interface()
        interface.name = name
        interface.description = description
        interface.direction = direction
        interface.interface_type = interface_type
        interface.data_format = data_format
        return interface
    
    def add_template_interfaces(self, module, template):
        """为模块模板添加接口"""
        from ..models.interface_model import Interface, InterfaceType, InterfaceDirection
        
        # 根据模板类型添加不同的接口
        if template == ModuleTemplate.SENSOR:
            # 传感器模块接口
            module.add_interface(self.create_interface(
                "传感器数据输入", "传感器数据输入接口", 
                InterfaceDirection.INPUT, InterfaceType.ALGORITHM_HARDWARE, "signal"))
            module.add_interface(self.create_interface(
                "传感器数据输出", "传感器数据输出接口",
                InterfaceDirection.OUTPUT, InterfaceType.ALGORITHM_HARDWARE, "data"))
            
        elif template == ModuleTemplate.ACTUATOR:
            # 执行器模块接口
            module.add_interface(self.create_interface(
                "控制信号输入", "控制信号输入接口",
                InterfaceDirection.INPUT, InterfaceType.ALGORITHM_HARDWARE, "control"))
            module.add_interface(self.create_interface(
                "状态反馈输出", "状态反馈输出接口",
                InterfaceDirection.OUTPUT, InterfaceType.ALGORITHM_HARDWARE, "signal"))
            
        else:
            # 其他模板使用通用接口
            module.add_interface(self.create_interface(
                "通用输入", "通用输入接口",
                InterfaceDirection.INPUT, InterfaceType.ALGORITHM_HARDWARE, "data"))
            module.add_interface(self.create_interface(
                "通用输出", "通用输出接口", 
                InterfaceDirection.OUTPUT, InterfaceType.ALGORITHM_HARDWARE, "data"))
    
    def update_module_tree(self):
        """更新模块树"""
        self.module_tree.clear()
        
        for module in self.modules.values():
            item = QTreeWidgetItem(self.module_tree)
            item.setText(0, module.name)
            item.setData(0, Qt.UserRole, module.id)
    
    def select_module(self, module):
        """选择模块"""
        self.current_module = module
        self.load_module_to_editor(module)
    
    def on_module_selected(self):
        """模块选择处理"""
        current_item = self.module_tree.currentItem()
        if current_item:
            module_id = current_item.data(0, Qt.UserRole)
            if module_id in self.modules:
                self.select_module(self.modules[module_id])
    
    def load_module_to_editor(self, module):
        """加载模块到编辑器"""
        if not module:
            return
        
        # 基本信息
        self.name_edit.setText(module.name)
        self.description_edit.setPlainText(module.description)
        
        # 设置模块类型
        for i in range(self.module_type_combo.count()):
            if self.module_type_combo.itemData(i) == module.module_type:
                self.module_type_combo.setCurrentIndex(i)
                break
        
        # 位置和大小
        self.pos_x_spin.setValue(module.position.x)
        self.pos_y_spin.setValue(module.position.y)
        self.size_width_spin.setValue(module.size.x)
        self.size_height_spin.setValue(module.size.y)
        
        # 图标
        self.icon_path_edit.setText(module.icon_path)
        
        # Python代码
        self.code_edit.setPlainText(module.python_code)
        
        # 更新接口列表
        self.update_connection_list()
        
        # 更新参数列表
        self.update_parameter_list()
        
        # 更新专用属性
        self.update_specific_properties()
    
    def update_connection_list(self):
        """更新接口列表"""
        self.connection_list.clear()
        if self.current_module:
            for interface_id, interface in self.current_module.interfaces.items():
                direction_text = {
                    InterfaceDirection.INPUT: "输入",
                    InterfaceDirection.OUTPUT: "输出", 
                    InterfaceDirection.BIDIRECTIONAL: "双向"
                }.get(interface.direction, "双向")
                
                item = QListWidgetItem(f"{interface.name} ({direction_text})")
                item.setData(Qt.UserRole, interface_id)
                self.connection_list.addItem(item)
    
    def update_parameter_list(self):
        """更新参数列表"""
        self.parameter_list.clear()
        if self.current_module:
            for key, value in self.current_module.parameters.items():
                item = QListWidgetItem(f"{key}: {value}")
                item.setData(Qt.UserRole, key)
                self.parameter_list.addItem(item)
    
    def update_specific_properties(self):
        """更新专用属性"""
        # 清除现有控件
        for i in reversed(range(self.specific_layout.count())):
            self.specific_layout.itemAt(i).widget().setParent(None)
        
        if not self.current_module:
            return
        
        # 根据模块类型添加专用属性编辑控件
        if isinstance(self.current_module, HardwareModule):
            self.add_hardware_specific_properties()
        elif isinstance(self.current_module, SoftwareModule):
            self.add_software_specific_properties()
        elif isinstance(self.current_module, AlgorithmModule):
            self.add_algorithm_specific_properties()
    
    def add_hardware_specific_properties(self):
        """添加硬件模块专用属性"""
        group = QGroupBox("硬件属性")
        layout = QFormLayout()
        
        # 这里添加硬件模块特有的属性编辑控件
        manufacturer_edit = QLineEdit(self.current_module.manufacturer)
        model_edit = QLineEdit(self.current_module.model)
        power_spin = QDoubleSpinBox()
        power_spin.setValue(self.current_module.power_consumption)
        
        layout.addRow("制造商:", manufacturer_edit)
        layout.addRow("型号:", model_edit)
        layout.addRow("功耗(W):", power_spin)
        
        group.setLayout(layout)
        self.specific_layout.addWidget(group)
    
    def add_software_specific_properties(self):
        """添加软件模块专用属性"""
        group = QGroupBox("软件属性")
        layout = QFormLayout()
        
        # 这里添加软件模块特有的属性编辑控件
        version_edit = QLineEdit(self.current_module.software_version)
        language_edit = QLineEdit(self.current_module.programming_language)
        memory_spin = QSpinBox()
        memory_spin.setValue(self.current_module.memory_usage)
        
        layout.addRow("版本:", version_edit)
        layout.addRow("编程语言:", language_edit)
        layout.addRow("内存使用(MB):", memory_spin)
        
        group.setLayout(layout)
        self.specific_layout.addWidget(group)
    
    def add_algorithm_specific_properties(self):
        """添加算法模块专用属性"""
        group = QGroupBox("算法属性")
        layout = QFormLayout()
        
        # 这里添加算法模块特有的属性编辑控件
        type_edit = QLineEdit(self.current_module.algorithm_type)
        complexity_edit = QLineEdit(self.current_module.complexity)
        accuracy_spin = QDoubleSpinBox()
        accuracy_spin.setRange(0, 1)
        accuracy_spin.setValue(self.current_module.accuracy)
        
        layout.addRow("算法类型:", type_edit)
        layout.addRow("复杂度:", complexity_edit)
        layout.addRow("准确率:", accuracy_spin)
        
        group.setLayout(layout)
        self.specific_layout.addWidget(group)
    
    def clear_editor(self):
        """清空编辑器"""
        self.name_edit.clear()
        self.description_edit.clear()
        self.code_edit.clear()
        self.connection_list.clear()
        self.parameter_list.clear()
        self.interface_editor.clear_form()
    
    def browse_icon(self):
        """浏览图标文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图标", "", "图像文件 (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.icon_path_edit.setText(file_path)
    
    def on_interface_selected(self):
        """接口选择变化"""
        current_item = self.connection_list.currentItem()
        if current_item and self.current_module:
            interface_id = current_item.data(Qt.UserRole)
            interface = self.current_module.get_interface(interface_id)
            if interface:
                # 加载接口到编辑器
                self.interface_editor.load_interface(interface)
                # 更新位置信息（接口对象中没有position属性，需要从其他地方获取）
                # 这里暂时设置默认值
                self.conn_pos_x_spin.setValue(50)
                self.conn_pos_y_spin.setValue(30)
                # 更新变量映射列表
                self.update_variable_mapping_list()
        else:
            self.interface_editor.clear_form()
            self.variable_mapping_list.clear()
    
    def on_interface_changed(self, interface):
        """接口数据变化"""
        if self.current_module and interface:
            # 更新模块中的接口
            self.current_module.interfaces[interface.id] = interface
            self.current_module.update_modified_time()
            # 更新接口列表显示
            self.update_connection_list()
            # 保存到系统
            self.save_modules_to_system()
            # 发射模块修改信号
            self.module_modified.emit(self.current_module)
    
    def update_variable_mapping_list(self):
        """更新变量映射列表"""
        self.variable_mapping_list.clear()
        current_item = self.connection_list.currentItem()
        if current_item and self.current_module:
            interface_id = current_item.data(Qt.UserRole)
            interface = self.current_module.get_interface(interface_id)
            if interface:
                # 显示接口参数与模块变量的映射关系
                for param_name in interface.parameters.keys():
                    # 检查是否有对应的模块变量映射
                    module_var = self.current_module.state_variables.get(f"interface_{interface.id}_{param_name}")
                    if module_var is not None:
                        item = QListWidgetItem(f"{param_name} -> {f'interface_{interface.id}_{param_name}'}")
                        item.setData(Qt.UserRole, (param_name, f"interface_{interface.id}_{param_name}"))
                        self.variable_mapping_list.addItem(item)
    
    def add_variable_mapping(self):
        """添加变量映射"""
        current_item = self.connection_list.currentItem()
        if current_item and self.current_module:
            interface_id = current_item.data(Qt.UserRole)
            interface = self.current_module.get_interface(interface_id)
            if interface:
                # 简单实现：为每个接口参数创建对应的模块变量
                for param_name, param_value in interface.parameters.items():
                    module_var_name = f"interface_{interface.id}_{param_name}"
                    self.current_module.state_variables[module_var_name] = param_value
                
                self.update_variable_mapping_list()
                QMessageBox.information(self, "成功", "已为接口参数创建对应的模块变量映射")
    
    def remove_variable_mapping(self):
        """删除变量映射"""
        current_item = self.variable_mapping_list.currentItem()
        if current_item and self.current_module:
            param_name, module_var_name = current_item.data(Qt.UserRole)
            if module_var_name in self.current_module.state_variables:
                del self.current_module.state_variables[module_var_name]
                self.update_variable_mapping_list()
                QMessageBox.information(self, "成功", "已删除变量映射")
    
    def add_connection_point(self):
        """添加接口"""
        if self.current_module:
            # 导入接口选择对话框
            from .interface_selector_dialog import InterfaceTemplateDialog
            
            # 获取可用的接口模板
            available_interfaces = {}
            if self.current_system and hasattr(self.current_system, 'interfaces'):
                available_interfaces = self.current_system.interfaces
            
            # 显示接口模板选择对话框
            dialog = InterfaceTemplateDialog(available_interfaces, self)
            if dialog.exec_() == QDialog.Accepted:
                template_interface = dialog.get_selected_interface()
                if template_interface:
                    # 创建接口的副本（实例化）
                    new_interface = Interface()
                    if hasattr(template_interface, 'interface_type'):
                        # 从模板复制属性
                        new_interface.name = f"{template_interface.name}_实例"
                        new_interface.interface_type = template_interface.interface_type
                        new_interface.direction = template_interface.direction
                        new_interface.description = template_interface.description
                        new_interface.protocol = template_interface.protocol
                        new_interface.data_format = template_interface.data_format
                        new_interface.bandwidth = template_interface.bandwidth
                        new_interface.latency = template_interface.latency
                        new_interface.reliability = template_interface.reliability
                        new_interface.parameters = template_interface.parameters.copy()
                        new_interface.failure_modes = template_interface.failure_modes.copy()
                        new_interface.python_code = template_interface.python_code
                    else:
                        # 创建新接口
                        new_interface.name = "新接口"
                        new_interface.description = "新创建的接口"
                    
                    # 添加到模块
                    self.current_module.add_interface(new_interface)
                    self.save_modules_to_system()
                    self.update_connection_list()
                    
                    # 选择新添加的接口
                    for i in range(self.connection_list.count()):
                        item = self.connection_list.item(i)
                        if item.data(Qt.UserRole) == new_interface.id:
                            self.connection_list.setCurrentItem(item)
                            break
                    
                    # 发射模块修改信号
                    self.module_modified.emit(self.current_module)
    
    def edit_connection_point(self):
        """编辑接口"""
        # 接口编辑功能已经集成到右侧的接口编辑器中
        # 用户选择接口后，右侧会自动显示编辑界面
        current_item = self.connection_list.currentItem()
        if current_item:
            QMessageBox.information(self, "提示", "请在右侧的接口编辑器中编辑接口属性")
        else:
            QMessageBox.warning(self, "警告", "请先选择一个接口")
    
    def remove_connection_point(self):
        """删除接口"""
        current_item = self.connection_list.currentItem()
        if current_item and self.current_module:
            interface_id = current_item.data(Qt.UserRole)
            interface = self.current_module.get_interface(interface_id)
            if interface:
                reply = QMessageBox.question(
                    self, "确认删除", 
                    f"确定要删除接口 '{interface.name}' 吗？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.current_module.remove_interface(interface_id)
                    self.update_connection_list()
                    self.interface_editor.clear_form()
                    self.variable_mapping_list.clear()
                    self.save_modules_to_system()
                    self.module_modified.emit(self.current_module)
    
    def add_parameter(self):
        """添加参数"""
        if self.current_module:
            param_name = self.param_name_edit.text()
            param_value = self.param_value_edit.text()
            if param_name:
                self.current_module.set_parameter(param_name, param_value)
                self.update_parameter_list()
    
    def edit_parameter(self):
        """编辑参数"""
        # 实现参数编辑逻辑
        pass
    
    def remove_parameter(self):
        """删除参数"""
        current_item = self.parameter_list.currentItem()
        if current_item and self.current_module:
            param_name = current_item.data(Qt.UserRole)
            if param_name in self.current_module.parameters:
                del self.current_module.parameters[param_name]
                self.update_parameter_list()
    
    def test_code(self):
        """测试Python代码"""
        if self.current_module:
            code = self.code_edit.toPlainText()
            self.current_module.python_code = code
            
            # 测试执行
            try:
                test_inputs = {'test_input': 1.0}
                outputs = self.current_module.execute_python_code(test_inputs)
                QMessageBox.information(self, "测试结果", f"代码执行成功\n输出: {outputs}")
            except Exception as e:
                QMessageBox.warning(self, "测试失败", f"代码执行出错: {str(e)}")
    
    def load_code(self):
        """加载代码文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载Python文件", "", "Python文件 (*.py);;所有文件 (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                self.code_edit.setPlainText(code)
            except Exception as e:
                QMessageBox.warning(self, "加载失败", f"无法加载文件: {str(e)}")
    
    def save_code(self):
        """保存代码文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存Python文件", "", "Python文件 (*.py);;所有文件 (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.code_edit.toPlainText())
                QMessageBox.information(self, "保存成功", "代码已保存")
            except Exception as e:
                QMessageBox.warning(self, "保存失败", f"无法保存文件: {str(e)}")
    
    def save_current_module(self):
        """保存当前模块的所有修改"""
        if not self.current_module:
            QMessageBox.warning(self, "警告", "请先选择要保存的模块")
            return
        
        try:
            # 更新基本信息
            self.current_module.name = self.name_edit.text()
            self.current_module.description = self.description_edit.toPlainText()
            
            # 更新模块类型
            module_type = self.module_type_combo.currentData()
            if module_type:
                self.current_module.module_type = module_type
            
            # 更新位置和大小
            self.current_module.position.x = self.pos_x_spin.value()
            self.current_module.position.y = self.pos_y_spin.value()
            self.current_module.size.x = self.size_width_spin.value()
            self.current_module.size.y = self.size_height_spin.value()
            
            # 更新图标路径
            self.current_module.icon_path = self.icon_path_edit.text()
            
            # 更新Python代码
            self.current_module.python_code = self.code_edit.toPlainText()
            
            # 保存到系统
            self.save_modules_to_system()
            
            # 更新模块树显示
            self.update_module_tree()
            
            # 发射模块修改信号
            self.module_modified.emit(self.current_module)
            
            QMessageBox.information(self, "保存成功", f"模块 '{self.current_module.name}' 已保存")
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存模块时出错: {str(e)}")
    
    def on_module_type_changed(self):
        """模块类型变化处理"""
        if self.current_module:
            module_type = self.module_type_combo.currentData()
            self.current_module.module_type = module_type
            self.update_specific_properties()
            
            # 标记为需要保存
            self.save_btn.setEnabled(True)
