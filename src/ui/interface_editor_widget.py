# -*- coding: utf-8 -*-
"""
接口编辑器控件
Interface Editor Widget

封装的接口编辑控件，可在接口建模和模块建模中复用
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QFormLayout, QLineEdit, QTextEdit, QComboBox,
                             QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QListWidget, QListWidgetItem,
                             QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal

from ..models.interface_model import (Interface, InterfaceType, HardwareInterfaceSubtype,
                                    InterfaceFailureMode, FailureMode, TriggerCondition,
                                    InterfaceDirection)


class InterfaceEditorWidget(QWidget):
    """接口编辑器控件"""
    
    # 信号定义
    interface_changed = pyqtSignal(object)  # 接口数据变化
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_interface = None
        self.init_ui()
        self.init_connections()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 创建标签页
        self.editor_tabs = QTabWidget()
        self.editor_tabs.addTab(self.create_basic_info_tab(), "基本信息")
        self.editor_tabs.addTab(self.create_failure_modes_tab(), "失效模式")
        self.editor_tabs.addTab(self.create_code_tab(), "功能代码")
        
        layout.addWidget(self.editor_tabs)
        
        # 保存按钮
        save_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存接口")
        self.reset_btn = QPushButton("重置")
        save_layout.addWidget(self.save_btn)
        save_layout.addWidget(self.reset_btn)
        save_layout.addStretch()
        
        layout.addLayout(save_layout)
        
        self.setLayout(layout)
    
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
        
        # 技术参数
        self.protocol_edit = QLineEdit()
        self.data_format_edit = QLineEdit()
        self.bandwidth_spin = QDoubleSpinBox()
        self.bandwidth_spin.setRange(0, 10000)
        self.bandwidth_spin.setSuffix(" Mbps")
        self.latency_spin = QDoubleSpinBox()
        self.latency_spin.setRange(0, 1000)
        self.latency_spin.setSuffix(" ms")
        self.reliability_spin = QDoubleSpinBox()
        self.reliability_spin.setRange(0, 1)
        self.reliability_spin.setDecimals(4)
        self.reliability_spin.setValue(0.99)
        
        form_layout.addRow("接口名称:", self.name_edit)
        form_layout.addRow("接口类型:", self.type_combo)
        form_layout.addRow("接口方向:", self.direction_combo)
        form_layout.addRow("接口子类型:", self.subtype_combo)
        form_layout.addRow("接口描述:", self.description_edit)
        form_layout.addRow("通信协议:", self.protocol_edit)
        form_layout.addRow("数据格式:", self.data_format_edit)
        form_layout.addRow("带宽:", self.bandwidth_spin)
        form_layout.addRow("延迟:", self.latency_spin)
        form_layout.addRow("可靠性:", self.reliability_spin)
        
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
        
        widget.setLayout(layout)
        return widget
    
    def create_code_tab(self):
        """创建功能代码标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 功能代码编辑
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
        # 按钮连接
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
        
        # 数据变化监听
        self.name_edit.textChanged.connect(self.on_data_changed)
        self.description_edit.textChanged.connect(self.on_data_changed)
        self.protocol_edit.textChanged.connect(self.on_data_changed)
        self.data_format_edit.textChanged.connect(self.on_data_changed)
        self.code_edit.textChanged.connect(self.on_data_changed)
    
    def load_interface(self, interface: Interface):
        """加载接口数据"""
        self.current_interface = interface
        if not interface:
            self.clear_form()
            return
        
        # 加载基本信息
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
        type_text = type_mapping.get(interface.interface_type, "一般接口")
        self.type_combo.setCurrentText(type_text)
        
        # 设置接口方向
        direction_mapping = {
            InterfaceDirection.INPUT: "输入",
            InterfaceDirection.OUTPUT: "输出",
            InterfaceDirection.BIDIRECTIONAL: "双向"
        }
        direction_text = direction_mapping.get(interface.direction, "双向")
        self.direction_combo.setCurrentText(direction_text)
        
        # 设置技术参数
        self.protocol_edit.setText(interface.protocol)
        self.data_format_edit.setText(interface.data_format)
        self.bandwidth_spin.setValue(interface.bandwidth)
        self.latency_spin.setValue(interface.latency)
        self.reliability_spin.setValue(interface.reliability)
        
        # 加载参数
        self.load_parameters()
        
        # 加载失效模式
        self.load_failure_modes()
        
        # 加载代码
        self.code_edit.setPlainText(interface.python_code)
        
        # 更新子类型
        self.update_subtype_combo()
    
    def clear_form(self):
        """清空表单"""
        self.name_edit.clear()
        self.description_edit.clear()
        self.protocol_edit.clear()
        self.data_format_edit.clear()
        self.bandwidth_spin.setValue(0)
        self.latency_spin.setValue(0)
        self.reliability_spin.setValue(0.99)
        self.param_list.clear()
        self.failure_list.clear()
        self.code_edit.clear()
    
    def save_interface(self):
        """保存接口"""
        if not self.current_interface:
            self.current_interface = Interface()
        
        # 保存基本信息
        self.current_interface.name = self.name_edit.text()
        self.current_interface.description = self.description_edit.toPlainText()
        
        # 保存接口类型
        type_mapping = {
            "算法-操作系统接口": InterfaceType.ALGORITHM_OS,
            "算法-智能框架接口": InterfaceType.ALGORITHM_FRAMEWORK,
            "算法-应用接口": InterfaceType.ALGORITHM_APPLICATION,
            "算法-数据平台接口": InterfaceType.ALGORITHM_DATA_PLATFORM,
            "算法-硬件设备接口": InterfaceType.ALGORITHM_HARDWARE,
            "一般接口": InterfaceType.SOFTWARE_HARDWARE
        }
        self.current_interface.interface_type = type_mapping.get(
            self.type_combo.currentText(), InterfaceType.SOFTWARE_HARDWARE)
        
        # 保存接口方向
        direction_mapping = {
            "输入": InterfaceDirection.INPUT,
            "输出": InterfaceDirection.OUTPUT,
            "双向": InterfaceDirection.BIDIRECTIONAL
        }
        self.current_interface.direction = direction_mapping.get(
            self.direction_combo.currentText(), InterfaceDirection.BIDIRECTIONAL)
        
        # 保存技术参数
        self.current_interface.protocol = self.protocol_edit.text()
        self.current_interface.data_format = self.data_format_edit.text()
        self.current_interface.bandwidth = self.bandwidth_spin.value()
        self.current_interface.latency = self.latency_spin.value()
        self.current_interface.reliability = self.reliability_spin.value()
        
        # 保存代码
        self.current_interface.python_code = self.code_edit.toPlainText()
        
        # 更新修改时间
        self.current_interface.update_modified_time()
        
        # 发送信号
        self.interface_changed.emit(self.current_interface)
        
        QMessageBox.information(self, "成功", "接口保存成功！")
    
    def reset_form(self):
        """重置表单"""
        if self.current_interface:
            self.load_interface(self.current_interface)
        else:
            self.clear_form()
    
    def on_type_changed(self):
        """接口类型变化"""
        self.update_subtype_combo()
    
    def update_subtype_combo(self):
        """更新子类型下拉框"""
        self.subtype_combo.clear()
        current_type = self.type_combo.currentText()
        
        if current_type == "算法-硬件设备接口":
            self.subtype_combo.addItems(["传感器接口", "执行器接口", "专用计算硬件接口"])
        else:
            self.subtype_combo.addItem("无")
    
    def load_parameters(self):
        """加载参数列表"""
        self.param_list.clear()
        if self.current_interface:
            for key, value in self.current_interface.parameters.items():
                item = QListWidgetItem(f"{key}: {value}")
                item.setData(Qt.UserRole, key)
                self.param_list.addItem(item)
    
    def load_failure_modes(self):
        """加载失效模式列表"""
        self.failure_list.clear()
        if self.current_interface:
            for failure_mode in self.current_interface.failure_modes:
                item = QListWidgetItem(failure_mode.name)
                item.setData(Qt.UserRole, failure_mode)
                self.failure_list.addItem(item)
    
    def on_parameter_selected(self):
        """参数选择变化"""
        current_item = self.param_list.currentItem()
        if current_item and self.current_interface:
            param_key = current_item.data(Qt.UserRole)
            param_value = self.current_interface.parameters.get(param_key, "")
            self.param_name_edit.setText(param_key)
            self.param_value_edit.setText(str(param_value))
    
    def add_parameter(self):
        """添加参数"""
        param_name = self.param_name_edit.text().strip()
        param_value = self.param_value_edit.text().strip()
        
        if not param_name:
            QMessageBox.warning(self, "警告", "请输入参数名称")
            return
        
        if not self.current_interface:
            self.current_interface = Interface()
        
        # 根据类型转换值
        param_type = self.param_type_combo.currentText()
        try:
            if param_type == "int":
                param_value = int(param_value)
            elif param_type == "float":
                param_value = float(param_value)
            elif param_type == "bool":
                param_value = param_value.lower() in ('true', '1', 'yes', 'on')
            elif param_type == "list":
                param_value = eval(param_value) if param_value else []
            elif param_type == "dict":
                param_value = eval(param_value) if param_value else {}
        except:
            QMessageBox.warning(self, "警告", f"参数值格式错误，无法转换为{param_type}类型")
            return
        
        self.current_interface.parameters[param_name] = param_value
        self.load_parameters()
        self.param_name_edit.clear()
        self.param_value_edit.clear()
    
    def update_parameter(self):
        """更新参数"""
        self.add_parameter()  # 添加和更新逻辑相同
    
    def remove_parameter(self):
        """删除参数"""
        current_item = self.param_list.currentItem()
        if current_item and self.current_interface:
            param_key = current_item.data(Qt.UserRole)
            if param_key in self.current_interface.parameters:
                del self.current_interface.parameters[param_key]
                self.load_parameters()
                self.param_name_edit.clear()
                self.param_value_edit.clear()
    
    def add_failure_mode(self):
        """添加失效模式"""
        # 这里可以打开失效模式编辑对话框
        QMessageBox.information(self, "提示", "失效模式编辑功能待实现")
    
    def edit_failure_mode(self):
        """编辑失效模式"""
        QMessageBox.information(self, "提示", "失效模式编辑功能待实现")
    
    def remove_failure_mode(self):
        """删除失效模式"""
        current_item = self.failure_list.currentItem()
        if current_item and self.current_interface:
            failure_mode = current_item.data(Qt.UserRole)
            self.current_interface.failure_modes.remove(failure_mode)
            self.load_failure_modes()
    
    def validate_code(self):
        """验证代码"""
        code = self.code_edit.toPlainText()
        if not code.strip():
            QMessageBox.warning(self, "警告", "请输入代码")
            return
        
        try:
            compile(code, '<string>', 'exec')
            QMessageBox.information(self, "成功", "代码语法验证通过")
        except SyntaxError as e:
            QMessageBox.warning(self, "语法错误", f"代码语法错误：\n{e}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"代码验证失败：\n{e}")
    
    def run_test(self):
        """运行测试"""
        QMessageBox.information(self, "提示", "代码测试功能待实现")
    
    def on_data_changed(self):
        """数据变化"""
        # 可以在这里实现实时保存或其他逻辑
        pass
    
    def get_interface(self) -> Interface:
        """获取当前接口对象"""
        return self.current_interface
    
    def set_read_only(self, read_only: bool):
        """设置只读模式"""
        self.name_edit.setReadOnly(read_only)
        self.description_edit.setReadOnly(read_only)
        self.protocol_edit.setReadOnly(read_only)
        self.data_format_edit.setReadOnly(read_only)
        self.code_edit.setReadOnly(read_only)
        
        self.type_combo.setEnabled(not read_only)
        self.direction_combo.setEnabled(not read_only)
        self.subtype_combo.setEnabled(not read_only)
        self.bandwidth_spin.setEnabled(not read_only)
        self.latency_spin.setEnabled(not read_only)
        self.reliability_spin.setEnabled(not read_only)
        
        self.save_btn.setEnabled(not read_only)
        self.reset_btn.setEnabled(not read_only)
        self.add_param_btn.setEnabled(not read_only)
        self.edit_param_btn.setEnabled(not read_only)
        self.remove_param_btn.setEnabled(not read_only)
        self.add_failure_btn.setEnabled(not read_only)
        self.edit_failure_btn.setEnabled(not read_only)
        self.remove_failure_btn.setEnabled(not read_only)