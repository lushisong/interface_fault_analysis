#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建无人机系统案例演示
Create Drone System Case Demo

基于用户提供的无人机系统架构创建完整的演示案例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.system_model import SystemStructure, Module, Connection
from src.models.module_model import ModuleType, ModuleTemplate
from src.models.interface_model import Interface, InterfaceType, HardwareInterfaceSubtype, InterfaceFailureMode, FailureMode, TriggerCondition
from src.models.task_profile_model import TaskProfile, SuccessCriteria, TaskPhase, SuccessCriteriaType, ComparisonOperator
from src.models.environment_model import EnvironmentModule, StressFactor, EnvironmentType, StressType
from src.core.project_manager import ProjectManager
from src.core.fault_tree_generator import FaultTreeGenerator


def create_drone_system():
    """创建无人机系统"""
    print("创建无人机系统...")
    
    # 创建系统结构
    system = SystemStructure("无人机智能系统", "基于多传感器融合的无人机智能监控系统")
    
    # 1. 传感器模块
    gps_sensor = Module("GPS传感器", "全球定位系统传感器")
    gps_sensor.module_type = ModuleType.HARDWARE
    gps_sensor.template = ModuleTemplate.SENSOR
    gps_sensor.parameters = {
        "accuracy": "±3m",
        "update_rate": "10Hz",
        "power_consumption": "0.5W"
    }
    gps_sensor.failure_rate = 1e-5  # 每小时失效率
    gps_sensor.position = {'x': 100, 'y': 100}
    system.add_module(gps_sensor)
    
    imu_sensor = Module("IMU传感器", "惯性测量单元")
    imu_sensor.module_type = ModuleType.HARDWARE
    imu_sensor.template = ModuleTemplate.SENSOR
    imu_sensor.parameters = {
        "gyro_range": "±2000°/s",
        "accel_range": "±16g",
        "update_rate": "100Hz"
    }
    imu_sensor.failure_rate = 2e-5
    imu_sensor.position = {'x': 250, 'y': 100}
    system.add_module(imu_sensor)
    
    camera_sensor = Module("视觉传感器", "高清摄像头")
    camera_sensor.module_type = ModuleType.HARDWARE
    camera_sensor.template = ModuleTemplate.SENSOR
    camera_sensor.parameters = {
        "resolution": "1920x1080",
        "frame_rate": "30fps",
        "field_of_view": "90°"
    }
    camera_sensor.failure_rate = 3e-5
    camera_sensor.position = {'x': 400, 'y': 100}
    system.add_module(camera_sensor)
    
    lidar_sensor = Module("激光雷达", "3D激光雷达传感器")
    lidar_sensor.module_type = ModuleType.HARDWARE
    lidar_sensor.template = ModuleTemplate.SENSOR
    lidar_sensor.parameters = {
        "range": "100m",
        "accuracy": "±2cm",
        "scan_rate": "10Hz"
    }
    lidar_sensor.failure_rate = 4e-5
    lidar_sensor.position = {'x': 550, 'y': 100}
    system.add_module(lidar_sensor)
    
    # 2. 处理器模块
    flight_controller = Module("飞控系统", "飞行控制器")
    flight_controller.module_type = ModuleType.HARDWARE
    flight_controller.template = ModuleTemplate.PROCESSOR
    flight_controller.parameters = {
        "cpu": "ARM Cortex-A72",
        "memory": "4GB RAM",
        "storage": "32GB eMMC"
    }
    flight_controller.failure_rate = 1e-4
    flight_controller.position = {'x': 200, 'y': 250}
    system.add_module(flight_controller)
    
    ai_processor = Module("AI处理器", "人工智能计算单元")
    ai_processor.module_type = ModuleType.HARDWARE
    ai_processor.template = ModuleTemplate.PROCESSOR
    ai_processor.parameters = {
        "gpu": "NVIDIA Jetson Xavier",
        "ai_performance": "32 TOPS",
        "power": "30W"
    }
    ai_processor.failure_rate = 2e-4
    ai_processor.position = {'x': 400, 'y': 250}
    system.add_module(ai_processor)
    
    # 3. 执行器模块
    motor1 = Module("电机1", "前左螺旋桨电机")
    motor1.module_type = ModuleType.HARDWARE
    motor1.template = ModuleTemplate.ACTUATOR
    motor1.parameters = {"max_power": "500W", "max_rpm": "8000"}
    motor1.failure_rate = 5e-4
    motor1.position = {'x': 100, 'y': 400}
    system.add_module(motor1)
    
    motor2 = Module("电机2", "前右螺旋桨电机")
    motor2.module_type = ModuleType.HARDWARE
    motor2.template = ModuleTemplate.ACTUATOR
    motor2.parameters = {"max_power": "500W", "max_rpm": "8000"}
    motor2.failure_rate = 5e-4
    motor2.position = {'x': 250, 'y': 400}
    system.add_module(motor2)
    
    motor3 = Module("电机3", "后左螺旋桨电机")
    motor3.module_type = ModuleType.HARDWARE
    motor3.template = ModuleTemplate.ACTUATOR
    motor3.parameters = {"max_power": "500W", "max_rpm": "8000"}
    motor3.failure_rate = 5e-4
    motor3.position = {'x': 400, 'y': 400}
    system.add_module(motor3)
    
    motor4 = Module("电机4", "后右螺旋桨电机")
    motor4.module_type = ModuleType.HARDWARE
    motor4.template = ModuleTemplate.ACTUATOR
    motor4.parameters = {"max_power": "500W", "max_rpm": "8000"}
    motor4.failure_rate = 5e-4
    motor4.position = {'x': 550, 'y': 400}
    system.add_module(motor4)
    
    # 4. 通信模块
    comm_module = Module("通信模块", "无线通信系统")
    comm_module.module_type = ModuleType.HARDWARE
    comm_module.template = ModuleTemplate.COMMUNICATION
    comm_module.parameters = {
        "frequency": "2.4GHz/5.8GHz",
        "range": "10km",
        "data_rate": "100Mbps"
    }
    comm_module.failure_rate = 1e-4
    comm_module.position = {'x': 300, 'y': 550}
    system.add_module(comm_module)
    
    print(f"✓ 创建了 {len(system.modules)} 个模块")
    return system


