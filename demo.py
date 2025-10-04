#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接口故障机理分析原型系统 - 功能演示脚本
"""

import sys
import os
import json
from datetime import datetime

# 添加src目录到路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

try:
    from models.module_model import HardwareModule, SoftwareModule, AlgorithmModule
    from models.interface_model import Interface, InterfaceType, FailureMode
    from models.system_model import SystemStructure, Connection
    from core.project_manager import ProjectManager
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"当前路径: {os.getcwd()}")
    print(f"src路径: {src_path}")
    print(f"src路径存在: {os.path.exists(src_path)}")
    if os.path.exists(src_path):
        print(f"src目录内容: {os.listdir(src_path)}")
    sys.exit(1)

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """打印章节标题"""
    print(f"\n--- {title} ---")

def demo_module_modeling():
    """演示模块建模功能"""
    print_header("模块建模功能演示")
    
    # 创建硬件模块
    print_section("1. 创建硬件模块")
    camera = HardwareModule(
        id="camera_001",
        name="前置摄像头",
        description="用于环境感知的前置摄像头模块",
        position=(100, 100),
        icon_path="icons/camera.png"
    )
    
    # 添加接口点
    camera.add_interface_point("data_out", (50, 0), "数据输出接口")
    camera.add_interface_point("power_in", (0, 25), "电源输入接口")
    camera.add_interface_point("control_in", (0, 50), "控制信号输入接口")
    
    # 设置Python代码模型
    camera.set_python_code("""
# 摄像头模块工作原理
def process_frame():
    # 图像采集
    frame = capture_image()
    
    # 图像预处理
    processed_frame = preprocess(frame)
    
    # 输出数据
    return processed_frame

def handle_control_signal(signal):
    # 处理控制信号
    if signal == 'start':
        start_capture()
    elif signal == 'stop':
        stop_capture()
""")
    
    print(f"创建硬件模块: {camera.name}")
    print(f"  - ID: {camera.id}")
    print(f"  - 类型: {camera.module_type}")
    print(f"  - 接口点数量: {len(camera.interface_points)}")
    print(f"  - 代码行数: {len(camera.python_code.split('\\n'))}")
    
    # 创建软件模块
    print_section("2. 创建软件模块")
    image_processor = SoftwareModule(
        id="img_proc_001",
        name="图像处理模块",
        description="负责图像处理和特征提取的软件模块",
        position=(300, 100)
    )
    
    image_processor.add_interface_point("image_in", (0, 25), "图像输入接口")
    image_processor.add_interface_point("features_out", (50, 25), "特征输出接口")
    
    image_processor.set_python_code("""
import cv2
import numpy as np

def extract_features(image):
    # 特征提取算法
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    features = cv2.goodFeaturesToTrack(gray, 100, 0.01, 10)
    return features

def process_image(image):
    # 图像处理流程
    features = extract_features(image)
    return {
        'features': features,
        'timestamp': time.time()
    }
""")
    
    print(f"创建软件模块: {image_processor.name}")
    print(f"  - ID: {image_processor.id}")
    print(f"  - 类型: {image_processor.module_type}")
    
    # 创建算法模块
    print_section("3. 创建算法模块")
    object_detector = AlgorithmModule(
        id="obj_det_001",
        name="目标检测算法",
        description="基于深度学习的目标检测算法模块",
        position=(500, 100)
    )
    
    object_detector.add_interface_point("features_in", (0, 25), "特征输入接口")
    object_detector.add_interface_point("detections_out", (50, 25), "检测结果输出接口")
    
    object_detector.set_python_code("""
import torch
import torchvision

class ObjectDetector:
    def __init__(self):
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
        self.model.eval()
    
    def detect_objects(self, features):
        # 目标检测推理
        with torch.no_grad():
            predictions = self.model(features)
        
        return self.post_process(predictions)
    
    def post_process(self, predictions):
        # 后处理
        boxes = predictions[0]['boxes']
        scores = predictions[0]['scores']
        labels = predictions[0]['labels']
        
        return {
            'boxes': boxes.cpu().numpy(),
            'scores': scores.cpu().numpy(),
            'labels': labels.cpu().numpy()
        }
""")
    
    print(f"创建算法模块: {object_detector.name}")
    print(f"  - ID: {object_detector.id}")
    print(f"  - 类型: {object_detector.module_type}")
    
    return [camera, image_processor, object_detector]

def demo_interface_modeling():
    """演示接口建模功能"""
    print_header("接口建模功能演示")
    
    # 创建算法-操作系统接口
    print_section("1. 算法-操作系统接口")
    algo_os_interface = Interface(
        id="algo_os_001",
        name="算法-操作系统内存接口",
        interface_type=InterfaceType.ALGORITHM_OS,
        description="算法模块与操作系统之间的内存管理接口"
    )
    
    # 添加失效模式
    memory_leak = FailureMode(
        id="mem_leak_001",
        name="内存泄漏",
        description="算法模块未正确释放内存导致的内存泄漏",
        trigger_conditions=["长时间运行", "大量数据处理", "异常退出"],
        failure_rate=0.001,
        python_code="""
