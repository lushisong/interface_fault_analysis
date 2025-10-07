# -*- coding: utf-8 -*-
"""
系统画布
System Canvas

类似Simulink的图形化建模界面，支持拖拽模块和连线
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, 
                             QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
                             QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem,
                             QGraphicsPathItem,
                             QPushButton, QToolBar, QAction, QActionGroup, QLabel, 
                             QDialog, QFormLayout, QLineEdit, QTextEdit, QComboBox,
                             QDialogButtonBox, QListWidget, QListWidgetItem, QSplitter,
                             QGroupBox, QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QTimer
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QFont, QPainterPath


class ModuleConfigDialog(QDialog):
    """模块配置对话框"""
    
    def __init__(self, module, parent=None):
        super().__init__(parent)
        self.module = module
        self.setWindowTitle(f"配置模块: {module.name}")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        self.load_module_data()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["硬件模块", "软件模块", "算法模块"])
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        
        basic_layout.addRow("名称:", self.name_edit)
        basic_layout.addRow("类型:", self.type_combo)
        basic_layout.addRow("描述:", self.description_edit)
        basic_group.setLayout(basic_layout)
        
        # 接口信息
        interface_group = QGroupBox("接口配置")
        interface_layout = QVBoxLayout()
        
        self.interface_list = QListWidget()
        interface_layout.addWidget(QLabel("接口列表:"))
        interface_layout.addWidget(self.interface_list)
        interface_group.setLayout(interface_layout)
        
        # Python代码
        code_group = QGroupBox("功能代码")
        code_layout = QVBoxLayout()
        
        self.code_edit = QTextEdit()
        self.code_edit.setPlainText("# 在此编写模块的功能代码\ndef process(inputs):\n    # 处理逻辑\n    return outputs")
        code_layout.addWidget(self.code_edit)
        code_group.setLayout(code_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(basic_group)
        layout.addWidget(interface_group)
        layout.addWidget(code_group)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_module_data(self):
        """加载模块数据"""
        self.name_edit.setText(self.module.name)
        self.type_combo.setCurrentText(self.module.module_type.value)
        self.description_edit.setPlainText(self.module.description)
        
        # 加载接口列表
        for interface in self.module.interfaces:
            self.interface_list.addItem(f"{interface.name} ({interface.direction.value})")
        
        if hasattr(self.module, 'code') and self.module.code:
            self.code_edit.setPlainText(self.module.code)
    
    def get_module_data(self):
        """获取修改后的模块数据"""
        return {
            'name': self.name_edit.text(),
            'type': self.type_combo.currentText(),
            'description': self.description_edit.toPlainText(),
            'code': self.code_edit.toPlainText()
        }


class InterfaceGraphicsItem(QGraphicsEllipseItem):
    """接口图形项"""
    
    # 信号定义
    connection_started = pyqtSignal(object, str)  # 开始连线 (接口项, 接口ID)
    
    def __init__(self, connection_point, parent=None):
        super().__init__(0, 0, 12, 12, parent)
        self.connection_point = connection_point
        
        # 设置外观
        if connection_point.connection_type == "input":
            self.setBrush(QBrush(QColor(0, 255, 0)))  # 输入接口为绿色
        elif connection_point.connection_type == "output":
            self.setBrush(QBrush(QColor(255, 165, 0)))  # 输出接口为橙色
        else:
            self.setBrush(QBrush(QColor(135, 206, 250)))  # 双向接口为天蓝色
            
        self.setPen(QPen(QColor(0, 0, 0), 1))
        
        # 设置工具提示
        tooltip_text = f"接口: {connection_point.name}\n类型: {connection_point.connection_type}\n数据类型: {connection_point.data_type}"
        if hasattr(connection_point, 'variables') and connection_point.variables:
            tooltip_text += f"\n变量: {', '.join(connection_point.variables)}"
        tooltip_text += "\n\n点击开始连线"
        self.setToolTip(tooltip_text)
        
        # 设置可选择和可点击
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        print(f"InterfaceGraphicsItem 鼠标按下: {event.button()}")
        # 阻止事件传播，防止触发模块的鼠标事件
        event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件 - 防止崩溃"""
        print("InterfaceGraphicsItem 鼠标双击")
        event.accept()  # 阻止事件传播
    
    def hoverEnterEvent(self, event):
        """鼠标悬停进入事件"""
        self.setPen(QPen(QColor(255, 0, 0), 2))  # 高亮显示
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """鼠标悬停离开事件"""
        self.setPen(QPen(QColor(0, 0, 0), 1))  # 恢复正常
        super().hoverLeaveEvent(event)