def create_drone_interfaces(system):
    """创建无人机接口"""
    print("创建系统接口...")
    
    # 1. 传感器-飞控接口
    gps_interface = Interface("GPS数据接口", "GPS传感器到飞控的数据接口")
    gps_interface.interface_type = InterfaceType.HARDWARE_HARDWARE
    gps_interface.subtype = HardwareInterfaceSubtype.SENSOR
    gps_interface.protocol = "UART"
    gps_interface.data_rate = "9600 bps"
    
    # 添加失效模式
    comm_failure = InterfaceFailureMode(FailureMode.COMMUNICATION_FAILURE, "GPS通信失效")
    comm_failure.occurrence_rate = 1e-6
    comm_failure.description = "GPS传感器与飞控通信中断"
    gps_interface.add_failure_mode(comm_failure)
    
    data_corruption = InterfaceFailureMode(FailureMode.DATA_CORRUPTION, "GPS数据损坏")
    data_corruption.occurrence_rate = 5e-7
    data_corruption.description = "GPS数据在传输过程中损坏"
    gps_interface.add_failure_mode(data_corruption)
    
    system.add_interface(gps_interface)
    
    # 2. IMU-飞控接口
    imu_interface = Interface("IMU数据接口", "IMU传感器到飞控的数据接口")
    imu_interface.interface_type = InterfaceType.HARDWARE_HARDWARE
    imu_interface.subtype = HardwareInterfaceSubtype.SENSOR
    imu_interface.protocol = "SPI"
    imu_interface.data_rate = "1 MHz"
    
    imu_comm_failure = InterfaceFailureMode(FailureMode.COMMUNICATION_FAILURE, "IMU通信失效")
    imu_comm_failure.occurrence_rate = 2e-6
    imu_interface.add_failure_mode(imu_comm_failure)
    
    system.add_interface(imu_interface)
    
    # 3. 视觉-AI处理器接口
    vision_interface = Interface("视觉数据接口", "摄像头到AI处理器的数据接口")
    vision_interface.interface_type = "sensor_to_ai"
    vision_interface.protocol = "CSI-2"
    vision_interface.data_rate = "1.5 Gbps"
    
    vision_failure = InterfaceFailureMode(FailureMode.COMMUNICATION_FAILURE, "视觉数据传输失效")
    vision_failure.occurrence_rate = 3e-6
    vision_interface.add_failure_mode(vision_failure)
    
    system.add_interface(vision_interface)
    
    # 4. 飞控-电机接口
    motor_interface = Interface("电机控制接口", "飞控到电机的控制接口")
    motor_interface.interface_type = "controller_to_actuator"
    motor_interface.protocol = "PWM"
    motor_interface.data_rate = "50 Hz"
    
    motor_failure = InterfaceFailureMode(FailureMode.COMMUNICATION_FAILURE, "电机控制失效")
    motor_failure.occurrence_rate = 1e-5
    motor_interface.add_failure_mode(motor_failure)
    
    system.add_interface(motor_interface)
    
    # 5. 通信接口
    radio_interface = Interface("无线通信接口", "无人机与地面站通信接口")
    radio_interface.interface_type = "wireless_communication"
    radio_interface.protocol = "WiFi/LTE"
    radio_interface.data_rate = "100 Mbps"
    
    radio_failure = InterfaceFailureMode(FailureMode.COMMUNICATION_FAILURE, "无线通信中断")
    radio_failure.occurrence_rate = 1e-4
    radio_interface.add_failure_mode(radio_failure)
    
    system.add_interface(radio_interface)
    
    print(f"✓ 创建了 {len(system.interfaces)} 个接口")
    return system


