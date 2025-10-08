#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无人机系统故障机理分析演示案例
基于详细架构的无人机抵近侦察系统
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.system_model import SystemStructure, Connection
from src.models.module_model import Module, ModuleType, ModuleTemplate
from src.models.interface_model import Interface, InterfaceType, HardwareInterfaceSubtype, InterfaceFailureMode, FailureMode
from src.models.task_profile_model import TaskProfile, SuccessCriteria, TaskPhase, SuccessCriteriaType, ComparisonOperator
from src.models.environment_model import EnvironmentModule, StressFactor, EnvironmentType, StressType
from src.core.project_manager import ProjectManager
from src.core.fault_tree_generator import FaultTreeGenerator


def create_drone_system():
    """创建无人机系统"""
    print("创建无人机系统架构...")
    
    # 创建系统结构
    system = SystemStructure("无人机抵近侦察系统", "基于多源传感器融合的自主侦察无人机系统")
    
    # ============================================================================
    # 1. 外部硬件模块（左侧和右侧）
    # ============================================================================
    
    # 左侧传感器硬件
    imu_hardware = Module("惯性测量单元", "IMU传感器硬件")
    imu_hardware.module_type = ModuleType.HARDWARE
    imu_hardware.template = ModuleTemplate.SENSOR
    imu_hardware.parameters = {"update_rate": "200Hz", "interface": "SPI"}
    imu_hardware.failure_rate = 2e-5
    imu_hardware.position = {'x': 50, 'y': 200}
    system.add_module(imu_hardware)
    
    gnss_hardware = Module("全球定位模块", "GNSS接收机")
    gnss_hardware.module_type = ModuleType.HARDWARE
    gnss_hardware.template = ModuleTemplate.SENSOR
    gnss_hardware.parameters = {"accuracy": "1.5m", "update_rate": "10Hz"}
    gnss_hardware.failure_rate = 1e-5
    gnss_hardware.position = {'x': 50, 'y': 300}
    system.add_module(gnss_hardware)
    
    camera_hardware = Module("光电红外摄像机", "红外与可见光双模摄像机")
    camera_hardware.module_type = ModuleType.HARDWARE
    camera_hardware.template = ModuleTemplate.SENSOR
    camera_hardware.parameters = {"resolution": "1920x1080", "frame_rate": "30fps"}
    camera_hardware.failure_rate = 3e-5
    camera_hardware.position = {'x': 50, 'y': 400}
    system.add_module(camera_hardware)
    
    radar_hardware = Module("毫米波雷达", "77GHz毫米波雷达")
    radar_hardware.module_type = ModuleType.HARDWARE
    radar_hardware.template = ModuleTemplate.SENSOR
    radar_hardware.parameters = {"range": "200m", "accuracy": "0.1m"}
    radar_hardware.failure_rate = 4e-5
    radar_hardware.position = {'x': 50, 'y': 500}
    system.add_module(radar_hardware)
    
    # 右侧硬件
    autopilot_hardware = Module("自驾仪", "飞行控制自驾仪")
    autopilot_hardware.module_type = ModuleType.HARDWARE
    autopilot_hardware.template = ModuleTemplate.PROCESSOR
    autopilot_hardware.parameters = {"cpu": "STM32H7", "interface": "CAN/UART"}
    autopilot_hardware.failure_rate = 1e-4
    autopilot_hardware.position = {'x': 700, 'y': 200}
    system.add_module(autopilot_hardware)
    
    actuator_hardware = Module("执行器", "电机与舵机执行器")
    actuator_hardware.module_type = ModuleType.HARDWARE
    actuator_hardware.template = ModuleTemplate.ACTUATOR
    actuator_hardware.parameters = {"type": "BLDC Motor", "control": "PWM"}
    actuator_hardware.failure_rate = 5e-4
    actuator_hardware.position = {'x': 700, 'y': 300}
    system.add_module(actuator_hardware)
    
    comm_hardware = Module("通信模块", "数传与图传电台")
    comm_hardware.module_type = ModuleType.HARDWARE
    comm_hardware.template = ModuleTemplate.COMMUNICATION
    comm_hardware.parameters = {"frequency": "2.4GHz", "range": "10km"}
    comm_hardware.failure_rate = 1e-4
    comm_hardware.position = {'x': 700, 'y': 400}
    system.add_module(comm_hardware)
    
    gimbal_hardware = Module("摄像机云台", "三轴稳定云台")
    gimbal_hardware.module_type = ModuleType.HARDWARE
    gimbal_hardware.template = ModuleTemplate.ACTUATOR
    gimbal_hardware.parameters = {"stabilization": "0.01°", "control": "CAN"}
    gimbal_hardware.failure_rate = 2e-4
    gimbal_hardware.position = {'x': 700, 'y': 500}
    system.add_module(gimbal_hardware)
    
    ground_station = Module("地面站", "地面控制站")
    ground_station.module_type = ModuleType.HARDWARE
    ground_station.template = ModuleTemplate.COMMUNICATION
    ground_station.parameters = {"interface": "Ethernet/Wifi", "range": "10km"}
    ground_station.failure_rate = 1e-5
    ground_station.position = {'x': 700, 'y': 600}
    system.add_module(ground_station)
    
    # ============================================================================
    # 2. 机载计算机内部模块
    # ============================================================================
    
    # 飞控任务应用软件（作为容器）
    flight_control_app = Module("飞控任务应用软件", "无人机任务管理与控制应用")
    flight_control_app.module_type = ModuleType.SOFTWARE
    flight_control_app.template = ModuleTemplate.APPLICATION
    flight_control_app.parameters = {"type": "Real-time Application", "language": "C++"}
    flight_control_app.failure_rate = 1e-4
    flight_control_app.position = {'x': 300, 'y': 250}
    system.add_module(flight_control_app)
    
    # 7个算法单元（椭圆）
    time_sync_algo = Module("时间同步算法", "多源传感器时间同步")
    time_sync_algo.module_type = ModuleType.ALGORITHM
    time_sync_algo.template = ModuleTemplate.ALGORITHM
    time_sync_algo.parameters = {"method": "PTP", "accuracy": "1ms"}
    time_sync_algo.failure_rate = 5e-5
    time_sync_algo.position = {'x': 250, 'y': 200}
    system.add_module(time_sync_algo)
    
    spatial_reg_algo = Module("空间配准算法", "多传感器坐标系配准")
    spatial_reg_algo.module_type = ModuleType.ALGORITHM
    spatial_reg_algo.template = ModuleTemplate.ALGORITHM
    spatial_reg_algo.parameters = {"method": "ICP", "accuracy": "0.1m"}
    spatial_reg_algo.failure_rate = 5e-5
    spatial_reg_algo.position = {'x': 350, 'y': 200}
    system.add_module(spatial_reg_algo)
    
    target_detect_algo = Module("目标检测算法", "基于深度学习的目标检测")
    target_detect_algo.module_type = ModuleType.ALGORITHM
    target_detect_algo.template = ModuleTemplate.ALGORITHM
    target_detect_algo.parameters = {"model": "YOLOv5", "accuracy": "95%"}
    target_detect_algo.failure_rate = 8e-5
    target_detect_algo.position = {'x': 450, 'y': 200}
    system.add_module(target_detect_algo)
    
    env_perception_algo = Module("环境感知算法", "环境建模与理解")
    env_perception_algo.module_type = ModuleType.ALGORITHM
    env_perception_algo.template = ModuleTemplate.ALGORITHM
    env_perception_algo.parameters = {"method": "SLAM", "update_rate": "10Hz"}
    env_perception_algo.failure_rate = 7e-5
    env_perception_algo.position = {'x': 250, 'y': 300}
    system.add_module(env_perception_algo)
    
    path_planning_algo = Module("路径规划算法", "实时路径规划")
    path_planning_algo.module_type = ModuleType.ALGORITHM
    path_planning_algo.template = ModuleTemplate.ALGORITHM
    path_planning_algo.parameters = {"method": "A*", "update_rate": "5Hz"}
    path_planning_algo.failure_rate = 6e-5
    path_planning_algo.position = {'x': 350, 'y': 300}
    system.add_module(path_planning_algo)
    
    obstacle_avoid_algo = Module("避障算法", "实时障碍物规避")
    obstacle_avoid_algo.module_type = ModuleType.ALGORITHM
    obstacle_avoid_algo.template = ModuleTemplate.ALGORITHM
    obstacle_avoid_algo.parameters = {"method": "Potential Field", "response_time": "100ms"}
    obstacle_avoid_algo.failure_rate = 1e-4
    obstacle_avoid_algo.position = {'x': 450, 'y': 300}
    system.add_module(obstacle_avoid_algo)
    
    flight_control_algo = Module("飞控控制算法", "飞行姿态与轨迹控制")
    flight_control_algo.module_type = ModuleType.ALGORITHM
    flight_control_algo.template = ModuleTemplate.ALGORITHM
    flight_control_algo.parameters = {"method": "PID", "update_rate": "100Hz"}
    flight_control_algo.failure_rate = 2e-4
    flight_control_algo.position = {'x': 350, 'y': 400}
    system.add_module(flight_control_algo)
    
    # 机器学习框架
    ml_framework = Module("机器学习框架", "TensorRT推理引擎")
    ml_framework.module_type = ModuleType.SOFTWARE
    ml_framework.template = ModuleTemplate.APPLICATION  # 使用APPLICATION代替FRAMEWORK
    ml_framework.parameters = {"version": "8.0", "precision": "FP16"}
    ml_framework.failure_rate = 3e-5
    ml_framework.position = {'x': 450, 'y': 400}
    system.add_module(ml_framework)
    
    # 嵌入式OS
    embedded_os = Module("嵌入式OS", "实时操作系统")
    embedded_os.module_type = ModuleType.SOFTWARE
    embedded_os.template = ModuleTemplate.APPLICATION  # 使用APPLICATION代替OPERATING_SYSTEM
    embedded_os.parameters = {"name": "VxWorks", "version": "7.0"}
    embedded_os.failure_rate = 1e-6
    embedded_os.position = {'x': 350, 'y': 500}
    system.add_module(embedded_os)
    
    # 专用算力设备
    fpga_accelerator = Module("专用算力设备", "FPGA加速卡")
    fpga_accelerator.module_type = ModuleType.HARDWARE
    fpga_accelerator.template = ModuleTemplate.PROCESSOR
    fpga_accelerator.parameters = {"type": "Xilinx Zynq", "performance": "1TOPS"}
    fpga_accelerator.failure_rate = 2e-4
    fpga_accelerator.position = {'x': 250, 'y': 400}
    system.add_module(fpga_accelerator)
    
    print(f"✓ 创建了 {len(system.modules)} 个模块")
    return system


