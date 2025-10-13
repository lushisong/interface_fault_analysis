#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
故障树分析面板
Fault Tree Analysis Panel
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QTabWidget,
                             QTableWidget, QTableWidgetItem, QGroupBox,
                             QLabel, QLineEdit, QTextEdit, QComboBox,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
                             QFormLayout, QGridLayout, QHeaderView, QMessageBox,
                             QDialog, QDialogButtonBox, QFrame, QProgressBar,
                             QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem,
                             QGraphicsLineItem)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QPoint
from PyQt5.QtGui import QIcon, QFont, QColor, QPen, QBrush, QPainter, QCursor

from ..models.fault_tree_model import FaultTree, FaultTreeEvent, FaultTreeGate, EventType, GateType
from ..core.fault_tree_generator import FaultTreeGenerator


class FaultTreeGenerationThread(QThread):
    """故障树生成线程"""
    
    progress_updated = pyqtSignal(int, str)
    generation_completed = pyqtSignal(object)
    generation_failed = pyqtSignal(str)
    
    def __init__(self, system, task_profile, config):
        super().__init__()
        self.system = system
        self.task_profile = task_profile
        self.config = config
    
    def run(self):
        """运行故障树生成"""
        try:
            self.progress_updated.emit(10, "初始化故障树生成器...")
            generator = FaultTreeGenerator()
            
            self.progress_updated.emit(30, "分析系统结构...")
            
            self.progress_updated.emit(50, "生成故障树结构...")
            fault_tree = generator.generate_fault_tree(self.system, self.task_profile, self.config)
            
            self.progress_updated.emit(70, "计算最小割集...")
            fault_tree.find_minimal_cut_sets()
            
            self.progress_updated.emit(85, "计算系统概率...")
            fault_tree.calculate_system_probability()
            
            self.progress_updated.emit(95, "计算重要度指标...")
            fault_tree.calculate_importance_measures()
            
            self.progress_updated.emit(100, "故障树生成完成")
            self.generation_completed.emit(fault_tree)
            
        except Exception as e:
            self.generation_failed.emit(str(e))


