#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""\
无人机系统接口故障机理演示脚本
================================

该脚本根据“接口故障模式对无人智能系统任务可靠性的影响机理研究”中的描述，
构建无人机智能系统的结构、接口、任务剖面与环境，并对“抵近侦察”与“物资
投放”两个典型任务剖面执行故障树分析。脚本在原始结构基础上补充了多模态
感知冗余等结构，使最小割集包含组合事件，便于展示接口冗余失效机理。
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.fault_tree_generator import FaultTreeGenerator
from src.core.project_manager import ProjectManager
from src.models.base_model import Point
from src.models.environment_model import (
    EnvironmentModule,
    EnvironmentType,
    StressFactor,
    StressType,
)
from src.models.interface_model import (
    FailureMode,
    HardwareInterfaceSubtype,
    Interface,
    InterfaceDirection,
    InterfaceFailureMode,
    InterfaceType,
)
from src.models.module_model import Module, ModuleTemplate, ModuleType
from src.models.system_model import Connection, SystemStructure
from src.models.task_profile_model import (
    ComparisonOperator,
    SuccessCriteria,
    SuccessCriteriaType,
    TaskPhase,
    TaskProfile,
)


# ---------------------------------------------------------------------------
# 数据定义
# ---------------------------------------------------------------------------

MODULE_SPECS: List[Dict[str, object]] = [
    {
        "name": "惯性测量单元",
        "description": "IMU传感器硬件",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.SENSOR,
        "position": (40, 200),
        "parameters": {"update_rate": "200Hz", "interface": "SPI"},
        "failure_rate": 2e-5,
    },
    {
        "name": "全球定位模块",
        "description": "GNSS接收机",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.SENSOR,
        "position": (40, 300),
        "parameters": {"accuracy": "1.5m", "update_rate": "10Hz"},
        "failure_rate": 1.2e-5,
    },
    {
        "name": "光电红外摄像机",
        "description": "双谱段光电红外摄像机",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.SENSOR,
        "position": (40, 410),
        "parameters": {"resolution": "1920x1080", "frame_rate": "30fps"},
        "failure_rate": 3.5e-5,
    },
    {
        "name": "毫米波雷达",
        "description": "77GHz毫米波雷达",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.SENSOR,
        "position": (40, 520),
        "parameters": {"range": "200m", "accuracy": "0.1m"},
        "failure_rate": 4.1e-5,
    },
    {
        "name": "飞控任务应用软件",
        "description": "无人机任务管理与飞控任务容器",
        "type": ModuleType.SOFTWARE,
        "template": ModuleTemplate.APPLICATION,
        "position": (320, 240),
        "parameters": {"language": "C++", "runtime": "RTOS"},
        "failure_rate": 1.0e-4,
    },
    {
        "name": "时间同步算法",
        "description": "多源传感器时间同步算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (220, 180),
        "parameters": {"method": "PTP", "accuracy": "1ms"},
        "failure_rate": 5.0e-5,
    },
    {
        "name": "空间配准算法",
        "description": "多源坐标系配准算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (320, 180),
        "parameters": {"method": "ICP", "accuracy": "0.1m"},
        "failure_rate": 5.0e-5,
    },
    {
        "name": "多模态感知冗余管理",
        "description": "双通道感知数据冗余与健康监测模块",
        "type": ModuleType.SOFTWARE,
        "template": ModuleTemplate.APPLICATION,
        "position": (420, 240),
        "parameters": {"mode": "dual-feed", "latency_budget_ms": 40},
        "failure_rate": 4.5e-5,
    },
    {
        "name": "目标检测算法",
        "description": "基于深度学习的目标检测算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (520, 180),
        "parameters": {"model": "YOLOv5", "pd": 0.95},
        "failure_rate": 8.0e-5,
    },
    {
        "name": "环境感知算法",
        "description": "多传感环境理解算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (520, 300),
        "parameters": {"method": "OccupancyFusion", "update_rate": "10Hz"},
        "failure_rate": 7.0e-5,
    },
    {
        "name": "路径规划算法",
        "description": "实时路径规划算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (620, 240),
        "parameters": {"method": "A*", "replan_period": 0.3},
        "failure_rate": 6.0e-5,
    },
    {
        "name": "避障算法",
        "description": "动态避障与安全裕度评估算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (720, 240),
        "parameters": {"method": "ModelPredictive", "latency": "120ms"},
        "failure_rate": 1.1e-4,
    },
    {
        "name": "飞控控制算法",
        "description": "姿态/航迹闭环控制算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (620, 360),
        "parameters": {"method": "PID+LQR", "rate": "100Hz"},
        "failure_rate": 2.0e-4,
    },
    {
        "name": "自驾仪",
        "description": "飞行控制自驾仪硬件",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.PROCESSOR,
        "position": (840, 200),
        "parameters": {"cpu": "STM32H7", "buses": "CAN/UART"},
        "failure_rate": 1.1e-4,
    },
    {
        "name": "执行器",
        "description": "电机与舵面执行器阵列",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.ACTUATOR,
        "position": (950, 280),
        "parameters": {"type": "BLDC", "control": "PWM"},
        "failure_rate": 4.8e-4,
    },
    {
        "name": "通信模块",
        "description": "机载通信与数传模块",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.COMMUNICATION,
        "position": (840, 360),
        "parameters": {"band": "2.4/5.8GHz", "range": "10km"},
        "failure_rate": 1.1e-4,
    },
    {
        "name": "通信链路健康管理",
        "description": "通信链路心跳与干扰监测服务",
        "type": ModuleType.SOFTWARE,
        "template": ModuleTemplate.APPLICATION,
        "position": (720, 360),
        "parameters": {"heartbeat_period_ms": 500, "failover": True},
        "failure_rate": 5.5e-5,
    },
    {
        "name": "摄像机云台",
        "description": "三轴稳定云台",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.ACTUATOR,
        "position": (950, 180),
        "parameters": {"precision": "0.01°", "control": "CAN"},
        "failure_rate": 2.2e-4,
    },
    {
        "name": "地面站",
        "description": "地面控制站",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.COMMUNICATION,
        "position": (950, 420),
        "parameters": {"link": "Ethernet/Wireless", "range": "15km"},
        "failure_rate": 1.0e-5,
    },
    {
        "name": "机器学习框架",
        "description": "TensorRT推理框架",
        "type": ModuleType.SOFTWARE,
        "template": ModuleTemplate.APPLICATION,
        "position": (520, 420),
        "parameters": {"version": "8.5", "precision": "FP16"},
        "failure_rate": 3.5e-5,
    },
    {
        "name": "嵌入式OS",
        "description": "实时嵌入式操作系统",
        "type": ModuleType.SOFTWARE,
        "template": ModuleTemplate.APPLICATION,
        "position": (420, 420),
        "parameters": {"name": "VxWorks", "scheduler": "Priority"},
        "failure_rate": 1.0e-6,
    },
    {
        "name": "专用算力设备",
        "description": "FPGA/SoC算力加速设备",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.PROCESSOR,
        "position": (220, 300),
        "parameters": {"type": "Zynq", "tops": "1.2"},
        "failure_rate": 2.0e-4,
    },
]


