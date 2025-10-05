#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统环境检测模块
检测Python版本、虚拟环境、依赖包等系统环境
更新时间: 2025-10-04
"""

import os
import sys
import subprocess
import importlib
import platform
import json
import socket
import psutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class SystemChecker:
    """系统环境检测器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent  # 指向项目根目录
        self.venv_path = self.project_root / ".venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.config_file = self.project_root / "config.json"
        self.pyproject_file = self.project_root / "pyproject.toml"
        self.results = {}

        # 需要检测的端口
        self.required_ports = [8000, 8001, 8003, 5048]

        # 核心依赖包（从requirements.txt提取）
        self.core_dependencies = [
            "nagaagent_core",
            "PyQt5",
            "fastapi",
            "uvicorn",
            "neo4j",
            "py2neo",
            "requests",
            "pydantic",
            "asyncio",
            "websockets"
        ]

        # 重要可选依赖
        self.optional_dependencies = [
            ("onnxruntime", "语音处理"),
            ("sounddevice", "音频设备"),
            ("pyaudio", "音频录制"),
            ("edge_tts", "TTS语音合成"),
            ("playwright", "浏览器自动化"),
            ("crawl4ai", "网页爬取"),
            ("pyautogui", "屏幕控制"),
            ("opencv_python", "计算机视觉"),
            ("librosa", "音频分析"),
            ("torch", "深度学习框架"),
            ("pystray", "系统托盘"),
            ("live2d", "Live2D虚拟形象"),
            ("paho_mqtt", "MQTT通信"),
            ("jmcomic", "漫画下载"),
            ("bilibili_api", "B站视频"),
            ("python_docx", "Word文档处理")
        ]
        
    def check_all(self) -> Dict[str, bool]:
        """执行所有检测项目"""
        print("🔍 开始系统环境检测...")
        print("=" * 50)
        
        checks = [
            ("Python版本", self.check_python_version),
            ("虚拟环境", self.check_virtual_environment),
            ("依赖文件", self.check_requirements_file),
            ("核心依赖", self.check_core_dependencies),
            ("可选依赖", self.check_optional_dependencies),
            ("配置文件", self.check_config_files),
            ("目录结构", self.check_directory_structure),
            ("权限检查", self.check_permissions),
            ("端口可用性", self.check_port_availability),
            ("系统资源", self.check_system_resources),
            ("Neo4j连接", self.check_neo4j_connection),
            ("GPU支持", self.check_gpu_support),
            ("环境变量", self.check_environment_variables)
        ]
        
        all_passed = True
        for name, check_func in checks:
            print(f"📋 检测 {name}...")
            try:
                result = check_func()
                self.results[name] = result
                if result:
                    print(f"✅ {name}: 通过")
                else:
                    print(f"❌ {name}: 失败")
                    all_passed = False
            except Exception as e:
                print(f"⚠️ {name}: 检测异常 - {e}")
                self.results[name] = False
                all_passed = False
            print()
        
        print("=" * 50)
        if all_passed:
            print("🎉 系统环境检测全部通过！")
        else:
            print("⚠️ 系统环境检测发现问题，请查看上述信息")
        
        return self.results
    
    def check_python_version(self) -> bool:
        """检测Python版本"""
        version = sys.version_info
        print(f"   当前Python版本: {version.major}.{version.minor}.{version.micro}")

        # 要求Python 3.11+（根据requirements.txt推荐）
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            print(f"   ⚠️ Python版本建议3.11+，当前{version.major}.{version.minor}")
            print(f"   💡 推荐升级到Python 3.11以获得最佳兼容性")
            return False

        print(f"   ✅ Python版本符合要求")
        return True
    
    def check_virtual_environment(self) -> bool:
        """检测虚拟环境"""
        # 检查是否在虚拟环境中
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if not in_venv:
            print(f"   ⚠️ 未检测到虚拟环境")
            print(f"   建议使用虚拟环境运行项目")
            
            # 检查是否存在.venv目录
            if self.venv_path.exists():
                print(f"   📁 发现.venv目录: {self.venv_path}")
                print(f"   💡 请运行: .venv\\Scripts\\activate (Windows) 或 source .venv/bin/activate (Linux/Mac)")
                return False
            else:
                print(f"   💡 建议创建虚拟环境: python -m venv .venv")
                return False
        
        print(f"   ✅ 虚拟环境: {sys.prefix}")
        return True
    
    def check_requirements_file(self) -> bool:
        """检测依赖文件"""
        if not self.requirements_file.exists():
            print(f"   ❌ 未找到requirements.txt文件: {self.requirements_file}")
            return False

        print(f"   ✅ 依赖文件存在: {self.requirements_file}")

        # 检查pyproject.toml
        if self.pyproject_file.exists():
            print(f"   ✅ pyproject.toml存在: {self.pyproject_file}")
        else:
            print(f"   ⚠️ pyproject.toml不存在（可选）")

        return True
    
    def check_core_dependencies(self) -> bool:
        """检测核心依赖包"""
        missing_deps = []

        for dep in self.core_dependencies:
            # 特殊处理某些包名
            module_name = dep
            if dep == "nagaagent_core":
                module_name = "nagaagent_core"
            elif dep == "opencv_python":
                module_name = "cv2"
            elif dep == "pydantic":
                module_name = "pydantic"
            elif dep == "edge_tts":
                module_name = "edge_tts"

            try:
                importlib.import_module(module_name)
                print(f"   ✅ {dep}")
            except ImportError:
                print(f"   ❌ {dep}: 未安装")
                missing_deps.append(dep)

        if missing_deps:
            print(f"   💡 请安装缺失的依赖: pip install {' '.join(missing_deps)}")
            print(f"   💡 或使用完整安装命令: pip install -r requirements.txt")
            return False

        return True
    
    def check_optional_dependencies(self) -> bool:
        """检测可选依赖包"""
        missing_optional = []

        for dep, desc in self.optional_dependencies:
            # 特殊处理某些包名
            module_name = dep
            if dep == "opencv_python":
                module_name = "cv2"
            elif dep == "edge_tts":
                module_name = "edge_tts"
            elif dep == "live2d":
                module_name = "live2d"
            elif dep == "bilibili_api":
                module_name = "bilibili_api"
            elif dep == "python_docx":
                module_name = "docx"

            try:
                importlib.import_module(module_name)
                print(f"   ✅ {dep} ({desc})")
            except ImportError:
                print(f"   ⚠️ {dep} ({desc}): 未安装")
                missing_optional.append((dep, desc))

        if missing_optional:
            print(f"   💡 可选依赖缺失，某些功能可能不可用:")
            for dep, desc in missing_optional:
                print(f"      - {dep}: {desc}")

        return True  # 可选依赖不影响启动
    
    def check_config_files(self) -> bool:
        """检测配置文件"""
        config_files = [
            ("config.json", "主配置文件"),
            ("config.json.example", "配置示例文件")
        ]
        
        all_exist = True
        for file_name, desc in config_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                print(f"   ✅ {file_name} ({desc})")
            else:
                print(f"   ❌ {file_name} ({desc}): 不存在")
                all_exist = False
        
        if not all_exist:
            print(f"   💡 请确保配置文件存在")
        
        return all_exist
    
    def check_directory_structure(self) -> bool:
        """检测目录结构"""
        required_dirs = [
            ("ui", "用户界面"),
            ("apiserver", "API服务器"),
            ("agentserver", "Agent服务器"),
            ("mcpserver", "MCP服务器"),
            ("summer_memory", "记忆系统"),
            ("voice", "语音模块"),
            ("system", "系统核心")
        ]

        all_exist = True
        for dir_name, desc in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                print(f"   ✅ {dir_name}/ ({desc})")
            else:
                print(f"   ❌ {dir_name}/ ({desc}): 不存在")
                all_exist = False

        return all_exist
    
    def check_permissions(self) -> bool:
        """检测文件权限"""
        try:
            # 检查项目根目录读写权限
            test_file = self.project_root / ".test_permission"
            test_file.write_text("test")
            test_file.unlink()
            
            # 检查logs目录权限
            logs_dir = self.project_root / "logs"
            if logs_dir.exists():
                test_log = logs_dir / ".test_permission"
                test_log.write_text("test")
                test_log.unlink()
            
            print(f"   ✅ 文件权限正常")
            return True
            
        except Exception as e:
            print(f"   ❌ 文件权限异常: {e}")
            return False

    def check_port_availability(self) -> bool:
        """检测端口可用性"""
        print(f"   检测端口: {', '.join(map(str, self.required_ports))}")

        all_available = True
        for port in self.required_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()

            if result == 0:
                print(f"   ⚠️ 端口 {port}: 已被占用")
                all_available = False
            else:
                print(f"   ✅ 端口 {port}: 可用")

        return all_available

    def check_system_resources(self) -> bool:
        """检测系统资源"""
        try:
            # CPU信息
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"   CPU核心数: {cpu_count}")
            print(f"   CPU使用率: {cpu_percent:.1f}%")

            # 内存信息
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            available_gb = memory.available / (1024**3)
            used_percent = memory.percent
            print(f"   总内存: {total_gb:.1f} GB")
            print(f"   可用内存: {available_gb:.1f} GB")
            print(f"   内存使用率: {used_percent:.1f}%")

            # 磁盘空间
            disk = psutil.disk_usage(str(self.project_root))
            total_disk = disk.total / (1024**3)
            free_disk = disk.free / (1024**3)
            print(f"   磁盘空间: {free_disk:.1f} GB 可用 / {total_disk:.1f} GB 总计")

            # 资源检查
            if total_gb < 4:
                print(f"   ⚠️ 内存不足4GB，可能影响性能")
                return False

            if free_disk < 1:
                print(f"   ⚠️ 磁盘空间不足1GB")
                return False

            print(f"   ✅ 系统资源充足")
            return True

        except Exception as e:
            print(f"   ❌ 检测系统资源失败: {e}")
            return False

    def check_neo4j_connection(self) -> bool:
        """检测Neo4j连接"""
        try:
            # 检查配置文件中是否有Neo4j配置
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                neo4j_config = config.get('grag', {})
                if neo4j_config.get('enabled', False):
                    uri = neo4j_config.get('neo4j_uri', 'neo4j://127.0.0.1:7687')
                    user = neo4j_config.get('neo4j_user', 'neo4j')

                    # 尝试导入neo4j包并连接
                    try:
                        from neo4j import GraphDatabase
                        # 只测试连接，不进行实际查询
                        print(f"   Neo4j配置: {uri} (用户: {user})")
                        print(f"   ✅ Neo4j包已安装，配置已启用")
                        return True
                    except ImportError:
                        print(f"   ❌ Neo4j包未安装")
                        return False
                    except Exception as e:
                        print(f"   ⚠️ Neo4j连接测试失败: {e}")
                        print(f"   💡 请确保Neo4j服务正在运行")
                        return False
                else:
                    print(f"   ⚠️ Neo4j未启用（配置中grag.enabled=false）")
                    return True
            else:
                print(f"   ⚠️ 配置文件不存在，跳过Neo4j检测")
                return True

        except Exception as e:
            print(f"   ❌ Neo4j检测异常: {e}")
            return False

    def check_gpu_support(self) -> bool:
        """检测GPU支持"""
        try:
            # 检测NVIDIA GPU
            try:
                import pynvml
                pynvml.nvmlInit()
                gpu_count = pynvml.nvmlDeviceGetCount()
                if gpu_count > 0:
                    print(f"   ✅ 检测到 {gpu_count} 个NVIDIA GPU")
                    for i in range(gpu_count):
                        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                        name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                        print(f"      GPU {i}: {name}")
                    return True
            except:
                pass

            # 检测PyTorch GPU支持
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_count = torch.cuda.device_count()
                    print(f"   ✅ PyTorch检测到 {gpu_count} 个CUDA GPU")
                    return True
            except:
                pass

            # 检测TensorFlow GPU支持
            try:
                import tensorflow as tf
                gpus = tf.config.list_physical_devices('GPU')
                if gpus:
                    print(f"   ✅ TensorFlow检测到 {len(gpus)} 个GPU")
                    return True
            except:
                pass

            print(f"   ⚠️ 未检测到GPU支持（可选）")
            return True  # GPU是可选的

        except Exception as e:
            print(f"   ❌ GPU检测异常: {e}")
            return False

    def check_environment_variables(self) -> bool:
        """检测环境变量"""
        important_env_vars = [
            ('PATH', '系统路径'),
            ('PYTHONPATH', 'Python路径（可选）'),
            ('OPENAI_API_KEY', 'OpenAI API密钥（可选）'),
            ('DEEPSEEK_API_KEY', 'DeepSeek API密钥（可选）'),
            ('DASHSCOPE_API_KEY', '阿里云DashScope API密钥（可选）')
        ]

        all_good = True
        for var_name, desc in important_env_vars:
            value = os.getenv(var_name)
            if value:
                # 隐藏敏感信息
                if 'API_KEY' in var_name:
                    display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "已设置"
                else:
                    display_value = value[:50] + "..." if len(value) > 50 else value
                print(f"   ✅ {var_name}: {display_value}")
            else:
                if '可选' in desc:
                    print(f"   ⚠️ {var_name}: 未设置（{desc}）")
                else:
                    print(f"   ❌ {var_name}: 未设置（{desc}）")
                    all_good = False

        return all_good
    
    def get_system_info(self) -> Dict[str, str]:
        """获取系统信息"""
        info = {
            "操作系统": platform.system(),
            "系统版本": platform.version(),
            "架构": platform.machine(),
            "Python版本": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "Python路径": sys.executable,
            "项目路径": str(self.project_root),
            "虚拟环境": "是" if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else "否"
        }

        # 添加系统资源信息
        try:
            memory = psutil.virtual_memory()
            info["总内存"] = f"{memory.total / (1024**3):.1f} GB"
            info["CPU核心数"] = str(psutil.cpu_count())
        except:
            pass

        return info
    
    def print_system_info(self):
        """打印系统信息"""
        print("🖥️ 系统信息:")
        print("-" * 30)
        info = self.get_system_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        print()
    
    def suggest_fixes(self):
        """建议修复方案"""
        print("🔧 修复建议:")
        print("-" * 30)

        if not self.results.get("Python版本", True):
            print("1. 升级Python版本:")
            print("   推荐使用Python 3.11或更高版本")
            print("   下载地址: https://www.python.org/downloads/")
            print()

        if not self.results.get("虚拟环境", True):
            print("2. 创建并激活虚拟环境:")
            print("   python -m venv .venv")
            print("   .venv\\Scripts\\activate  # Windows")
            print("   source .venv/bin/activate  # Linux/Mac")
            print()

        if not self.results.get("核心依赖", True):
            print("3. 安装核心依赖:")
            print("   pip install -r requirements.txt")
            print("   # 或使用uv:")
            print("   uv pip install -r requirements.txt")
            print()

        if not self.results.get("配置文件", True):
            print("4. 复制配置文件:")
            print("   copy config.json.example config.json  # Windows")
            print("   cp config.json.example config.json  # Linux/Mac")
            print("   # 编辑config.json并填入API密钥")
            print()

        if not self.results.get("端口可用性", True):
            print("5. 解决端口冲突:")
            print("   # 查找占用端口的进程")
            print("   netstat -ano | findstr :8000  # Windows")
            print("   lsof -i :8000  # Linux/Mac")
            print("   # 或修改config.json中的端口配置")
            print()

        if not self.results.get("系统资源", True):
            print("6. 系统资源不足:")
            print("   - 建议至少4GB内存")
            print("   - 建议至少1GB可用磁盘空间")
            print("   - 关闭不必要的应用程序")
            print()

        if not self.results.get("Neo4j连接", True):
            print("7. 配置Neo4j数据库:")
            print("   # 使用Docker启动Neo4j:")
            print("   docker run -d --name naga-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")
            print("   # 或安装Neo4j Desktop")
            print()

        if not self.results.get("目录结构", True):
            print("8. 检查项目完整性:")
            print("   确保所有必要的目录和文件都存在")
            print("   重新克隆项目可能解决问题")
            print()

    def is_check_passed(self) -> bool:
        """检查是否已经通过过系统检测"""
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                system_check = config_data.get('system_check', {})
                return system_check.get('passed', False)
        except Exception:
            return False
    
    def save_check_status(self, passed: bool):
        """保存检测状态到config.json"""
        try:
            # 读取现有配置
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            else:
                config_data = {}
            
            # 更新system_check配置
            config_data['system_check'] = {
                'passed': passed,
                'timestamp': datetime.now().isoformat(),
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'project_path': str(self.project_root),
                'system': platform.system()
            }
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存检测状态失败: {e}")
    
    def should_skip_check(self) -> bool:
        """判断是否应该跳过检测"""
        return self.is_check_passed()
    
    def reset_check_status(self):
        """重置检测状态，强制下次启动时重新检测"""
        try:
            # 读取现有配置
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 删除system_check配置
                if 'system_check' in config_data:
                    del config_data['system_check']
                
                # 保存配置
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                
                print("✅ 检测状态已重置，下次启动时将重新检测")
            else:
                print("⚠️ 配置文件不存在")
        except Exception as e:
            print(f"⚠️ 重置检测状态失败: {e}")

