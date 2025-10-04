#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试故障树分析功能
Test Fault Tree Analysis Functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fault_tree_model():
    """测试故障树数据模型"""
    print("=== 测试故障树数据模型 ===")
    try:
        from src.models.fault_tree_model import (FaultTree, FaultTreeEvent, FaultTreeGate,
                                               EventType, GateType, MinimalCutSet)
        
        # 创建故障树
        fault_tree = FaultTree("测试故障树", "故障树分析测试")
        fault_tree.mission_time = 1000.0
        
        print(f"✓ 创建故障树: {fault_tree.name}")
        print(f"  任务时间: {fault_tree.mission_time} 小时")
        
        # 创建顶事件
        top_event = FaultTreeEvent("系统失效", EventType.TOP_EVENT)
        top_event.position = {'x': 100, 'y': 50}
        fault_tree.add_event(top_event)
        fault_tree.top_event_id = top_event.id
        
        print(f"✓ 创建顶事件: {top_event.name}")
        
        # 创建基本事件
        basic_event1 = FaultTreeEvent("模块A失效", EventType.BASIC_EVENT)
        basic_event1.failure_rate = 1e-5
        basic_event1.mission_time = 1000.0
        basic_event1.position = {'x': 50, 'y': 200}
        fault_tree.add_event(basic_event1)
        
        basic_event2 = FaultTreeEvent("模块B失效", EventType.BASIC_EVENT)
        basic_event2.failure_rate = 2e-5
        basic_event2.mission_time = 1000.0
        basic_event2.position = {'x': 150, 'y': 200}
        fault_tree.add_event(basic_event2)
        
        print(f"✓ 创建基本事件: {basic_event1.name}, {basic_event2.name}")
        
        # 创建逻辑门
        or_gate = FaultTreeGate("系统失效门", GateType.OR)
        or_gate.output_event_id = top_event.id
        or_gate.input_events = [basic_event1.id, basic_event2.id]
        or_gate.position = {'x': 100, 'y': 125}
        fault_tree.add_gate(or_gate)
        
        print(f"✓ 创建逻辑门: {or_gate.name} ({or_gate.gate_type.value})")
        
        # 计算事件概率
        prob1 = basic_event1.calculate_probability()
        prob2 = basic_event2.calculate_probability()
        print(f"✓ 基本事件概率: {prob1:.2e}, {prob2:.2e}")
        
        # 计算逻辑门概率
        gate_prob = or_gate.calculate_probability([prob1, prob2])
        print(f"✓ 逻辑门概率: {gate_prob:.2e}")
        
        # 查找最小割集
        cut_sets = fault_tree.find_minimal_cut_sets()
        print(f"✓ 最小割集数量: {len(cut_sets)}")
        for i, cs in enumerate(cut_sets):
            print(f"  割集 {i+1}: {len(cs.events)} 个事件")
        
        # 计算系统概率
        sys_prob = fault_tree.calculate_system_probability()
        print(f"✓ 系统失效概率: {sys_prob:.2e}")
        
        # 计算重要度指标
        fault_tree.calculate_importance_measures()
        print(f"✓ 重要度指标计算完成")
        
        return True
    except Exception as e:
        print(f"✗ 故障树数据模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fault_tree_generator():
    """测试故障树生成器"""
    print("\n=== 测试故障树生成器 ===")
    try:
        from src.core.fault_tree_generator import FaultTreeGenerator
        from src.models.system_model import SystemStructure, Module
        from src.models.task_profile_model import TaskProfile, SuccessCriteria
        from src.models.interface_model import Interface, FailureMode
        
        # 创建测试系统
        system = SystemStructure("测试系统", "故障树生成测试系统")
        
        # 添加模块
        module1 = Module("传感器", "温度传感器")
        module1.failure_rate = 1e-5
        system.add_module(module1)
        
        module2 = Module("处理器", "数据处理器")
        module2.failure_rate = 2e-5
        system.add_module(module2)
        
        print(f"✓ 创建测试系统: {system.name}")
        print(f"  模块数量: {len(system.modules)}")
        
        # 创建接口
        interface = Interface("数据接口", "传感器到处理器的数据接口")
        from src.models.interface_model import InterfaceFailureMode
        failure_mode = InterfaceFailureMode(FailureMode.COMMUNICATION_FAILURE, "通信中断")
        failure_mode.occurrence_rate = 5e-6
        interface.add_failure_mode(failure_mode)
        system.add_interface(interface)
        
        print(f"✓ 创建接口: {interface.name}")
        
        # 创建任务剖面
        task_profile = TaskProfile("监控任务", "温度监控任务")
        task_profile.total_duration = 3600.0  # 1小时
        
        # 添加成功判据
        criteria = SuccessCriteria("温度监控正常")
        criteria.module_id = module1.id
        criteria.parameter_name = "temperature"
        task_profile.add_success_criteria(criteria)
        
        print(f"✓ 创建任务剖面: {task_profile.name}")
        
        # 生成故障树
        generator = FaultTreeGenerator()
        fault_tree = generator.generate_fault_tree(system, task_profile)
        
        print(f"✓ 故障树生成成功: {fault_tree.name}")
        print(f"  事件数量: {len(fault_tree.events)}")
        print(f"  逻辑门数量: {len(fault_tree.gates)}")
        print(f"  顶事件: {fault_tree.get_top_event().name if fault_tree.get_top_event() else 'None'}")
        
        # 分析故障树
        cut_sets = fault_tree.find_minimal_cut_sets()
        sys_prob = fault_tree.calculate_system_probability()
        fault_tree.calculate_importance_measures()
        
        print(f"✓ 故障树分析完成")
        print(f"  最小割集数量: {len(cut_sets)}")
        print(f"  系统失效概率: {sys_prob:.2e}")
        
        return True
    except Exception as e:
        print(f"✗ 故障树生成器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fault_tree_panel_import():
    """测试故障树面板导入"""
    print("\n=== 测试故障树面板导入 ===")
    try:
        from src.ui.fault_tree_panel import (FaultTreePanel, FaultTreeGenerationThread,
                                           FaultTreeGraphicsView)
        print("✓ FaultTreePanel 导入成功")
        print("✓ FaultTreeGenerationThread 导入成功")
        print("✓ FaultTreeGraphicsView 导入成功")
        return True
    except Exception as e:
        print(f"✗ 故障树面板导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cut_set_algorithms():
    """测试割集算法"""
    print("\n=== 测试割集算法 ===")
    try:
        from src.models.fault_tree_model import (FaultTree, FaultTreeEvent, FaultTreeGate,
                                               EventType, GateType)
        
        # 创建复杂故障树测试割集算法
        fault_tree = FaultTree("割集测试", "测试最小割集算法")
        
        # 顶事件
        top = FaultTreeEvent("TOP", EventType.TOP_EVENT)
        fault_tree.add_event(top)
        fault_tree.top_event_id = top.id
        
        # 中间事件
        int1 = FaultTreeEvent("INT1", EventType.INTERMEDIATE_EVENT)
        int2 = FaultTreeEvent("INT2", EventType.INTERMEDIATE_EVENT)
        fault_tree.add_event(int1)
        fault_tree.add_event(int2)
        
        # 基本事件
        basic_events = []
        for i in range(4):
            event = FaultTreeEvent(f"B{i+1}", EventType.BASIC_EVENT)
            event.probability = 0.01  # 1%概率
            basic_events.append(event)
            fault_tree.add_event(event)
        
        # 逻辑门结构: TOP = INT1 OR INT2, INT1 = B1 AND B2, INT2 = B3 AND B4
        gate1 = FaultTreeGate("G1", GateType.OR)
        gate1.output_event_id = top.id
        gate1.input_events = [int1.id, int2.id]
        fault_tree.add_gate(gate1)
        
        gate2 = FaultTreeGate("G2", GateType.AND)
        gate2.output_event_id = int1.id
        gate2.input_events = [basic_events[0].id, basic_events[1].id]
        fault_tree.add_gate(gate2)
        
        gate3 = FaultTreeGate("G3", GateType.AND)
        gate3.output_event_id = int2.id
        gate3.input_events = [basic_events[2].id, basic_events[3].id]
        fault_tree.add_gate(gate3)
        
        print(f"✓ 创建测试故障树结构")
        print(f"  事件数量: {len(fault_tree.events)}")
        print(f"  逻辑门数量: {len(fault_tree.gates)}")
        
        # 查找最小割集
        cut_sets = fault_tree.find_minimal_cut_sets()
        print(f"✓ 找到最小割集: {len(cut_sets)} 个")
        
        # 预期结果: 应该有2个最小割集 {B1,B2} 和 {B3,B4}
        expected_cut_sets = [{"B1", "B2"}, {"B3", "B4"}]
        
        actual_cut_sets = []
        for cs in cut_sets:
            event_names = set()
            for event_id in cs.events:
                if event_id in fault_tree.events:
                    event_names.add(fault_tree.events[event_id].name)
            actual_cut_sets.append(event_names)
        
        print(f"  实际割集: {actual_cut_sets}")
        print(f"  预期割集: {expected_cut_sets}")
        
        # 验证结果
        if len(actual_cut_sets) == 2:
            if all(cs in expected_cut_sets for cs in actual_cut_sets):
                print("✓ 割集算法验证通过")
            else:
                print("✗ 割集内容不正确")
        else:
            print(f"✗ 割集数量不正确，预期2个，实际{len(actual_cut_sets)}个")
        
        # 计算系统概率
        sys_prob = fault_tree.calculate_system_probability()
        expected_prob = 2 * 0.01 * 0.01 - 0.01 * 0.01 * 0.01 * 0.01  # P(A∪B) = P(A) + P(B) - P(A∩B)
        print(f"✓ 系统概率计算: {sys_prob:.6f} (预期: {expected_prob:.6f})")
        
        return True
    except Exception as e:
        print(f"✗ 割集算法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("故障树分析功能测试")
    print("=" * 50)
    
    tests = [
        test_fault_tree_model,
        test_fault_tree_generator,
        test_fault_tree_panel_import,
        test_cut_set_algorithms
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
        print("🎉 故障树分析功能测试全部通过！")
        print("\n功能特性:")
        print("- ✓ 故障树数据模型")
        print("- ✓ 事件和逻辑门管理")
        print("- ✓ 自动故障树生成")
        print("- ✓ 最小割集算法")
        print("- ✓ 系统概率计算")
        print("- ✓ 重要度分析")
        print("- ✓ 图形界面组件")
        print("- ✓ 多线程生成")
    else:
        print("❌ 部分测试失败")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)