INTERFACE_SPECS: List[Dict[str, object]] = [
    {
        "id": 1,
        "name": "IMU数据采集",
        "description": "惯性测量单元 → 自驾仪",
        "source": "惯性测量单元",
        "target": "自驾仪",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.HARDWARE_HARDWARE,
        "subtype": HardwareInterfaceSubtype.SENSOR,
        "protocol": "SPI",
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "时间戳漂移",
            "description": "时间戳漂移导致姿态解算渐偏",
            "rate": 2.5e-5,
        },
    },
    {
        "id": 2,
        "name": "GNSS数据采集",
        "description": "GNSS → 自驾仪",
        "source": "全球定位模块",
        "target": "自驾仪",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.HARDWARE_HARDWARE,
        "subtype": HardwareInterfaceSubtype.SENSOR,
        "protocol": "UART",
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "PPS抖动",
            "description": "PPS抖动引起对时偏差",
            "rate": 1.8e-5,
        },
    },
    {
        "id": 3,
        "name": "光电红外图像采集",
        "description": "摄像机 → 时间同步算法",
        "source": "光电红外摄像机",
        "target": "时间同步算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "subtype": HardwareInterfaceSubtype.SENSOR,
        "protocol": "GigE Vision",
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "高负载丢帧",
            "description": "高负载下图像帧丢失",
            "rate": 3.2e-5,
        },
    },
    {
        "id": 4,
        "name": "雷达点云采集",
        "description": "毫米波雷达 → 时间同步算法",
        "source": "毫米波雷达",
        "target": "时间同步算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "subtype": HardwareInterfaceSubtype.SENSOR,
        "protocol": "UDP",
        "failure_mode": {
            "category": FailureMode.COMMUNICATION_FAILURE,
            "name": "UDP分片丢包",
            "description": "UDP分片丢包导致点云缺失",
            "rate": 3.0e-5,
        },
    },
    {
        "id": 5,
        "name": "同步-OS",
        "description": "时间同步算法 ↔ 嵌入式OS",
        "source": "时间同步算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "protocol": "RTIPC",
        "failure_mode": {
            "category": FailureMode.RESOURCE_EXHAUSTION,
            "name": "优先级反转",
            "description": "优先级反转导致对时超时",
            "rate": 1.0e-5,
        },
    },
    {
        "id": 6,
        "name": "同步-算力设备",
        "description": "时间同步算法 ↔ 专用算力设备",
        "source": "时间同步算法",
        "target": "专用算力设备",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "subtype": HardwareInterfaceSubtype.COMPUTING_HARDWARE,
        "protocol": "DMA",
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "DMA传输超时",
            "description": "DMA传输超时导致同步窗口失配",
            "rate": 2.6e-5,
        },
    },
    {
        "id": 7,
        "name": "配准-算力设备",
        "description": "空间配准算法 ↔ 专用算力设备",
        "source": "空间配准算法",
        "target": "专用算力设备",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "subtype": HardwareInterfaceSubtype.COMPUTING_HARDWARE,
        "protocol": "DMA",
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "缓存不一致",
            "description": "缓存不一致导致结果失效",
            "rate": 2.4e-5,
        },
    },
    {
        "id": 8,
        "name": "同步-配准",
        "description": "时间同步算法 → 空间配准算法",
        "source": "时间同步算法",
        "target": "空间配准算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "帧错配",
            "description": "时空窗口错位导致帧错配",
            "rate": 1.9e-5,
        },
    },
    {
        "id": 9,
        "name": "配准-感知",
        "description": "空间配准算法 → 环境感知算法",
        "source": "空间配准算法",
        "target": "环境感知算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "坐标系错标",
            "description": "坐标系标签错误",
            "rate": 2.1e-5,
        },
    },
    {
        "id": 10,
        "name": "配准-OS",
        "description": "空间配准算法 ↔ 嵌入式OS",
        "source": "空间配准算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.RESOURCE_EXHAUSTION,
            "name": "环形缓冲溢出",
            "description": "环形缓冲溢出导致数据丢失",
            "rate": 1.4e-5,
        },
    },
    {
        "id": 11,
        "name": "配准-检测",
        "description": "空间配准算法 → 目标检测算法",
        "source": "空间配准算法",
        "target": "目标检测算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.CONFIGURATION_ERROR,
            "name": "分辨率错配",
            "description": "分辨率/步幅错配导致输入失效",
            "rate": 2.0e-5,
        },
    },
    {
        "id": 12,
        "name": "检测-OS",
        "description": "目标检测算法 ↔ 嵌入式OS",
        "source": "目标检测算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.RESOURCE_EXHAUSTION,
            "name": "推理进程OOM",
            "description": "推理进程因内存不足被终止",
            "rate": 2.7e-5,
        },
    },
    {
        "id": 13,
        "name": "检测-ML",
        "description": "目标检测算法 ↔ 机器学习框架",
        "source": "目标检测算法",
        "target": "机器学习框架",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_FRAMEWORK,
        "failure_mode": {
            "category": FailureMode.VERSION_INCOMPATIBILITY,
            "name": "模型版本不兼容",
            "description": "模型/算子版本不兼容",
            "rate": 1.8e-5,
        },
    },
    {
        "id": 14,
        "name": "检测-规划",
        "description": "目标检测算法 → 路径规划算法",
        "source": "目标检测算法",
        "target": "路径规划算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "目标ID跳变",
            "description": "目标ID跳变引起航迹震荡",
            "rate": 2.3e-5,
        },
    },
    {
        "id": 15,
        "name": "检测-云台",
        "description": "目标检测算法 → 摄像机云台",
        "source": "目标检测算法",
        "target": "摄像机云台",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "subtype": HardwareInterfaceSubtype.ACTUATOR,
        "failure_mode": {
            "category": FailureMode.COMMUNICATION_FAILURE,
            "name": "指向命令丢失",
            "description": "云台指向命令丢失",
            "rate": 1.7e-5,
        },
    },
    {
        "id": 16,
        "name": "数据存档",
        "description": "飞控任务应用软件 → 嵌入式OS",
        "source": "飞控任务应用软件",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_DATA_PLATFORM,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "阻塞I/O",
            "description": "阻塞I/O反压上游链路",
            "rate": 1.3e-5,
        },
    },
    {
        "id": 17,
        "name": "感知-OS",
        "description": "环境感知算法 ↔ 嵌入式OS",
        "source": "环境感知算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.RESOURCE_EXHAUSTION,
            "name": "线程池枯竭",
            "description": "线程池枯竭导致感知滞后",
            "rate": 2.5e-5,
        },
    },
    {
        "id": 18,
        "name": "感知-避障",
        "description": "环境感知算法 → 避障算法",
        "source": "环境感知算法",
        "target": "避障算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "时间窗越界",
            "description": "时间窗外数据被消费",
            "rate": 2.9e-5,
        },
    },
    {
        "id": 19,
        "name": "规划-OS",
        "description": "路径规划算法 ↔ 嵌入式OS",
        "source": "路径规划算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "定时器漂移",
            "description": "定时器漂移导致重规划窗口漂移",
            "rate": 2.2e-5,
        },
    },
    {
        "id": 20,
        "name": "规划-通信",
        "description": "路径规划算法 ↔ 通信模块",
        "source": "路径规划算法",
        "target": "通信模块",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "failure_mode": {
            "category": FailureMode.COMMUNICATION_FAILURE,
            "name": "报文分片丢失",
            "description": "报文分片丢失导致下行指令缺失",
            "rate": 2.0e-5,
        },
    },
    {
        "id": 21,
        "name": "规划-避障",
        "description": "路径规划算法 ↔ 避障算法",
        "source": "路径规划算法",
        "target": "避障算法",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "交互死锁",
            "description": "规划与避障交互死锁",
            "rate": 2.8e-5,
        },
    },
    {
        "id": 22,
        "name": "避障-ML",
        "description": "避障算法 ↔ 机器学习框架",
        "source": "避障算法",
        "target": "机器学习框架",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_FRAMEWORK,
        "failure_mode": {
            "category": FailureMode.HARDWARE_FAULT,
            "name": "GPU内核异常",
            "description": "GPU内核异常导致避障推理失败",
            "rate": 2.1e-5,
        },
    },
    {
        "id": 23,
        "name": "避障-OS",
        "description": "避障算法 ↔ 嵌入式OS",
        "source": "避障算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "周期漂移",
            "description": "周期漂移导致控制空洞",
            "rate": 2.3e-5,
        },
    },
    {
        "id": 24,
        "name": "航迹指令",
        "description": "避障算法 → 飞控控制算法",
        "source": "避障算法",
        "target": "飞控控制算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "指令NaN/Inf",
            "description": "航迹指令包含NaN/Inf",
            "rate": 3.0e-5,
        },
    },
    {
        "id": 25,
        "name": "飞控-通信",
        "description": "飞控控制算法 ↔ 通信模块",
        "source": "飞控控制算法",
        "target": "通信模块",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "心跳中断",
            "description": "飞控-通信心跳中断触发保护",
            "rate": 2.4e-5,
        },
    },
    {
        "id": 26,
        "name": "飞控指令",
        "description": "飞控控制算法 → 自驾仪",
        "source": "飞控控制算法",
        "target": "自驾仪",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "串口黏包",
            "description": "串口黏包/超时导致指令失效",
            "rate": 2.5e-5,
        },
    },
    {
        "id": 27,
        "name": "自驾仪状态反馈",
        "description": "自驾仪 → 飞控控制算法",
        "source": "自驾仪",
        "target": "飞控控制算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.HARDWARE_HARDWARE,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "状态未更新",
            "description": "状态值未正确更新",
            "rate": 2.7e-5,
        },
    },
    {
        "id": 28,
        "name": "飞控算法-OS",
        "description": "飞控控制算法 ↔ 嵌入式OS",
        "source": "飞控控制算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "看门狗漏触",
            "description": "抖动下看门狗漏触/误触",
            "rate": 1.9e-5,
        },
    },
    {
        "id": 29,
        "name": "位姿反馈",
        "description": "自驾仪 → 空间配准算法",
        "source": "自驾仪",
        "target": "空间配准算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.HARDWARE_HARDWARE,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "姿态突变",
            "description": "姿态突变（跳变）",
            "rate": 2.6e-5,
        },
    },
    {
        "id": 30,
        "name": "自驾仪-执行器",
        "description": "自驾仪 ↔ 执行器",
        "source": "自驾仪",
        "target": "执行器",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.HARDWARE_HARDWARE,
        "subtype": HardwareInterfaceSubtype.ACTUATOR,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "总线饱和",
            "description": "总线饱和导致回授丢失",
            "rate": 3.1e-5,
        },
    },
    {
        "id": 31,
        "name": "无人机-地面站链路",
        "description": "通信模块 ↔ 地面站",
        "source": "通信模块",
        "target": "地面站",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_DATA_PLATFORM,
        "failure_mode": {
            "category": FailureMode.COMMUNICATION_FAILURE,
            "name": "链路干扰",
            "description": "干扰致BER升高与丢包",
            "rate": 2.8e-5,
        },
    },
    {
        "id": 32,
        "name": "冗余感知仲裁",
        "description": "空间配准算法 → 多模态感知冗余管理",
        "source": "空间配准算法",
        "target": "多模态感知冗余管理",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.CONFIGURATION_ERROR,
            "name": "冗余策略失效",
            "description": "冗余仲裁逻辑配置错误",
            "rate": 1.2e-5,
        },
    },
    {
        "id": 33,
        "name": "冗余输出-检测",
        "description": "多模态感知冗余管理 → 目标检测算法",
        "source": "多模态感知冗余管理",
        "target": "目标检测算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "冗余输出漂移",
            "description": "冗余仲裁输出漂移导致检测输入异常",
            "rate": 1.1e-5,
        },
    },
    {
        "id": 34,
        "name": "冗余输出-感知",
        "description": "多模态感知冗余管理 → 环境感知算法",
        "source": "多模态感知冗余管理",
        "target": "环境感知算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "冗余输出不一致",
            "description": "冗余输出不一致导致环境感知失效",
            "rate": 1.15e-5,
        },
    },
    {
        "id": 35,
        "name": "通信心跳监测",
        "description": "通信模块 ↔ 通信链路健康管理",
        "source": "通信模块",
        "target": "通信链路健康管理",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.SOFTWARE_HARDWARE,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "心跳判决失效",
            "description": "链路健康监测错判导致切换失败",
            "rate": 1.6e-5,
        },
    },
]

