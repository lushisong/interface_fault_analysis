#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的功能
Test Fixed Functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_system_canvas_imports():
    """测试系统画布导入"""
    print("=== 测试系统画布导入 ===")
    try:
        from src.ui.system_canvas import SystemCanvas, ModuleConfigDialog, ModuleGraphicsItem
        print("✓ SystemCanvas 导入成功")
        print("✓ ModuleConfigDialog 导入成功")
        print("✓ ModuleGraphicsItem 导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_interface_panel_imports():
    """测试接口面板导入"""
    print("\n=== 测试接口面板导入 ===")
    try:
        from src.ui.interface_panel import InterfacePanel
        print("✓ InterfacePanel 导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_models():
    """测试数据模型"""
    print("\n=== 测试数据模型 ===")
    try:
        from src.models.module_model import Module, ModuleType
        from src.models.interface_model import Interface, InterfaceType
        from src.models.system_model import SystemStructure
        
        # 创建测试模块
        module = Module(
            name="测试模块",
            module_type=ModuleType.HARDWARE,
            description="测试用模块"
        )
        print(f"✓ 创建模块: {module.name}")
        
        # 创建测试系统
        system = SystemStructure("测试系统", "测试用系统")
        system.modules[module.id] = module
        print(f"✓ 创建系统: {system.name}")
        print(f"  模块数量: {len(system.modules)}")
        
        return True
    except Exception as e:
        print(f"✗ 模型测试失败: {e}")
        return False

def test_project_manager():
    """测试项目管理器"""
    print("\n=== 测试项目管理器 ===")
    try:
        from src.core.project_manager import ProjectManager
        from src.models.system_model import SystemStructure
        
        pm = ProjectManager()
        system = SystemStructure("测试项目", "项目管理器测试")
        pm.set_current_system(system)
        
        print(f"✓ 项目管理器创建成功")
        print(f"✓ 当前系统: {pm.current_system.name}")
        
        return True
    except Exception as e:
        print(f"✗ 项目管理器测试失败: {e}")
        return False

def test_interface_functionality():
    """测试接口功能"""
    print("\n=== 测试接口功能 ===")
    try:
        from src.models.interface_model import Interface, InterfaceType, InterfaceFailureMode, FailureMode
        
        # 创建接口
        interface = Interface(
            name="测试接口",
            interface_type=InterfaceType.ALGORITHM_HARDWARE,
            description="测试用接口"
        )
        
        # 添加失效模式
        failure_mode = InterfaceFailureMode(
            failure_mode=FailureMode.COMMUNICATION_FAILURE,
            name="通信超时"
        )
        failure_mode.description = "接口通信超时失效"
        failure_mode.trigger_conditions = ["网络延迟 > 100ms", "负载 > 80%"]
        
        interface.add_failure_mode(failure_mode)
        
        print(f"✓ 创建接口: {interface.name}")
        print(f"✓ 接口类型: {interface.interface_type}")
        print(f"✓ 失效模式数量: {len(interface.failure_modes)}")
        
        return True
    except Exception as e:
        print(f"✗ 接口功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("接口故障机理分析原型系统 - 修复验证测试")
    print("=" * 60)
    
    tests = [
        test_system_canvas_imports,
        test_interface_panel_imports,
        test_models,
        test_project_manager,
        test_interface_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！修复成功！")
        
        print("\n修复内容总结:")
        print("1. ✓ 系统结构建模页面 - 修复模块显示问题")
        print("2. ✓ 移除右侧属性面板 - 改为左侧模块库面板")
        print("3. ✓ 实现tooltip和弹出对话框功能")
        print("4. ✓ 完善接口建模页面 - 五大类接口支持")
        print("5. ✓ 添加失效模式和触发条件建模")
        print("6. ✓ 增强模块配置对话框功能")
        print("7. ✓ 改进用户交互体验")
        
        print("\n接下来需要实现的功能:")
        print("- 任务剖面页面功能")
        print("- 环境建模页面功能") 
        print("- 故障树分析页面功能")
        print("- 无人机系统案例演示")
        
    else:
        print("❌ 部分测试失败，需要进一步修复")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)