def simulate_memory_leak():
    # 模拟内存泄漏
    memory_usage = get_memory_usage()
    
    if memory_usage > MEMORY_THRESHOLD:
        return True  # 触发内存泄漏故障
    
    # 检查内存增长趋势
    if memory_growth_rate() > MAX_GROWTH_RATE:
        return True
    
    return False
"""
    )
    
    algo_os_interface.add_failure_mode(memory_leak)
    
    print(f"创建接口: {algo_os_interface.name}")
    print(f"  - 类型: {algo_os_interface.interface_type.value}")
    print(f"  - 失效模式数量: {len(algo_os_interface.failure_modes)}")
    
    # 创建算法-硬件设备接口
    print_section("2. 算法-硬件设备接口")
    algo_hw_interface = Interface(
        id="algo_hw_001",
        name="算法-GPU计算接口",
        interface_type=InterfaceType.ALGORITHM_HARDWARE,
        description="算法模块与GPU硬件之间的计算接口"
    )
    
    gpu_failure = FailureMode(
        id="gpu_fail_001",
        name="GPU计算错误",
        description="GPU硬件故障或驱动问题导致的计算错误",
        trigger_conditions=["高温环境", "电压不稳", "驱动版本不兼容"],
        failure_rate=0.0005,
        python_code="""
def check_gpu_status():
    # 检查GPU状态
    gpu_temp = get_gpu_temperature()
    gpu_memory = get_gpu_memory_usage()
    
    if gpu_temp > MAX_GPU_TEMP:
        return 'overheating'
    
    if gpu_memory > MAX_GPU_MEMORY:
        return 'memory_overflow'
    
    # 检查计算结果一致性
    if not verify_computation_accuracy():
        return 'computation_error'
    
    return 'normal'