class FaultTreeGraphicsView(QGraphicsView):
    """故障树图形视图"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.fault_tree = None
        
        # 设置视图属性
        self.setDragMode(QGraphicsView.NoDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        # 交互状态
        self._is_panning = False
        self._pan_start = QPoint()

    def set_fault_tree(self, fault_tree: FaultTree):
        """设置故障树"""
        self.fault_tree = fault_tree
        self.draw_fault_tree()
    
    def draw_fault_tree(self):
        """绘制故障树"""
        if not self.fault_tree:
            return
        
        self.scene.clear()
        
        # 绘制事件
        for event in self.fault_tree.events.values():
            self._draw_event(event)
        
        # 绘制逻辑门
        for gate in self.fault_tree.gates.values():
            self._draw_gate(gate)
        
        # 绘制连线
        self._draw_connections()

        # 调整视图
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.resetTransform()
        if not self.scene.sceneRect().isNull():
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        """滚轮缩放"""
        if not self.scene.items():
            return

        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            factor = zoom_in_factor
        else:
            factor = zoom_out_factor

        self.scale(factor, factor)
        event.accept()

    def mousePressEvent(self, event):
        """启用中键平移"""
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._pan_start = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """处理中键拖拽平移"""
        if self._is_panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """结束平移"""
        if event.button() == Qt.MiddleButton and self._is_panning:
            self._is_panning = False
            self.setCursor(QCursor(Qt.ArrowCursor))
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def zoom_in(self):
        """放大视图"""
        self.scale(1.15, 1.15)

    def zoom_out(self):
        """缩小视图"""
        self.scale(1 / 1.15, 1 / 1.15)

    def reset_view(self):
        """重置视图到适应屏幕"""
        if not self.scene.items():
            return
        self.resetTransform()
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def _draw_event(self, event: FaultTreeEvent):
        """绘制事件"""
        x = event.position['x']
        y = event.position['y']
        width = event.size['width']
        height = event.size['height']
        
        # 根据事件类型选择形状和颜色
        if event.event_type == EventType.TOP_EVENT:
            # 顶事件 - 矩形，红色
            rect = QGraphicsRectItem(x, y, width, height)
            rect.setBrush(QBrush(QColor(255, 200, 200)))
            rect.setPen(QPen(QColor(255, 0, 0), 2))
        elif event.event_type == EventType.INTERMEDIATE_EVENT:
            # 中间事件 - 矩形，黄色
            rect = QGraphicsRectItem(x, y, width, height)
            rect.setBrush(QBrush(QColor(255, 255, 200)))
            rect.setPen(QPen(QColor(200, 200, 0), 2))
        elif event.event_type == EventType.BASIC_EVENT:
            # 基本事件 - 圆形，绿色
            rect = QGraphicsEllipseItem(x, y, width, height)
            rect.setBrush(QBrush(QColor(200, 255, 200)))
            rect.setPen(QPen(QColor(0, 150, 0), 2))
        else:
            # 其他事件 - 矩形，灰色
            rect = QGraphicsRectItem(x, y, width, height)
            rect.setBrush(QBrush(QColor(220, 220, 220)))
            rect.setPen(QPen(QColor(100, 100, 100), 2))
        
        self.scene.addItem(rect)
        
        # 添加文本
        text = QGraphicsTextItem(event.name)
        text.setPos(x + 5, y + 5)
        text.setTextWidth(width - 10)
        font = text.font()
        font.setPointSize(8)
        text.setFont(font)
        self.scene.addItem(text)
        
        # 添加概率信息
        if event.probability > 0:
            prob_text = QGraphicsTextItem(f"P={event.probability:.2e}")
            prob_text.setPos(x + 5, y + height - 20)
            font = prob_text.font()
            font.setPointSize(6)
            prob_text.setFont(font)
            prob_text.setDefaultTextColor(QColor(100, 100, 100))
            self.scene.addItem(prob_text)
    
    def _draw_gate(self, gate: FaultTreeGate):
        """绘制逻辑门"""
        x = gate.position['x']
        y = gate.position['y']
        width = gate.size['width']
        height = gate.size['height']
        
        # 根据门类型选择形状
        if gate.gate_type == GateType.AND:
            # 与门 - 弧形顶部
            rect = QGraphicsRectItem(x, y + height//2, width, height//2)
            rect.setBrush(QBrush(QColor(200, 200, 255)))
            rect.setPen(QPen(QColor(0, 0, 200), 2))
            self.scene.addItem(rect)
            
            # 弧形顶部
            arc = QGraphicsEllipseItem(x, y, width, height)
            arc.setBrush(QBrush(QColor(200, 200, 255)))
            arc.setPen(QPen(QColor(0, 0, 200), 2))
            arc.setStartAngle(0)
            arc.setSpanAngle(180 * 16)  # 180度
            self.scene.addItem(arc)
            
            # 文本
            text = QGraphicsTextItem("&")
            text.setPos(x + width//2 - 5, y + height//2 - 10)
            font = text.font()
            font.setPointSize(12)
            font.setBold(True)
            text.setFont(font)
            self.scene.addItem(text)
        
        elif gate.gate_type == GateType.OR:
            # 或门 - 尖顶
            rect = QGraphicsRectItem(x, y + height//2, width, height//2)
            rect.setBrush(QBrush(QColor(255, 200, 255)))
            rect.setPen(QPen(QColor(200, 0, 200), 2))
            self.scene.addItem(rect)
            
            # 尖顶（简化为三角形）
            # 这里简化处理，实际应该绘制曲线
            
            # 文本
            text = QGraphicsTextItem("≥1")
            text.setPos(x + width//2 - 8, y + height//2 - 10)
            font = text.font()
            font.setPointSize(10)
            font.setBold(True)
            text.setFont(font)
            self.scene.addItem(text)
        
        else:
            # 其他门类型 - 简单矩形
            rect = QGraphicsRectItem(x, y, width, height)
            rect.setBrush(QBrush(QColor(240, 240, 240)))
            rect.setPen(QPen(QColor(100, 100, 100), 2))
            self.scene.addItem(rect)
            
            # 文本
            text = QGraphicsTextItem(gate.gate_type.value.upper())
            text.setPos(x + 5, y + height//2 - 10)
            font = text.font()
            font.setPointSize(8)
            text.setFont(font)
            self.scene.addItem(text)
    
    def _draw_connections(self):
        """绘制连线"""
        if not self.fault_tree:
            return
        
        for gate in self.fault_tree.gates.values():
            # 从逻辑门到输出事件的连线
            if gate.output_event_id in self.fault_tree.events:
                output_event = self.fault_tree.events[gate.output_event_id]
                
                # 连线起点（逻辑门底部中心）
                start_x = gate.position['x'] + gate.size['width'] // 2
                start_y = gate.position['y'] + gate.size['height']
                
                # 连线终点（事件顶部中心）
                end_x = output_event.position['x'] + output_event.size['width'] // 2
                end_y = output_event.position['y']
                
                line = QGraphicsLineItem(start_x, start_y, end_x, end_y)
                line.setPen(QPen(QColor(0, 0, 0), 2))
                self.scene.addItem(line)
            
            # 从输入事件到逻辑门的连线
            for input_event_id in gate.input_events:
                if input_event_id in self.fault_tree.events:
                    input_event = self.fault_tree.events[input_event_id]
                    
                    # 连线起点（事件底部中心）
                    start_x = input_event.position['x'] + input_event.size['width'] // 2
                    start_y = input_event.position['y'] + input_event.size['height']
                    
                    # 连线终点（逻辑门顶部中心）
                    end_x = gate.position['x'] + gate.size['width'] // 2
                    end_y = gate.position['y']
                    
                    line = QGraphicsLineItem(start_x, start_y, end_x, end_y)
                    line.setPen(QPen(QColor(0, 0, 0), 2))
                    self.scene.addItem(line)


class FaultTreePanel(QWidget):
    """故障树分析面板"""
    
    fault_tree_generated = pyqtSignal(object)  # 故障树生成信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_fault_tree = None
        self.project_manager = None
        self.generation_thread = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成故障树")
        self.generate_btn.clicked.connect(self.generate_fault_tree)
        
        self.analyze_btn = QPushButton("分析故障树")
        self.analyze_btn.clicked.connect(self.analyze_fault_tree)
        self.analyze_btn.setEnabled(False)
        
        self.export_btn = QPushButton("导出结果")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        
        toolbar_layout.addWidget(self.generate_btn)
        toolbar_layout.addWidget(self.analyze_btn)
        toolbar_layout.addWidget(self.export_btn)
        toolbar_layout.addStretch()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addLayout(toolbar_layout)
        layout.addLayout(progress_layout)
        
        # 主内容区域
        self.content_widget = self.create_content_widget()
        layout.addWidget(self.content_widget)
    
    def create_content_widget(self):
        """创建内容组件"""
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：故障树图形视图
        left_widget = self.create_tree_view()
        
        # 右侧：分析结果
        right_widget = self.create_analysis_results()
        right_widget.setMaximumWidth(400)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([800, 400])
        
        return splitter
    
    def create_tree_view(self):
        """创建故障树视图"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 标题
        title_label = QLabel("故障树结构")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)

        # 故障树图形视图
        self.tree_view = FaultTreeGraphicsView()

        # 视图控制按钮
        controls_layout = QHBoxLayout()
        self.zoom_in_btn = QPushButton("放大")
        self.zoom_out_btn = QPushButton("缩小")
        self.reset_view_btn = QPushButton("适应屏幕")

        self.zoom_in_btn.clicked.connect(self.tree_view.zoom_in)
        self.zoom_out_btn.clicked.connect(self.tree_view.zoom_out)
        self.reset_view_btn.clicked.connect(self.tree_view.reset_view)

        controls_layout.addWidget(self.zoom_in_btn)
        controls_layout.addWidget(self.zoom_out_btn)
        controls_layout.addWidget(self.reset_view_btn)

        hint_label = QLabel("提示: 滚轮缩放，按住中键拖动可平移")
        hint_label.setStyleSheet("color: #666666; font-size: 11px;")
        controls_layout.addStretch()
        controls_layout.addWidget(hint_label)

        layout.addLayout(controls_layout)

        layout.addWidget(self.tree_view)

        return widget
    
    def create_analysis_results(self):
        """创建分析结果组件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题
        title_label = QLabel("分析结果")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # 标签页
        tab_widget = QTabWidget()
        
        # 基本信息标签页
        basic_tab = self.create_basic_info_tab()
        tab_widget.addTab(basic_tab, "基本信息")
        
        # 最小割集标签页
        cut_sets_tab = self.create_cut_sets_tab()
        tab_widget.addTab(cut_sets_tab, "最小割集")
        
        # 重要度分析标签页
        importance_tab = self.create_importance_tab()
        tab_widget.addTab(importance_tab, "重要度分析")
        
        # 定量分析标签页
        quantitative_tab = self.create_quantitative_tab()
        tab_widget.addTab(quantitative_tab, "定量分析")
        
        layout.addWidget(tab_widget)
        
        return widget
    
    def create_basic_info_tab(self):
        """创建基本信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 故障树信息
        info_group = QGroupBox("故障树信息")
        info_layout = QFormLayout(info_group)
        
        self.tree_name_label = QLabel("-")
        self.tree_description_label = QLabel("-")
        self.event_count_label = QLabel("-")
        self.gate_count_label = QLabel("-")
        self.basic_event_count_label = QLabel("-")
        
        info_layout.addRow("名称:", self.tree_name_label)
        info_layout.addRow("描述:", self.tree_description_label)
        info_layout.addRow("事件总数:", self.event_count_label)
        info_layout.addRow("逻辑门数:", self.gate_count_label)
        info_layout.addRow("基本事件数:", self.basic_event_count_label)
        
        # 任务信息
        task_group = QGroupBox("任务信息")
        task_layout = QFormLayout(task_group)
        
        self.mission_time_label = QLabel("-")
        self.task_profile_label = QLabel("-")
        
        task_layout.addRow("任务时间:", self.mission_time_label)
        task_layout.addRow("任务剖面:", self.task_profile_label)
        
        layout.addWidget(info_group)
        layout.addWidget(task_group)
        layout.addStretch()
        
        return widget
    
    def create_cut_sets_tab(self):
        """创建最小割集标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 割集统计
        stats_group = QGroupBox("割集统计")
        stats_layout = QFormLayout(stats_group)
        
        self.cut_set_count_label = QLabel("-")
        self.min_order_label = QLabel("-")
        self.max_order_label = QLabel("-")
        
        stats_layout.addRow("割集总数:", self.cut_set_count_label)
        stats_layout.addRow("最小阶数:", self.min_order_label)
        stats_layout.addRow("最大阶数:", self.max_order_label)
        
        # 割集列表
        self.cut_sets_table = QTableWidget()
        self.cut_sets_table.setColumnCount(4)
        self.cut_sets_table.setHorizontalHeaderLabels([
            "序号", "阶数", "事件", "概率"
        ])
        
        header = self.cut_sets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(stats_group)
        layout.addWidget(QLabel("最小割集列表:"))
        layout.addWidget(self.cut_sets_table)
        
        return widget
    
    def create_importance_tab(self):
        """创建重要度分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 重要度表格
        self.importance_table = QTableWidget()
        self.importance_table.setColumnCount(4)
        self.importance_table.setHorizontalHeaderLabels([
            "事件", "结构重要度", "概率重要度", "关键重要度"
        ])
        
        header = self.importance_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(QLabel("重要度指标:"))
        layout.addWidget(self.importance_table)
        
        return widget
    
    def create_quantitative_tab(self):
        """创建定量分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 系统可靠性指标
        reliability_group = QGroupBox("系统可靠性指标")
        reliability_layout = QFormLayout(reliability_group)
        
        self.system_probability_label = QLabel("-")
        self.system_reliability_label = QLabel("-")
        self.mtbf_label = QLabel("-")
        
        reliability_layout.addRow("系统失效概率:", self.system_probability_label)
        reliability_layout.addRow("系统可靠度:", self.system_reliability_label)
        reliability_layout.addRow("平均故障间隔时间:", self.mtbf_label)
        
        layout.addWidget(reliability_group)
        layout.addStretch()
        
        return widget
    
    def set_project_manager(self, project_manager):
        """设置项目管理器"""
        self.project_manager = project_manager
    
    def generate_fault_tree(self):
        """生成故障树"""
        if not self.project_manager or not self.project_manager.current_system:
            QMessageBox.warning(self, "警告", "请先创建或打开一个系统")
            return
        
        # 检查是否有任务剖面
        system = self.project_manager.current_system
        if not hasattr(system, 'task_profiles') or not system.task_profiles:
            QMessageBox.warning(self, "警告", "请先创建任务剖面")
            return
        
        # 选择任务剖面
        from PyQt5.QtWidgets import QInputDialog
        
        task_profiles = list(system.task_profiles.values())
        profile_names = [profile.name for profile in task_profiles]
        
        profile_name, ok = QInputDialog.getItem(
            self, "选择任务剖面", "请选择要分析的任务剖面:", profile_names, 0, False
        )
        
        if not ok or not profile_name:
            return
        
        # 找到选中的任务剖面
        selected_profile = None
        for profile in task_profiles:
            if profile.name == profile_name:
                selected_profile = profile
                break
        
        if not selected_profile:
            return
        
        # 生成配置
        config = {
            'include_interface_failures': True,
            'include_module_failures': True,
            'include_environment_effects': True,
            'max_depth': 5,
            'min_probability_threshold': 1e-6
        }
        
        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("准备生成故障树...")
        
        # 启动生成线程
        self.generation_thread = FaultTreeGenerationThread(system, selected_profile, config)
        self.generation_thread.progress_updated.connect(self.on_generation_progress)
        self.generation_thread.generation_completed.connect(self.on_generation_completed)
        self.generation_thread.generation_failed.connect(self.on_generation_failed)
        self.generation_thread.start()
        
        # 禁用生成按钮
        self.generate_btn.setEnabled(False)
    
    def on_generation_progress(self, progress, message):
        """生成进度更新"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
    
    def on_generation_completed(self, fault_tree):
        """生成完成"""
        self.current_fault_tree = fault_tree
        
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # 启用按钮
        self.generate_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        # 显示故障树
        self.tree_view.set_fault_tree(fault_tree)
        
        # 更新分析结果
        self.update_analysis_results()
        
        # 发送信号
        self.fault_tree_generated.emit(fault_tree)
        
        QMessageBox.information(self, "生成完成", "故障树生成完成")
    
    def on_generation_failed(self, error_message):
        """生成失败"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # 启用按钮
        self.generate_btn.setEnabled(True)
        
        QMessageBox.critical(self, "生成失败", f"故障树生成失败:\n{error_message}")
    
    def analyze_fault_tree(self):
        """分析故障树"""
        if not self.current_fault_tree:
            return
        
        try:
            # 重新计算分析结果
            self.current_fault_tree.find_minimal_cut_sets()
            self.current_fault_tree.calculate_system_probability()
            self.current_fault_tree.calculate_importance_measures()
            
            # 更新显示
            self.update_analysis_results()
            
            QMessageBox.information(self, "分析完成", "故障树分析完成")
            
        except Exception as e:
            QMessageBox.critical(self, "分析失败", f"故障树分析失败:\n{str(e)}")
    
    def update_analysis_results(self):
        """更新分析结果显示"""
        if not self.current_fault_tree:
            return
        
        # 更新基本信息
        self.tree_name_label.setText(self.current_fault_tree.name)
        self.tree_description_label.setText(self.current_fault_tree.description or "-")
        self.event_count_label.setText(str(len(self.current_fault_tree.events)))
        self.gate_count_label.setText(str(len(self.current_fault_tree.gates)))
        
        basic_events = self.current_fault_tree.get_basic_events()
        self.basic_event_count_label.setText(str(len(basic_events)))
        
        self.mission_time_label.setText(f"{self.current_fault_tree.mission_time:.1f} 小时")
        
        # 更新最小割集
        cut_sets = self.current_fault_tree.minimal_cut_sets
        self.cut_set_count_label.setText(str(len(cut_sets)))
        
        if cut_sets:
            orders = [cs.order for cs in cut_sets]
            self.min_order_label.setText(str(min(orders)))
            self.max_order_label.setText(str(max(orders)))
            
            # 更新割集表格
            self.cut_sets_table.setRowCount(len(cut_sets))
            for row, cut_set in enumerate(cut_sets):
                self.cut_sets_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                self.cut_sets_table.setItem(row, 1, QTableWidgetItem(str(cut_set.order)))
                
                # 事件名称
                event_names = []
                for event_id in cut_set.events:
                    if event_id in self.current_fault_tree.events:
                        event_names.append(self.current_fault_tree.events[event_id].name)
                
                self.cut_sets_table.setItem(row, 2, QTableWidgetItem(", ".join(event_names)))
                self.cut_sets_table.setItem(row, 3, QTableWidgetItem(f"{cut_set.probability:.2e}"))
        
        # 更新重要度分析
        self.importance_table.setRowCount(len(basic_events))
        for row, event in enumerate(basic_events):
            self.importance_table.setItem(row, 0, QTableWidgetItem(event.name))
            
            measures = event.importance_measures
            struct_imp = measures.get('structure_importance', 0.0)
            prob_imp = measures.get('probability_importance', 0.0)
            crit_imp = measures.get('critical_importance', 0.0)
            
            self.importance_table.setItem(row, 1, QTableWidgetItem(f"{struct_imp:.3f}"))
            self.importance_table.setItem(row, 2, QTableWidgetItem(f"{prob_imp:.2e}"))
            self.importance_table.setItem(row, 3, QTableWidgetItem(f"{crit_imp:.3f}"))
        
        # 更新定量分析
        sys_prob = self.current_fault_tree.system_probability
        sys_rel = 1.0 - sys_prob
        
        self.system_probability_label.setText(f"{sys_prob:.2e}")
        self.system_reliability_label.setText(f"{sys_rel:.6f}")
        
        if sys_prob > 0:
            mtbf = self.current_fault_tree.mission_time / sys_prob
            self.mtbf_label.setText(f"{mtbf:.1f} 小时")
        else:
            self.mtbf_label.setText("∞")
    
    def export_results(self):
        """导出结果"""
        if not self.current_fault_tree:
            return
        
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出故障树分析结果", 
            f"{self.current_fault_tree.name}_分析结果.txt",
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if file_path:
            try:
                self._export_to_file(file_path)
                QMessageBox.information(self, "导出成功", f"分析结果已导出到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出失败:\n{str(e)}")
    
    def _export_to_file(self, file_path):
        """导出到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("故障树分析结果报告\n")
            f.write("=" * 50 + "\n\n")
            
            # 基本信息
            f.write("1. 基本信息\n")
            f.write(f"故障树名称: {self.current_fault_tree.name}\n")
            f.write(f"描述: {self.current_fault_tree.description}\n")
            f.write(f"事件总数: {len(self.current_fault_tree.events)}\n")
            f.write(f"逻辑门数: {len(self.current_fault_tree.gates)}\n")
            f.write(f"基本事件数: {len(self.current_fault_tree.get_basic_events())}\n")
            f.write(f"任务时间: {self.current_fault_tree.mission_time:.1f} 小时\n\n")
            
            # 定量分析结果
            f.write("2. 定量分析结果\n")
            f.write(f"系统失效概率: {self.current_fault_tree.system_probability:.2e}\n")
            f.write(f"系统可靠度: {1.0 - self.current_fault_tree.system_probability:.6f}\n\n")
            
            # 最小割集
            f.write("3. 最小割集\n")
            f.write(f"割集总数: {len(self.current_fault_tree.minimal_cut_sets)}\n")
            for i, cut_set in enumerate(self.current_fault_tree.minimal_cut_sets):
                f.write(f"割集 {i+1} (阶数={cut_set.order}, 概率={cut_set.probability:.2e}):\n")
                for event_id in cut_set.events:
                    if event_id in self.current_fault_tree.events:
                        event_name = self.current_fault_tree.events[event_id].name
                        f.write(f"  - {event_name}\n")
                f.write("\n")
            
            # 重要度分析
            f.write("4. 重要度分析\n")
            basic_events = self.current_fault_tree.get_basic_events()
            for event in basic_events:
                f.write(f"事件: {event.name}\n")
                measures = event.importance_measures
                f.write(f"  结构重要度: {measures.get('structure_importance', 0.0):.3f}\n")
                f.write(f"  概率重要度: {measures.get('probability_importance', 0.0):.2e}\n")
                f.write(f"  关键重要度: {measures.get('critical_importance', 0.0):.3f}\n")
                f.write("\n")