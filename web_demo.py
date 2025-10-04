#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web演示界面
Web Demo Interface

使用Flask创建Web界面来展示系统功能
"""

import sys
import os
import json
from flask import Flask, render_template, jsonify, request, send_from_directory

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.module_model import Module, HardwareModule, SoftwareModule, AlgorithmModule
from src.models.interface_model import Interface, InterfaceType, FailureMode
from src.models.system_model import SystemStructure, TaskProfile
from src.core.project_manager import ProjectManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'interface_fault_analysis_system'

# 全局项目管理器
project_manager = ProjectManager()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/system/info')
def get_system_info():
    """获取系统信息"""
    system = project_manager.get_current_system()
    if not system:
        return jsonify({'error': '没有加载的系统'})
    
    return jsonify({
        'name': system.name,
        'description': system.description,
        'modules_count': len(system.modules),
        'interfaces_count': len(system.interfaces),
        'task_profiles_count': len(system.task_profiles),
        'environment_models_count': len(system.environment_models)
    })


@app.route('/api/modules')
def get_modules():
    """获取模块列表"""
    system = project_manager.get_current_system()
    if not system:
        return jsonify([])
    
    modules = []
    for module in system.modules.values():
        modules.append({
            'id': module.id,
            'name': module.name,
            'description': module.description,
            'type': module.module_type.value,
            'position': {'x': module.position.x, 'y': module.position.y},
            'size': {'x': module.size.x, 'y': module.size.y},
            'connection_points_count': len(module.connection_points),
            'parameters_count': len(module.parameters)
        })
    
    return jsonify(modules)


@app.route('/api/interfaces')
def get_interfaces():
    """获取接口列表"""
    system = project_manager.get_current_system()
    if not system:
        return jsonify([])
    
    interfaces = []
    for interface in system.interfaces.values():
        interfaces.append({
            'id': interface.id,
            'name': interface.name,
            'description': interface.description,
            'type': interface.interface_type.value,
            'protocol': interface.protocol,
            'reliability': interface.reliability,
            'failure_modes_count': len(interface.failure_modes)
        })
    
    return jsonify(interfaces)


@app.route('/api/module/<module_id>')
def get_module_detail(module_id):
    """获取模块详情"""
    system = project_manager.get_current_system()
    if not system or module_id not in system.modules:
        return jsonify({'error': '模块不存在'})
    
    module = system.modules[module_id]
    
    # 获取连接点信息
    connection_points = []
    for cp in module.connection_points:
        connection_points.append({
            'id': cp.id,
            'name': cp.name,
            'type': cp.connection_type,
            'data_type': cp.data_type,
            'position': {'x': cp.position.x, 'y': cp.position.y},
            'variables': cp.variables
        })
    
    detail = {
        'id': module.id,
        'name': module.name,
        'description': module.description,
        'type': module.module_type.value,
        'position': {'x': module.position.x, 'y': module.position.y},
        'size': {'x': module.size.x, 'y': module.size.y},
        'connection_points': connection_points,
        'parameters': module.parameters,
        'python_code': module.python_code
    }
    
    # 添加特定类型的属性
    if isinstance(module, HardwareModule):
        detail.update({
            'manufacturer': module.manufacturer,
            'model': module.model,
            'power_consumption': module.power_consumption
        })
    elif isinstance(module, SoftwareModule):
        detail.update({
            'programming_language': module.programming_language,
            'software_version': module.software_version,
            'memory_usage': module.memory_usage
        })
    elif isinstance(module, AlgorithmModule):
        detail.update({
            'algorithm_type': module.algorithm_type,
            'complexity': module.complexity,
            'accuracy': module.accuracy
        })
    
    return jsonify(detail)


@app.route('/api/interface/<interface_id>')
def get_interface_detail(interface_id):
    """获取接口详情"""
    system = project_manager.get_current_system()
    if not system or interface_id not in system.interfaces:
        return jsonify({'error': '接口不存在'})
    
    interface = system.interfaces[interface_id]
    
    # 获取失效模式信息
    failure_modes = []
    for fm in interface.failure_modes:
        failure_modes.append({
            'name': fm.name,
            'type': fm.failure_mode.value,
            'description': fm.description,
            'severity': fm.severity,
            'occurrence_rate': fm.occurrence_rate,
            'detection_rate': fm.detection_rate,
            'trigger_conditions_count': len(fm.trigger_conditions)
        })
    
    detail = {
        'id': interface.id,
        'name': interface.name,
        'description': interface.description,
        'type': interface.interface_type.value,
        'protocol': interface.protocol,
        'data_format': interface.data_format,
        'bandwidth': interface.bandwidth,
        'latency': interface.latency,
        'reliability': interface.reliability,
        'failure_modes': failure_modes,
        'python_code': interface.python_code
    }
    
    return jsonify(detail)


@app.route('/api/simulate/module/<module_id>', methods=['POST'])
def simulate_module(module_id):
    """模拟模块执行"""
    system = project_manager.get_current_system()
    if not system or module_id not in system.modules:
        return jsonify({'error': '模块不存在'})
    
    module = system.modules[module_id]
    
    # 获取输入数据
    inputs = request.json.get('inputs', {})
    
    try:
        outputs = module.execute_python_code(inputs)
        return jsonify({
            'success': True,
            'inputs': inputs,
            'outputs': outputs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/project/load')
def load_demo_project():
    """加载演示项目"""
    try:
        project_file = "data/test_project.json"
        if os.path.exists(project_file):
            system = project_manager.load_project(project_file)
            return jsonify({
                'success': True,
                'message': f'已加载项目: {system.name}'
            })
        else:
            return jsonify({
                'success': False,
                'error': '演示项目文件不存在'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/project/create_demo')
def create_demo_project():
    """创建演示项目"""
    try:
        # 创建一个更复杂的演示系统
        system = SystemStructure("智能家居控制系统", "基于物联网的智能家居自动化控制系统")
        
        # 创建传感器模块
        temp_sensor = HardwareModule("温度传感器", "DHT22温湿度传感器")
        temp_sensor.manufacturer = "Aosong"
        temp_sensor.model = "DHT22"
        temp_sensor.power_consumption = 0.0025
        temp_sensor.position.x = 100
        temp_sensor.position.y = 100
        temp_sensor.python_code = """