def create_drone_task_profiles(system):
    """创建无人机任务剖面"""
    print("创建任务剖面...")
    
    task_profiles = {}
    
    # 1. 巡航监控任务
    patrol_task = TaskProfile("巡航监控任务", "无人机执行区域巡航监控任务")
    patrol_task.mission_type = "surveillance"
    patrol_task.total_duration = 3600.0  # 1小时
    
    # 添加成功判据
    # 判据1：GPS定位精度
    gps_criteria = SuccessCriteria("GPS定位精度")
    gps_criteria.description = "GPS定位精度满足要求"
    gps_criteria.criteria_type = SuccessCriteriaType.MODULE_OUTPUT
    gps_criteria.module_id = [m.id for m in system.modules.values() if m.name == "GPS传感器"][0]
    gps_criteria.parameter_name = "position_accuracy"
    gps_criteria.operator = ComparisonOperator.LESS
    gps_criteria.target_value = 5.0  # 小于5米
    gps_criteria.weight = 2.0
    patrol_task.add_success_criteria(gps_criteria)
    
    # 判据2：飞行高度维持
    altitude_criteria = SuccessCriteria("飞行高度维持")
    altitude_criteria.description = "维持指定飞行高度"
    altitude_criteria.criteria_type = SuccessCriteriaType.MODULE_OUTPUT
    altitude_criteria.module_id = [m.id for m in system.modules.values() if m.name == "飞控系统"][0]
    altitude_criteria.parameter_name = "altitude"
    altitude_criteria.operator = ComparisonOperator.IN_RANGE
    altitude_criteria.range_min = 95.0
    altitude_criteria.range_max = 105.0  # 100±5米
    altitude_criteria.weight = 3.0
    patrol_task.add_success_criteria(altitude_criteria)
    
    # 判据3：通信链路正常
    comm_criteria = SuccessCriteria("通信链路正常")
    comm_criteria.description = "与地面站通信正常"
    comm_criteria.criteria_type = SuccessCriteriaType.MODULE_OUTPUT
    comm_criteria.module_id = [m.id for m in system.modules.values() if m.name == "通信模块"][0]
    comm_criteria.parameter_name = "signal_strength"
    comm_criteria.operator = ComparisonOperator.GREATER
    comm_criteria.target_value = -80.0  # dBm
    comm_criteria.weight = 2.0
    patrol_task.add_success_criteria(comm_criteria)
    
    # 添加任务阶段
    takeoff_phase = TaskPhase("起飞阶段")
    takeoff_phase.description = "无人机起飞到指定高度"
    takeoff_phase.start_time = 0.0
    takeoff_phase.duration = 120.0  # 2分钟
    patrol_task.add_task_phase(takeoff_phase)
    
    cruise_phase = TaskPhase("巡航阶段")
    cruise_phase.description = "按预定路线巡航监控"
    cruise_phase.start_time = 120.0
    cruise_phase.duration = 3300.0  # 55分钟
    patrol_task.add_task_phase(cruise_phase)
    
    landing_phase = TaskPhase("降落阶段")
    landing_phase.description = "返回起飞点并降落"
    landing_phase.start_time = 3420.0
    landing_phase.duration = 180.0  # 3分钟
    patrol_task.add_task_phase(landing_phase)
    
    task_profiles[patrol_task.id] = patrol_task
    
    # 2. 目标跟踪任务
    tracking_task = TaskProfile("目标跟踪任务", "无人机执行特定目标跟踪任务")
    tracking_task.mission_type = "tracking"
    tracking_task.total_duration = 1800.0  # 30分钟
    
    # 添加成功判据
    tracking_criteria = SuccessCriteria("目标跟踪精度")
    tracking_criteria.description = "目标跟踪精度满足要求"
    tracking_criteria.criteria_type = SuccessCriteriaType.MODULE_OUTPUT
    tracking_criteria.module_id = [m.id for m in system.modules.values() if m.name == "AI处理器"][0]
    tracking_criteria.parameter_name = "tracking_accuracy"
    tracking_criteria.operator = ComparisonOperator.GREATER
    tracking_criteria.target_value = 0.9  # 90%准确率
    tracking_criteria.weight = 3.0
    tracking_task.add_success_criteria(tracking_criteria)
    
    task_profiles[tracking_task.id] = tracking_task
    
    # 将任务剖面添加到系统
    system.task_profiles = task_profiles
    
    print(f"✓ 创建了 {len(task_profiles)} 个任务剖面")
    return system