# ---------------------------------------------------------------------------
# 布局常量
# ---------------------------------------------------------------------------

MODULE_WIDTH = 120.0
MODULE_HEIGHT = 80.0
HORIZONTAL_MARGIN = 60.0
VERTICAL_MARGIN = 40.0


# ---------------------------------------------------------------------------
# 数据定义
# ---------------------------------------------------------------------------

MODULE_SPECS: List[Dict[str, object]] = [
    {
        "name": "惯性测量单元",
        "description": "IMU传感器硬件",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.SENSOR,
        "position": (40, 200),
        "parameters": {"update_rate": "200Hz", "interface": "SPI"},
        "failure_rate": 2e-5,
    },
    {
        "name": "全球定位模块",
        "description": "GNSS接收机",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.SENSOR,
        "position": (40, 300),
        "parameters": {"accuracy": "1.5m", "update_rate": "10Hz"},
        "failure_rate": 1.2e-5,
    },
    {
        "name": "光电红外摄像机",
        "description": "双谱段光电红外摄像机",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.SENSOR,
        "position": (40, 410),
        "parameters": {"resolution": "1920x1080", "frame_rate": "30fps"},
        "failure_rate": 3.5e-5,
    },
    {
        "name": "毫米波雷达",
        "description": "77GHz毫米波雷达",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.SENSOR,
        "position": (40, 520),
        "parameters": {"range": "200m", "accuracy": "0.1m"},
        "failure_rate": 4.1e-5,
    },
    {
        "name": "飞控任务应用软件",
        "description": "无人机任务管理与飞控任务容器",
        "type": ModuleType.SOFTWARE,
        "template": ModuleTemplate.APPLICATION,
        "position": (320, 240),
        "parameters": {"language": "C++", "runtime": "RTOS"},
        "failure_rate": 1.0e-4,
    },
    {
        "name": "时间同步算法",
        "description": "多源传感器时间同步算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (220, 180),
        "parameters": {"method": "PTP", "accuracy": "1ms"},
        "failure_rate": 5.0e-5,
    },
    {
        "name": "空间配准算法",
        "description": "多源坐标系配准算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (320, 180),
        "parameters": {"method": "ICP", "accuracy": "0.1m"},
        "failure_rate": 5.0e-5,
    },
    {
        "name": "多模态感知冗余管理",
        "description": "双通道感知数据冗余与健康监测模块",
        "type": ModuleType.SOFTWARE,
        "template": ModuleTemplate.APPLICATION,
        "position": (420, 240),
        "parameters": {"mode": "dual-feed", "latency_budget_ms": 40},
        "failure_rate": 4.5e-5,
    },
    {
        "name": "目标检测算法",
        "description": "基于深度学习的目标检测算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (520, 180),
        "parameters": {"model": "YOLOv5", "pd": 0.95},
        "failure_rate": 8.0e-5,
    },
    {
        "name": "环境感知算法",
        "description": "多传感环境理解算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (520, 300),
        "parameters": {"method": "OccupancyFusion", "update_rate": "10Hz"},
        "failure_rate": 7.0e-5,
    },
    {
        "name": "路径规划算法",
        "description": "实时路径规划算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (620, 240),
        "parameters": {"method": "A*", "replan_period": 0.3},
        "failure_rate": 6.0e-5,
    },
    {
        "name": "避障算法",
        "description": "动态避障与安全裕度评估算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (720, 240),
        "parameters": {"method": "ModelPredictive", "latency": "120ms"},
        "failure_rate": 1.1e-4,
    },
    {
        "name": "飞控控制算法",
        "description": "姿态/航迹闭环控制算法",
        "type": ModuleType.ALGORITHM,
        "template": ModuleTemplate.ALGORITHM,
        "position": (620, 360),
        "parameters": {"method": "PID+LQR", "rate": "100Hz"},
        "failure_rate": 2.0e-4,
    },
    {
        "name": "自驾仪",
        "description": "飞行控制自驾仪硬件",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.PROCESSOR,
        "position": (840, 200),
        "parameters": {"cpu": "STM32H7", "buses": "CAN/UART"},
        "failure_rate": 1.1e-4,
    },
    {
        "name": "执行器",
        "description": "电机与舵面执行器阵列",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.ACTUATOR,
        "position": (950, 280),
        "parameters": {"type": "BLDC", "control": "PWM"},
        "failure_rate": 4.8e-4,
    },
    {
        "name": "通信模块",
        "description": "机载通信与数传模块",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.COMMUNICATION,
        "position": (840, 360),
        "parameters": {"band": "2.4/5.8GHz", "range": "10km"},
        "failure_rate": 1.1e-4,
    },
    {
        "name": "通信链路健康管理",
        "description": "通信链路心跳与干扰监测服务",
        "type": ModuleType.SOFTWARE,
        "template": ModuleTemplate.APPLICATION,
        "position": (720, 360),
        "parameters": {"heartbeat_period_ms": 500, "failover": True},
        "failure_rate": 5.5e-5,
    },
    {
        "name": "摄像机云台",
        "description": "三轴稳定云台",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.ACTUATOR,
        "position": (950, 180),
        "parameters": {"precision": "0.01°", "control": "CAN"},
        "failure_rate": 2.2e-4,
    },
    {
        "name": "地面站",
        "description": "地面控制站",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.COMMUNICATION,
        "position": (950, 420),
        "parameters": {"link": "Ethernet/Wireless", "range": "15km"},
        "failure_rate": 1.0e-5,
    },
    {
        "name": "机器学习框架",
        "description": "TensorRT推理框架",
        "type": ModuleType.SOFTWARE,
        "template": ModuleTemplate.APPLICATION,
        "position": (520, 420),
        "parameters": {"version": "8.5", "precision": "FP16"},
        "failure_rate": 3.5e-5,
    },
    {
        "name": "嵌入式OS",
        "description": "实时嵌入式操作系统",
        "type": ModuleType.SOFTWARE,
        "template": ModuleTemplate.APPLICATION,
        "position": (420, 420),
        "parameters": {"name": "VxWorks", "scheduler": "Priority"},
        "failure_rate": 1.0e-6,
    },
    {
        "name": "专用算力设备",
        "description": "FPGA/SoC算力加速设备",
        "type": ModuleType.HARDWARE,
        "template": ModuleTemplate.PROCESSOR,
        "position": (220, 300),
        "parameters": {"type": "Zynq", "tops": "1.2"},
        "failure_rate": 2.0e-4,
    },
]