class ModuleGraphicsItem(QGraphicsRectItem):
    """模块图形项"""
    
    def __init__(self, module, parent=None):
        super().__init__(parent)
        self.module = module
        self.interface_items = []  # 接口图形项列表
        
        self.setRect(0, 0, module.size.x, module.size.y)
        self.setPos(module.position.x, module.position.y)
        
        # 设置外观
        self.setPen(QPen(QColor(0, 0, 0), 2))
        if module.module_type.value == "hardware":
            self.setBrush(QBrush(QColor(200, 220, 255)))  # 硬件模块为浅蓝色
        elif module.module_type.value == "software":
            self.setBrush(QBrush(QColor(255, 220, 200)))  # 软件模块为浅橙色
        else:  # algorithm
            self.setBrush(QBrush(QColor(220, 255, 220)))  # 算法模块为浅绿色
        
        # 设置可移动和可选择
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # 添加文本标签
        self.text_item = QGraphicsTextItem(module.name, self)
        self.text_item.setPos(5, 5)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.text_item.setFont(font)
        
        # 创建接口图形项
        self.create_interface_items()
        
        # Tooltip内容
        tooltip_text = f"模块: {module.name}\n类型: {module.module_type.value}\n描述: {module.description}"
        if hasattr(module, 'connection_points') and module.connection_points:
            tooltip_text += f"\n接口数量: {len(module.connection_points)}"
        self.setToolTip(tooltip_text)
    
    def update_position(self):
        """更新模块位置后刷新接口位置"""
        # 更新模块位置
        self.module.position.x = self.pos().x()
        self.module.position.y = self.pos().y()
        
        # 刷新所有连接的连线
        if hasattr(self, 'scene') and self.scene():
            for item in self.scene().items():
                if isinstance(item, ConnectionGraphicsItem):
                    if (item.connection.source_module_id == self.module.id or 
                        item.connection.target_module_id == self.module.id):
                        item.update_path()
    
    def create_interface_items(self):
        """创建接口图形项"""
        if not hasattr(self.module, 'connection_points'):
            return
        
        rect = self.rect()
        interface_count = len(self.module.connection_points)
        
        if interface_count == 0:
            return
        
        # 清除现有接口项
        for item in self.interface_items:
            if item.scene():
                item.scene().removeItem(item)
        self.interface_items.clear()
        
        # 计算接口位置
        for i, cp in enumerate(self.module.connection_points):
            interface_item = InterfaceGraphicsItem(cp, self)
            
            # 根据接口类型确定位置和颜色
            if cp.connection_type == "input":
                # 输入接口在左侧
                x = -8
                y = rect.height() * (i + 1) / (interface_count + 1) - 4
                color = QColor(0, 255, 0)  # 绿色
            elif cp.connection_type == "output":
                # 输出接口在右侧
                x = rect.width()
                y = rect.height() * (i + 1) / (interface_count + 1) - 4
                color = QColor(255, 255, 0)  # 黄色
            else:  # bidirectional
                # 双向接口在顶部或底部
                x = rect.width() * (i + 1) / (interface_count + 1) - 4
                y = -8 if i % 2 == 0 else rect.height()
                color = QColor(255, 192, 203)  # 粉色
            
            interface_item.setPos(x, y)
            interface_item.setBrush(QBrush(color))
            self.interface_items.append(interface_item)
    
    def update_interfaces(self):
        """更新接口显示"""
        self.create_interface_items()
    
    def get_interface_position(self, interface_id):
        """获取指定接口的全局位置"""
        for item in self.interface_items:
            if item.connection_point.id == interface_id:
                return self.mapToScene(item.pos() + QPointF(4, 4))  # 接口中心点
        return None
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.RightButton:
            # 右键打开配置对话框
            try:
                print(f"模块右键点击: {self.module.name}")
                # 创建简单的配置对话框，避免访问不存在的属性
                dialog = QDialog(self.scene().views()[0])
                dialog.setWindowTitle(f"配置模块: {self.module.name}")
                dialog.resize(400, 300)
                
                layout = QVBoxLayout()
                
                # 基本信息
                form_layout = QFormLayout()
                name_edit = QLineEdit(self.module.name)
                description_edit = QTextEdit()
                description_edit.setPlainText(self.module.description)
                description_edit.setMaximumHeight(100)
                
                form_layout.addRow("名称:", name_edit)
                form_layout.addRow("描述:", description_edit)
                
                # 按钮
                button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                button_box.accepted.connect(dialog.accept)
                button_box.rejected.connect(dialog.reject)
                
                layout.addLayout(form_layout)
                layout.addWidget(button_box)
                dialog.setLayout(layout)
                
                if dialog.exec_() == QDialog.Accepted:
                    self.module.name = name_edit.text()
                    self.module.description = description_edit.toPlainText()
                    
                    # 更新显示
                    self.text_item.setPlainText(self.module.name)
                    tooltip_text = f"模块: {self.module.name}\n类型: {self.module.module_type.value}\n描述: {self.module.description}"
                    self.setToolTip(tooltip_text)
                    
                    # 标记项目已修改
                    if hasattr(self.scene().views()[0], 'project_manager'):
                        self.scene().views()[0].project_manager.mark_modified()
                        
            except Exception as e:
                print(f"处理模块右键事件时出错: {e}")
                QMessageBox.warning(None, "错误", f"处理模块右键事件时出错: {str(e)}")
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        super().mouseMoveEvent(event)
        self.update_position()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        super().mouseReleaseEvent(event)
        self.update_position()
    
    def hoverEnterEvent(self, event):
        """鼠标悬停进入"""
        self.setBrush(QBrush(QColor(220, 240, 255)))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """鼠标悬停离开"""
        self.setBrush(QBrush(QColor(200, 220, 255)))
        super().hoverLeaveEvent(event)


