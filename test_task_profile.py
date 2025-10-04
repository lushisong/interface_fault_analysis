#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试任务剖面功能
Test Task Profile Functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_task_profile_model():
    """测试任务剖面模型"""
    print("=== 测试任务剖面模型 ===")
    try:
        from src.models.task_profile_model import (TaskProfile, SuccessCriteria, TaskPhase,
                                                 SuccessCriteriaType, ComparisonOperator,
                                                 TASK_PROFILE_TEMPLATES)
        
        # 创建任务剖面
        profile = TaskProfile("无人机巡航任务", "无人机执行巡航监控任务")
        profile.mission_type = "surveillance"
        profile.total_duration = 1800.0
        
        print(f"✓ 创建任务剖面: {profile.name}")
        print(f"  任务类型: {profile.mission_type}")
        print(f"  持续时间: {profile.total_duration}秒")
        
        # 创建成功判据
        criteria = SuccessCriteria("飞行高度维持")
        criteria.description = "维持指定飞行高度"
        criteria.criteria_type = SuccessCriteriaType.MODULE_OUTPUT
        criteria.module_id = "flight_controller"
        criteria.parameter_name = "altitude"
        criteria.operator = ComparisonOperator.IN_RANGE
        criteria.range_min = 95.0
        criteria.range_max = 105.0
        criteria.weight = 2.0
        
        profile.add_success_criteria(criteria)
        print(f"✓ 添加成功判据: {criteria.name}")
        
        # 创建任务阶段
        phase = TaskPhase("起飞阶段")
        phase.description = "无人机起飞到指定高度"
        phase.start_time = 0.0
        phase.duration = 120.0
        
        profile.add_task_phase(phase)
        print(f"✓ 添加任务阶段: {phase.name}")
        
        # 测试成功判据评估
        system_state = {
            "flight_controller": {
                "altitude": 100.0,
                "speed": 15.0
            }
        }
        
        results = profile.evaluate_success(system_state)
        print(f"✓ 任务评估结果:")
        print(f"  整体成功: {results['overall_success']}")
        print(f"  成功率: {results['success_rate']:.2f}")
        
        # 测试模板
        print(f"✓ 可用模板数量: {len(TASK_PROFILE_TEMPLATES)}")
        for template_name in TASK_PROFILE_TEMPLATES.keys():
            print(f"  - {template_name}")
        
        return True
    except Exception as e:
        print(f"✗ 任务剖面模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_profile_panel_import():
    """测试任务剖面面板导入"""
    print("\n=== 测试任务剖面面板导入 ===")
    try:
        from src.ui.task_profile_panel import TaskProfilePanel, SuccessCriteriaDialog, TaskPhaseDialog
        print("✓ TaskProfilePanel 导入成功")
        print("✓ SuccessCriteriaDialog 导入成功")
        print("✓ TaskPhaseDialog 导入成功")
        return True
    except Exception as e:
        print(f"✗ 任务剖面面板导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_integration():
    """测试系统集成"""
    print("\n=== 测试系统集成 ===")
    try:
        from src.models.system_model import SystemStructure
        from src.models.task_profile_model import TaskProfile
        from src.core.project_manager import ProjectManager
        
        # 创建项目管理器和系统
        pm = ProjectManager()
        system = SystemStructure("测试系统", "集成测试系统")
        pm.set_current_system(system)
        
        # 创建任务剖面
        profile = TaskProfile("测试任务", "集成测试任务")
        system.task_profiles[profile.id] = profile
        
        print(f"✓ 系统集成成功")
        print(f"  系统名称: {system.name}")
        print(f"  任务剖面数量: {len(system.task_profiles)}")
        
        return True
    except Exception as e:
        print(f"✗ 系统集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("任务剖面功能测试")
    print("=" * 50)
    
    tests = [
        test_task_profile_model,
        test_task_profile_panel_import,
        test_system_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 任务剖面功能测试全部通过！")
        print("\n功能特性:")
        print("- ✓ 任务剖面创建和管理")
        print("- ✓ 成功判据定义和评估")
        print("- ✓ 任务阶段规划")
        print("- ✓ 模板支持")
        print("- ✓ 系统集成")
        print("- ✓ 图形界面组件")
    else:
        print("❌ 部分测试失败")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)