INTERFACE_SPECS: List[Dict[str, object]] = [
    {
        "id": 1,
        "name": "IMU数据采集",
        "description": "惯性测量单元 → 自驾仪",
        "source": "惯性测量单元",
        "target": "自驾仪",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.HARDWARE_HARDWARE,
        "subtype": HardwareInterfaceSubtype.SENSOR,
        "protocol": "SPI",
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "时间戳漂移",
            "description": "时间戳漂移导致姿态解算渐偏",
            "rate": 2.5e-5,
        },
    },
    {
        "id": 2,
        "name": "GNSS数据采集",
        "description": "GNSS → 自驾仪",
        "source": "全球定位模块",
        "target": "自驾仪",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.HARDWARE_HARDWARE,
        "subtype": HardwareInterfaceSubtype.SENSOR,
        "protocol": "UART",
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "PPS抖动",
            "description": "PPS抖动引起对时偏差",
            "rate": 1.8e-5,
        },
    },
    {
        "id": 3,
        "name": "光电红外图像采集",
        "description": "摄像机 → 时间同步算法",
        "source": "光电红外摄像机",
        "target": "时间同步算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "subtype": HardwareInterfaceSubtype.SENSOR,
        "protocol": "GigE Vision",
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "高负载丢帧",
            "description": "高负载下图像帧丢失",
            "rate": 3.2e-5,
        },
    },
    {
        "id": 4,
        "name": "雷达点云采集",
        "description": "毫米波雷达 → 时间同步算法",
        "source": "毫米波雷达",
        "target": "时间同步算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "subtype": HardwareInterfaceSubtype.SENSOR,
        "protocol": "UDP",
        "failure_mode": {
            "category": FailureMode.COMMUNICATION_FAILURE,
            "name": "UDP分片丢包",
            "description": "UDP分片丢包导致点云缺失",
            "rate": 3.0e-5,
        },
    },
    {
        "id": 5,
        "name": "同步-OS",
        "description": "时间同步算法 ↔ 嵌入式OS",
        "source": "时间同步算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "protocol": "RTIPC",
        "failure_mode": {
            "category": FailureMode.RESOURCE_EXHAUSTION,
            "name": "优先级反转",
            "description": "优先级反转导致对时超时",
            "rate": 1.0e-5,
        },
    },
    {
        "id": 6,
        "name": "同步-算力设备",
        "description": "时间同步算法 ↔ 专用算力设备",
        "source": "时间同步算法",
        "target": "专用算力设备",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "subtype": HardwareInterfaceSubtype.COMPUTING_HARDWARE,
        "protocol": "DMA",
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "DMA传输超时",
            "description": "DMA传输超时导致同步窗口失配",
            "rate": 2.6e-5,
        },
    },
    {
        "id": 7,
        "name": "配准-算力设备",
        "description": "空间配准算法 ↔ 专用算力设备",
        "source": "空间配准算法",
        "target": "专用算力设备",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "subtype": HardwareInterfaceSubtype.COMPUTING_HARDWARE,
        "protocol": "DMA",
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "缓存不一致",
            "description": "缓存不一致导致结果失效",
            "rate": 2.4e-5,
        },
    },
    {
        "id": 8,
        "name": "同步-配准",
        "description": "时间同步算法 → 空间配准算法",
        "source": "时间同步算法",
        "target": "空间配准算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "帧错配",
            "description": "时空窗口错位导致帧错配",
            "rate": 1.9e-5,
        },
    },
    {
        "id": 9,
        "name": "配准-感知",
        "description": "空间配准算法 → 环境感知算法",
        "source": "空间配准算法",
        "target": "环境感知算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "坐标系错标",
            "description": "坐标系标签错误",
            "rate": 2.1e-5,
        },
    },
    {
        "id": 10,
        "name": "配准-OS",
        "description": "空间配准算法 ↔ 嵌入式OS",
        "source": "空间配准算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.RESOURCE_EXHAUSTION,
            "name": "环形缓冲溢出",
            "description": "环形缓冲溢出导致数据丢失",
            "rate": 1.4e-5,
        },
    },
    {
        "id": 11,
        "name": "配准-检测",
        "description": "空间配准算法 → 目标检测算法",
        "source": "空间配准算法",
        "target": "目标检测算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.CONFIGURATION_ERROR,
            "name": "分辨率错配",
            "description": "分辨率/步幅错配导致输入失效",
            "rate": 2.0e-5,
        },
    },
    {
        "id": 12,
        "name": "检测-OS",
        "description": "目标检测算法 ↔ 嵌入式OS",
        "source": "目标检测算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.RESOURCE_EXHAUSTION,
            "name": "推理进程OOM",
            "description": "推理进程因内存不足被终止",
            "rate": 2.7e-5,
        },
    },
    {
        "id": 13,
        "name": "检测-ML",
        "description": "目标检测算法 ↔ 机器学习框架",
        "source": "目标检测算法",
        "target": "机器学习框架",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_FRAMEWORK,
        "failure_mode": {
            "category": FailureMode.VERSION_INCOMPATIBILITY,
            "name": "模型版本不兼容",
            "description": "模型/算子版本不兼容",
            "rate": 1.8e-5,
        },
    },
    {
        "id": 14,
        "name": "检测-规划",
        "description": "目标检测算法 → 路径规划算法",
        "source": "目标检测算法",
        "target": "路径规划算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "目标ID跳变",
            "description": "目标ID跳变引起航迹震荡",
            "rate": 2.3e-5,
        },
    },
    {
        "id": 15,
        "name": "检测-云台",
        "description": "目标检测算法 → 摄像机云台",
        "source": "目标检测算法",
        "target": "摄像机云台",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "subtype": HardwareInterfaceSubtype.ACTUATOR,
        "failure_mode": {
            "category": FailureMode.COMMUNICATION_FAILURE,
            "name": "指向命令丢失",
            "description": "云台指向命令丢失",
            "rate": 1.7e-5,
        },
    },
    {
        "id": 16,
        "name": "数据存档",
        "description": "飞控任务应用软件 → 嵌入式OS",
        "source": "飞控任务应用软件",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_DATA_PLATFORM,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "阻塞I/O",
            "description": "阻塞I/O反压上游链路",
            "rate": 1.3e-5,
        },
    },
    {
        "id": 17,
        "name": "感知-OS",
        "description": "环境感知算法 ↔ 嵌入式OS",
        "source": "环境感知算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.RESOURCE_EXHAUSTION,
            "name": "线程池枯竭",
            "description": "线程池枯竭导致感知滞后",
            "rate": 2.5e-5,
        },
    },
    {
        "id": 18,
        "name": "感知-避障",
        "description": "环境感知算法 → 避障算法",
        "source": "环境感知算法",
        "target": "避障算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "时间窗越界",
            "description": "时间窗外数据被消费",
            "rate": 2.9e-5,
        },
    },
    {
        "id": 19,
        "name": "规划-OS",
        "description": "路径规划算法 ↔ 嵌入式OS",
        "source": "路径规划算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "定时器漂移",
            "description": "定时器漂移导致重规划窗口漂移",
            "rate": 2.2e-5,
        },
    },
    {
        "id": 20,
        "name": "规划-通信",
        "description": "路径规划算法 ↔ 通信模块",
        "source": "路径规划算法",
        "target": "通信模块",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "failure_mode": {
            "category": FailureMode.COMMUNICATION_FAILURE,
            "name": "报文分片丢失",
            "description": "报文分片丢失导致下行指令缺失",
            "rate": 2.0e-5,
        },
    },
    {
        "id": 21,
        "name": "规划-避障",
        "description": "路径规划算法 ↔ 避障算法",
        "source": "路径规划算法",
        "target": "避障算法",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "交互死锁",
            "description": "规划与避障交互死锁",
            "rate": 2.8e-5,
        },
    },
    {
        "id": 22,
        "name": "避障-ML",
        "description": "避障算法 ↔ 机器学习框架",
        "source": "避障算法",
        "target": "机器学习框架",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_FRAMEWORK,
        "failure_mode": {
            "category": FailureMode.HARDWARE_FAULT,
            "name": "GPU内核异常",
            "description": "GPU内核异常导致避障推理失败",
            "rate": 2.1e-5,
        },
    },
    {
        "id": 23,
        "name": "避障-OS",
        "description": "避障算法 ↔ 嵌入式OS",
        "source": "避障算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "周期漂移",
            "description": "周期漂移导致控制空洞",
            "rate": 2.3e-5,
        },
    },
    {
        "id": 24,
        "name": "航迹指令",
        "description": "避障算法 → 飞控控制算法",
        "source": "避障算法",
        "target": "飞控控制算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "指令NaN/Inf",
            "description": "航迹指令包含NaN/Inf",
            "rate": 3.0e-5,
        },
    },
    {
        "id": 25,
        "name": "飞控-通信",
        "description": "飞控控制算法 ↔ 通信模块",
        "source": "飞控控制算法",
        "target": "通信模块",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "心跳中断",
            "description": "飞控-通信心跳中断触发保护",
            "rate": 2.4e-5,
        },
    },
    {
        "id": 26,
        "name": "飞控指令",
        "description": "飞控控制算法 → 自驾仪",
        "source": "飞控控制算法",
        "target": "自驾仪",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_HARDWARE,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "串口黏包",
            "description": "串口黏包/超时导致指令失效",
            "rate": 2.5e-5,
        },
    },
    {
        "id": 27,
        "name": "自驾仪状态反馈",
        "description": "自驾仪 → 飞控控制算法",
        "source": "自驾仪",
        "target": "飞控控制算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.HARDWARE_HARDWARE,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "状态未更新",
            "description": "状态值未正确更新",
            "rate": 2.7e-5,
        },
    },
    {
        "id": 28,
        "name": "飞控算法-OS",
        "description": "飞控控制算法 ↔ 嵌入式OS",
        "source": "飞控控制算法",
        "target": "嵌入式OS",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_OS,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "看门狗漏触",
            "description": "抖动下看门狗漏触/误触",
            "rate": 1.9e-5,
        },
    },
    {
        "id": 29,
        "name": "位姿反馈",
        "description": "自驾仪 → 空间配准算法",
        "source": "自驾仪",
        "target": "空间配准算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.HARDWARE_HARDWARE,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "姿态突变",
            "description": "姿态突变（跳变）",
            "rate": 2.6e-5,
        },
    },
    {
        "id": 30,
        "name": "自驾仪-执行器",
        "description": "自驾仪 ↔ 执行器",
        "source": "自驾仪",
        "target": "执行器",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.HARDWARE_HARDWARE,
        "subtype": HardwareInterfaceSubtype.ACTUATOR,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "总线饱和",
            "description": "总线饱和导致回授丢失",
            "rate": 3.1e-5,
        },
    },
    {
        "id": 31,
        "name": "无人机-地面站链路",
        "description": "通信模块 ↔ 地面站",
        "source": "通信模块",
        "target": "地面站",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.ALGORITHM_DATA_PLATFORM,
        "failure_mode": {
            "category": FailureMode.COMMUNICATION_FAILURE,
            "name": "链路干扰",
            "description": "干扰致BER升高与丢包",
            "rate": 2.8e-5,
        },
    },
    {
        "id": 32,
        "name": "冗余感知仲裁",
        "description": "空间配准算法 → 多模态感知冗余管理",
        "source": "空间配准算法",
        "target": "多模态感知冗余管理",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.CONFIGURATION_ERROR,
            "name": "冗余策略失效",
            "description": "冗余仲裁逻辑配置错误",
            "rate": 1.2e-5,
        },
    },
    {
        "id": 33,
        "name": "冗余输出-检测",
        "description": "多模态感知冗余管理 → 目标检测算法",
        "source": "多模态感知冗余管理",
        "target": "目标检测算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "冗余输出漂移",
            "description": "冗余仲裁输出漂移导致检测输入异常",
            "rate": 1.1e-5,
        },
    },
    {
        "id": 34,
        "name": "冗余输出-感知",
        "description": "多模态感知冗余管理 → 环境感知算法",
        "source": "多模态感知冗余管理",
        "target": "环境感知算法",
        "direction": InterfaceDirection.OUTPUT,
        "type": InterfaceType.ALGORITHM_APPLICATION,
        "failure_mode": {
            "category": FailureMode.DATA_CORRUPTION,
            "name": "冗余输出不一致",
            "description": "冗余输出不一致导致环境感知失效",
            "rate": 1.15e-5,
        },
    },
    {
        "id": 35,
        "name": "通信心跳监测",
        "description": "通信模块 ↔ 通信链路健康管理",
        "source": "通信模块",
        "target": "通信链路健康管理",
        "direction": InterfaceDirection.BIDIRECTIONAL,
        "type": InterfaceType.SOFTWARE_HARDWARE,
        "failure_mode": {
            "category": FailureMode.TIMEOUT,
            "name": "心跳判决失效",
            "description": "链路健康监测错判导致切换失败",
            "rate": 1.6e-5,
        },
    },
]