import random
import time
# 模拟温湿度传感器
temperature = 20 + random.uniform(-3, 7)  # 17-27度
humidity = 50 + random.uniform(-10, 20)   # 40-70%
outputs['temperature'] = round(temperature, 1)
outputs['humidity'] = round(humidity, 1)
outputs['timestamp'] = time.time()
"""
        
        light_sensor = HardwareModule("光照传感器", "BH1750光照强度传感器")
        light_sensor.manufacturer = "ROHM"
        light_sensor.model = "BH1750"
        light_sensor.position.x = 300
        light_sensor.position.y = 100
        light_sensor.python_code = """
import random
import time
# 模拟光照传感器
current_hour = time.localtime().tm_hour
if 6 <= current_hour <= 18:  # 白天
    light_intensity = random.uniform(200, 1000)
else:  # 夜晚
    light_intensity = random.uniform(0, 50)
outputs['light_intensity'] = round(light_intensity, 1)
outputs['timestamp'] = time.time()
"""
        
        # 创建控制器模块
        main_controller = SoftwareModule("主控制器", "智能家居系统主控制软件")
        main_controller.programming_language = "Python"
        main_controller.software_version = "2.1.0"
        main_controller.memory_usage = 128
        main_controller.position.x = 200
        main_controller.position.y = 250
        main_controller.python_code = """
# 主控制逻辑
temperature = inputs.get('temperature', 20)
humidity = inputs.get('humidity', 50)
light_intensity = inputs.get('light_intensity', 100)

# 空调控制逻辑
if temperature > 26:
    outputs['ac_command'] = 'cooling'
elif temperature < 18:
    outputs['ac_command'] = 'heating'
else:
    outputs['ac_command'] = 'off'

# 灯光控制逻辑
if light_intensity < 100:
    outputs['light_command'] = 'on'
else:
    outputs['light_command'] = 'off'

