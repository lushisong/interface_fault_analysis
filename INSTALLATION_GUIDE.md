# 接口故障机理分析原型系统 - 安装和使用指南

## 系统要求

### 操作系统
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, CentOS 7+)

### Python环境
- Python 3.8 或更高版本
- 推荐使用 Python 3.8-3.11 (已测试)

## 安装步骤

### 1. 解压项目文件
```bash
# 如果是tar.gz文件
tar -xzf interface_fault_analysis_system.tar.gz
cd project

# 如果是zip文件
unzip interface_fault_analysis_system.zip
cd project
```

### 2. 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. 安装依赖包
```bash
# 安装所有依赖
pip install -r requirements.txt

# 或者手动安装主要依赖
pip install PyQt5 matplotlib networkx scipy Pillow flask json5
```

### 4. 验证安装
```bash
# 运行测试验证系统功能
python test_models.py

# 运行功能演示
python simple_demo.py
```

## 运行程序

### 图形界面版本（推荐）
```bash
# 启动主程序
python main.py
```

**注意**: 如果遇到 "Could not load the Qt platform plugin" 错误，说明当前环境不支持图形界面。请使用Web版本或在有图形界面的环境中运行。

### Web版本（无头环境）
```bash
# 启动Web服务器
python web_demo.py

# 然后在浏览器中访问: http://localhost:8080
```

### 命令行演示
```bash
# 运行功能演示脚本
python simple_demo.py
```

## 常见问题解决

### 1. PyQt5安装问题

**Windows系统**:
```bash
pip install PyQt5
```

**Linux系统**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt5
pip install PyQt5

# CentOS/RHEL
sudo yum install qt5-qtbase-devel
pip install PyQt5
```

**macOS系统**:
```bash
# 使用Homebrew
brew install pyqt5
pip install PyQt5
```

### 2. 图形界面无法启动

如果遇到以下错误：
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

**解决方案**:
1. 使用Web版本: `python web_demo.py`
2. 安装图形界面支持:
   ```bash
   # Linux
   sudo apt-get install libxcb-xinerama0
   export QT_QPA_PLATFORM=offscreen  # 无头模式
   ```

### 3. 依赖包版本冲突

如果遇到版本冲突，建议使用虚拟环境：
```bash
python -m venv fresh_env
source fresh_env/bin/activate  # Linux/macOS
# 或 fresh_env\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 使用指南

### 1. 创建新项目
- 启动程序后，选择"文件" -> "新建项目"
- 输入项目名称和描述

### 2. 模块建模
- 在左侧模块面板中选择模块类型
- 设置模块属性和参数
- 添加接口点和连接点

### 3. 接口建模
- 在接口面板中创建新接口
- 选择接口类型（五大类）
- 定义失效模式和触发条件

### 4. 系统结构建模
- 在中央画布中拖拽模块
- 连接模块间的接口
- 配置系统参数

### 5. 故障树分析
- 设置任务剖面
- 生成故障树
- 进行定性和定量分析

## 项目结构说明

```
project/
├── main.py                 # 主程序入口（PyQt5版本）
├── web_demo.py            # Web版本入口
├── simple_demo.py         # 功能演示脚本
├── test_models.py         # 测试脚本
├── requirements.txt       # 依赖包列表
├── PROJECT_SUMMARY.md     # 项目总结文档
├── INSTALLATION_GUIDE.md  # 安装指南
├── src/                   # 源代码目录
│   ├── models/           # 数据模型
│   ├── ui/               # 用户界面
│   ├── core/             # 核心功能
│   ├── analysis/         # 分析功能
│   ├── templates/        # 模板库
│   └── utils/            # 工具函数
├── data/                 # 数据文件
├── icons/                # 图标资源
└── docs/                 # 文档
```

## 开发环境设置

如果您想参与开发或修改代码：

### 1. 开发依赖
```bash
pip install -r requirements.txt
pip install pytest pytest-qt  # 测试框架
```

### 2. 代码规范
- 使用PEP 8代码风格
- 添加适当的注释和文档字符串
- 运行测试确保功能正常

### 3. 测试
```bash
# 运行所有测试
python test_models.py

# 运行特定测试
python -m pytest tests/
```

## 技术支持

### 文档资源
- `PROJECT_SUMMARY.md` - 项目功能详细说明
- `src/models/` - 数据模型API文档
- `src/ui/` - 用户界面组件说明

### 常用命令
```bash
# 查看系统信息
python --version
pip list

# 清理缓存
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# 重新安装依赖
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### 性能优化建议
1. 使用虚拟环境避免依赖冲突
2. 定期清理Python缓存文件
3. 在有图形界面的环境中运行PyQt5版本
4. 大型项目建议使用Web版本

## 版本信息

- **当前版本**: 1.0.0
- **开发语言**: Python 3.8+
- **UI框架**: PyQt5 / Flask (Web版)
- **支持平台**: Windows, macOS, Linux

---

如有问题，请查看项目文档或联系开发团队。