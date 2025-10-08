# -*- coding: utf-8 -*-
"""
接口面板
Interface Panel

接口建模功能界面，支持创建、编辑各种接口和失效模式
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QTabWidget,
                             QFormLayout, QLineEdit, QTextEdit, QComboBox,
                             QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QListWidget, QListWidgetItem,
                             QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal

from ..models.interface_model import (Interface, InterfaceType, HardwareInterfaceSubtype,
                                    InterfaceFailureMode, FailureMode, TriggerCondition)


class InterfacePanel(QWidget):
    """接口面板组件"""
    
    # 信号定义
    interface_created = pyqtSignal(object)
    interface_modified = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.current_interface = None
        self.interfaces = {}
        self.project_manager = None  # 项目管理器
        self.current_system = None  # 当前系统
        
        self.init_ui()
        self.init_connections()
    
    def set_project_manager(self, project_manager):
        """设置项目管理器"""
        self.project_manager = project_manager
        self.load_interfaces_from_system()
    
    def set_current_system(self, system):
        """设置当前系统"""
        self.current_system = system
        self.load_interfaces_from_system()
    
    def load_interfaces_from_system(self):
        """从系统中加载接口"""
        if self.current_system:
            self.interfaces = self.current_system.interfaces.copy()
            self.update_interface_tree()
    
    def save_interfaces_to_system(self):
        """保存接口到系统"""
        if self.current_system:
            self.current_system.interfaces = self.interfaces.copy()
            if self.project_manager:
                self.project_manager.mark_modified()
    
    def update_interface_tree(self):
        """更新接口树"""
        # 保存当前选择
        current_selection = None
        current_item = self.interface_tree.currentItem()
        if current_item:
            data = current_item.data(0, Qt.UserRole)
            if data and data.get('type') == 'interface_instance':
                current_selection = data.get('interface_id')
        
        # 清除现有项目（保留模板分类）
        root = self.interface_tree.invisibleRootItem()
        for i in range(root.childCount()):
            category_item = root.child(i)
            # 移除所有实例接口，保留模板
            for j in range(category_item.childCount()-1, -1, -1):
                child = category_item.child(j)
                child_data = child.data(0, Qt.UserRole)
                if child_data and child_data.get('type') == 'interface_instance':
                    category_item.removeChild(child)
        
        # 添加已保存的接口实例
        for interface_id, interface in self.interfaces.items():
            # 根据接口类型找到对应的分类
            category_name = self.get_category_name(interface.interface_type)
            category_item = self.find_category_item(category_name)
            
            if category_item:
                # 创建接口实例项
                instance_item = QTreeWidgetItem(category_item)
                instance_item.setText(0, interface.name)
                instance_item.setData(0, Qt.UserRole, {
                    'type': 'interface_instance',
                    'interface_id': interface_id,
                    'category': category_name,
                    'name': interface.name
                })
                # 插入到模板项之前
                category_item.insertChild(0, instance_item)
        
        # 恢复选择
        if current_selection:
            self.select_interface_in_tree(current_selection)
    
    def init_ui(self):
        """初始化用户界面"""
        # 主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：接口库和分类
        left_panel = self.create_interface_library()
        main_splitter.addWidget(left_panel)
        
        # 右侧：接口详情和编辑
        right_panel = self.create_interface_editor()
        main_splitter.addWidget(right_panel)
        
        # 设置分割器比例
        main_splitter.setSizes([400, 600])
        
        # 主布局
        layout = QHBoxLayout()
        layout.addWidget(main_splitter)
        self.setLayout(layout)
    
    def create_interface_library(self):
        """创建接口库面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        layout.addWidget(QLabel("接口库"))
        
        # 接口分类树
        self.interface_tree = QTreeWidget()
        self.interface_tree.setHeaderLabel("接口分类")
        
        # 创建接口分类
        self.create_interface_categories()
        
        layout.addWidget(self.interface_tree)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.new_interface_btn = QPushButton("新建接口")
        self.delete_interface_btn = QPushButton("删除接口")
        self.duplicate_interface_btn = QPushButton("复制接口")
        
        button_layout.addWidget(self.new_interface_btn)
        button_layout.addWidget(self.delete_interface_btn)
        button_layout.addWidget(self.duplicate_interface_btn)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_interface_categories(self):
        """创建接口分类"""
        # 五大类接口
        categories = {
            "算法-操作系统接口": [
                "进程调度接口", "内存管理接口", "文件系统接口", "网络接口", "设备驱动接口"
            ],
            "算法-智能框架接口": [
                "模型加载接口", "推理执行接口", "数据预处理接口", "后处理接口", "GPU加速接口"
            ],
            "算法-应用接口": [
                "API调用接口", "数据交换接口", "配置管理接口", "状态监控接口", "事件通知接口"
            ],
            "算法-数据平台接口": [
                "数据读取接口", "数据写入接口", "数据查询接口", "数据同步接口", "缓存接口"
            ],
            "算法-硬件设备接口": [
                "传感器接口", "执行器接口", "专用计算硬件接口", "通信硬件接口", "存储硬件接口"
            ],
            "一般接口": [
                "软件-硬件接口", "软件-软件接口", "硬件-硬件接口", "用户接口", "网络接口"
            ]
        }
        
        for category, interfaces in categories.items():
            category_item = QTreeWidgetItem(self.interface_tree)
            category_item.setText(0, category)
            category_item.setExpanded(True)
            
            for interface_name in interfaces:
                interface_item = QTreeWidgetItem(category_item)
                interface_item.setText(0, interface_name)
                interface_item.setData(0, Qt.UserRole, {
                    'type': 'interface_template',
                    'category': category,
                    'name': interface_name
                })
    
    def create_interface_editor(self):
        """创建接口编辑器"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 标签页
        self.editor_tabs = QTabWidget()
        
        # 基本信息标签页
        basic_tab = self.create_basic_info_tab()
        self.editor_tabs.addTab(basic_tab, "基本信息")
        
        # 失效模式标签页
        failure_tab = self.create_failure_modes_tab()
        self.editor_tabs.addTab(failure_tab, "失效模式")
        
        # Python代码标签页
        code_tab = self.create_code_tab()
        self.editor_tabs.addTab(code_tab, "功能代码")
        
        layout.addWidget(self.editor_tabs)
        
        # 保存按钮
        save_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存接口")
        self.reset_btn = QPushButton("重置")
        save_layout.addWidget(self.save_btn)
        save_layout.addWidget(self.reset_btn)
        save_layout.addStretch()
        
        layout.addLayout(save_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_basic_info_tab(self):
        """创建基本信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 基本信息表单
        form_group = QGroupBox("接口基本信息")
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "算法-操作系统接口", "算法-智能框架接口", "算法-应用接口",
            "算法-数据平台接口", "算法-硬件设备接口", "一般接口"
        ])
        
        # 添加接口方向选择
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["输入", "输出", "双向"])
        
        self.subtype_combo = QComboBox()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        
        form_layout.addRow("接口名称:", self.name_edit)
        form_layout.addRow("接口类型:", self.type_combo)
        form_layout.addRow("接口方向:", self.direction_combo)
        form_layout.addRow("接口子类型:", self.subtype_combo)
        form_layout.addRow("接口描述:", self.description_edit)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 接口参数
        param_group = QGroupBox("接口参数")
        param_layout = QVBoxLayout()
        
        self.param_list = QListWidget()
        param_layout.addWidget(self.param_list)
        
        # 参数编辑区域
        param_edit_group = QGroupBox("参数编辑")
        param_edit_layout = QFormLayout()
        
        self.param_name_edit = QLineEdit()
        self.param_value_edit = QLineEdit()
        self.param_type_combo = QComboBox()
        self.param_type_combo.addItems(["string", "int", "float", "bool", "list", "dict"])
        
        param_edit_layout.addRow("参数名:", self.param_name_edit)
        param_edit_layout.addRow("参数值:", self.param_value_edit)
        param_edit_layout.addRow("参数类型:", self.param_type_combo)
        
        param_edit_group.setLayout(param_edit_layout)
        param_layout.addWidget(param_edit_group)
        
        param_btn_layout = QHBoxLayout()
        self.add_param_btn = QPushButton("添加参数")
        self.edit_param_btn = QPushButton("更新参数")
        self.remove_param_btn = QPushButton("删除参数")
        param_btn_layout.addWidget(self.add_param_btn)
        param_btn_layout.addWidget(self.edit_param_btn)
        param_btn_layout.addWidget(self.remove_param_btn)
        param_btn_layout.addStretch()
        
        param_layout.addLayout(param_btn_layout)
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_failure_modes_tab(self):
        """创建失效模式标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 失效模式列表
        failure_group = QGroupBox("失效模式列表")
        failure_layout = QVBoxLayout()
        
        self.failure_list = QListWidget()
        failure_layout.addWidget(self.failure_list)
        
        # 失效模式操作按钮
        failure_btn_layout = QHBoxLayout()
        self.add_failure_btn = QPushButton("添加失效模式")
        self.edit_failure_btn = QPushButton("编辑失效模式")
        self.remove_failure_btn = QPushButton("删除失效模式")
        
        failure_btn_layout.addWidget(self.add_failure_btn)
        failure_btn_layout.addWidget(self.edit_failure_btn)
        failure_btn_layout.addWidget(self.remove_failure_btn)
        failure_btn_layout.addStretch()
        
        failure_layout.addLayout(failure_btn_layout)
        failure_group.setLayout(failure_layout)
        layout.addWidget(failure_group)
        
        # 失效模式详情
        detail_group = QGroupBox("失效模式详情")
        detail_layout = QFormLayout()
        
        self.failure_name_edit = QLineEdit()
        self.failure_type_combo = QComboBox()
        self.failure_type_combo.addItems([
            "功能失效", "性能降级", "时序异常", "数据错误", "资源耗尽", "通信中断"
        ])
        
        self.failure_desc_edit = QTextEdit()
        self.failure_desc_edit.setMaximumHeight(80)
        
        self.trigger_condition_edit = QTextEdit()
        self.trigger_condition_edit.setMaximumHeight(80)
        self.trigger_condition_edit.setPlaceholderText("描述触发此失效模式的条件...")
        
        detail_layout.addRow("失效模式名称:", self.failure_name_edit)
        detail_layout.addRow("失效类型:", self.failure_type_combo)
        detail_layout.addRow("失效描述:", self.failure_desc_edit)
        detail_layout.addRow("触发条件:", self.trigger_condition_edit)
        
        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_code_tab(self):
        """创建代码标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 代码编辑器
        code_group = QGroupBox("接口功能代码")
        code_layout = QVBoxLayout()
        
        self.code_edit = QTextEdit()
        self.code_edit.setPlainText("""# 接口功能代码示例
def interface_function(input_data):
    \"\"\"
    接口功能实现
    
    Args:
        input_data: 输入数据
        
    Returns:
        处理后的数据
    \"\"\"
    try:
        # 数据处理逻辑
        processed_data = process_data(input_data)
        
        # 返回结果
        return {
            'success': True,
            'data': processed_data,
            'timestamp': time.time()
        }
    except Exception as e:
        # 异常处理
        return {
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        }

def process_data(data):
    \"\"\"数据处理函数\"\"\"
    # 在此实现具体的数据处理逻辑
    return data
""")
        
        code_layout.addWidget(self.code_edit)
        code_group.setLayout(code_layout)
        layout.addWidget(code_group)
        
        # 代码验证按钮
        validate_layout = QHBoxLayout()
        self.validate_code_btn = QPushButton("验证代码")
        self.run_test_btn = QPushButton("运行测试")
        validate_layout.addWidget(self.validate_code_btn)
        validate_layout.addWidget(self.run_test_btn)
        validate_layout.addStretch()
        
        layout.addLayout(validate_layout)
        
        widget.setLayout(layout)
        return widget
    
    def init_connections(self):
        """初始化信号连接"""
        # 接口树选择
        self.interface_tree.itemSelectionChanged.connect(self.on_interface_selected)
        
        # 按钮连接
        self.new_interface_btn.clicked.connect(self.create_new_interface)
        self.delete_interface_btn.clicked.connect(self.delete_interface)
        self.duplicate_interface_btn.clicked.connect(self.duplicate_interface)
        
        self.save_btn.clicked.connect(self.save_interface)
        self.reset_btn.clicked.connect(self.reset_form)
        
        # 失效模式按钮
        self.add_failure_btn.clicked.connect(self.add_failure_mode)
        self.edit_failure_btn.clicked.connect(self.edit_failure_mode)
        self.remove_failure_btn.clicked.connect(self.remove_failure_mode)
        
        # 参数按钮
        self.add_param_btn.clicked.connect(self.add_parameter)
        self.edit_param_btn.clicked.connect(self.update_parameter)
        self.remove_param_btn.clicked.connect(self.remove_parameter)
        self.param_list.currentItemChanged.connect(self.on_parameter_selected)
        
        # 代码验证
        self.validate_code_btn.clicked.connect(self.validate_code)
        self.run_test_btn.clicked.connect(self.run_test)
        
        # 类型变化
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
    
    def on_interface_selected(self):
        """接口选择变化"""
        current_item = self.interface_tree.currentItem()
        if current_item:
            data = current_item.data(0, Qt.UserRole)
            if data:
                if data.get('type') == 'interface_template':
                    self.load_interface_template(data)
                elif data.get('type') == 'interface_instance':
                    self.load_interface_instance(data.get('interface_id'))
    
    def load_interface_template(self, template_data):
        """加载接口模板"""
        self.name_edit.setText(template_data['name'])
        self.type_combo.setCurrentText(template_data['category'])
        self.description_edit.setPlainText(f"这是一个{template_data['name']}的接口模板")
        
        # 清空参数列表
        self.param_list.clear()
        
        # 根据接口类型加载默认失效模式
        self.load_default_failure_modes(template_data['category'])
    
    def load_interface_instance(self, interface_id):
        """加载接口实例"""
        if interface_id in self.interfaces:
            interface = self.interfaces[interface_id]
            self.name_edit.setText(interface.name)
            self.description_edit.setPlainText(interface.description)
            
            # 设置接口类型
            type_mapping = {
                InterfaceType.ALGORITHM_OS: "算法-操作系统接口",
                InterfaceType.ALGORITHM_FRAMEWORK: "算法-智能框架接口",
                InterfaceType.ALGORITHM_APPLICATION: "算法-应用接口",
                InterfaceType.ALGORITHM_DATA_PLATFORM: "算法-数据平台接口",
                InterfaceType.ALGORITHM_HARDWARE: "算法-硬件设备接口",
                InterfaceType.SOFTWARE_HARDWARE: "一般接口"
            }
            interface_type = type_mapping.get(interface.interface_type, "一般接口")
            self.type_combo.setCurrentText(interface_type)
            
            # 设置方向
            direction_mapping = {
                InterfaceDirection.INPUT: "输入",
                InterfaceDirection.OUTPUT: "输出", 
                InterfaceDirection.BIDIRECTIONAL: "双向"
            }
            direction = direction_mapping.get(interface.direction, "双向")
            self.direction_combo.setCurrentText(direction)
            
            # 加载参数
            self.param_list.clear()
            for param_name, param_value in interface.parameters.items():
                param_data = {
                    'name': param_name,
                    'value': param_value,
                    'type': type(param_value).__name__
                }
                item = QListWidgetItem(f"{param_name}: {param_value} ({param_data['type']})")
                item.setData(Qt.UserRole, param_data)
                self.param_list.addItem(item)
            
            # 加载失效模式
            self.failure_list.clear()
            for failure_mode in interface.failure_modes:
                self.failure_list.addItem(failure_mode.name)
            
            # 加载代码
            self.code_edit.setPlainText(interface.python_code)
    
    def load_default_failure_modes(self, interface_type):
        """加载默认失效模式"""
        self.failure_list.clear()
        
        # 根据接口类型定义常见失效模式
        failure_modes = {
            "算法-操作系统接口": [
                "优先级反转导致对时超时", "环形缓冲溢出", "线程池枯竭", "定时器漂移", "看门狗漏触"
            ],
            "算法-智能框架接口": [
                "模型/算子版本不兼容", "GPU内核异常", "推理进程被OOM杀死", "DMA传输超时", "缓存不一致导致结果失效"
            ],
            "算法-应用接口": [
                "目标ID跳变引起航迹震荡", "指令NaN/Inf被传播", "交互死锁", "心跳中断触发保护", "报文分片丢失"
            ],
            "算法-数据平台接口": [
                "阻塞I/O反压上游链路", "时间窗外数据被消费", "帧错配（时空窗错位）", "坐标系标签错误", "分辨率/步幅错配"
            ],
            "算法-硬件设备接口": [
                "时间戳漂移导致姿态解算渐偏", "PPS抖动引起对时偏差", "高负载下丢帧", "UDP分片丢包", "串口黏包/超时"
            ]
        }
        
        modes = failure_modes.get(interface_type, ["通用失效模式"])
        for mode in modes:
            self.failure_list.addItem(mode)
    
    def create_new_interface(self):
        """创建新接口"""
        self.reset_form()
        self.name_edit.setText("新接口")
        self.name_edit.setFocus()
    
    def delete_interface(self):
        """删除接口"""
        current_item = self.interface_tree.currentItem()
        if current_item:
            data = current_item.data(0, Qt.UserRole)
            if data and data.get('type') == 'interface_instance':
                interface_id = data.get('interface_id')
                reply = QMessageBox.question(self, "确认删除", 
                                           f"确定要删除接口 '{current_item.text(0)}' 吗？")
                if reply == QMessageBox.Yes:
                    # 从接口字典中删除
                    if interface_id in self.interfaces:
                        del self.interfaces[interface_id]
                        # 保存到系统
                        self.save_interfaces_to_system()
                        # 更新接口树
                        self.update_interface_tree()
                        # 清空编辑器
                        self.reset_form()
                        QMessageBox.information(self, "成功", "接口已删除")
                    else:
                        QMessageBox.warning(self, "错误", "未找到要删除的接口")
            else:
                QMessageBox.warning(self, "警告", "只能删除已创建的接口实例")
    
    def duplicate_interface(self):
        """复制接口"""
        current_item = self.interface_tree.currentItem()
        if current_item:
            # 复制接口逻辑
            pass
    
    def save_interface(self):
        """保存接口"""
        try:
            if not self.name_edit.text().strip():
                QMessageBox.warning(self, "警告", "请输入接口名称")
                return
            
            # 创建或更新接口
            interface_name = self.name_edit.text().strip()
            
            # 获取当前选中的树项
            current_item = self.interface_tree.currentItem()
            
            # 如果当前选择的是模板，则创建新接口
            if current_item and current_item.data(0, Qt.UserRole) and \
               current_item.data(0, Qt.UserRole).get('type') == 'interface_template':
                # 创建新接口
                from ..models.interface_model import Interface, InterfaceType, InterfaceDirection
                
                # 映射接口类型
                type_mapping = {
                    "算法-操作系统接口": InterfaceType.ALGORITHM_OS,
                    "算法-智能框架接口": InterfaceType.ALGORITHM_FRAMEWORK,
                    "算法-应用接口": InterfaceType.ALGORITHM_APPLICATION,
                    "算法-数据平台接口": InterfaceType.ALGORITHM_DATA_PLATFORM,
                    "算法-硬件设备接口": InterfaceType.ALGORITHM_HARDWARE,
                    "一般接口": InterfaceType.SOFTWARE_HARDWARE
                }
                
                # 映射方向
                direction_mapping = {
                    "输入": InterfaceDirection.INPUT,
                    "输出": InterfaceDirection.OUTPUT,
                    "双向": InterfaceDirection.BIDIRECTIONAL
                }
                
                interface_type = type_mapping.get(self.type_combo.currentText(), InterfaceType.SOFTWARE_HARDWARE)
                direction = direction_mapping.get(self.direction_combo.currentText(), InterfaceDirection.BIDIRECTIONAL)
                
                interface = Interface(interface_name, self.description_edit.toPlainText(), 
                                     interface_type, direction)
                
                # 设置参数
                interface.parameters = {}
                for i in range(self.param_list.count()):
                    item = self.param_list.item(i)
                    param_data = item.data(Qt.UserRole)
                    if param_data:
                        interface.parameters[param_data['name']] = param_data['value']
                
                # 设置代码
                interface.python_code = self.code_edit.toPlainText()
                
                # 添加到接口库
                self.interfaces[interface.id] = interface
                
                # 保存到系统
                self.save_interfaces_to_system()
                
                # 更新接口树
                self.update_interface_tree()
                
                # 选择新创建的接口
                self.select_interface_in_tree(interface.id)
                
                QMessageBox.information(self, "成功", "接口已保存")
                
                # 发射信号
                self.interface_created.emit(interface)
            else:
                # 更新现有接口
                if current_item and current_item.data(0, Qt.UserRole):
                    data = current_item.data(0, Qt.UserRole)
                    if data.get('type') == 'interface_instance':
                        interface_id = data.get('interface_id')
                        if interface_id and interface_id in self.interfaces:
                            interface = self.interfaces[interface_id]
                            interface.name = interface_name
                            interface.description = self.description_edit.toPlainText()
                            
                            # 更新类型和方向
                            type_mapping = {
                                "算法-操作系统接口": InterfaceType.ALGORITHM_OS,
                                "算法-智能框架接口": InterfaceType.ALGORITHM_FRAMEWORK,
                                "算法-应用接口": InterfaceType.ALGORITHM_APPLICATION,
                                "算法-数据平台接口": InterfaceType.ALGORITHM_DATA_PLATFORM,
                                "算法-硬件设备接口": InterfaceType.ALGORITHM_HARDWARE,
                                "一般接口": InterfaceType.SOFTWARE_HARDWARE
                            }
                            direction_mapping = {
                                "输入": InterfaceDirection.INPUT,
                                "输出": InterfaceDirection.OUTPUT,
                                "双向": InterfaceDirection.BIDIRECTIONAL
                            }
                            interface.interface_type = type_mapping.get(self.type_combo.currentText(), InterfaceType.SOFTWARE_HARDWARE)
                            interface.direction = direction_mapping.get(self.direction_combo.currentText(), InterfaceDirection.BIDIRECTIONAL)
                            
                            # 更新参数
                            interface.parameters = {}
                            for i in range(self.param_list.count()):
                                item = self.param_list.item(i)
                                param_data = item.data(Qt.UserRole)
                                if param_data:
                                    interface.parameters[param_data['name']] = param_data['value']
                            
                            # 更新代码
                            interface.python_code = self.code_edit.toPlainText()
                            
                            # 保存到系统
                            self.save_interfaces_to_system()
                            
                            # 更新接口树
                            self.update_interface_tree()
                            
                            QMessageBox.information(self, "成功", "接口已更新")
                            
                            # 发射信号
                            self.interface_modified.emit(interface)
                        else:
                            QMessageBox.warning(self, "错误", "未找到要更新的接口")
                    else:
                        QMessageBox.warning(self, "警告", "请选择要保存的接口")
                else:
                    QMessageBox.warning(self, "警告", "请选择要保存的接口")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存接口时发生错误：{str(e)}")
    
    def reset_form(self):
        """重置表单"""
        self.name_edit.clear()
        self.type_combo.setCurrentIndex(0)
        self.subtype_combo.clear()
        self.description_edit.clear()
        self.param_list.clear()
        self.failure_list.clear()
        self.failure_name_edit.clear()
        self.failure_desc_edit.clear()
        self.trigger_condition_edit.clear()
    
    def add_failure_mode(self):
        """添加失效模式"""
        if self.failure_name_edit.text().strip():
            self.failure_list.addItem(self.failure_name_edit.text())
            self.failure_name_edit.clear()
    
    def edit_failure_mode(self):
        """编辑失效模式"""
        current_item = self.failure_list.currentItem()
        if current_item:
            self.failure_name_edit.setText(current_item.text())
    
    def remove_failure_mode(self):
        """删除失效模式"""
        current_row = self.failure_list.currentRow()
        if current_row >= 0:
            self.failure_list.takeItem(current_row)
    
    def add_parameter(self):
        """添加参数"""
        # 这里可以打开一个参数编辑对话框
        param_name = f"参数{self.param_list.count() + 1}"
        self.param_list.addItem(param_name)
    
    def on_parameter_selected(self, current, previous):
        """参数选择事件"""
        if current:
            param_data = current.data(Qt.UserRole)
            if param_data:
                self.param_name_edit.setText(param_data.get('name', ''))
                self.param_value_edit.setText(str(param_data.get('value', '')))
                self.param_type_combo.setCurrentText(param_data.get('type', 'string'))
    
    def add_parameter(self):
        """添加参数"""
        param_name = self.param_name_edit.text().strip()
        param_value = self.param_value_edit.text().strip()
        param_type = self.param_type_combo.currentText()
        
        if not param_name:
            QMessageBox.warning(self, "警告", "请输入参数名")
            return
        
        # 创建参数数据
        param_data = {
            'name': param_name,
            'value': param_value,
            'type': param_type
        }
        
        # 添加到列表
        item = QListWidgetItem(f"{param_name}: {param_value} ({param_type})")
        item.setData(Qt.UserRole, param_data)
        self.param_list.addItem(item)
        
        # 清空编辑区域
        self.param_name_edit.clear()
        self.param_value_edit.clear()
    
    def update_parameter(self):
        """更新参数"""
        current_item = self.param_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要更新的参数")
            return
        
        param_name = self.param_name_edit.text().strip()
        param_value = self.param_value_edit.text().strip()
        param_type = self.param_type_combo.currentText()
        
        if not param_name:
            QMessageBox.warning(self, "警告", "请输入参数名")
            return
        
        # 更新参数数据
        param_data = {
            'name': param_name,
            'value': param_value,
            'type': param_type
        }
        
        # 更新列表项
        current_item.setText(f"{param_name}: {param_value} ({param_type})")
        current_item.setData(Qt.UserRole, param_data)
    
    def remove_parameter(self):
        """删除参数"""
        current_row = self.param_list.currentRow()
        if current_row >= 0:
            self.param_list.takeItem(current_row)
    
    def validate_code(self):
        """验证代码"""
        code = self.code_edit.toPlainText()
        try:
            compile(code, '<string>', 'exec')
            QMessageBox.information(self, "验证成功", "代码语法正确")
        except SyntaxError as e:
            QMessageBox.warning(self, "语法错误", f"代码语法错误：{str(e)}")
    
    def run_test(self):
        """运行测试"""
        QMessageBox.information(self, "测试", "测试功能待实现")
    
    def on_type_changed(self, interface_type):
        """接口类型变化"""
        # 更新子类型选项
        subtypes = {
            "算法-操作系统接口": ["进程管理", "内存管理", "文件系统", "网络通信", "设备驱动"],
            "算法-智能框架接口": ["模型管理", "推理引擎", "数据处理", "GPU加速", "分布式计算"],
            "算法-应用接口": ["API接口", "数据交换", "配置管理", "状态监控", "事件处理"],
            "算法-数据平台接口": ["数据访问", "数据存储", "数据查询", "数据同步", "缓存管理"],
            "算法-硬件设备接口": ["传感器", "执行器", "计算硬件", "通信硬件", "存储硬件"],
            "一般接口": ["软硬件", "软件间", "硬件间", "用户接口", "网络接口"]
        }
        
        self.subtype_combo.clear()
        if interface_type in subtypes:
            self.subtype_combo.addItems(subtypes[interface_type])