class ConnectionGraphicsItem(QGraphicsPathItem):
    """连接图形项"""
    
    def __init__(self, connection, system_canvas):
        super().__init__()
        self.connection = connection
        self.system_canvas = system_canvas
        self.control_points = []  # 贝塞尔曲线控制点
        
        # 设置外观
        self.setPen(QPen(QColor(0, 100, 200), 2))
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # 更新路径
        self.update_path()
    
    def update_path(self):
        """更新连线路径"""
        source_item = self.system_canvas.graphics_items.get(self.connection.source_module_id)
        target_item = self.system_canvas.graphics_items.get(self.connection.target_module_id)
        
        if not source_item or not target_item:
            return
        
        # 获取接口位置
        source_pos = source_item.get_interface_position(self.connection.source_point_id)
        target_pos = target_item.get_interface_position(self.connection.target_point_id)
        
        if not source_pos or not target_pos:
            return
        
        # 创建贝塞尔曲线路径
        path = QPainterPath()
        path.moveTo(source_pos)
        
        # 计算控制点，使连线更平滑
        dx = target_pos.x() - source_pos.x()
        dy = target_pos.y() - source_pos.y()
        
        # 使用两个控制点创建三次贝塞尔曲线
        control1 = QPointF(source_pos.x() + dx * 0.3, source_pos.y())
        control2 = QPointF(target_pos.x() - dx * 0.3, target_pos.y())
        
        path.cubicTo(control1, control2, target_pos)
        
        self.setPath(path)
    
    def hoverEnterEvent(self, event):
        """鼠标悬停进入事件"""
        self.setPen(QPen(QColor(255, 0, 0), 3))  # 高亮显示
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """鼠标悬停离开事件"""
        self.setPen(QPen(QColor(0, 100, 200), 2))  # 恢复正常
        super().hoverLeaveEvent(event)