def create_drone_environments(system):
    """创建无人机环境模型"""
    print("创建环境模型...")
    
    environments = {}
    
    # 1. 恶劣天气环境
    weather_env = EnvironmentModule("恶劣天气环境", "包含强风、降雨等恶劣天气条件")
    weather_env.environment_type = EnvironmentType.WEATHER
    weather_env.color = "#87CEEB"
    weather_env.position = {'x': 50, 'y': 50}
    
    # 添加风速应力因子
    wind_stress = StressFactor("风速")
    wind_stress.stress_type = StressType.CUSTOM
    wind_stress.description = "环境风速变化"
    wind_stress.base_value = 10.0  # m/s
    wind_stress.variation_range = 15.0
    wind_stress.distribution = "normal"
    wind_stress.time_profile = "random"
    wind_stress.duration = 3600.0
    weather_env.add_stress_factor(wind_stress)
    
    # 添加降雨应力因子
    rain_stress = StressFactor("降雨强度")
    rain_stress.stress_type = StressType.CUSTOM
    rain_stress.description = "降雨强度变化"
    rain_stress.base_value = 5.0  # mm/h
    rain_stress.variation_range = 10.0
    rain_stress.distribution = "exponential"
    rain_stress.time_profile = "linear"
    rain_stress.duration = 1800.0
    weather_env.add_stress_factor(rain_stress)
    
    # 影响的模块
    weather_env.affected_modules = [
        [m.id for m in system.modules.values() if m.name == "GPS传感器"][0],
        [m.id for m in system.modules.values() if m.name == "视觉传感器"][0],
        [m.id for m in system.modules.values() if m.name == "通信模块"][0]
    ]
    
    environments[weather_env.id] = weather_env
    
    # 2. 电磁干扰环境
    emi_env = EnvironmentModule("电磁干扰环境", "电磁干扰对通信和导航的影响")
    emi_env.environment_type = EnvironmentType.ELECTROMAGNETIC
    emi_env.color = "#FFD700"
    emi_env.position = {'x': 200, 'y': 50}
    
    # 添加电磁干扰应力因子
    emi_stress = StressFactor("电磁场强度")
    emi_stress.stress_type = StressType.ELECTROMAGNETIC
    emi_stress.description = "电磁场强度变化"
    emi_stress.base_value = 5.0  # V/m
    emi_stress.variation_range = 3.0
    emi_stress.distribution = "uniform"
    emi_stress.time_profile = "sinusoidal"
    emi_stress.parameters = {"frequency": 0.1}
    emi_stress.duration = 3600.0
    emi_env.add_stress_factor(emi_stress)
    
    # 影响的模块
    emi_env.affected_modules = [
        [m.id for m in system.modules.values() if m.name == "GPS传感器"][0],
        [m.id for m in system.modules.values() if m.name == "通信模块"][0]
    ]
    
    environments[emi_env.id] = emi_env
    
    # 3. 高温环境
    thermal_env = EnvironmentModule("高温环境", "高温对电子设备的影响")
    thermal_env.environment_type = EnvironmentType.THERMAL
    thermal_env.color = "#FF6B6B"
    thermal_env.position = {'x': 350, 'y': 50}
    
    # 添加温度应力因子
    temp_stress = StressFactor("环境温度")
    temp_stress.stress_type = StressType.TEMPERATURE
    temp_stress.description = "环境温度变化"
    temp_stress.base_value = 45.0  # °C
    temp_stress.variation_range = 15.0
    temp_stress.distribution = "normal"
    temp_stress.time_profile = "sinusoidal"
    temp_stress.parameters = {"frequency": 0.05}
    temp_stress.duration = 3600.0
    thermal_env.add_stress_factor(temp_stress)
    
    # 影响所有电子模块
    thermal_env.affected_modules = [
        [m.id for m in system.modules.values() if m.name == "飞控系统"][0],
        [m.id for m in system.modules.values() if m.name == "AI处理器"][0],
        [m.id for m in system.modules.values() if m.name == "通信模块"][0]
    ]
    
    environments[thermal_env.id] = thermal_env
    
    # 将环境模型添加到系统
    system.environment_models = environments
    
    print(f"✓ 创建了 {len(environments)} 个环境模型")
    return system