# ---------------------------------------------------------------------------
# 系统结构创建
# ---------------------------------------------------------------------------


def build_modules(system: SystemStructure) -> Dict[str, Module]:
    """根据模块规格表创建系统模块。"""

    module_map: Dict[str, Module] = {}

    for spec in MODULE_SPECS:
        module = Module(spec["name"], spec["description"], spec["type"])
        module.template = spec.get("template")
        module.parameters = spec.get("parameters", {}).copy()
        module.failure_rate = spec.get("failure_rate", 1e-5)
        pos_x, pos_y = spec.get("position", (0, 0))
        module.position = {"x": pos_x, "y": pos_y}
        system.add_module(module)
        module_map[module.name] = module

    print(f"✓ 已创建 {len(module_map)} 个模块")
    return module_map


def build_interfaces(system: SystemStructure, module_map: Dict[str, Module]) -> Dict[int, Interface]:
    """根据接口规格表创建接口并挂接到模块。"""

    interface_map: Dict[int, Interface] = {}

    for spec in INTERFACE_SPECS:
        source_module = module_map[spec["source"]]
        target_module = module_map[spec["target"]]
        interface_name = f"接口#{spec['id']} {spec['name']}"

        interface = Interface(
            interface_name,
            spec["description"],
            interface_type=spec.get("type", InterfaceType.SOFTWARE_HARDWARE),
            direction=spec.get("direction", InterfaceDirection.BIDIRECTIONAL),
        )
        interface.protocol = spec.get("protocol", "")
        interface.source_module_id = source_module.id
        interface.target_module_id = target_module.id
        interface.parameters.update(spec.get("parameters", {}))
        if spec.get("subtype"):
            interface.subtype = spec["subtype"]

        failure_spec = spec.get("failure_mode", {})
        failure_mode = InterfaceFailureMode(
            failure_spec.get("category", FailureMode.COMMUNICATION_FAILURE),
            failure_spec.get("name", "接口失效"),
        )
        failure_mode.id = f"fm_{spec['id']}"
        failure_mode.description = failure_spec.get("description", "")
        failure_mode.occurrence_rate = failure_spec.get("rate", 1e-5)
        failure_mode.failure_rate = failure_spec.get("rate", 1e-5)
        failure_mode.severity = failure_spec.get("severity", 3)
        failure_mode.enabled = True
        interface.add_failure_mode(failure_mode)

        system.add_interface(interface)
        source_module.add_interface(interface)
        target_module.add_interface(interface)
        interface_map[spec["id"]] = interface

    print(f"✓ 已创建 {len(interface_map)} 条接口")
    return interface_map


def _extract_xy(position) -> Tuple[float, float]:
    """统一提取模块坐标。"""

    if isinstance(position, dict):
        return float(position.get("x", 0.0)), float(position.get("y", 0.0))
    return float(getattr(position, "x", 0.0)), float(getattr(position, "y", 0.0))


def _module_center(module: Module) -> Tuple[float, float]:
    """估算模块的中心点，便于生成折线路径。"""

    x, y = _extract_xy(module.position)
    return x + MODULE_WIDTH / 2.0, y + MODULE_HEIGHT / 2.0


def _route_connection(
    source_module: Module,
    target_module: Module,
) -> List[Tuple[float, float]]:
    """生成带有避让的折线控制点，避免连线穿过模块。"""

    sx, sy = _module_center(source_module)
    tx, ty = _module_center(target_module)

    points: List[Tuple[float, float]] = [(sx, sy)]

    if abs(sx - tx) < 1e-3:
        # 同列：向上/下偏移，再对齐
        vertical_dir = 1.0 if ty >= sy else -1.0
        offset_y = sy + vertical_dir * (MODULE_HEIGHT / 2.0 + VERTICAL_MARGIN)
        points.append((sx, offset_y))
        points.append((tx, offset_y))
    else:
        horizontal_dir = 1.0 if tx >= sx else -1.0
        exit_x = sx + horizontal_dir * (MODULE_WIDTH / 2.0 + HORIZONTAL_MARGIN)
        entry_x = tx - horizontal_dir * (MODULE_WIDTH / 2.0 + HORIZONTAL_MARGIN)

        # 如果存在交叉，采用中间列绕行
        if (horizontal_dir > 0 and exit_x > entry_x) or (
            horizontal_dir < 0 and exit_x < entry_x
        ):
            mid_x = (sx + tx) / 2.0
            exit_x = entry_x = mid_x

        points.append((exit_x, sy))
        points.append((exit_x, ty))

    points.append((tx, ty))

    # 去除重复点
    simplified: List[Tuple[float, float]] = []
    for px, py in points:
        if not simplified or (px, py) != simplified[-1]:
            simplified.append((px, py))

    return simplified