class SystemCanvas(QWidget):
    """系统画布组件"""
    
    # 信号定义
    module_selected = pyqtSignal(str)  # 模块被选中
    module_moved = pyqtSignal(str, float, float)  # 模块被移动
    connection_created = pyqtSignal(object)  # 连接被创建
    
    def __init__(self):
        super().__init__()
        self.current_system = None
        self.graphics_items = {}  # 模块图形项字典
        self.connection_items = {}  # 连接图形项字典
        self.project_manager = None  # 项目管理器引用
        self.connecting_mode = False  # 是否处于连线模式
        self.temp_line = None  # 临时连线
        self.start_interface = None  # 开始连线的接口
        self.start_interface_id = None  # 开始连线的接口ID
        
        self.init_ui()
        self.init_scene()
    
    def init_ui(self):
        """初始化用户界面"""
        # 主布局
        main_layout = QHBoxLayout()
        
        # 左侧模块库面板
        module_panel = self.create_module_panel()
        main_layout.addWidget(module_panel, 0)
        
        # 右侧画布区域
        canvas_layout = QVBoxLayout()
        
        # 工具栏
        toolbar = self.create_toolbar()
        canvas_layout.addWidget(toolbar)
        
        # 图形视图
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        
        # 设置视图属性
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        
        canvas_layout.addWidget(self.graphics_view)
        
        canvas_widget = QWidget()
        canvas_widget.setLayout(canvas_layout)
        main_layout.addWidget(canvas_widget, 1)
        
        self.setLayout(main_layout)
    
    def create_module_panel(self):
        """创建模块库面板"""
        panel = QGroupBox("模块库")
        panel.setMaximumWidth(250)
        layout = QVBoxLayout()
        
        # 模块列表
        self.module_library_list = QListWidget()
        self.module_library_list.setDragDropMode(QListWidget.DragOnly)
        layout.addWidget(QLabel("已创建的模块:"))
        layout.addWidget(self.module_library_list)
        
        # 添加模块按钮
        add_button = QPushButton("添加到画布")
        add_button.clicked.connect(self.add_selected_module)
        layout.addWidget(add_button)
        
        # 刷新按钮
        refresh_button = QPushButton("刷新模块")
        refresh_button.clicked.connect(self.refresh_module_library)
        layout.addWidget(refresh_button)
        
        panel.setLayout(layout)
        return panel
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        
        # 选择工具
        self.select_action = QAction("选择", self)
        self.select_action.setCheckable(True)
        self.select_action.setChecked(True)
        self.select_action.triggered.connect(self.activate_selection_mode)
        toolbar.addAction(self.select_action)
        
        # 连线工具
        self.connect_action = QAction("连线", self)
        self.connect_action.setCheckable(True)
        self.connect_action.triggered.connect(self.activate_connection_mode)
        toolbar.addAction(self.connect_action)
        
        # 工具按钮组（使用QActionGroup管理互斥的QAction）
        self.tool_group = QActionGroup(self)
        self.tool_group.addAction(self.select_action)
        self.tool_group.addAction(self.connect_action)
        self.tool_group.setExclusive(True)
        
        toolbar.addSeparator()
        
        # 缩放工具
        zoom_in_action = QAction("放大", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        zoom_fit_action = QAction("适应窗口", self)
        zoom_fit_action.triggered.connect(self.zoom_fit)
        toolbar.addAction(zoom_fit_action)
        
        toolbar.addSeparator()
        
        # 网格显示
        grid_action = QAction("显示网格", self)
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        grid_action.triggered.connect(self.toggle_grid)
        toolbar.addAction(grid_action)
        
        return toolbar
    
    def activate_selection_mode(self):
        """激活选择模式"""
        self.connecting_mode = False
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        # 清除临时连线
        if self.temp_line:
            self.graphics_scene.removeItem(self.temp_line)
            self.temp_line = None
    
    def activate_connection_mode(self):
        """激活连线模式"""
        self.connecting_mode = True
        self.graphics_view.setDragMode(QGraphicsView.NoDrag)
        # 清除临时连线
        if self.temp_line:
            self.graphics_scene.removeItem(self.temp_line)
            self.temp_line = None
    
    def scene_mouse_press_event(self, event):
        """场景鼠标按下事件"""
        try:
            if self.connecting_mode:
                # 在连线模式下，检查是否点击了接口
                item = self.graphics_scene.itemAt(event.scenePos(), self.graphics_view.transform())
                print(f"鼠标按下，点击的项: {item}, 类型: {type(item)}")
                if isinstance(item, InterfaceGraphicsItem):
                    # 开始连线
                    print(f"开始连线，接口ID: {item.connection_point.id}")
                    self.start_connection(item, event.scenePos())
                    event.accept()
                    return
            # 默认处理
            QGraphicsScene.mousePressEvent(self.graphics_scene, event)
        except Exception as e:
            print(f"场景鼠标按下事件出错: {e}")
            # 防止崩溃，继续默认处理
            QGraphicsScene.mousePressEvent(self.graphics_scene, event)
    
    def scene_mouse_move_event(self, event):
        """场景鼠标移动事件"""
        if self.connecting_mode and self.temp_line and self.start_interface:
            # 更新临时连线的终点
            end_pos = event.scenePos()
            self.update_temp_line(end_pos)
            event.accept()
        else:
            QGraphicsScene.mouseMoveEvent(self.graphics_scene, event)
    
    def scene_mouse_release_event(self, event):
        """场景鼠标释放事件"""
        if self.connecting_mode and self.temp_line and self.start_interface:
            # 使用 items() 方法获取所有在鼠标位置下的项，排除临时连线
            items = self.graphics_scene.items(event.scenePos())
            target_interface = None
            
            # 查找目标接口
            for item in items:
                # 跳过临时连线项
                if item == self.temp_line:
                    continue
                # 跳过开始连线的接口
                if item == self.start_interface:
                    continue
                # 检查是否是接口项
                if isinstance(item, InterfaceGraphicsItem):
                    target_interface = item
                    break
            
            print(f"鼠标释放，找到的目标接口: {target_interface}")
            
            if target_interface:
                # 完成连线
                print(f"完成连线，从 {self.start_interface_id} 到 {target_interface.connection_point.id}")
                self.finish_connection(target_interface, event.scenePos())
                event.accept()
            else:
                # 取消连线
                print("取消连线，未找到目标接口")
                self.cancel_connection()
                event.accept()
        else:
            QGraphicsScene.mouseReleaseEvent(self.graphics_scene, event)
    
    def start_connection(self, interface_item, scene_pos):
        """开始连线"""
        try:
            self.start_interface = interface_item
            self.start_interface_id = interface_item.connection_point.id
            
            # 创建临时连线
            self.temp_line = QGraphicsLineItem()
            self.temp_line.setPen(QPen(QColor(0, 100, 200), 2, Qt.DashLine))
            # 设置临时连线为不可选择，减少干扰
            self.temp_line.setFlag(QGraphicsItem.ItemIsSelectable, False)
            start_pos = interface_item.scenePos() + QPointF(6, 6)  # 接口中心点
            self.temp_line.setLine(start_pos.x(), start_pos.y(), scene_pos.x(), scene_pos.y())
            self.graphics_scene.addItem(self.temp_line)
        except Exception as e:
            print(f"开始连线时出错: {e}")
            self.cancel_connection()
    
    def update_temp_line(self, end_pos):
        """更新临时连线"""
        if self.temp_line and self.start_interface:
            start_pos = self.start_interface.scenePos() + QPointF(6, 6)  # 接口中心点
            self.temp_line.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
    
    def finish_connection(self, end_interface, end_pos):
        """完成连线"""
        try:
            if not self.current_system or not self.project_manager:
                print("错误：没有当前系统或项目管理器")
                self.cancel_connection()
                return
            
            # 暂时跳过接口兼容性检查
            print("跳过接口兼容性检查，直接建立连接")
            
            # 创建连接
            try:
                from ..models.system_model import Connection
            except ImportError:
                from src.models.system_model import Connection
            
            # 生成连接ID
            connection_id = f"connection_{len(self.current_system.connections) + 1}"
            
            # 获取模块ID
            start_module_item = self.start_interface.parentItem()
            end_module_item = end_interface.parentItem()
            
            if not start_module_item or not end_module_item:
                QMessageBox.warning(self.graphics_view, "连线失败", "无法找到模块")
                self.cancel_connection()
                return
                
            start_module_id = start_module_item.module.id
            end_module_id = end_module_item.module.id
            
            # 创建连接对象
            connection = Connection(
                id=connection_id,
                source_module_id=start_module_id,
                target_module_id=end_module_id,
                source_point_id=self.start_interface_id,
                target_point_id=end_interface.connection_point.id
            )
            
            # 添加到系统
            self.current_system.connections[connection_id] = connection
            
            # 绘制连接线
            self.draw_connection(connection)
            
            # 标记项目已修改
            if self.project_manager:
                self.project_manager.mark_modified()
            
            # 清除临时状态
            self.cleanup_connection()
            
            QMessageBox.information(self.graphics_view, "连线成功", "模块连接已创建")
        except Exception as e:
            print(f"完成连线时出错: {e}")
            QMessageBox.warning(self.graphics_view, "连线失败", f"连线过程中出错: {str(e)}")
            self.cancel_connection()
    
    def cancel_connection(self):
        """取消连线"""
        if self.temp_line:
            self.graphics_scene.removeItem(self.temp_line)
            self.temp_line = None
        self.cleanup_connection()
    
    def cleanup_connection(self):
        """清理连线状态"""
        self.start_interface = None
        self.start_interface_id = None
    
    def check_interface_compatibility(self, start_interface, end_interface):
        """检查接口兼容性"""
        # 基本规则：输出接口只能连接到输入接口
        start_type = start_interface.connection_point.connection_type
        end_type = end_interface.connection_point.connection_type
        
        # 允许的连接类型：
        # 1. 输出 -> 输入
        # 2. 输入 -> 输出（双向通信）
        # 3. 双向 -> 双向
        # 4. 输出 -> 双向
        # 5. 双向 -> 输入
        if (start_type == "output" and end_type == "input") or \
           (start_type == "input" and end_type == "output") or \
           (start_type == "bidirectional" and end_type == "bidirectional") or \
           (start_type == "output" and end_type == "bidirectional") or \
           (start_type == "bidirectional" and end_type == "input"):
            return True
        else:
            return False

    def init_scene(self):
        """初始化场景"""
        # 设置场景大小
        self.graphics_scene.setSceneRect(0, 0, 2000, 1500)
        
        # 设置背景
        self.graphics_scene.setBackgroundBrush(QBrush(QColor(250, 250, 250)))
        
        # 绘制网格
        self.draw_grid()
        
        # 连接场景的鼠标事件
        self.graphics_scene.mousePressEvent = self.scene_mouse_press_event
        self.graphics_scene.mouseMoveEvent = self.scene_mouse_move_event
        self.graphics_scene.mouseReleaseEvent = self.scene_mouse_release_event
    
    def draw_grid(self):
        """绘制网格"""
        # 清除现有网格
        for item in self.graphics_scene.items():
            if hasattr(item, 'is_grid_line'):
                self.graphics_scene.removeItem(item)
        
        # 绘制网格线
        grid_size = 20
        scene_rect = self.graphics_scene.sceneRect()
        
        # 垂直线
        x = scene_rect.left()
        while x <= scene_rect.right():
            line = self.graphics_scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(),
                                             QPen(QColor(200, 200, 200), 1))
            line.is_grid_line = True
            x += grid_size
        
        # 水平线
        y = scene_rect.top()
        while y <= scene_rect.bottom():
            line = self.graphics_scene.addLine(scene_rect.left(), y, scene_rect.right(), y,
                                             QPen(QColor(200, 200, 200), 1))
            line.is_grid_line = True
            y += grid_size
    
    def set_system(self, system):
        """设置当前系统"""
        self.current_system = system
        self.update_canvas()
        self.refresh_module_library()
    
    def update_canvas(self):
        """更新画布内容"""
        if not self.current_system:
            return
        
        # 清除现有的模块图形项和连接图形项
        for item in list(self.graphics_items.values()):
            self.graphics_scene.removeItem(item)
        self.graphics_items.clear()
        
        for item in list(self.connection_items.values()):
            self.graphics_scene.removeItem(item)
        self.connection_items.clear()
        
        # 添加模块
        for module in self.current_system.modules.values():
            self.add_module_to_canvas(module)
        
        # 添加连接线
        self.update_connections()
    
    def add_module_to_canvas(self, module):
        """添加模块到画布"""
        module_item = ModuleGraphicsItem(module)
        self.graphics_scene.addItem(module_item)
        self.graphics_items[module.id] = module_item
    
    def update_connections(self):
        """更新连接线"""
        if not self.current_system:
            return
        
        # 移除现有连接线
        for item in list(self.connection_items.values()):
            self.graphics_scene.removeItem(item)
        self.connection_items.clear()
        
        # 绘制新的连接线
        for connection in self.current_system.connections.values():
            self.draw_connection(connection)
    
    def draw_connection(self, connection):
        """绘制连接线"""
        # 创建连接图形项
        connection_item = ConnectionGraphicsItem(connection, self)
        self.graphics_scene.addItem(connection_item)
        self.connection_items[connection.id] = connection_item
    
    def zoom_in(self):
        """放大"""
        self.graphics_view.scale(1.2, 1.2)
    
    def zoom_out(self):
        """缩小"""
        self.graphics_view.scale(0.8, 0.8)
    
    def zoom_fit(self):
        """适应窗口"""
        self.graphics_view.fitInView(self.graphics_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
    
    def toggle_grid(self, show_grid):
        """切换网格显示"""
        if show_grid:
            self.draw_grid()
        else:
            # 隐藏网格
            for item in self.graphics_scene.items():
                if hasattr(item, 'is_grid_line'):
                    item.setVisible(False)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        super().mousePressEvent(event)
    
    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """拖放事件"""
        # 处理从模块库拖拽过来的模块
        if event.mimeData().hasText():
            module_type = event.mimeData().text()
            pos = self.graphics_view.mapToScene(event.pos())
            self.create_module_at_position(module_type, pos)
            event.acceptProposedAction()
    
    def add_selected_module(self):
        """添加选中的模块到画布"""
        current_item = self.module_library_list.currentItem()
        if current_item:
            module_id = current_item.data(Qt.UserRole)
            if module_id and self.current_system and module_id in self.current_system.modules:
                # 获取模块定义
                module_def = self.current_system.modules[module_id]
                # 在画布中心创建模块的副本
                center_pos = QPointF(400, 300)
                self.create_module_from_definition(module_def, center_pos)
            else:
                QMessageBox.warning(self, "警告", "请先选择有效的模块")
        else:
            QMessageBox.warning(self, "警告", "请先选择要添加的模块")
    
    def create_module_from_definition(self, module_def, position):
        """根据模块定义在指定位置创建模块实例"""
        if not self.current_system or not self.project_manager:
            return
        
        # 导入模块模型
        try:
            from ..models.module_model import Module, ModuleType, Position, Size
        except ImportError:
            from src.models.module_model import Module, ModuleType, Position, Size
        
        # 创建模块的副本
        import copy
        module = copy.deepcopy(module_def)
        
        # 生成新的ID
        module_id = f"module_{len(self.current_system.modules) + 1}"
        module.id = module_id
        
        # 更新位置
        module.position.x = position.x()
        module.position.y = position.y()
        
        # 添加到系统
        self.current_system.modules[module_id] = module
        
        # 添加到画布
        self.add_module_to_canvas(module)
        
        # 标记项目已修改
        if self.project_manager:
            self.project_manager.mark_modified()
    
    def refresh_module_library(self):
        """刷新模块库显示"""
        self.module_library_list.clear()
        
        if self.current_system and self.current_system.modules:
            for module_id, module in self.current_system.modules.items():
                item = QListWidgetItem(f"{module.name} ({module.module_type.value})")
                item.setData(Qt.UserRole, module_id)
                self.module_library_list.addItem(item)
    
    def refresh_modules(self):
        """刷新模块显示"""
        # 更新现有模块的接口显示
        for module_id, module_item in self.graphics_items.items():
            if hasattr(module_item, 'update_interfaces'):
                module_item.update_interfaces()
        
        # 如果有新模块，重新构建整个画布
        if self.current_system:
            current_module_ids = set(self.graphics_items.keys())
            system_module_ids = set(self.current_system.modules.keys())
            
            if current_module_ids != system_module_ids:
                self.update_canvas()
        
        # 刷新模块库
        self.refresh_module_library()
    
    def set_project_manager(self, project_manager):
        """设置项目管理器"""
        self.project_manager = project_manager