def generate_fault_tree_demo(system):
    """生成故障树演示"""
    print("生成故障树分析...")
    
    # 选择巡航监控任务
    patrol_task = None
    for task in system.task_profiles.values():
        if task.name == "巡航监控任务":
            patrol_task = task
            break
    
    if not patrol_task:
        print("✗ 未找到巡航监控任务")
        return None
    
    # 生成故障树
    generator = FaultTreeGenerator()
    fault_tree = generator.generate_fault_tree(system, patrol_task)
    
    print(f"✓ 故障树生成成功: {fault_tree.name}")
    print(f"  事件数量: {len(fault_tree.events)}")
    print(f"  逻辑门数量: {len(fault_tree.gates)}")
    
    # 分析故障树
    cut_sets = fault_tree.find_minimal_cut_sets()
    sys_prob = fault_tree.calculate_system_probability()
    fault_tree.calculate_importance_measures()
    
    print(f"✓ 故障树分析完成")
    print(f"  最小割集数量: {len(cut_sets)}")
    print(f"  系统失效概率: {sys_prob:.2e}")
    
    # 显示前5个最小割集
    print("  前5个最小割集:")
    for i, cut_set in enumerate(cut_sets[:5]):
        event_names = []
        for event_id in cut_set.events:
            if event_id in fault_tree.events:
                event_names.append(fault_tree.events[event_id].name)
        print(f"    {i+1}. {', '.join(event_names)} (概率: {cut_set.probability:.2e})")
    
    return fault_tree


