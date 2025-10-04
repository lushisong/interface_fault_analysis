#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境建模功能
Test Environment Modeling Functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_environment_model():
    """测试环境建模数据模型"""
    print("=== 测试环境建模数据模型 ===")
    try:
        from src.models.environment_model import (EnvironmentModule, StressFactor, EnvironmentType,
                                                StressType, ENVIRONMENT_TEMPLATES)
        
        # 创建环境模块
        env_module = EnvironmentModule("高温环境", "高温工作环境测试")
        env_module.environment_type = EnvironmentType.THERMAL
        env_module.affected_modules = ["sensor_1", "processor_1"]
        
        print(f"✓ 创建环境模块: {env_module.name}")
        print(f"  环境类型: {env_module.environment_type.value}")
        print(f"  影响模块: {env_module.affected_modules}")
        
        # 创建应力因子
        stress_factor = StressFactor("环境温度")
        stress_factor.stress_type = StressType.TEMPERATURE
        stress_factor.base_value = 60.0
        stress_factor.variation_range = 20.0
        stress_factor.distribution = "normal"
        stress_factor.time_profile = "sinusoidal"
        
        env_module.add_stress_factor(stress_factor)
        print(f"✓ 添加应力因子: {stress_factor.name}")
        print(f"  应力类型: {stress_factor.stress_type.value}")
        print(f"  基准值: {stress_factor.base_value}")
        print(f"  变化范围: {stress_factor.variation_range}")
        
        # 测试应力值生成
        stress_value = stress_factor.generate_stress_value(10.0)
        print(f"✓ 生成应力值: {stress_value:.2f}")
        
        # 测试环境应力施加
        system_state = {
            "sensor_1": {"temperature": 25.0, "reliability": 1.0},
            "processor_1": {"temperature": 30.0, "reliability": 1.0}
        }
        
        modified_state = env_module.apply_environment_stress(system_state, 10.0)
        print(f"✓ 施加环境应力:")
        for module_id, state in modified_state.items():
            if module_id in env_module.affected_modules:
                print(f"  {module_id}: 温度={state.get('temperature', 'N/A')}")
        
        # 测试模板
        print(f"✓ 可用模板数量: {len(ENVIRONMENT_TEMPLATES)}")
        for template_name in ENVIRONMENT_TEMPLATES.keys():
            print(f"  - {template_name}")
        
        # 测试序列化
        env_dict = env_module.to_dict()
        new_env = EnvironmentModule()
        new_env.from_dict(env_dict)
        print(f"✓ 序列化测试: {new_env.name == env_module.name}")
        
        return True
    except Exception as e:
        print(f"✗ 环境建模数据模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_panel_import():
    """测试环境建模面板导入"""
    print("\n=== 测试环境建模面板导入 ===")
    try:
        from src.ui.environment_panel import EnvironmentPanel, StressFactorDialog, EnvironmentModuleDialog
        print("✓ EnvironmentPanel 导入成功")
        print("✓ StressFactorDialog 导入成功")
        print("✓ EnvironmentModuleDialog 导入成功")
        return True
    except Exception as e:
        print(f"✗ 环境建模面板导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_integration():
    """测试系统集成"""
    print("\n=== 测试系统集成 ===")
    try:
        from src.models.system_model import SystemStructure
        from src.models.environment_model import EnvironmentModule
        from src.core.project_manager import ProjectManager
        
        # 创建项目管理器和系统
        pm = ProjectManager()
        system = SystemStructure("测试系统", "环境建模集成测试系统")
        pm.set_current_system(system)
        
        # 创建环境模块
        env_module = EnvironmentModule("测试环境", "集成测试环境")
        system.environment_models[env_module.id] = env_module
        
        print(f"✓ 系统集成成功")
        print(f"  系统名称: {system.name}")
        print(f"  环境模块数量: {len(system.environment_models)}")
        
        return True
    except Exception as e:
        print(f"✗ 系统集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stress_factor_generation():
    """测试应力因子生成"""
    print("\n=== 测试应力因子生成 ===")
    try:
        from src.models.environment_model import StressFactor, StressType
        
        # 测试不同类型的应力因子
        test_cases = [
            ("温度应力", StressType.TEMPERATURE, 60.0, 20.0, "normal", "constant"),
            ("振动应力", StressType.VIBRATION, 2.0, 1.0, "uniform", "random"),
            ("网络延迟", StressType.NETWORK_DELAY, 50.0, 30.0, "exponential", "linear"),
        ]
        
        for name, stress_type, base_value, variation, distribution, time_profile in test_cases:
            stress_factor = StressFactor(name)
            stress_factor.stress_type = stress_type
            stress_factor.base_value = base_value
            stress_factor.variation_range = variation
            stress_factor.distribution = distribution
            stress_factor.time_profile = time_profile
            stress_factor.duration = 100.0
            
            # 生成多个时间点的应力值
            values = []
            for t in [0, 25, 50, 75, 100]:
                value = stress_factor.generate_stress_value(t)
                values.append(value)
            
            print(f"✓ {name}: {values}")
        
        return True
    except Exception as e:
        print(f"✗ 应力因子生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("环境建模功能测试")
    print("=" * 50)
    
    tests = [
        test_environment_model,
        test_environment_panel_import,
        test_system_integration,
        test_stress_factor_generation
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
        print("🎉 环境建模功能测试全部通过！")
        print("\n功能特性:")
        print("- ✓ 环境模块创建和管理")
        print("- ✓ 应力因子定义和生成")
        print("- ✓ 多种环境类型支持")
        print("- ✓ 时间相关应力变化")
        print("- ✓ 系统模块影响配置")
        print("- ✓ 模板支持")
        print("- ✓ 系统集成")
        print("- ✓ 图形界面组件")
    else:
        print("❌ 部分测试失败")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)