# -*- coding: utf-8 -*-
"""
主窗口
Main Window

系统的主界面，包含菜单栏、工具栏、状态栏和各功能面板
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QTabWidget, QMenuBar, QMenu, QAction,
                             QToolBar, QStatusBar, QDockWidget, QTreeWidget,
                             QTreeWidgetItem, QLabel, QPushButton, QMessageBox,
                             QFileDialog, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QKeySequence, QFont

from ..models.system_model import SystemStructure
from .system_canvas import SystemCanvas
from .module_panel import ModulePanel
from .interface_panel import InterfacePanel
from .task_profile_panel import TaskProfilePanel
from .environment_panel import EnvironmentPanel
from .fault_tree_panel import FaultTreePanel
from .property_panel import PropertyPanel
from ..core.project_manager import ProjectManager


class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 信号定义
    project_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.project_manager = ProjectManager()
        self.current_system = None
        
        self.init_ui()
        self.init_connections()
        self.init_status()
        
        # 创建新项目
        self.new_project()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("接口故障机理分析原型系统 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # 设置应用图标
        # self.setWindowIcon(QIcon('resources/icons/app_icon.png'))
        
        # 创建中央部件
        self.setup_central_widget()
        
        # 创建菜单栏
        self.setup_menu_bar()
        
        # 创建工具栏
        self.setup_tool_bar()
        
        # 创建状态栏
        self.setup_status_bar()
        
        # 创建停靠面板
        self.setup_dock_widgets()
        
        # 应用样式
        self.apply_styles()
    
    def setup_central_widget(self):
        """设置中央部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板 - 项目树
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # 中央面板 - 主工作区（包含系统画布的模块库面板）
        center_panel = self.create_center_panel()
        main_splitter.addWidget(center_panel)
        
        # 设置分割器比例（移除右侧面板）
        main_splitter.setSizes([250, 1050])
        
        # 设置布局
        layout = QHBoxLayout()
        layout.addWidget(main_splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(layout)
    
    def create_left_panel(self):
        """创建左侧面板"""
        left_widget = QWidget()
        layout = QVBoxLayout()
        
        # 项目树
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabel("项目结构")
        layout.addWidget(self.project_tree)
        
        left_widget.setLayout(layout)
        return left_widget
    
    def create_center_panel(self):
        """创建中央面板"""
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # 系统结构建模标签页
        self.system_canvas = SystemCanvas()
        self.system_canvas.set_project_manager(self.project_manager)
        self.tab_widget.addTab(self.system_canvas, "系统结构建模")
        
        # 模块建模标签页
        self.module_panel = ModulePanel()
        self.tab_widget.addTab(self.module_panel, "模块建模")
        
        # 接口建模标签页
        self.interface_panel = InterfacePanel()
        self.tab_widget.addTab(self.interface_panel, "接口建模")
        
        # 任务剖面标签页
        self.task_profile_panel = TaskProfilePanel()
        self.task_profile_panel.set_project_manager(self.project_manager)
        self.tab_widget.addTab(self.task_profile_panel, "任务剖面")
        
        # 环境建模标签页
        self.environment_panel = EnvironmentPanel()
        self.environment_panel.set_project_manager(self.project_manager)
        self.tab_widget.addTab(self.environment_panel, "环境建模")
        
        # 故障树分析标签页
        self.fault_tree_panel = FaultTreePanel()
        self.fault_tree_panel.set_project_manager(self.project_manager)
        self.tab_widget.addTab(self.fault_tree_panel, "故障树分析")
        
        return self.tab_widget
    
    def create_right_panel(self):
        """创建右侧面板"""
        # 属性面板
        self.property_panel = PropertyPanel()
        return self.property_panel
    
    def setup_menu_bar(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        # 新建项目
        new_action = QAction('新建项目(&N)', self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # 打开项目
        open_action = QAction('打开项目(&O)', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # 保存项目
        save_action = QAction('保存项目(&S)', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        # 另存为
        save_as_action = QAction('另存为(&A)', self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑(&E)')
        
        # 撤销
        undo_action = QAction('撤销(&U)', self)
        undo_action.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_action)
        
        # 重做
        redo_action = QAction('重做(&R)', self)
        redo_action.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具(&T)')
        
        # 分析菜单
        analysis_menu = menubar.addMenu('分析(&A)')
        
        # 生成故障树
        generate_ft_action = QAction('生成故障树(&G)', self)
        generate_ft_action.triggered.connect(self.generate_fault_tree)
        analysis_menu.addAction(generate_ft_action)
        
        # 故障树分析
        analyze_ft_action = QAction('故障树分析(&A)', self)
        analyze_ft_action.triggered.connect(self.analyze_fault_tree)
        analysis_menu.addAction(analyze_ft_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        # 关于
        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_tool_bar(self):
        """设置工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 新建
        new_action = QAction('新建', self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        # 打开
        open_action = QAction('打开', self)
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        # 保存
        save_action = QAction('保存', self)
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 运行仿真
        run_action = QAction('运行仿真', self)
        run_action.triggered.connect(self.run_simulation)
        toolbar.addAction(run_action)
        
        # 生成故障树
        ft_action = QAction('生成故障树', self)
        ft_action.triggered.connect(self.generate_fault_tree)
        toolbar.addAction(ft_action)
    
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 项目信息标签
        self.project_label = QLabel("无项目")
        self.status_bar.addPermanentWidget(self.project_label)
    
    def setup_dock_widgets(self):
        """设置停靠面板"""
        # 这里可以添加更多的停靠面板
        pass
    
    def apply_styles(self):
        """应用样式"""
        # 设置现代化的样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
            QTreeWidget {
                background-color: white;
                border: 1px solid #c0c0c0;
            }
            QToolBar {
                background-color: #f8f8f8;
                border: none;
                spacing: 3px;
            }
            QStatusBar {
                background-color: #f8f8f8;
                border-top: 1px solid #c0c0c0;
            }
        """)
    
    def init_connections(self):
        """初始化信号连接"""
        # 项目树选择变化
        self.project_tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        
        # 标签页变化
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def init_status(self):
        """初始化状态"""
        self.update_status("系统已启动")
    
    def new_project(self):
        """新建项目"""
        try:
            self.current_system = SystemStructure("新项目", "智能系统接口故障分析项目")
            self.project_manager.set_current_system(self.current_system)
            
            # 设置系统画布
            self.system_canvas.set_system(self.current_system)
            
            self.update_project_tree()
            self.update_status("已创建新项目")
            self.project_label.setText("新项目")
            self.project_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建新项目失败：{str(e)}")
    
    def open_project(self):
        """打开项目"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开项目", "", "项目文件 (*.json);;所有文件 (*)")
        
        if file_path:
            try:
                self.current_system = self.project_manager.load_project(file_path)
                
                # 设置系统画布
                self.system_canvas.set_system(self.current_system)
                
                self.update_project_tree()
                self.update_status(f"已打开项目：{file_path}")
                self.project_label.setText(os.path.basename(file_path))
                self.project_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开项目失败：{str(e)}")
    
    def save_project(self):
        """保存项目"""
        if self.project_manager.current_file_path:
            try:
                self.project_manager.save_project()
                self.update_status("项目已保存")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存项目失败：{str(e)}")
        else:
            self.save_project_as()
    
    def save_project_as(self):
        """另存为项目"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "另存为", "", "项目文件 (*.json);;所有文件 (*)")
        
        if file_path:
            try:
                self.project_manager.save_project_as(file_path)
                self.update_status(f"项目已保存为：{file_path}")
                self.project_label.setText(os.path.basename(file_path))
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存项目失败：{str(e)}")
    
    def run_simulation(self):
        """运行仿真"""
        if not self.current_system:
            QMessageBox.warning(self, "警告", "请先创建或打开一个项目")
            return
        
        try:
            # 运行系统仿真
            results = self.current_system.simulate_system()
            self.update_status("仿真完成")
            
            # 显示结果（这里可以创建一个结果显示对话框）
            QMessageBox.information(self, "仿真结果", f"仿真完成，共处理了 {len(results)} 个模块")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"仿真失败：{str(e)}")
    
    def generate_fault_tree(self):
        """生成故障树"""
        if not self.current_system:
            QMessageBox.warning(self, "警告", "请先创建或打开一个项目")
            return
        
        current_task = self.current_system.get_current_task_profile()
        if not current_task:
            QMessageBox.warning(self, "警告", "请先创建任务剖面")
            return
        
        try:
            # 切换到故障树分析标签页
            self.tab_widget.setCurrentWidget(self.fault_tree_panel)
            
            # 生成故障树
            self.fault_tree_panel.generate_fault_tree(self.current_system, current_task)
            self.update_status("故障树生成完成")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成故障树失败：{str(e)}")
    
    def analyze_fault_tree(self):
        """分析故障树"""
        if not self.current_system:
            QMessageBox.warning(self, "警告", "请先创建或打开一个项目")
            return
        
        try:
            # 切换到故障树分析标签页
            self.tab_widget.setCurrentWidget(self.fault_tree_panel)
            
            # 执行故障树分析
            self.fault_tree_panel.analyze_fault_tree()
            self.update_status("故障树分析完成")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"故障树分析失败：{str(e)}")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "接口故障机理分析原型系统 v1.0\n\n"
                         "基于Python 3.8 + PyQt5开发\n"
                         "支持智能系统建模和故障分析\n\n"
                         "开发者：OpenHands AI Assistant")
    
    def update_project_tree(self):
        """更新项目树"""
        self.project_tree.clear()
        
        if not self.current_system:
            return
        
        # 根节点
        root = QTreeWidgetItem(self.project_tree)
        root.setText(0, self.current_system.name)
        root.setExpanded(True)
        
        # 模块节点
        modules_node = QTreeWidgetItem(root)
        modules_node.setText(0, f"模块 ({len(self.current_system.modules)})")
        modules_node.setExpanded(True)
        
        for module in self.current_system.modules.values():
            module_item = QTreeWidgetItem(modules_node)
            module_item.setText(0, module.name)
            module_item.setData(0, Qt.UserRole, ('module', module.id))
        
        # 接口节点
        interfaces_node = QTreeWidgetItem(root)
        interfaces_node.setText(0, f"接口 ({len(self.current_system.interfaces)})")
        interfaces_node.setExpanded(True)
        
        for interface in self.current_system.interfaces.values():
            interface_item = QTreeWidgetItem(interfaces_node)
            interface_item.setText(0, interface.name)
            interface_item.setData(0, Qt.UserRole, ('interface', interface.id))
        
        # 任务剖面节点
        tasks_node = QTreeWidgetItem(root)
        tasks_node.setText(0, f"任务剖面 ({len(self.current_system.task_profiles)})")
        tasks_node.setExpanded(True)
        
        for task in self.current_system.task_profiles.values():
            task_item = QTreeWidgetItem(tasks_node)
            task_item.setText(0, task.name)
            task_item.setData(0, Qt.UserRole, ('task', task.id))
        
        # 环境模型节点
        env_node = QTreeWidgetItem(root)
        env_node.setText(0, f"环境模型 ({len(self.current_system.environment_models)})")
        env_node.setExpanded(True)
        
        for env in self.current_system.environment_models.values():
            env_item = QTreeWidgetItem(env_node)
            env_item.setText(0, env.name)
            env_item.setData(0, Qt.UserRole, ('environment', env.id))
    
    def on_tree_selection_changed(self):
        """项目树选择变化处理"""
        current_item = self.project_tree.currentItem()
        if current_item:
            data = current_item.data(0, Qt.UserRole)
            if data:
                item_type, item_id = data
                # 在属性面板中显示选中项的属性
                self.property_panel.show_item_properties(item_type, item_id, self.current_system)
    
    def on_tab_changed(self, index):
        """标签页变化处理"""
        current_widget = self.tab_widget.widget(index)
        tab_name = self.tab_widget.tabText(index)
        self.update_status(f"切换到：{tab_name}")
    
    def close_tab(self, index):
        """关闭标签页"""
        # 保留主要的标签页，不允许关闭
        if index < 6:  # 前6个是主要功能标签页
            return
        
        self.tab_widget.removeTab(index)
    
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_label.setText(message)
        
        # 3秒后恢复为"就绪"状态
        QTimer.singleShot(3000, lambda: self.status_label.setText("就绪"))
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 检查是否有未保存的更改
        if self.project_manager.has_unsaved_changes():
            reply = QMessageBox.question(
                self, "确认退出", 
                "项目有未保存的更改，是否保存？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save)
            
            if reply == QMessageBox.Save:
                self.save_project()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()