def save_demo_project(system, fault_tree=None):
    """保存演示项目"""
    print("保存演示项目...")
    
    # 创建项目管理器
    pm = ProjectManager()
    pm.set_current_system(system)
    
    # 保存项目
    project_path = "/workspace/project/demo_projects/drone_system_demo.json"
    os.makedirs(os.path.dirname(project_path), exist_ok=True)
    
    try:
        # 先测试序列化
        system_dict = system.to_dict()
        print(f"✓ 系统序列化成功，数据大小: {len(str(system_dict))} 字符")
        
        pm.save_project_as(project_path)
        print(f"✓ 项目已保存到: {project_path}")
        
        # 验证文件是否正确保存
        if os.path.getsize(project_path) > 0:
            print(f"✓ 项目文件大小: {os.path.getsize(project_path)} 字节")
        else:
            print("✗ 项目文件为空")
        
        # 生成演示报告
        report_path = "/workspace/project/demo_projects/drone_system_report.txt"
        generate_demo_report(system, fault_tree, report_path)
        print(f"✓ 演示报告已生成: {report_path}")
        
        return True
    except Exception as e:
        print(f"✗ 保存项目失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_demo_report(system, fault_tree, report_path):
    """生成演示报告"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("无人机智能系统故障机理分析演示报告\n")
        f.write("=" * 60 + "\n\n")
        
        # 系统概述
        f.write("1. 系统概述\n")
        f.write(f"系统名称: {system.name}\n")
        f.write(f"系统描述: {system.description}\n")
        f.write(f"模块数量: {len(system.modules)}\n")
        f.write(f"接口数量: {len(system.interfaces)}\n")
        f.write(f"任务剖面数量: {len(system.task_profiles)}\n")
        f.write(f"环境模型数量: {len(system.environment_models)}\n\n")
        
        # 模块列表
        f.write("2. 系统模块\n")
        for module in system.modules.values():
            f.write(f"- {module.name}: {module.description}\n")
            f.write(f"  类型: {module.module_type}\n")
            f.write(f"  失效率: {module.failure_rate:.2e} /小时\n")
        f.write("\n")
        
        # 接口列表
        f.write("3. 系统接口\n")
        for interface in system.interfaces.values():
            f.write(f"- {interface.name}: {interface.description}\n")
            f.write(f"  协议: {interface.protocol}\n")
            f.write(f"  失效模式数量: {len(interface.failure_modes)}\n")
        f.write("\n")
        
        # 任务剖面
        f.write("4. 任务剖面\n")
        for task in system.task_profiles.values():
            f.write(f"- {task.name}: {task.description}\n")
            f.write(f"  任务类型: {task.mission_type}\n")
            f.write(f"  持续时间: {task.total_duration/3600:.1f} 小时\n")
            f.write(f"  成功判据数量: {len(task.success_criteria)}\n")
            f.write(f"  任务阶段数量: {len(task.task_phases)}\n")
        f.write("\n")
        
        # 环境模型
        f.write("5. 环境模型\n")
        for env in system.environment_models.values():
            f.write(f"- {env.name}: {env.description}\n")
            f.write(f"  环境类型: {env.environment_type.value}\n")
            f.write(f"  应力因子数量: {len(env.stress_factors)}\n")
            f.write(f"  影响模块数量: {len(env.affected_modules)}\n")
        f.write("\n")
        
        # 故障树分析结果
        if fault_tree:
            f.write("6. 故障树分析结果\n")
            f.write(f"故障树名称: {fault_tree.name}\n")
            f.write(f"事件总数: {len(fault_tree.events)}\n")
            f.write(f"逻辑门数量: {len(fault_tree.gates)}\n")
            f.write(f"最小割集数量: {len(fault_tree.minimal_cut_sets)}\n")
            f.write(f"系统失效概率: {fault_tree.system_probability:.2e}\n")
            f.write(f"系统可靠度: {1.0 - fault_tree.system_probability:.6f}\n\n")
            
            # 重要度分析
            f.write("7. 重要度分析\n")
            basic_events = fault_tree.get_basic_events()
            for event in basic_events:
                measures = event.importance_measures
                f.write(f"- {event.name}:\n")
                f.write(f"  结构重要度: {measures.get('structure_importance', 0.0):.3f}\n")
                f.write(f"  概率重要度: {measures.get('probability_importance', 0.0):.2e}\n")
                f.write(f"  关键重要度: {measures.get('critical_importance', 0.0):.3f}\n")
        
        f.write("\n演示报告生成完成。\n")


def main():
    """主函数"""
    print("无人机智能系统故障机理分析演示")
    print("=" * 60)
    
    try:
        # 1. 创建系统结构
        system = create_drone_system()
        
        # 2. 创建接口
        system = create_drone_interfaces(system)
        
        # 3. 创建任务剖面
        system = create_drone_task_profiles(system)
        
        # 4. 创建环境模型
        system = create_drone_environments(system)
        
        # 5. 生成故障树
        fault_tree = generate_fault_tree_demo(system)
        
        # 6. 保存演示项目
        success = save_demo_project(system, fault_tree)
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 无人机系统演示案例创建成功！")
            print("\n演示内容包括:")
            print("- ✓ 完整的无人机系统架构（11个模块）")
            print("- ✓ 五大类接口建模（5个接口）")
            print("- ✓ 多任务剖面定义（2个任务）")
            print("- ✓ 环境应力建模（3个环境）")
            print("- ✓ 自动故障树生成与分析")
            print("- ✓ 定性和定量分析结果")
            print("- ✓ 重要度指标计算")
            print("\n项目文件:")
            print("- 项目数据: demo_projects/drone_system_demo.json")
            print("- 分析报告: demo_projects/drone_system_report.txt")
            print("\n可以通过GUI界面打开项目文件进行进一步分析。")
        else:
            print("❌ 演示案例创建失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 创建演示案例时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)