def build_connections(
    system: SystemStructure,
    module_map: Dict[str, Module],
    interface_map: Dict[int, Interface],
) -> None:
    """为系统模块创建连接关系。"""

    for spec in INTERFACE_SPECS:
        interface = interface_map[spec["id"]]
        source_module = module_map[spec["source"]]
        target_module = module_map[spec["target"]]

        connection = Connection(
            id=f"connection_{spec['id']}",
            source_module_id=source_module.id,
            target_module_id=target_module.id,
            source_point_id=interface.id,
            target_point_id=interface.id,
        )
        connection.interface_id = interface.id
        connection.name = f"{source_module.name}→{target_module.name}({interface.name})"

        routed_points = _route_connection(source_module, target_module)
        if len(routed_points) > 2:
            intermediates = routed_points[1:-1]
        else:
            intermediates = routed_points[1:]

        connection.connection_points = [Point(x, y) for x, y in intermediates]
        source_position = source_module.position
        target_position = target_module.position

        sx = source_position["x"] if isinstance(source_position, dict) else source_position.x
        sy = source_position["y"] if isinstance(source_position, dict) else source_position.y
        tx = target_position["x"] if isinstance(target_position, dict) else target_position.x
        ty = target_position["y"] if isinstance(target_position, dict) else target_position.y

        offset = 120 if sx <= tx else -40
        connection.connection_points = [
            Point(sx + offset, sy + 30),
            Point(tx, ty + 30),
        ]

        system.add_connection(connection)

    print(f"✓ 已建立 {len(system.connections)} 条连接")


# ---------------------------------------------------------------------------
# 任务剖面
# ---------------------------------------------------------------------------


def _create_phase(
    phase_info: Tuple[str, str, float, List[int]],
    interface_map: Dict[int, Interface],
) -> TaskPhase:
    name, description, duration_min, interface_ids = phase_info
    phase = TaskPhase(name)
    phase.description = description
    phase.duration = duration_min * 60.0
    critical_interfaces = [
        interface_map[idx].id for idx in interface_ids if idx in interface_map
    ]
    phase.parameters["critical_interfaces"] = critical_interfaces
    phase.parameters["critical_interface_names"] = [
        interface_map[idx].name for idx in interface_ids if idx in interface_map
    ]
    phase.parameters["duration_minutes"] = duration_min
    phase.critical_interfaces = [
        interface_map[idx].id for idx in interface_ids if idx in interface_map
    ]
    return phase


def _add_success_criteria(
    task: TaskProfile,
    module: Module,
    name: str,
    parameter: str,
    operator: ComparisonOperator,
    target_value: float,
    description: str,
    weight: float = 1.0,
    criteria_type: SuccessCriteriaType = SuccessCriteriaType.MODULE_OUTPUT,
) -> None:
    criteria = SuccessCriteria(name)
    criteria.description = description
    criteria.module_id = module.id
    criteria.parameter_name = parameter
    criteria.operator = operator
    criteria.target_value = target_value
    criteria.weight = weight
    criteria.criteria_type = criteria_type
    task.add_success_criteria(criteria)


def create_task_profiles(
    system: SystemStructure,
    module_map: Dict[str, Module],
    interface_map: Dict[int, Interface],
) -> Dict[str, TaskProfile]:
    """创建抵近侦察与物资投放两个任务剖面。"""

    task_profiles: Dict[str, TaskProfile] = {}

    # ----------------------------- 抵近侦察任务 ----------------------------
    recon_task = TaskProfile("抵近侦察任务", "目标识别、保持安全距离并按时脱离返航")
    recon_task.mission_type = "reconnaissance"

    recon_phases = [
        (
            "R1 上电与联合对时",
            "设备自检、GNSS锁定、跨源对时与配准初始化",
            1.5,
            [1, 2, 5, 8, 10, 27],
        ),
        (
            "R2 起飞与进入任务空域",
            "解锁起飞、姿态/位置闭环、进场通报",
            3.5,
            [24, 26, 27, 28, 30, 25, 31],
        ),
        (
            "R3 抵近指向与目标识别",
            "多模态采集、同步配准、检测与云台指向稳定",
            10.0,
            [3, 4, 5, 8, 11, 12, 13, 14, 15, 27, 28, 32, 33],
        ),
        (
            "R4 脱离与返航",
            "航迹重构、空域通报与返航执行",
            5.5,
            [19, 21, 24, 26, 27, 28, 30, 20, 25, 31, 35],
        ),
        (
            "R5 进近与着陆",
            "自动进近、姿态控制与落地",
            3.5,
            [24, 26, 27, 28, 30, 25, 31, 35],
        ),
    ]

    start_time = 0.0
    for phase_info in recon_phases:
        phase = _create_phase(phase_info, interface_map)
        phase.start_time = start_time
        recon_task.add_task_phase(phase)
        start_time += phase.duration

    recon_task.total_duration = start_time

    _add_success_criteria(
        recon_task,
        module_map["时间同步算法"],
        "R1-跨源时间对齐",
        "time_alignment_error_ms",
        ComparisonOperator.LESS_EQUAL,
        5.0,
        "跨源时间对齐误差≤±5 ms",
        weight=1.5,
    )
    _add_success_criteria(
        recon_task,
        module_map["自驾仪"],
        "R1-状态输出连续",
        "state_stream_rate_hz",
        ComparisonOperator.GREATER_EQUAL,
        50.0,
        "自驾仪状态输出频率≥50 Hz",
    )
    _add_success_criteria(
        recon_task,
        module_map["飞控控制算法"],
        "R2-姿态闭环稳定",
        "attitude_stability_index",
        ComparisonOperator.GREATER_EQUAL,
        0.95,
        "姿态闭环稳定性指标≥0.95",
        weight=1.8,
    )
    _add_success_criteria(
        recon_task,
        module_map["飞控控制算法"],
        "R2-升限误差",
        "altitude_error_m",
        ComparisonOperator.LESS_EQUAL,
        2.0,
        "升限（航高）误差在±2 m以内",
    )
    _add_success_criteria(
        recon_task,
        module_map["通信链路健康管理"],
        "R2-心跳连续",
        "heartbeat_loss_ratio",
        ComparisonOperator.LESS_EQUAL,
        0.01,
        "与地面站心跳连接连续",
    )
    _add_success_criteria(
        recon_task,
        module_map["光电红外摄像机"],
        "R3-有效帧率",
        "effective_fps",
        ComparisonOperator.GREATER_EQUAL,
        15.0,
        "有效图像帧率不低于15 FPS",
        weight=1.4,
    )
    _add_success_criteria(
        recon_task,
        module_map["目标检测算法"],
        "R3-检测概率",
        "detection_probability",
        ComparisonOperator.GREATER_EQUAL,
        0.90,
        "检测概率Pd≥0.90",
        weight=1.4,
    )
    _add_success_criteria(
        recon_task,
        module_map["摄像机云台"],
        "R3-指向误差",
        "pointing_error_deg",
        ComparisonOperator.LESS_EQUAL,
        1.0,
        "云台指向误差≤1.0°",
    )
    _add_success_criteria(
        recon_task,
        module_map["路径规划算法"],
        "R4-航迹均方误差",
        "track_rmse_m",
        ComparisonOperator.LESS_EQUAL,
        10.0,
        "航迹跟踪均方误差≤10 m",
    )
    _add_success_criteria(
        recon_task,
        module_map["通信模块"],
        "R4-通信可用率",
        "availability",
        ComparisonOperator.GREATER_EQUAL,
        0.98,
        "返航阶段通信可用率≥0.98",
    )
    _add_success_criteria(
        recon_task,
        module_map["自驾仪"],
        "R5-进近落地速度",
        "landing_ground_speed_ms",
        ComparisonOperator.LESS_EQUAL,
        1.0,
        "接地瞬时地速≤1 m/s",
        weight=1.6,
    )

    system.add_task_profile(recon_task)
    task_profiles[recon_task.name] = recon_task

    # ----------------------------- 物资投放任务 ----------------------------
    delivery_task = TaskProfile("物资投放任务", "复杂环境穿越、动态重规划与投放执行")
    delivery_task.mission_type = "supply_delivery"

    delivery_phases = [
        (
            "D1 上电与联合对时",
            "自检、对时、配准初始化",
            1.5,
            [1, 2, 5, 8, 10, 27],
        ),
        (
            "D2 起飞与入口汇合",
            "起飞、到达入口并保持通信",
            5.0,
            [24, 26, 27, 28, 30, 25, 31, 35],
        ),
        (
            "D3 复杂环境穿越",
            "多模态感知建图、避障介入与快速重规划",
            14.0,
            [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 19, 21, 22, 23, 24, 27, 28, 32, 33, 34],
        ),
        (
            "D4 投放窗口定位",
            "投放点定位、航迹微调、释放执行",
            2.0,
            [3, 5, 8, 11, 12, 13, 14, 24, 26, 27, 28, 30],
        ),
        (
            "D5 脱离返航与着陆",
            "脱离、返航与着陆",
            5.5,
            [19, 21, 24, 26, 27, 28, 30, 20, 25, 31, 35],
        ),
    ]

    start_time = 0.0
    for phase_info in delivery_phases:
        phase = _create_phase(phase_info, interface_map)
        phase.start_time = start_time
        delivery_task.add_task_phase(phase)
        start_time += phase.duration

    delivery_task.total_duration = start_time

    _add_success_criteria(
        delivery_task,
        module_map["时间同步算法"],
        "D1-对时误差",
        "time_alignment_error_ms",
        ComparisonOperator.LESS_EQUAL,
        5.0,
        "对时误差≤±5 ms",
        weight=1.2,
    )
    _add_success_criteria(
        delivery_task,
        module_map["空间配准算法"],
        "D1-配准缓存",
        "buffer_overflow",
        ComparisonOperator.EQUAL,
        0.0,
        "配准初始化完成且缓存无溢出",
    )
    _add_success_criteria(
        delivery_task,
        module_map["路径规划算法"],
        "D2-入口汇合",
        "entry_position_error_m",
        ComparisonOperator.LESS_EQUAL,
        10.0,
        "入口汇合误差≤10 m",
    )
    _add_success_criteria(
        delivery_task,
        module_map["通信链路健康管理"],
        "D2-强制通信链",
        "heartbeat_loss_ratio",
        ComparisonOperator.LESS_EQUAL,
        0.005,
        "强制通信链保持心跳",
    )
    _add_success_criteria(
        delivery_task,
        module_map["光电红外摄像机"],
        "D3-图像帧率",
        "effective_fps",
        ComparisonOperator.GREATER_EQUAL,
        15.0,
        "图像帧率≥15 FPS",
        weight=1.3,
    )
    _add_success_criteria(
        delivery_task,
        module_map["毫米波雷达"],
        "D3-点云有效率",
        "valid_ratio",
        ComparisonOperator.GREATER_EQUAL,
        0.90,
        "点云数据有效率≥90%",
        weight=1.3,
    )
    _add_success_criteria(
        delivery_task,
        module_map["路径规划算法"],
        "D3-重规划周期",
        "replan_cycle_s",
        ComparisonOperator.LESS_EQUAL,
        0.30,
        "重规划周期≤0.30 s",
        weight=1.6,
    )
    _add_success_criteria(
        delivery_task,
        module_map["避障算法"],
        "D3-侧向安全裕度",
        "lateral_margin_m",
        ComparisonOperator.GREATER_EQUAL,
        4.0,
        "最小侧向安全裕度≥4 m",
    )
    _add_success_criteria(
        delivery_task,
        module_map["目标检测算法"],
        "D4-投放点定位",
        "drop_position_error_m",
        ComparisonOperator.LESS_EQUAL,
        3.0,
        "投放点定位误差≤3 m",
        weight=1.5,
    )
    _add_success_criteria(
        delivery_task,
        module_map["飞控控制算法"],
        "D4-释放高度",
        "release_altitude_error_m",
        ComparisonOperator.LESS_EQUAL,
        2.0,
        "释放高度偏差≤±2 m",
    )
    _add_success_criteria(
        delivery_task,
        module_map["通信模块"],
        "D5-通信可用率",
        "availability",
        ComparisonOperator.GREATER_EQUAL,
        0.98,
        "返航通信可用率≥0.98",
    )
    _add_success_criteria(
        delivery_task,
        module_map["自驾仪"],
        "D5-落地速度",
        "landing_ground_speed_ms",
        ComparisonOperator.LESS_EQUAL,
        1.0,
        "接地瞬时地速≤1 m/s",
        weight=1.6,
    )

    system.add_task_profile(delivery_task)
    task_profiles[delivery_task.name] = delivery_task

    if not system.current_task_profile_id:
        system.current_task_profile_id = recon_task.id

    print(f"✓ 已创建 {len(task_profiles)} 个任务剖面")
    return task_profiles


