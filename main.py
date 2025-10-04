#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接口故障机理分析原型系统 - 主程序入口
Interface Fault Mechanism Analysis Prototype System - Main Entry Point

Author: OpenHands AI Assistant
Date: 2025-10-01
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.main_window import MainWindow


def main():
    """主程序入口"""
    # 创建QApplication实例
    app = QApplication(sys.argv)
    app.setApplicationName("接口故障机理分析原型系统")
    app.setApplicationVersion("1.0.0")
    
    # 设置高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建主窗口
    main_window = MainWindow()
    main_window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()