def create_drone_interfaces(system):
    """创建无人机接口"""
    print("创建系统接口...")
    
    # 定义所有31个接口及其故障模式
    interfaces_data = [
        # 传感输入接口
        {
            "id": 1, "name": "IMU数据采集接口", "description": "惯性测量单元→自驾仪",
            "failure_mode": "时间戳漂移导致姿态解算渐偏", "rate": 2e-6
        },
        {
            "id": 2, "name": "GNSS数据采集接口", "description": "全球定位模块→自驾仪", 
            "failure_mode": "PPS抖动引起对时偏差", "rate": 1e-6
        },
        {
            "id": 3, "name": "光电红外图像采集接口", "description": "摄像机→时间同步算法",
            "failure_mode": "高负载下丢帧", "rate": 3e-6
        },
        {
            "id": 4, "name": "雷达点云采集接口", "description": "毫米波雷达→时间同步算法",
            "failure_mode": "UDP分片丢包", "rate": 4e-6
        },
        # OS服务接口
        {
            "id": 5, "name": "同步-OS接口", "description": "时间同步算法↔嵌入式OS",
            "failure_mode": "优先级反转导致对时超时", "rate": 5e-6
        },
        # 专用算力设备接口
        {
            "id": 6, "name": "同步-算力设备接口", "description": "专用算力设备↔时间同步算法", 
            "failure_mode": "DMA传输超时", "rate": 3e-5
        },
        {
            "id": 7, "name": "配准-算力设备接口", "description": "专用算力设备↔空间配准算法",
            "failure_mode": "缓存不一致导致结果失效", "rate": 3e-5
        },
        # 应用内处理链接口
        {
            "id": 8, "name": "同步-配准接口", "description": "时间同步算法→空间配准算法",
            "failure_mode": "帧错配（时空窗错位）", "rate": 2e-5
        },
        {
            "id": 9, "name": "配准-感知接口", "description": "空间配准算法→环境感知算法", 
            "failure_mode": "坐标系标签错误", "rate": 2e-5
        },
        {
            "id": 10, "name": "配准-OS接口", "description": "空间配准算法↔嵌入式OS",
            "failure_mode": "环形缓冲溢出", "rate": 1e-5
        },
        {
            "id": 11, "name": "配准-检测接口", "description": "空间配准算法→目标检测算法",
            "failure_mode": "分辨率/步幅错配", "rate": 2e-5
        },
        {
            "id": 12, "name": "检测-OS接口", "description": "目标检测算法↔嵌入式OS",
            "failure_mode": "推理进程被OOM杀死", "rate": 8e-5
        },
        {
            "id": 13, "name": "检测-ML接口", "description": "目标检测算法↔机器学习框架",
            "failure_mode": "模型/算子版本不兼容", "rate": 5e-5
        },
        {
            "id": 14, "name": "检测-规划接口", "description": "目标检测算法→路径规划算法",
            "failure_mode": "目标ID跳变引起航迹震荡", "rate": 3e-5
        },
        {
            "id": 15, "name": "检测-云台接口", "description": "目标检测算法→摄像机云台",
            "failure_mode": "指向命令丢失", "rate": 2e-5
        },
        {
            "id": 16, "name": "数据存档接口", "description": "飞控任务应用软件→嵌入式OS",
            "failure_mode": "阻塞I/O反压上游链路", "rate": 1e-5
        },
        {
            "id": 17, "name": "感知-OS接口", "description": "环境感知算法↔嵌入式OS",
            "failure_mode": "线程池枯竭", "rate": 2e-5
        },
        {
            "id": 18, "name": "感知-避障接口", "description": "环境感知算法→避障算法",
            "failure_mode": "时间窗外数据被消费", "rate": 2e-5
        },
        {
            "id": 19, "name": "规划-OS接口", "description": "路径规划算法↔嵌入式OS", 
            "failure_mode": "定时器漂移", "rate": 1e-5
        },
        {
            "id": 20, "name": "规划-通信接口", "description": "路径规划算法↔通信模块",
            "failure_mode": "报文分片丢失", "rate": 2e-5
        },
        {
            "id": 21, "name": "规划-避障接口", "description": "路径规划算法↔避障算法",
            "failure_mode": "交互死锁", "rate": 3e-5
        },
        {
            "id": 22, "name": "避障-ML接口", "description": "避障算法↔机器学习框架",
            "failure_mode": "GPU内核异常", "rate": 4e-5
        },
        {
            "id": 23, "name": "避障-OS接口", "description": "避障算法↔嵌入式OS",
            "failure_mode": "周期漂移导致控制空洞", "rate": 2e-5
        },
        {
            "id": 24, "name": "航迹指令接口", "description": "避障算法→飞控控制算法",
            "failure_mode": "指令NaN/Inf被传播", "rate": 5e-5
        },
        {
            "id": 25, "name": "飞控-通信接口", "description": "飞控控制算法↔通信模块",
            "failure_mode": "心跳中断触发保护", "rate": 2e-5
        },
        {
            "id": 26, "name": "飞控指令接口", "description": "飞控控制算法→自驾仪",
            "failure_mode": "串口黏包/超时", "rate": 1e-4
        },
        {
            "id": 27, "name": "自驾仪状态反馈接口", "description": "自驾仪→飞控控制算法",
            "failure_mode": "状态值未正确更新", "rate": 5e-5
        },
        {
            "id": 28, "name": "飞控算法-OS接口", "description": "飞控控制算法↔嵌入式OS",
            "failure_mode": "看门狗漏触", "rate": 1e-5
        },
        {
            "id": 29, "name": "位姿反馈接口", "description": "自驾仪→空间配准算法",
            "failure_mode": "姿态突变（跳变）", "rate": 3e-5
        },
        {
            "id": 30, "name": "自驾仪-执行器接口", "description": "自驾仪↔执行器",
            "failure_mode": "总线饱和导致回授丢失", "rate": 5e-4
        },
        {
            "id": 31, "name": "无人机-地面站链路接口", "description": "通信模块↔地面站",
            "failure_mode": "干扰致BER升高与丢包", "rate": 1e-4
        }
    ]
    
    # 创建接口对象
    for iface_data in interfaces_data:
        interface = Interface(
            iface_data["name"], 
            iface_data["description"]
        )
        
        # 设置接口类型 - 使用有效的InterfaceType枚举值
        description = iface_data["description"]
        name = iface_data["name"]
        
        # 硬件到硬件接口
        if ("→" in description and 
            ("硬件" in description or "自驾仪" in description or 
             "执行器" in description or "摄像机" in description or
             "地面站" in description)):
            interface.interface_type = InterfaceType.HARDWARE_HARDWARE
        # 软件到软件接口
        elif ("↔" in description and 
              ("OS" in name or "ML" in name or "算法" in description)):
            interface.interface_type = InterfaceType.SOFTWARE_SOFTWARE
        # 软件到硬件接口
        elif ("→" in description and 
              ("算法" in description or "应用软件" in description)):
            interface.interface_type = InterfaceType.SOFTWARE_HARDWARE
        # 硬件到软件接口  
        elif ("→" in description and 
              ("传感器" in description or "摄像机" in description or
               "雷达" in description)):
            interface.interface_type = InterfaceType.HARDWARE_SOFTWARE
        # 默认使用硬件到硬件
        else:
            interface.interface_type = InterfaceType.HARDWARE_HARDWARE
        
        # 添加故障模式
        failure_mode = InterfaceFailureMode(
            FailureMode.COMMUNICATION_FAILURE,
            iface_data["failure_mode"]
        )
        failure_mode.occurrence_rate = iface_data["rate"]
        failure_mode.description = iface_data["failure_mode"]
        interface.add_failure_mode(failure_mode)
        
        system.add_interface(interface)
    
    print(f"✓ 创建了 {len(system.interfaces)} 个接口")
    return system