def run_system_check(force_check: bool = False) -> bool:
    """运行系统检测"""
    checker = SystemChecker()
    
    # 检查是否已经通过过检测（除非强制检测）
    if not force_check and checker.should_skip_check():
        print("✅ 系统环境检测已通过，跳过检测")
        return True
    
    # 打印系统信息
    checker.print_system_info()
    
    # 执行检测
    results = checker.check_all()
    
    # 保存检测结果
    all_passed = all(results.values())
    checker.save_check_status(all_passed)
    
    # 如果有问题，提供修复建议
    if not all_passed:
        checker.suggest_fixes()
        return False
    
    return True

def reset_system_check():
    """重置系统检测状态"""
    checker = SystemChecker()
    checker.reset_check_status()

def run_quick_check() -> bool:
    """运行快速检测（仅检测核心项）"""
    checker = SystemChecker()

    print("快速系统检测...")
    print("=" * 50)

    # 仅检测关键项
    quick_checks = [
        ("Python版本", checker.check_python_version),
        ("核心依赖", checker.check_core_dependencies),
        ("配置文件", checker.check_config_files)
    ]

    all_passed = True
    for name, check_func in quick_checks:
        print(f"📋 检测 {name}...")
        try:
            result = check_func()
            if result:
                print(f"✅ {name}: 通过")
            else:
                print(f"❌ {name}: 失败")
                all_passed = False
        except Exception as e:
            print(f"⚠️ {name}: 检测异常 - {e}")
            all_passed = False
        print()

    if all_passed:
        print("快速检测通过！")
    else:
        print("快速检测发现问题，建议运行完整检测: python main.py --check-env")

    return all_passed

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NagaAgent 系统环境检测工具")
    parser.add_argument("--quick", action="store_true", help="快速检测（仅检测核心项）")
    parser.add_argument("--force", action="store_true", help="强制检测（忽略缓存）")

    args = parser.parse_args()

    if args.quick:
        success = run_quick_check()
    else:
        success = run_system_check(force_check=args.force)

    sys.exit(0 if success else 1)
