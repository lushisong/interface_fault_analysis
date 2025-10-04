#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据模型
Test Data Models

验证数据模型的基本功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.module_model import Module, HardwareModule, SoftwareModule, AlgorithmModule, ModuleType
from src.models.interface_model import Interface, InterfaceType, FailureMode, InterfaceFailureMode
from src.models.system_model import SystemStructure, TaskProfile, SuccessCriteria
from src.models.base_model import Point, ConnectionPoint
from src.core.project_manager import ProjectManager


def test_module_creation():
    """测试模块创建"""
    print("=== 测试模块创建 ===")
    
    # 创建硬件模块
    sensor = HardwareModule("温度传感器", "用于测量环境温度的传感器")
    sensor.manufacturer = "Bosch"
    sensor.model = "BME280"
    sensor.power_consumption = 0.003  # 3mW
    
    # 添加连接点
    output_point = ConnectionPoint("温度输出", Point(100, 30), "output", "signal")
    output_point.add_variable("temperature")
    sensor.add_connection_point(output_point)
    
    # 设置Python代码
    sensor.python_code = """
# 温度传感器模拟
import random
temperature = 20 + random.uniform(-5, 5)  # 模拟温度变化
outputs['temperature'] = temperature
"""
    
    print(f"创建硬件模块: {sensor.name}")
    print(f"制造商: {sensor.manufacturer}")
    print(f"型号: {sensor.model}")
    print(f"连接点数量: {len(sensor.connection_points)}")
    
    # 创建软件模块
    controller = SoftwareModule("温度控制器", "温度控制算法软件")
    controller.programming_language = "Python"
    controller.memory_usage = 50  # 50MB
    
    print(f"创建软件模块: {controller.name}")
    print(f"编程语言: {controller.programming_language}")
    
    # 创建算法模块
    pid_algorithm = AlgorithmModule("PID控制算法", "比例-积分-微分控制算法")
    pid_algorithm.algorithm_type = "PID控制"
    pid_algorithm.complexity = "O(1)"
    pid_algorithm.accuracy = 0.95
    
    print(f"创建算法模块: {pid_algorithm.name}")
    print(f"算法类型: {pid_algorithm.algorithm_type}")
    print(f"准确率: {pid_algorithm.accuracy}")
    
    return sensor, controller, pid_algorithm


def test_interface_creation():
    """测试接口创建"""
    print("\n=== 测试接口创建 ===")
    
    # 创建接口
    interface = Interface("传感器-控制器接口", "传感器与控制器之间的数据接口", 
                         InterfaceType.ALGORITHM_HARDWARE)
    interface.protocol = "I2C"
    interface.data_format = "JSON"
    interface.bandwidth = 100  # 100 Kbps
    interface.latency = 10  # 10ms
    interface.reliability = 0.999
    
    # 添加失效模式
    comm_failure = InterfaceFailureMode(FailureMode.COMMUNICATION_FAILURE, "通信失效")
    comm_failure.description = "I2C总线通信中断"
    comm_failure.severity = 8
    comm_failure.occurrence_rate = 0.001
    comm_failure.detection_rate = 0.9
    
    interface.add_failure_mode(comm_failure)
    
    print(f"创建接口: {interface.name}")
    print(f"接口类型: {interface.interface_type.value}")
    print(f"协议: {interface.protocol}")
    print(f"失效模式数量: {len(interface.failure_modes)}")
    
    return interface


def test_system_structure():
    """测试系统结构"""
    print("\n=== 测试系统结构 ===")
    
    # 创建系统结构
    system = SystemStructure("智能温控系统", "基于传感器的智能温度控制系统")
    
    # 创建模块
    sensor, controller, algorithm = test_module_creation()
    
    # 添加模块到系统
    system.add_module(sensor)
    system.add_module(controller)
    system.add_module(algorithm)
    
    # 创建接口
    interface = test_interface_creation()
    interface.source_module_id = sensor.id
    interface.target_module_id = controller.id
    system.add_interface(interface)
    
    # 创建任务剖面
    task = TaskProfile("温度控制任务", "维持室内温度在设定范围内")
    task.duration = 3600  # 1小时
    
    # 添加成功判据
    criteria = SuccessCriteria("温度稳定性", "threshold")
    criteria.target_module_id = sensor.id
    criteria.target_parameter = "temperature"
    criteria.threshold_value = 22.0
    criteria.comparison_operator = "<="
    task.add_success_criteria(criteria)
    
    system.add_task_profile(task)
    
    print(f"创建系统: {system.name}")
    print(f"模块数量: {len(system.modules)}")
    print(f"接口数量: {len(system.interfaces)}")
    print(f"任务剖面数量: {len(system.task_profiles)}")
    
    return system


def test_project_manager():
    """测试项目管理器"""
    print("\n=== 测试项目管理器 ===")
    
    # 创建项目管理器
    pm = ProjectManager()
    
    # 创建系统
    system = test_system_structure()
    pm.set_current_system(system)
    
    # 保存项目
    project_file = "data/test_project.json"
    os.makedirs("data", exist_ok=True)
    
    try:
        pm.save_project_as(project_file)
        print(f"项目已保存到: {project_file}")
        
        # 加载项目
        loaded_system = pm.load_project(project_file)
        print(f"项目已加载: {loaded_system.name}")
        print(f"加载的模块数量: {len(loaded_system.modules)}")
        
    except Exception as e:
        print(f"项目保存/加载失败: {e}")


def test_module_execution():
    """测试模块执行"""
    print("\n=== 测试模块执行 ===")
    
    # 创建一个简单的模块
    module = Module("测试模块", "用于测试Python代码执行的模块")
    module.set_parameter("gain", 2.0)
    module.set_parameter("offset", 1.0)
    
    # 设置Python代码
    module.python_code = """
# 简单的线性变换
input_value = inputs.get('input', 0)
gain = parameters.get('gain', 1.0)
offset = parameters.get('offset', 0.0)

result = input_value * gain + offset
outputs['result'] = result
outputs['status'] = 'success'

print(f"输入: {input_value}, 增益: {gain}, 偏移: {offset}, 输出: {result}")
"""
    
    # 执行模块
    test_inputs = {'input': 5.0}
    outputs = module.execute_python_code(test_inputs)
    
    print(f"模块执行结果: {outputs}")


def main():
    """主测试函数"""
    print("接口故障机理分析原型系统 - 数据模型测试")
    print("=" * 50)
    
    try:
        # 测试各个组件
        test_module_creation()
        test_interface_creation()
        test_system_structure()
        test_project_manager()
        test_module_execution()
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()