# ---------------------------------------------------------------------------
# 环境模型
# ---------------------------------------------------------------------------


def create_environment_models(system: SystemStructure, module_map: Dict[str, Module]) -> None:
    weather_env = EnvironmentModule("恶劣天气环境", "强风/降雨等天气应力")
    weather_env.environment_type = EnvironmentType.WEATHER
    weather_env.position = {"x": 60, "y": 40}

    wind = StressFactor("风速扰动")
    wind.stress_type = StressType.CUSTOM
    wind.description = "阵风引起的侧向干扰"
    wind.base_value = 12.0
    wind.variation_range = 18.0
    wind.distribution = "gust"
    wind.time_profile = "random"
    wind.duration = 3600.0
    weather_env.add_stress_factor(wind)

    rain = StressFactor("降雨强度")
    rain.stress_type = StressType.CUSTOM
    rain.description = "降雨造成的光学衰减"
    rain.base_value = 6.0
    rain.variation_range = 10.0
    rain.distribution = "exponential"
    rain.time_profile = "linear"
    rain.duration = 2400.0
    weather_env.add_stress_factor(rain)

    weather_env.affected_modules = [
        module_map["光电红外摄像机"].id,
        module_map["通信模块"].id,
        module_map["毫米波雷达"].id,
    ]

    emi_env = EnvironmentModule("电磁干扰环境", "电磁场干扰通信与导航")
    emi_env.environment_type = EnvironmentType.ELECTROMAGNETIC
    emi_env.position = {"x": 260, "y": 40}

    emi = StressFactor("电磁场强度")
    emi.stress_type = StressType.ELECTROMAGNETIC
    emi.description = "复杂电磁环境干扰"
    emi.base_value = 5.5
    emi.variation_range = 3.0
    emi.distribution = "uniform"
    emi.time_profile = "sinusoidal"
    emi.parameters = {"frequency": 0.2}
    emi.duration = 3600.0
    emi_env.add_stress_factor(emi)

    emi_env.affected_modules = [
        module_map["全球定位模块"].id,
        module_map["通信模块"].id,
        module_map["通信链路健康管理"].id,
    ]

    thermal_env = EnvironmentModule("高温环境", "高温对电子设备的影响")
    thermal_env.environment_type = EnvironmentType.THERMAL
    thermal_env.position = {"x": 460, "y": 40}

    temp = StressFactor("环境温度")
    temp.stress_type = StressType.TEMPERATURE
    temp.description = "机身受日照导致的高温"
    temp.base_value = 48.0
    temp.variation_range = 12.0
    temp.distribution = "normal"
    temp.time_profile = "sinusoidal"
    temp.parameters = {"frequency": 0.03}
    temp.duration = 5400.0
    thermal_env.add_stress_factor(temp)

    thermal_env.affected_modules = [
        module_map["专用算力设备"].id,
        module_map["飞控任务应用软件"].id,
        module_map["避障算法"].id,
    ]

    system.add_environment_model(weather_env)
    system.add_environment_model(emi_env)
    system.add_environment_model(thermal_env)

    print(f"✓ 已配置 {len(system.environment_models)} 个环境模型")


# ---------------------------------------------------------------------------
# 故障树分析
# ---------------------------------------------------------------------------


