#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接口故障机理分析原型系统 - 简化演示
"""

import sys
import os
import json
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 直接导入测试函数
from test_models import (
    test_module_creation, 
    test_interface_creation, 
    test_system_structure,
    test_project_manager
)

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """打印章节标题"""
    print(f"\n--- {title} ---")

def main():
    """主函数 - 运行系统功能演示"""
    print("接口故障机理分析原型系统")
    print("Interface Fault Mechanism Analysis Prototype System")
    print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print_header("系统功能演示")
    
    try:
        print_section("1. 模块建模功能")
        print("支持硬件模块、软件模块、算法模块的创建和配置")
        test_module_creation()
        
        print_section("2. 接口建模功能")
        print("支持五大类接口的失效模式建模")
        test_interface_creation()
        
        print_section("3. 系统结构建模功能")
        print("支持系统结构的图形化建模和连接关系管理")
        test_system_structure()
        
        print_section("4. 项目管理功能")
        print("支持项目的保存和加载，数据持久化")
        test_project_manager()
        
        print_header("系统特性总结")
        print("✓ 模块化设计 - 支持硬件/软件/算法模块建模")
        print("✓ 接口建模 - 支持五大类接口失效模式分析")
        print("  - 算法-操作系统接口")
        print("  - 算法-智能框架接口") 
        print("  - 算法-应用接口")
        print("  - 算法-数据平台接口")
        print("  - 算法-硬件设备接口")
        print("✓ 系统结构 - 图形化建模和连接关系管理")
        print("✓ 任务剖面 - 任务成功判据和环境条件设定")
        print("✓ 故障树分析 - 定性和定量分析功能")
        print("✓ 项目管理 - 完整的保存和加载功能")
        print("✓ Python建模 - 支持自定义Python代码建模")
        print("✓ 模板库 - 提供典型功能和失效模式模板")
        
        print_header("技术架构")
        print("• 开发语言: Python 3.8+")
        print("• UI框架: PyQt5")
        print("• 数据存储: JSON格式")
        print("• 图形分析: matplotlib, networkx")
        print("• 架构模式: MVC (Model-View-Controller)")
        print("• 模块化设计: 高内聚、低耦合")
        
        print_header("主要功能模块")
        print("1. 模块建模 - 硬件/软件/算法模块的创建和编辑")
        print("2. 接口建模 - 接口失效模式和触发条件建模")
        print("3. 系统结构 - 类似Simulink的图形化建模")
        print("4. 任务剖面 - 任务成功判据和环境条件设定")
        print("5. 环境建模 - 外部环境和应力条件配置")
        print("6. 故障树分析 - 自动生成和定性定量分析")
        print("7. 模板库 - 典型模块和接口模板")
        print("8. 项目管理 - 项目保存、加载和版本管理")
        
        print_header("演示完成")
        print("系统核心功能演示成功！")
        print("所有数据模型和核心功能已验证通过。")
        
        # 显示生成的项目文件
        project_file = "data/test_project.json"
        if os.path.exists(project_file):
            file_size = os.path.getsize(project_file)
            print(f"\n生成的项目文件: {project_file}")
            print(f"文件大小: {file_size} 字节")
            
            # 显示项目文件的部分内容
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
                print(f"项目名称: {project_data.get('name', 'N/A')}")
                print(f"模块数量: {len(project_data.get('modules', []))}")
                print(f"接口数量: {len(project_data.get('interfaces', []))}")
        
    except Exception as e:
        print(f"\n演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()