outputs['system_status'] = 'running'
"""
        
        # 创建执行器模块
        ac_unit = HardwareModule("空调系统", "变频空调控制单元")
        ac_unit.manufacturer = "Midea"
        ac_unit.model = "KFR-35GW"
        ac_unit.power_consumption = 1200
        ac_unit.position.x = 50
        ac_unit.position.y = 400
        
        smart_light = HardwareModule("智能灯具", "可调光LED灯具")
        smart_light.manufacturer = "Philips"
        smart_light.model = "Hue White"
        smart_light.power_consumption = 9
        smart_light.position.x = 350
        smart_light.position.y = 400
        
        # 添加模块到系统
        system.add_module(temp_sensor)
        system.add_module(light_sensor)
        system.add_module(main_controller)
        system.add_module(ac_unit)
        system.add_module(smart_light)
        
        # 创建接口
        temp_interface = Interface("温度传感器接口", "温度传感器与主控制器的通信接口", 
                                 InterfaceType.ALGORITHM_HARDWARE)
        temp_interface.protocol = "I2C"
        temp_interface.source_module_id = temp_sensor.id
        temp_interface.target_module_id = main_controller.id
        temp_interface.reliability = 0.998
        
        light_interface = Interface("光照传感器接口", "光照传感器与主控制器的通信接口",
                                  InterfaceType.ALGORITHM_HARDWARE)
        light_interface.protocol = "I2C"
        light_interface.source_module_id = light_sensor.id
        light_interface.target_module_id = main_controller.id
        light_interface.reliability = 0.999
        
        ac_interface = Interface("空调控制接口", "主控制器与空调系统的控制接口",
                               InterfaceType.ALGORITHM_HARDWARE)
        ac_interface.protocol = "RS485"
        ac_interface.source_module_id = main_controller.id
        ac_interface.target_module_id = ac_unit.id
        ac_interface.reliability = 0.995
        
        system.add_interface(temp_interface)
        system.add_interface(light_interface)
        system.add_interface(ac_interface)
        
        # 创建任务剖面
        comfort_task = TaskProfile("舒适度控制任务", "维持室内环境舒适度")
        comfort_task.duration = 86400  # 24小时
        system.add_task_profile(comfort_task)
        
        # 设置为当前系统
        project_manager.set_current_system(system)
        
        # 保存项目
        os.makedirs("data", exist_ok=True)
        project_manager.save_project_as("data/demo_project.json")
        
        return jsonify({
            'success': True,
            'message': f'已创建演示项目: {system.name}',
            'modules_count': len(system.modules),
            'interfaces_count': len(system.interfaces)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


def create_html_template():
    """创建HTML模板"""
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>接口故障机理分析原型系统</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .nav {
            background: #f8f9fa;
            padding: 10px 20px;
            border-bottom: 1px solid #dee2e6;
        }
        .nav button {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            margin-right: 10px;
            border-radius: 4px;
            cursor: pointer;
        }
        .nav button:hover {
            background: #0056b3;
        }
        .content {
            padding: 20px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .info-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007bff;
        }
        .info-card h3 {
            margin: 0 0 10px 0;
            color: #495057;
        }
        .info-card .number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #495057;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .module-grid, .interface-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .module-card, .interface-card {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .module-card h4, .interface-card h4 {
            margin: 0 0 10px 0;
            color: #495057;
        }
        .module-type {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }
        .interface-type {
            display: inline-block;
            background: #17a2b8;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }
        .detail-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
        }
        .detail-btn:hover {
            background: #545b62;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 20px;
            border-radius: 8px;
            width: 80%;
            max-width: 800px;
            max-height: 80%;
            overflow-y: auto;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: black;
        }
        .code-block {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            overflow-x: auto;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>接口故障机理分析原型系统</h1>
            <p>Interface Fault Mechanism Analysis Prototype System</p>
        </div>
        
        <div class="nav">
            <button onclick="loadDemoProject()">加载演示项目</button>
            <button onclick="createDemoProject()">创建演示项目</button>
            <button onclick="refreshData()">刷新数据</button>
        </div>
        
        <div class="content">
            <div id="status"></div>
            
            <div class="info-grid">
                <div class="info-card">
                    <h3>模块数量</h3>
                    <div class="number" id="modules-count">0</div>
                </div>
                <div class="info-card">
                    <h3>接口数量</h3>
                    <div class="number" id="interfaces-count">0</div>
                </div>
                <div class="info-card">
                    <h3>任务剖面</h3>
                    <div class="number" id="tasks-count">0</div>
                </div>
                <div class="info-card">
                    <h3>环境模型</h3>
                    <div class="number" id="env-count">0</div>
                </div>
            </div>
            
            <div class="section">
                <h2>系统模块</h2>
                <div class="module-grid" id="modules-grid"></div>
            </div>
            
            <div class="section">
                <h2>系统接口</h2>
                <div class="interface-grid" id="interfaces-grid"></div>
            </div>
        </div>
    </div>
    
    <!-- 模态框 -->
    <div id="detailModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="modal-body"></div>
        </div>
    </div>
    
    <script>
        // 全局变量
        let systemData = null;
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadSystemInfo();
            loadModules();
            loadInterfaces();
            
            // 模态框关闭事件
            document.querySelector('.close').onclick = function() {
                document.getElementById('detailModal').style.display = 'none';
            }
            
            window.onclick = function(event) {
                const modal = document.getElementById('detailModal');
                if (event.target == modal) {
                    modal.style.display = 'none';
                }
            }
        });
        
        // 显示状态消息
        function showStatus(message, isError = false) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${isError ? 'error' : 'success'}">${message}</div>`;
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 3000);
        }
        
        // 加载系统信息
        async function loadSystemInfo() {
            try {
                const response = await fetch('/api/system/info');
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('modules-count').textContent = '0';
                    document.getElementById('interfaces-count').textContent = '0';
                    document.getElementById('tasks-count').textContent = '0';
                    document.getElementById('env-count').textContent = '0';
                } else {
                    document.getElementById('modules-count').textContent = data.modules_count;
                    document.getElementById('interfaces-count').textContent = data.interfaces_count;
                    document.getElementById('tasks-count').textContent = data.task_profiles_count;
                    document.getElementById('env-count').textContent = data.environment_models_count;
                }
            } catch (error) {
                console.error('加载系统信息失败:', error);
            }
        }
        
        // 加载模块列表
        async function loadModules() {
            try {
                const response = await fetch('/api/modules');
                const modules = await response.json();
                
                const grid = document.getElementById('modules-grid');
                grid.innerHTML = '';
                
                modules.forEach(module => {
                    const card = document.createElement('div');
                    card.className = 'module-card';
                    card.innerHTML = `
                        <h4>${module.name}</h4>
                        <span class="module-type">${module.type}</span>
                        <p>${module.description}</p>
                        <p><strong>连接点:</strong> ${module.connection_points_count}</p>
                        <p><strong>参数:</strong> ${module.parameters_count}</p>
                        <button class="detail-btn" onclick="showModuleDetail('${module.id}')">查看详情</button>
                        <button class="detail-btn" onclick="simulateModule('${module.id}')">模拟执行</button>
                    `;
                    grid.appendChild(card);
                });
            } catch (error) {
                console.error('加载模块列表失败:', error);
            }
        }
        
        // 加载接口列表
        async function loadInterfaces() {
            try {
                const response = await fetch('/api/interfaces');
                const interfaces = await response.json();
                
                const grid = document.getElementById('interfaces-grid');
                grid.innerHTML = '';
                
                interfaces.forEach(interface => {
                    const card = document.createElement('div');
                    card.className = 'interface-card';
                    card.innerHTML = `
                        <h4>${interface.name}</h4>
                        <span class="interface-type">${interface.type}</span>
                        <p>${interface.description}</p>
                        <p><strong>协议:</strong> ${interface.protocol}</p>
                        <p><strong>可靠性:</strong> ${interface.reliability}</p>
                        <p><strong>失效模式:</strong> ${interface.failure_modes_count}</p>
                        <button class="detail-btn" onclick="showInterfaceDetail('${interface.id}')">查看详情</button>
                    `;
                    grid.appendChild(card);
                });
            } catch (error) {
                console.error('加载接口列表失败:', error);
            }
        }
        
        // 显示模块详情
        async function showModuleDetail(moduleId) {
            try {
                const response = await fetch(`/api/module/${moduleId}`);
                const module = await response.json();
                
                if (module.error) {
                    showStatus(module.error, true);
                    return;
                }
                
                let specificInfo = '';
                if (module.manufacturer) {
                    specificInfo = `
                        <p><strong>制造商:</strong> ${module.manufacturer}</p>
                        <p><strong>型号:</strong> ${module.model}</p>
                        <p><strong>功耗:</strong> ${module.power_consumption}W</p>
                    `;
                } else if (module.programming_language) {
                    specificInfo = `
                        <p><strong>编程语言:</strong> ${module.programming_language}</p>
                        <p><strong>版本:</strong> ${module.software_version}</p>
                        <p><strong>内存使用:</strong> ${module.memory_usage}MB</p>
                    `;
                } else if (module.algorithm_type) {
                    specificInfo = `
                        <p><strong>算法类型:</strong> ${module.algorithm_type}</p>
                        <p><strong>复杂度:</strong> ${module.complexity}</p>
                        <p><strong>准确率:</strong> ${module.accuracy}</p>
                    `;
                }
                
                const modalBody = document.getElementById('modal-body');
                modalBody.innerHTML = `
                    <h2>${module.name}</h2>
                    <p><strong>类型:</strong> ${module.type}</p>
                    <p><strong>描述:</strong> ${module.description}</p>
                    <p><strong>位置:</strong> (${module.position.x}, ${module.position.y})</p>
                    <p><strong>大小:</strong> ${module.size.x} × ${module.size.y}</p>
                    ${specificInfo}
                    
                    <h3>连接点 (${module.connection_points.length})</h3>
                    ${module.connection_points.map(cp => `
                        <div style="background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 4px;">
                            <strong>${cp.name}</strong> (${cp.type}) - ${cp.data_type}<br>
                            位置: (${cp.position.x}, ${cp.position.y})<br>
                            变量: ${cp.variables.join(', ')}
                        </div>
                    `).join('')}
                    
                    <h3>参数</h3>
                    <div class="code-block">${JSON.stringify(module.parameters, null, 2)}</div>
                    
                    <h3>Python建模代码</h3>
                    <div class="code-block">${module.python_code}</div>
                `;
                
                document.getElementById('detailModal').style.display = 'block';
            } catch (error) {
                console.error('获取模块详情失败:', error);
                showStatus('获取模块详情失败', true);
            }
        }
        
        // 显示接口详情
        async function showInterfaceDetail(interfaceId) {
            try {
                const response = await fetch(`/api/interface/${interfaceId}`);
                const interface = await response.json();
                
                if (interface.error) {
                    showStatus(interface.error, true);
                    return;
                }
                
                const modalBody = document.getElementById('modal-body');
                modalBody.innerHTML = `
                    <h2>${interface.name}</h2>
                    <p><strong>类型:</strong> ${interface.type}</p>
                    <p><strong>描述:</strong> ${interface.description}</p>
                    <p><strong>协议:</strong> ${interface.protocol}</p>
                    <p><strong>数据格式:</strong> ${interface.data_format}</p>
                    <p><strong>带宽:</strong> ${interface.bandwidth} Mbps</p>
                    <p><strong>延迟:</strong> ${interface.latency} ms</p>
                    <p><strong>可靠性:</strong> ${interface.reliability}</p>
                    
                    <h3>失效模式 (${interface.failure_modes.length})</h3>
                    ${interface.failure_modes.map(fm => `
                        <div style="background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 4px;">
                            <strong>${fm.name}</strong> (${fm.type})<br>
                            ${fm.description}<br>
                            严重程度: ${fm.severity}/10, 发生率: ${fm.occurrence_rate}, 检测率: ${fm.detection_rate}
                        </div>
                    `).join('')}
                    
                    <h3>Python建模代码</h3>
                    <div class="code-block">${interface.python_code}</div>
                `;
                
                document.getElementById('detailModal').style.display = 'block';
            } catch (error) {
                console.error('获取接口详情失败:', error);
                showStatus('获取接口详情失败', true);
            }
        }
        
        // 模拟模块执行
        async function simulateModule(moduleId) {
            try {
                const inputs = {
                    'input': 10.0,
                    'test_data': 'hello'
                };
                
                const response = await fetch(`/api/simulate/module/${moduleId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({inputs: inputs})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const modalBody = document.getElementById('modal-body');
                    modalBody.innerHTML = `
                        <h2>模块执行结果</h2>
                        <h3>输入数据</h3>
                        <div class="code-block">${JSON.stringify(result.inputs, null, 2)}</div>
                        <h3>输出数据</h3>
                        <div class="code-block">${JSON.stringify(result.outputs, null, 2)}</div>
                    `;
                    document.getElementById('detailModal').style.display = 'block';
                } else {
                    showStatus(`模块执行失败: ${result.error}`, true);
                }
            } catch (error) {
                console.error('模块执行失败:', error);
                showStatus('模块执行失败', true);
            }
        }
        
        // 加载演示项目
        async function loadDemoProject() {
            try {
                const response = await fetch('/api/project/load');
                const result = await response.json();
                
                if (result.success) {
                    showStatus(result.message);
                    refreshData();
                } else {
                    showStatus(result.error, true);
                }
            } catch (error) {
                console.error('加载演示项目失败:', error);
                showStatus('加载演示项目失败', true);
            }
        }
        
        // 创建演示项目
        async function createDemoProject() {
            try {
                showStatus('正在创建演示项目...');
                const response = await fetch('/api/project/create_demo');
                const result = await response.json();
                
                if (result.success) {
                    showStatus(result.message);
                    refreshData();
                } else {
                    showStatus(result.error, true);
                }
            } catch (error) {
                console.error('创建演示项目失败:', error);
                showStatus('创建演示项目失败', true);
            }
        }
        
        // 刷新数据
        function refreshData() {
            loadSystemInfo();
            loadModules();
            loadInterfaces();
        }
    </script>
</body>
</html>'''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)


if __name__ == '__main__':
    # 创建模板目录
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # 创建HTML模板
    create_html_template()
    
    print("接口故障机理分析原型系统 - Web演示")
    print("启动Web服务器...")
    print("访问地址: http://localhost:8080")
    
    app.run(host='0.0.0.0', port=8080, debug=True)