def apply_redundancy_logic(fault_tree, task_name: str) -> None:
    """在故障树中注入冗余逻辑，确保存在组合最小割集。"""

    if "抵近侦察" not in task_name:
        return

    try:
        detection_event = next(
            event
            for event in fault_tree.events.values()
            if event.name == "目标检测算法失效"
        )
    except StopIteration:
        return

    detection_gate = next(
        (gate for gate in fault_tree.gates.values() if gate.output_event_id == detection_event.id),
        None,
    )
    if detection_gate is None:
        return

    sensor_event_groups = {"3": [], "4": []}
    for event in fault_tree.events.values():
        if event.name.startswith("接口#3") and "高负载丢帧" in event.name:
            sensor_event_groups["3"].append(event.id)
        elif event.name.startswith("接口#4") and "UDP分片丢包" in event.name:
            sensor_event_groups["4"].append(event.id)

    if not sensor_event_groups["3"] or not sensor_event_groups["4"]:
        return

    representative_ids = [
        sensor_event_groups["3"][0],
        sensor_event_groups["4"][0],
    ]
    removal_ids = sensor_event_groups["3"] + sensor_event_groups["4"]

    # 若传感器事件已直接接入检测门，先移除
    detection_gate.input_events = [
        eid for eid in detection_gate.input_events if eid not in removal_ids
    ]

    from src.models.fault_tree_model import FaultTreeEvent, FaultTreeGate, EventType, GateType

    combined_event = FaultTreeEvent(
        "多模态感知链路失效",
        event_type=EventType.INTERMEDIATE_EVENT,
    )
    combined_event.description = "光电与雷达链路同时退化导致检测输入中断"
    fault_tree.add_event(combined_event)

    and_gate = FaultTreeGate("多模态感知冗余门", GateType.AND)
    and_gate.output_event_id = combined_event.id
    and_gate.input_events = representative_ids
    fault_tree.add_gate(and_gate)

    detection_gate.input_events.append(combined_event.id)

    # 确保传感器事件仅通过冗余门传播
    for gate in fault_tree.gates.values():
        if gate.id == and_gate.id:
            continue
        if any(eid in removal_ids for eid in gate.input_events):
            gate.input_events = [
                eid for eid in gate.input_events if eid not in removal_ids
            ]


def run_fault_tree_analyses(system: SystemStructure) -> Dict[str, object]:
    """对系统的所有任务剖面执行故障树分析。"""

    fault_trees: Dict[str, object] = {}
    generator = FaultTreeGenerator()

    for task in system.task_profiles.values():
        print(f"生成任务[{task.name}]的故障树...")
        fault_tree = generator.generate_fault_tree(system, task)
        apply_redundancy_logic(fault_tree, task.name)
        cut_sets = fault_tree.find_minimal_cut_sets()
        system_prob = fault_tree.calculate_system_probability()
        fault_tree.calculate_importance_measures()

        print(
            f"✓ {task.name} 故障树生成成功: 事件{len(fault_tree.events)}个, 逻辑门{len(fault_tree.gates)}个, "
            f"最小割集{len(cut_sets)}个, 系统失效概率≈{system_prob:.2e}"
        )

        if cut_sets:
            print("  Top 5 最小割集:")
            for idx, cut_set in enumerate(cut_sets[:5], start=1):
                event_labels = [
                    fault_tree.events[eid].name
                    for eid in cut_set.events
                    if eid in fault_tree.events
                ]
                print(f"    {idx}. {', '.join(event_labels)} (P≈{cut_set.probability:.2e})")

        fault_trees[task.name] = fault_tree

    return fault_trees


# ---------------------------------------------------------------------------
# 项目保存与报告
# ---------------------------------------------------------------------------


        print(
            f"✓ {task.name} 故障树生成成功: 事件{len(fault_tree.events)}个, 逻辑门{len(fault_tree.gates)}个, "
            f"最小割集{len(cut_sets)}个, 系统失效概率≈{system_prob:.2e}"
        )

        if cut_sets:
            print("  Top 5 最小割集:")
            for idx, cut_set in enumerate(cut_sets[:5], start=1):
                event_labels = [
                    fault_tree.events[eid].name
                    for eid in cut_set.events
                    if eid in fault_tree.events
                ]
                print(f"    {idx}. {', '.join(event_labels)} (P≈{cut_set.probability:.2e})")

        fault_trees[task.name] = fault_tree

    return fault_trees


# ---------------------------------------------------------------------------
# 项目保存与报告
# ---------------------------------------------------------------------------


def generate_demo_report(
    system: SystemStructure,
    fault_trees: Dict[str, object],
    report_path: str,
) -> None:
    """生成文本报告，总结系统结构与两个任务的分析结果。"""

    with open(report_path, "w", encoding="utf-8") as report:
        report.write("无人机智能系统接口故障分析演示报告\n")
        report.write("=" * 70 + "\n\n")
        report.write(f"系统名称: {system.name}\n")
        report.write(f"系统描述: {system.description}\n")
        report.write(f"模块数量: {len(system.modules)}\n")
        report.write(f"接口数量: {len(system.interfaces)}\n")
        report.write(f"任务剖面数量: {len(system.task_profiles)}\n")
        report.write(f"环境模型数量: {len(system.environment_models)}\n\n")

        report.write("1. 系统模块列表\n")
        for module in system.modules.values():
            report.write(
                f"- {module.name} ({module.module_type.value}): {module.description}, 失效率≈{getattr(module, 'failure_rate', 1e-5):.2e}\n"
            )
        report.write("\n")

        report.write("2. 接口与失效模式\n")
        for interface in system.interfaces.values():
            report.write(f"- {interface.name}: {interface.description}\n")
            for failure in interface.failure_modes:
                report.write(
                    f"    • 失效模式: {failure.name}, 描述: {failure.description}, λ≈{failure.failure_rate:.2e}\n"
                )
        report.write("\n")

        report.write("3. 任务剖面概述\n")
        for task in system.task_profiles.values():
            report.write(f"- {task.name}: {task.description}\n")
            report.write(f"  总时长: {task.total_duration / 60:.1f} min\n")
            report.write(f"  成功判据数量: {len(task.success_criteria)}\n")
            report.write(f"  阶段数量: {len(task.task_phases)}\n")
        report.write("\n")

        report.write("4. 故障树分析结果\n")
        for task_name, fault_tree in fault_trees.items():
            report.write(f"- {task_name} 故障树\n")
            report.write(f"  事件数: {len(fault_tree.events)}, 逻辑门数: {len(fault_tree.gates)}\n")
            report.write(f"  最小割集数: {len(fault_tree.minimal_cut_sets)}\n")
            report.write(f"  系统失效概率: {fault_tree.system_probability:.2e}\n")
            report.write(f"  系统可靠度: {1.0 - fault_tree.system_probability:.6f}\n")

            if fault_tree.minimal_cut_sets:
                report.write("  代表性最小割集:\n")
                for cut_set in fault_tree.minimal_cut_sets[:5]:
                    labels = [
                        fault_tree.events[event_id].name
                        for event_id in cut_set.events
                        if event_id in fault_tree.events
                    ]
                    report.write(
                        f"    • {', '.join(labels)} (P≈{cut_set.probability:.2e})\n"
                    )
            report.write("\n")

        report.write("演示报告生成完成。\n")


def save_demo_project(system: SystemStructure, fault_trees: Dict[str, object]) -> bool:
    project_path = "./demo_projects/drone_system_demo.json"
    os.makedirs(os.path.dirname(project_path), exist_ok=True)

    pm = ProjectManager()
    pm.set_current_system(system)

    success = pm.save_project_as(project_path)
    if not success:
        print("✗ 项目保存失败")
        return False

    print(f"✓ 项目已保存到 {project_path}")
    report_path = "./demo_projects/drone_system_report.txt"
    generate_demo_report(system, fault_trees, report_path)
    print(f"✓ 分析报告已生成: {report_path}")
    return True


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def create_drone_system_demo() -> Tuple[SystemStructure, Dict[str, object]]:
    system = SystemStructure(
        "无人机智能任务系统",
        "基于多源传感融合的无人机任务执行与接口故障机理演示",
    )

    module_map = build_modules(system)
    interface_map = build_interfaces(system, module_map)
    build_connections(system, module_map, interface_map)
    create_task_profiles(system, module_map, interface_map)
    create_environment_models(system, module_map)

    fault_trees = run_fault_tree_analyses(system)
    return system, fault_trees


def main() -> bool:
    print("无人机智能系统任务可靠性分析演示")
    print("=" * 70)

    try:
        system, fault_trees = create_drone_system_demo()
        if save_demo_project(system, fault_trees):
            print("\n演示摘要:")
            print("- 系统模块: {}".format(len(system.modules)))
            print("- 接口数量: {}".format(len(system.interfaces)))
            print("- 任务剖面: {}".format(len(system.task_profiles)))
            print("- 环境模型: {}".format(len(system.environment_models)))
            print("- 生成故障树: {}".format(len(fault_trees)))
            print("- 项目文件: demo_projects/drone_system_demo.json")
            print("- 分析报告: demo_projects/drone_system_report.txt")
            return True
        return False
    except Exception as exc:  # pragma: no cover - 便于诊断
        print(f"✗ 演示过程发生异常: {exc}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