def create_drone_task_profiles(system):
    """创建无人机任务剖面"""
    print("创建任务剖面...")
    
    task_profiles = {}
    
    # 抵近侦察任务
    recon_task = TaskProfile("抵近侦察任务", "在目标区域内完成目标识别，保持安全距离，按时脱离返航")
    recon_task.mission_type = "reconnaissance"
    recon_task.total_duration = 35 * 60.0  # 35分钟
    
    # 添加任务阶段
    phases_data = [
        {
            "name": "上电与联合对时",
            "description": "设备自检、GNSS锁定、跨源对时与配准初始化",
            "duration": 2 * 60,  # 2分钟
            "interfaces": [1, 2, 5, 8, 10, 27]
        },
        {
            "name": "起飞与进入任务空域", 
            "description": "解锁起飞、姿态/位置闭环、进场通报",
            "duration": 5 * 60,  # 5分钟
            "interfaces": [24, 26, 27, 28, 30, 25, 31]
        },
        {
            "name": "抵近指向与目标识别",
            "description": "图像采集与同步配准、检测与置信度评估、云台指向稳定",
            "duration": 15 * 60,  # 15分钟
            "interfaces": [3, 5, 8, 11, 12, 13, 14, 15, 27, 28]
        },
        {
            "name": "脱离与返航",
            "description": "航迹重构、空域通报、返航执行", 
            "duration": 8 * 60,  # 8分钟
            "interfaces": [19, 21, 24, 26, 27, 28, 30, 20, 25, 31]
        },
        {
            "name": "进近与着陆",
            "description": "自动进近、姿态控制、落地",
            "duration": 5 * 60,  # 5分钟
            "interfaces": [24, 26, 27, 28, 30, 25, 31]
        }
    ]
    
    start_time = 0.0
    for phase_data in phases_data:
        phase = TaskPhase(phase_data["name"])
        phase.description = phase_data["description"]
        phase.start_time = start_time
        phase.duration = phase_data["duration"]
        phase.critical_interfaces = phase_data["interfaces"]
        recon_task.add_task_phase(phase)
        start_time += phase_data["duration"]
    
    # 添加成功判据
    # 判据1：目标识别成功
    target_criteria = SuccessCriteria("目标识别成功")
    target_criteria.description = "成功识别指定目标"
    target_criteria.criteria_type = SuccessCriteriaType.MODULE_OUTPUT
    target_detect_module = [m for m in system.modules.values() if m.name == "目标检测算法"][0]
    target_criteria.module_id = target_detect_module.id
    target_criteria.parameter_name = "detection_confidence"
    target_criteria.operator = ComparisonOperator.GREATER
    target_criteria.target_value = 0.8  # 80%置信度
    target_criteria.weight = 3.0
    recon_task.add_success_criteria(target_criteria)
    
    # 判据2：安全返航
    return_criteria = SuccessCriteria("安全返航")
    return_criteria.description = "无人机安全返回起飞点"
    return_criteria.criteria_type = SuccessCriteriaType.MODULE_OUTPUT
    flight_control_module = [m for m in system.modules.values() if m.name == "飞控控制算法"][0]
    return_criteria.module_id = flight_control_module.id
    return_criteria.parameter_name = "return_status"
    return_criteria.operator = ComparisonOperator.EQUAL
    return_criteria.target_value = 1.0  # 返航成功
    return_criteria.weight = 3.0
    recon_task.add_success_criteria(return_criteria)
    
    # 判据3：通信链路可用
    comm_criteria = SuccessCriteria("通信链路可用")
    comm_criteria.description = "与地面站保持必要通信"
    comm_criteria.criteria_type = SuccessCriteriaType.MODULE_OUTPUT
    comm_module = [m for m in system.modules.values() if m.name == "通信模块"][0]
    comm_criteria.module_id = comm_module.id
    comm_criteria.parameter_name = "link_quality"
    comm_criteria.operator = ComparisonOperator.GREATER
    comm_criteria.target_value = 0.7  # 70%链路质量
    comm_criteria.weight = 2.0
    recon_task.add_success_criteria(comm_criteria)
    
    task_profiles[recon_task.id] = recon_task
    
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
        [m.id for m in system.modules.values() if m.name == "全球定位模块"][0],
        [m.id for m in system.modules.values() if m.name == "光电红外摄像机"][0],
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
        [m.id for m in system.modules.values() if m.name == "全球定位模块"][0],
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
        [m.id for m in system.modules.values() if m.name == "自驾仪"][0],
        [m.id for m in system.modules.values() if m.name == "专用算力设备"][0],
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
    project_path = "./demo_projects/drone_system_demo.json"
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
        report_path = "./demo_projects/drone_system_report.txt"
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
