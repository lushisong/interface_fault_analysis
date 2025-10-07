"""
接口编辑对话框
复用接口建模的界面与逻辑
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QFormLayout, QLineEdit, QTextEdit, QComboBox,
                             QPushButton, QLabel, QGroupBox, QListWidget,
                             QListWidgetItem, QMessageBox, QCheckBox, QSpinBox,
                             QDoubleSpinBox, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ..models.interface_model import (Interface, InterfaceType, HardwareInterfaceSubtype,
                                    InterfaceFailureMode, FailureMode, TriggerCondition)
from ..models.base_model import ConnectionPoint


class InterfaceEditDialog(QDialog):
    """接口编辑对话框"""
    
    interface_saved = pyqtSignal(object)  # 接口保存信号
    
    def __init__(self, connection_point=None, parent=None):
        super().__init__(parent)
        self.connection_point = connection_point
        self.is_new = connection_point is None
        
        if self.is_new:
            self.setWindowTitle("新建接口")
            self.connection_point = ConnectionPoint()
        else:
            self.setWindowTitle(f"编辑接口 - {connection_point.name}")
        
        self.setModal(True)
        self.resize(800, 600)
        
        self.init_ui()
        self.init_connections()
        self.load_data()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 标签页
        self.editor_tabs = QTabWidget()
        
        # 基本信息标签页
        basic_tab = self.create_basic_info_tab()
        self.editor_tabs.addTab(basic_tab, "基本信息")
        
        # 变量标签页
        variables_tab = self.create_variables_tab()
        self.editor_tabs.addTab(variables_tab, "关联变量")
        
        layout.addWidget(self.editor_tabs)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.cancel_btn = QPushButton("取消")
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_basic_info_tab(self):
        """创建基本信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 基本信息表单
        form_group = QGroupBox("接口基本信息")
        form_layout = QFormLayout()
        
        # 名称
        self.name_edit = QLineEdit()
        form_layout.addRow("名称:", self.name_edit)
        
        # 类型
        self.type_combo = QComboBox()
        self.type_combo.addItems(["input", "output", "bidirectional"])
        form_layout.addRow("类型:", self.type_combo)
        
        # 数据类型
        self.data_type_edit = QLineEdit()
        form_layout.addRow("数据类型:", self.data_type_edit)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 位置信息
        position_group = QGroupBox("位置信息")
        position_layout = QFormLayout()
        
        self.pos_x_spin = QDoubleSpinBox()
        self.pos_x_spin.setRange(-1000, 1000)
        self.pos_x_spin.setValue(0)
        position_layout.addRow("X坐标:", self.pos_x_spin)
        
        self.pos_y_spin = QDoubleSpinBox()
        self.pos_y_spin.setRange(-1000, 1000)
        self.pos_y_spin.setValue(0)
        position_layout.addRow("Y坐标:", self.pos_y_spin)
        
        position_group.setLayout(position_layout)
        layout.addWidget(position_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_variables_tab(self):
        """创建变量标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 变量列表
        variables_group = QGroupBox("关联变量")
        variables_layout = QVBoxLayout()
        
        # 变量列表控件
        self.variables_list = QListWidget()
        variables_layout.addWidget(self.variables_list)
        
        # 变量操作按钮
        var_button_layout = QHBoxLayout()
        self.add_var_btn = QPushButton("添加变量")
        self.remove_var_btn = QPushButton("移除变量")
        
        var_button_layout.addWidget(self.add_var_btn)
        var_button_layout.addWidget(self.remove_var_btn)
        var_button_layout.addStretch()
        
        variables_layout.addLayout(var_button_layout)
        
        # 变量编辑区域
        var_edit_group = QGroupBox("变量编辑")
        var_edit_layout = QFormLayout()
        
        self.var_name_edit = QLineEdit()
        var_edit_layout.addRow("变量名:", self.var_name_edit)
        
        var_edit_group.setLayout(var_edit_layout)
        variables_layout.addWidget(var_edit_group)
        
        variables_group.setLayout(variables_layout)
        layout.addWidget(variables_group)
        
        widget.setLayout(layout)
        return widget
    
    def init_connections(self):
        """初始化信号连接"""
        self.save_btn.clicked.connect(self.save_interface)
        self.cancel_btn.clicked.connect(self.reject)
        
        # 变量操作
        self.add_var_btn.clicked.connect(self.add_variable)
        self.remove_var_btn.clicked.connect(self.remove_variable)
        self.variables_list.currentItemChanged.connect(self.on_variable_selected)
        
        # 变量名编辑
        self.var_name_edit.textChanged.connect(self.on_variable_name_changed)
    
    def load_data(self):
        """加载数据"""
        if self.connection_point:
            self.name_edit.setText(self.connection_point.name)
            self.type_combo.setCurrentText(self.connection_point.connection_type)
            self.data_type_edit.setText(self.connection_point.data_type)
            
            if self.connection_point.position:
                self.pos_x_spin.setValue(self.connection_point.position.x)
                self.pos_y_spin.setValue(self.connection_point.position.y)
            
            # 加载变量
            self.load_variables()
    
    def load_variables(self):
        """加载变量列表"""
        self.variables_list.clear()
        if hasattr(self.connection_point, 'variables'):
            for var_name in self.connection_point.variables:
                item = QListWidgetItem(var_name)
                self.variables_list.addItem(item)
    
    def add_variable(self):
        """添加变量"""
        var_name = f"变量{self.variables_list.count() + 1}"
        item = QListWidgetItem(var_name)
        self.variables_list.addItem(item)
        self.variables_list.setCurrentItem(item)
        self.var_name_edit.setText(var_name)
        self.var_name_edit.selectAll()
        self.var_name_edit.setFocus()
    
    def remove_variable(self):
        """移除变量"""
        current_item = self.variables_list.currentItem()
        if current_item:
            row = self.variables_list.row(current_item)
            self.variables_list.takeItem(row)
            self.var_name_edit.clear()
    
    def on_variable_selected(self, current, previous):
        """变量选择事件"""
        if current:
            self.var_name_edit.setText(current.text())
        else:
            self.var_name_edit.clear()
    
    def on_variable_name_changed(self, text):
        """变量名改变事件"""
        current_item = self.variables_list.currentItem()
        if current_item:
            current_item.setText(text)
    
    def save_interface(self):
        """保存接口"""
        # 验证输入
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入接口名称")
            return
        
        # 更新接口数据
        self.connection_point.name = self.name_edit.text().strip()
        self.connection_point.connection_type = self.type_combo.currentText()
        self.connection_point.data_type = self.data_type_edit.text().strip()
        
        # 更新位置
        from ..models.base_model import Point
        self.connection_point.position = Point(
            self.pos_x_spin.value(),
            self.pos_y_spin.value()
        )
        
        # 更新变量列表
        variables = []
        for i in range(self.variables_list.count()):
            item = self.variables_list.item(i)
            if item.text().strip():
                variables.append(item.text().strip())
        
        self.connection_point.variables = variables
        
        # 发送信号
        self.interface_saved.emit(self.connection_point)
        self.accept()
    
    def get_connection_point(self):
        """获取接口"""
        return self.connection_point