"""
    )
    
    algo_hw_interface.add_failure_mode(gpu_failure)
    
    print(f"创建接口: {algo_hw_interface.name}")
    print(f"  - 类型: {algo_hw_interface.interface_type.value}")
    print(f"  - 失效模式: {gpu_failure.name}")
    
    return [algo_os_interface, algo_hw_interface]

def demo_system_structure():
    """演示系统结构建模功能"""
    print_header("系统结构建模功能演示")
    
    # 创建系统结构
    system = SystemStructure(
        id="vision_system_001",
        name="智能视觉系统",
        description="基于深度学习的智能视觉感知系统"
    )
    
    # 添加模块（使用之前创建的模块）
    modules = demo_module_modeling()
    interfaces = demo_interface_modeling()
    
    for module in modules:
        system.add_module(module)
    
    for interface in interfaces:
        system.add_interface(interface)
    
    # 创建连接关系
    print_section("创建模块连接关系")
    
    # 摄像头 -> 图像处理模块
    conn1 = Connection(
        id="conn_001",
        source_module_id="camera_001",
        source_interface="data_out",
        target_module_id="img_proc_001",
        target_interface="image_in",
        interface_id="algo_hw_001"
    )
    system.add_connection(conn1)
    
    # 图像处理模块 -> 目标检测算法
    conn2 = Connection(
        id="conn_002",
        source_module_id="img_proc_001",
        source_interface="features_out",
        target_module_id="obj_det_001",
        target_interface="features_in",
        interface_id="algo_os_001"
    )
    system.add_connection(conn2)
    
    print(f"系统结构: {system.name}")
    print(f"  - 模块数量: {len(system.modules)}")
    print(f"  - 接口数量: {len(system.interfaces)}")
    print(f"  - 连接数量: {len(system.connections)}")
    
    # 显示连接关系
    print("\n连接关系:")
    for conn in system.connections:
        source_module = system.get_module(conn.source_module_id)
        target_module = system.get_module(conn.target_module_id)
        interface = system.get_interface(conn.interface_id)
        
        print(f"  {source_module.name} -> {target_module.name}")
        print(f"    接口: {interface.name}")
        print(f"    类型: {interface.interface_type.value}")
    
    return system

def demo_task_profile():
    """演示任务剖面建模功能"""
    print_header("任务剖面建模功能演示")
    
    print_section("任务剖面定义")
    
    task_profile = {
        "id": "task_001",
        "name": "车辆目标检测任务",
        "description": "在城市道路环境下检测和识别车辆目标",
        "duration": 3600,  # 1小时
        "success_criteria": [
            {
                "parameter": "detection_accuracy",
                "threshold": 0.95,
                "module_id": "obj_det_001",
                "output_param": "accuracy"
            },
            {
                "parameter": "response_time",
                "threshold": 100,  # 100ms
                "module_id": "img_proc_001",
                "output_param": "processing_time"
            }
        ],
        "environmental_conditions": {
            "weather": "晴天",
            "lighting": "日光",
            "traffic_density": "中等",
            "road_type": "城市道路"
        }
    }
    
    print(f"任务剖面: {task_profile['name']}")
    print(f"  - 持续时间: {task_profile['duration']}秒")
    print(f"  - 成功判据数量: {len(task_profile['success_criteria'])}")
    print(f"  - 环境条件: {len(task_profile['environmental_conditions'])}项")
    
    print("\n成功判据:")
    for i, criteria in enumerate(task_profile['success_criteria'], 1):
        print(f"  {i}. {criteria['parameter']} >= {criteria['threshold']}")
    
    return task_profile

def demo_fault_tree_analysis():
    """演示故障树分析功能"""
    print_header("故障树分析功能演示")
    
    print_section("故障树结构")
    
    # 简化的故障树结构
    fault_tree = {
        "top_event": {
            "name": "目标检测系统失效",
            "description": "系统无法正确检测和识别目标",
            "probability": 0.01
        },
        "intermediate_events": [
            {
                "name": "图像获取失效",
                "gate_type": "OR",
                "inputs": ["摄像头硬件故障", "图像传输接口故障"]
            },
            {
                "name": "算法处理失效", 
                "gate_type": "OR",
                "inputs": ["内存不足", "GPU计算错误", "算法模型错误"]
            }
        ],
        "basic_events": [
            {"name": "摄像头硬件故障", "probability": 0.001},
            {"name": "图像传输接口故障", "probability": 0.002},
            {"name": "内存不足", "probability": 0.003},
            {"name": "GPU计算错误", "probability": 0.0005},
            {"name": "算法模型错误", "probability": 0.001}
        ]
    }
    
    print(f"顶事件: {fault_tree['top_event']['name']}")
    print(f"中间事件数量: {len(fault_tree['intermediate_events'])}")
    print(f"基本事件数量: {len(fault_tree['basic_events'])}")
    
    print("\n定性分析 - 最小割集:")
    min_cut_sets = [
        ["摄像头硬件故障"],
        ["图像传输接口故障"],
        ["内存不足"],
        ["GPU计算错误"],
        ["算法模型错误"]
    ]
    
    for i, cut_set in enumerate(min_cut_sets, 1):
        print(f"  {i}. {' + '.join(cut_set)}")
    
    print("\n定量分析:")
    # 简化的概率计算
    total_probability = sum(event["probability"] for event in fault_tree["basic_events"])
    print(f"  系统失效概率: {total_probability:.6f}")
    print(f"  系统可靠度: {1 - total_probability:.6f}")
    
    return fault_tree

def demo_project_save_load():
    """演示项目保存和加载功能"""
    print_header("项目管理功能演示")
    
    # 创建项目管理器
    project_manager = ProjectManager()
    
    # 创建完整的项目数据
    system = demo_system_structure()
    task_profile = demo_task_profile()
    fault_tree = demo_fault_tree_analysis()
    
    # 构建项目数据
    project_data = {
        "project_info": {
            "name": "智能视觉系统分析项目",
            "version": "1.0.0",
            "created_date": datetime.now().isoformat(),
            "description": "基于深度学习的智能视觉感知系统接口故障分析"
        },
        "system_structure": system.to_dict(),
        "task_profiles": [task_profile],
        "fault_trees": [fault_tree]
    }
    
    # 保存项目
    print_section("保存项目")
    project_file = "data/demo_project.json"
    success = project_manager.save_project(project_data, project_file)
    
    if success:
        print(f"项目已保存到: {project_file}")
        
        # 获取文件大小
        file_size = os.path.getsize(project_file)
        print(f"文件大小: {file_size} 字节")
    else:
        print("项目保存失败")
        return
    
    # 加载项目
    print_section("加载项目")
    loaded_data = project_manager.load_project(project_file)
    
    if loaded_data:
        print("项目加载成功")
        print(f"项目名称: {loaded_data['project_info']['name']}")
        print(f"系统模块数量: {len(loaded_data['system_structure']['modules'])}")
        print(f"任务剖面数量: {len(loaded_data['task_profiles'])}")
        print(f"故障树数量: {len(loaded_data['fault_trees'])}")
    else:
        print("项目加载失败")

def main():
    """主函数"""
    print("接口故障机理分析原型系统")
    print("Interface Fault Mechanism Analysis Prototype System")
    print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 演示各个功能模块
        demo_module_modeling()
        demo_interface_modeling()
        demo_system_structure()
        demo_task_profile()
        demo_fault_tree_analysis()
        demo_project_save_load()
        
        print_header("演示完成")
        print("所有功能模块演示完成！")
        print("\n系统主要特性:")
        print("✓ 模块化设计 - 支持硬件/软件/算法模块建模")
        print("✓ 接口建模 - 支持五大类接口失效模式分析")
        print("✓ 系统结构 - 图形化建模和连接关系管理")
        print("✓ 任务剖面 - 任务成功判据和环境条件设定")
        print("✓ 故障树分析 - 定性和定量分析功能")
        print("✓ 项目管理 - 完整的保存和加载功能")
        print("✓ Python建模 - 支持自定义Python代码建模")
        
    except Exception as e:
        print(f"\n演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()