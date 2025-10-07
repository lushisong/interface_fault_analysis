"""
接口选择对话框
用于在模块建模中选择接口模板
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QPushButton, QLabel, QTextEdit,
                             QSplitter, QGroupBox, QFormLayout, QLineEdit,
                             QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ..models.interface_model import Interface
from ..models.base_model import ConnectionPoint


class InterfaceTemplateDialog(QDialog):
    """接口模板选择对话框"""
    
    interface_selected = pyqtSignal(object)  # 选择接口信号
    
    def __init__(self, interfaces_dict, parent=None):
        super().__init__(parent)
        self.interfaces = interfaces_dict
        self.selected_interface = None
        
        self.setWindowTitle("选择接口模板")
        self.setModal(True)
        self.resize(800, 600)
        
        self.init_ui()
        self.init_connections()
        self.load_interfaces()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 主分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：接口列表
        left_panel = self.create_interface_list()
        splitter.addWidget(left_panel)
        
        # 右侧：接口详情
        right_panel = self.create_interface_details()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        self.select_btn = QPushButton("选择")
        self.cancel_btn = QPushButton("取消")
        self.create_new_btn = QPushButton("创建新接口")
        
        button_layout.addStretch()
        button_layout.addWidget(self.create_new_btn)
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # 初始状态
        self.select_btn.setEnabled(False)
    
    def create_interface_list(self):
        """创建接口列表面板"""
        widget = QGroupBox("接口模板列表")
        layout = QVBoxLayout()
        
        self.interface_list = QListWidget()
        layout.addWidget(self.interface_list)
        
        widget.setLayout(layout)
        return widget
    
    def create_interface_details(self):
        """创建接口详情面板"""
        widget = QGroupBox("接口详情")
        layout = QVBoxLayout()
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        
        self.name_label = QLabel()
        self.type_label = QLabel()
        self.category_label = QLabel()
        self.data_type_label = QLabel()
        
        basic_layout.addRow("名称:", self.name_label)
        basic_layout.addRow("类型:", self.type_label)
        basic_layout.addRow("分类:", self.category_label)
        basic_layout.addRow("数据类型:", self.data_type_label)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 描述信息
        desc_group = QGroupBox("描述")
        desc_layout = QVBoxLayout()
        
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(100)
        
        desc_layout.addWidget(self.description_text)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # 失效模式
        failure_group = QGroupBox("失效模式")
        failure_layout = QVBoxLayout()
        
        self.failure_text = QTextEdit()
        self.failure_text.setReadOnly(True)
        self.failure_text.setMaximumHeight(100)
        
        failure_layout.addWidget(self.failure_text)
        failure_group.setLayout(failure_layout)
        layout.addWidget(failure_group)
        
        widget.setLayout(layout)
        return widget
    
    def init_connections(self):
        """初始化信号连接"""
        self.interface_list.currentItemChanged.connect(self.on_interface_selected)
        self.interface_list.itemDoubleClicked.connect(self.on_interface_double_clicked)
        
        self.select_btn.clicked.connect(self.accept_selection)
        self.cancel_btn.clicked.connect(self.reject)
        self.create_new_btn.clicked.connect(self.create_new_interface)
    
    def load_interfaces(self):
        """加载接口列表"""
        self.interface_list.clear()
        
        for interface_id, interface in self.interfaces.items():
            item = QListWidgetItem(f"{interface.name} ({interface.interface_type})")
            item.setData(Qt.UserRole, interface)
            self.interface_list.addItem(item)
    
    def on_interface_selected(self, current, previous):
        """接口选择事件"""
        if current:
            interface = current.data(Qt.UserRole)
            self.display_interface_details(interface)
            self.selected_interface = interface
            self.select_btn.setEnabled(True)
        else:
            self.clear_interface_details()
            self.selected_interface = None
            self.select_btn.setEnabled(False)
    
    def on_interface_double_clicked(self, item):
        """接口双击事件"""
        if item:
            self.selected_interface = item.data(Qt.UserRole)
            self.accept_selection()
    
    def display_interface_details(self, interface):
        """显示接口详情"""
        self.name_label.setText(interface.name)
        self.type_label.setText(interface.interface_type)
        self.category_label.setText(interface.category)
        self.data_type_label.setText(interface.data_type)
        self.description_text.setPlainText(interface.description)
        
        # 显示失效模式
        failure_modes = []
        for failure in interface.failure_modes:
            failure_modes.append(f"• {failure.name}: {failure.description}")
        self.failure_text.setPlainText("\n".join(failure_modes))
    
    def clear_interface_details(self):
        """清空接口详情"""
        self.name_label.setText("")
        self.type_label.setText("")
        self.category_label.setText("")
        self.data_type_label.setText("")
        self.description_text.setPlainText("")
        self.failure_text.setPlainText("")
    
    def accept_selection(self):
        """确认选择"""
        if self.selected_interface:
            self.interface_selected.emit(self.selected_interface)
            self.accept()
        else:
            QMessageBox.warning(self, "警告", "请先选择一个接口模板")
    
    def create_new_interface(self):
        """创建新接口"""
        # 这里可以打开接口编辑对话框创建新接口
        # 暂时先关闭对话框，返回空结果
        self.selected_interface = None
        self.reject()
    
    def get_selected_interface(self):
        """获取选择的接口"""
        return self.selected_interface


class InterfaceInstanceDialog(QDialog):
    """接口实例化编辑对话框"""
    
    def __init__(self, template_interface, parent=None):
        super().__init__(parent)
        self.template_interface = template_interface
        self.instance_interface = None
        
        self.setWindowTitle(f"编辑接口实例 - 基于 {template_interface.name}")
        self.setModal(True)
        self.resize(600, 500)
        
        self.init_ui()
        self.init_connections()
        self.load_template_data()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["input", "output", "bidirectional"])
        self.data_type_edit = QLineEdit()
        
        basic_layout.addRow("名称:", self.name_edit)
        basic_layout.addRow("类型:", self.type_combo)
        basic_layout.addRow("数据类型:", self.data_type_edit)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 描述信息
        desc_group = QGroupBox("描述")
        desc_layout = QVBoxLayout()
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        
        desc_layout.addWidget(self.description_edit)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def init_connections(self):
        """初始化信号连接"""
        self.ok_btn.clicked.connect(self.accept_instance)
        self.cancel_btn.clicked.connect(self.reject)
    
    def load_template_data(self):
        """加载模板数据"""
        self.name_edit.setText(f"{self.template_interface.name}_实例")
        self.type_combo.setCurrentText(self.template_interface.interface_type)
        self.data_type_edit.setText(self.template_interface.data_type)
        self.description_edit.setPlainText(self.template_interface.description)
    
    def accept_instance(self):
        """确认实例化"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入接口名称")
            return
        
        # 创建接口实例（这里创建ConnectionPoint而不是Interface）
        self.instance_interface = ConnectionPoint(
            name=self.name_edit.text().strip(),
            connection_type=self.type_combo.currentText(),
            data_type=self.data_type_edit.text().strip()
        )
        
        # 复制模板的一些属性
        if hasattr(self.template_interface, 'variables'):
            self.instance_interface.variables = self.template_interface.variables.copy()
        
        self.accept()
    
    def get_instance_interface(self):
        """获取实例化的接口"""
        return self.instance_interface