# 标准库导入
import asyncio
import json
import logging
import os
import re
import sys
import time
import traceback
from datetime import datetime
from typing import List, Dict, Any

# 第三方库导入
from nagaagent_core.core import AsyncOpenAI

# 本地模块导入
from system.config import config, AI_NAME
from mcpserver.mcp_manager import get_mcp_manager
from system.background_analyzer import get_background_analyzer
from system.prompt_repository import get_prompt
# from thinking import TreeThinkingEngine
# from thinking.config import COMPLEX_KEYWORDS  # 已废弃，不再使用

# 配置日志系统
def setup_logging():
    """统一配置日志系统"""
    log_level = getattr(logging, config.system.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )
    
    # 设置第三方库日志级别
    for logger_name in ["httpcore.connection", "httpcore.http11", "httpx", "openai._base_client", "asyncio"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger("NagaConversation")

# 全局状态管理
class SystemState:
    """系统状态管理器"""
    _tree_thinking_initialized = False
    _mcp_services_initialized = False
    _voice_enabled_logged = False
    _memory_initialized = False
    _persistent_context_initialized = False

# GRAG记忆系统导入
def init_memory_manager():
    """初始化GRAG记忆系统"""
    if not config.grag.enabled:
        return None
    
    try:
        from summer_memory.memory_manager import memory_manager
        print("[GRAG] ✅ 夏园记忆系统初始化成功")
        return memory_manager
    except Exception as e:
        logger.error(f"夏园记忆系统加载失败: {e}")
        return None

memory_manager = init_memory_manager()

# 工具函数
def now():
    """获取当前时间戳"""
    return time.strftime('%H:%M:%S:') + str(int(time.time() * 1000) % 10000)

_builtin_print = print
def print(*a, **k):
    """自定义打印函数"""
    return sys.stderr.write('[print] ' + (' '.join(map(str, a))) + '\n')

class NagaConversation: # 对话主类
    def __init__(self):
        self.mcp = get_mcp_manager()
        self.messages = []
        self.dev_mode = False
        self.async_client = AsyncOpenAI(api_key=config.api.api_key, base_url=config.api.base_url.rstrip('/') + '/')
        
        # 初始化Agent Server客户端（包含意图分析和MCP调度功能）
        self.agent_server_client = None
        self._init_agent_server_client()
        
        # 初始化MCP服务系统
        self._init_mcp_services()
        
        # 初始化GRAG记忆系统（只在首次初始化时显示日志）
        self.memory_manager = memory_manager
        if self.memory_manager and not SystemState._memory_initialized:
            logger.info("夏园记忆系统已初始化")
            SystemState._memory_initialized = True
        
        # 初始化持久化上下文（只在首次初始化时显示日志）
        if config.api.persistent_context and not SystemState._persistent_context_initialized:
            self._load_persistent_context()
            SystemState._persistent_context_initialized = True
        
        # 初始化语音处理系统
        self.voice = None
        if config.system.voice_enabled:
            try:
                # 语音功能已分为语音输入和输出两个独立模块
                # 语音输入：负责语音识别（ASR）和VAD
                # 语音输出：负责文本转语音（TTS）
                # 使用全局变量避免重复输出日志
                if not SystemState._voice_enabled_logged:
                    logger.info("语音功能已启用（语音输入+输出），由UI层管理")
                    SystemState._voice_enabled_logged = True
            except Exception as e:
                logger.warning(f"语音系统初始化失败: {e}")
                self.voice = None
        
        # 禁用树状思考系统
        self.tree_thinking = None
     
    def _init_agent_server_client(self):
        """初始化Agent Server客户端"""
        try:
            import aiohttp
            self.agent_server_client = aiohttp.ClientSession()
            logger.info("Agent Server客户端初始化成功")
        except Exception as e:
            logger.warning(f"Agent Server客户端初始化失败: {e}")
            self.agent_server_client = None

    async def _call_agent_server_analyze(self, messages: List[Dict[str, str]], session_id: str) -> Dict[str, Any]:
        """调用Agent Server进行意图分析"""
        try:
            if not self.agent_server_client:
                return {"has_tasks": False, "reason": "Agent Server客户端未初始化", "tasks": [], "priority": "low"}
            
            # 调用Agent Server的意图分析接口（端口8002）
            url = "http://localhost:8001/analyze_and_plan"
            payload = {
                "messages": messages,
                "session_id": session_id
            }
            
            async with self.agent_server_client.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        # 返回分析结果（这里需要根据实际API调整）
                        return {
                            "has_tasks": True,
                            "reason": "Agent Server分析完成",
                            "tasks": [],  # 实际任务由Agent Server后台处理
                            "priority": "medium"
                        }
                    else:
                        return {"has_tasks": False, "reason": "Agent Server分析失败", "tasks": [], "priority": "low"}
                else:
                    logger.error(f"Agent Server调用失败: {response.status}")
                    return {"has_tasks": False, "reason": f"HTTP错误: {response.status}", "tasks": [], "priority": "low"}
                    
        except Exception as e:
            logger.error(f"调用Agent Server失败: {e}")
            return {"has_tasks": False, "reason": f"调用失败: {e}", "tasks": [], "priority": "low"}
    
    async def _call_mcp_server(self, query: str, tool_calls: List[Dict[str, Any]], session_id: str = None) -> Dict[str, Any]:
        """调用MCP服务器执行工具调用"""
        try:
            if not self.agent_server_client:
                return {"success": False, "error": "HTTP客户端未初始化", "message": "无法执行MCP任务"}

            # 调用独立的MCP服务器
            url = "http://localhost:8003/schedule"
            payload = {
                "query": query,
                "tool_calls": tool_calls,
                "session_id": session_id
            }

            async with self.agent_server_client.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"MCP服务器调用失败: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "message": error_text
                    }

        except Exception as e:
            logger.error(f"调用MCP服务器失败: {e}")
            return {"success": False, "error": f"调用失败: {e}", "message": f"MCP服务器调用失败: {e}"}

    async def _process_streaming_tool_calls(self, text_chunk: str, session_id: str = "main_session") -> List[str]:
        """处理流式工具调用"""
        try:
            if not self.agent_server_client:
                return []

            # 调用MCPServer的流式处理接口
            url = "http://localhost:8003/stream/process"
            payload = {
                "text_chunk": text_chunk,
                "session_id": session_id
            }

            async with self.agent_server_client.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("results", [])
                else:
                    logger.error(f"流式工具调用处理失败: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"流式工具调用处理失败: {e}")
            return []

    async def _finish_streaming_processing(self, session_id: str = "main_session") -> List[str]:
        """完成流式处理"""
        try:
            if not self.agent_server_client:
                return []

            # 调用MCPServer的完成处理接口
            url = "http://localhost:8003/stream/finish"
            payload = {
                "session_id": session_id
            }

            async with self.agent_server_client.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("final_results", [])
                else:
                    logger.error(f"完成流式处理失败: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"完成流式处理失败: {e}")
            return []
    
    async def _call_agent_server_task(self, query: str, task_type: str, session_id: str = None) -> Dict[str, Any]:
        """调用AgentServer执行多智能体任务"""
        try:
            if not self.agent_server_client:
                return {"success": False, "error": "HTTP客户端未初始化", "message": "无法执行智能体任务"}
            
            # 调用AgentServer的任务调度接口
            url = "http://localhost:8001/tasks/schedule"
            payload = {
                "query": query,
                "task_type": task_type,
                "session_id": session_id
            }
            
            async with self.agent_server_client.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"AgentServer调用失败: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "message": error_text
                    }
                    
        except Exception as e:
            logger.error(f"调用AgentServer失败: {e}")
            return {"success": False, "error": f"调用失败: {e}", "message": f"AgentServer调用失败: {e}"}
    
    def _route_task(self, tool_calls: List[Dict[str, Any]]) -> str:
        """根据工具调用类型路由到合适的服务器"""
        if not tool_calls:
            return "none"
        
        # 检查工具调用类型
        for tool_call in tool_calls:
            agent_type = tool_call.get("agentType", "")
            service_name = tool_call.get("service_name", "")
            
            # MCP工具调用
            if agent_type == "mcp":
                return "mcp"
            
            # 电脑控制任务
            if agent_type == "agent" and "computer" in service_name.lower():
                return "agent"
            
            # 其他智能体任务
            if agent_type == "agent":
                return "agent"
        
        # 默认路由到MCP
        return "mcp"

    def _load_persistent_context(self):
        """从日志文件加载历史对话上下文"""
        if not config.api.context_parse_logs:
            return
            
        try:
            from apiserver.message_manager import message_manager
            
            # 计算最大消息数量
            max_messages = config.api.max_history_rounds * 2
            
            # 加载历史对话
            recent_messages = message_manager.load_recent_context(
                days=config.api.context_load_days,
                max_messages=max_messages
            )
            
            if recent_messages:
                self.messages = recent_messages
                logger.info(f"✅ 从日志文件加载了 {len(self.messages)} 条历史对话")
                
                # 显示统计信息
                try:
                    from apiserver.message_manager import parser
                    stats = parser.get_context_statistics(config.api.context_load_days)
                    logger.info(f"📊 上下文统计: {stats['total_files']}个文件, {stats['total_messages']}条消息")
                except ImportError:
                    logger.info("📊 上下文统计: 日志解析器不可用")
            else:
                logger.info("📝 未找到历史对话记录，将开始新的对话")
                
        except ImportError:
            logger.warning("⚠️ 日志解析器模块未找到，跳过持久化上下文加载")
        except Exception as e:
            logger.error(f"❌ 加载持久化上下文失败: {e}")
            # 失败时不影响正常使用，继续使用空上下文

    def _init_mcp_services(self):
        """初始化MCP服务系统（只在首次初始化时输出日志，后续静默）"""
        if SystemState._mcp_services_initialized:
            # 静默跳过，不输出任何日志
            return
        try:
            # 自动注册所有MCP服务和handoff
            self.mcp.auto_register_services()
            logger.info("MCP服务系统初始化完成")
            SystemState._mcp_services_initialized = True
            
            # 异步启动NagaPortal自动登录
            self._start_naga_portal_auto_login()
            
            # 异步启动物联网通讯连接状态检查
            self._start_mqtt_status_check()
        except Exception as e:
            logger.error(f"MCP服务系统初始化失败: {e}")
    
    def _start_naga_portal_auto_login(self):
        """启动NagaPortal自动登录（异步）"""
        try:
            # 检查是否配置了NagaPortal
            if not config.naga_portal.username or not config.naga_portal.password:
                return  # 静默跳过，不输出日志
            
            # 在新线程中异步执行登录
            def run_auto_login():
                try:
                    import sys
                    import os
                    # 添加项目根目录到Python路径
                    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    sys.path.insert(0, project_root)
                    
                    from mcpserver.agent_naga_portal.portal_login_manager import auto_login_naga_portal
                    
                    # 创建新的事件循环
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        # 执行自动登录
                        result = loop.run_until_complete(auto_login_naga_portal())
                        
                        if result['success']:
                            # 登录成功，显示状态
                            print("✅ NagaPortal自动登录成功")
                            self._show_naga_portal_status()
                        else:
                            # 登录失败，显示错误
                            error_msg = result.get('message', '未知错误')
                            print(f"❌ NagaPortal自动登录失败: {error_msg}")
                            self._show_naga_portal_status()
                    finally:
                        loop.close()
                        
                except Exception as e:
                    # 登录异常，显示错误
                    print(f"❌ NagaPortal自动登录异常: {e}")
                    self._show_naga_portal_status()
            
            # 启动后台线程
            import threading
            login_thread = threading.Thread(target=run_auto_login, daemon=True)
            login_thread.start()
            
        except Exception as e:
            # 启动异常，显示错误
            print(f"❌ NagaPortal自动登录启动失败: {e}")
            self._show_naga_portal_status()

    def _show_naga_portal_status(self):
        """显示NagaPortal状态（登录完成后调用）"""
        try:
            from mcpserver.agent_naga_portal.portal_login_manager import get_portal_login_manager
            login_manager = get_portal_login_manager()
            status = login_manager.get_status()
            cookies = login_manager.get_cookies()
            
            print(f"🌐 NagaPortal状态:")
            print(f"   地址: {config.naga_portal.portal_url}")
            print(f"   用户: {config.naga_portal.username[:3]}***{config.naga_portal.username[-3:] if len(config.naga_portal.username) > 6 else '***'}")
            
            if cookies:
                print(f"🍪 Cookie信息 ({len(cookies)}个):")
                for name, value in cookies.items():
                    print(f"   {name}: {value}")
            else:
                print(f"🍪 Cookie: 未获取到")
            
            user_id = status.get('user_id')
            if user_id:
                print(f"👤 用户ID: {user_id}")
            else:
                print(f"👤 用户ID: 未获取到")
                
            # 显示登录状态
            if status.get('is_logged_in'):
                print(f"✅ 登录状态: 已登录")
            else:
                print(f"❌ 登录状态: 未登录")
                if status.get('login_error'):
                    print(f"   错误: {status.get('login_error')}")
                    
        except Exception as e:
            print(f"🍪 NagaPortal状态获取失败: {e}")
    
    def _start_mqtt_status_check(self):
        """启动物联网通讯连接并显示状态（异步）"""
        try:
            # 检查是否配置了物联网通讯
            if not config.mqtt.enabled:
                return  # 静默跳过，不输出日志
            
            # 在新线程中异步执行物联网通讯连接
            def run_mqtt_connection():
                try:
                    import sys
                    import os
                    import time
                    # 添加项目根目录到Python路径
                    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    sys.path.insert(0, project_root)
                    
                    try:
                        from mqtt_tool.device_switch import device_manager
                        
                        # 尝试连接物联网设备
                        if hasattr(device_manager, 'connect'):
                            success = device_manager.connect()
                            if success:
                                print("🔗 物联网通讯状态: 已连接")
                            else:
                                print("⚠️ 物联网通讯状态: 连接失败（将在使用时重试）")
                        else:
                            print("❌ 物联网通讯功能不可用")
                            
                    except Exception as e:
                        print(f"⚠️ 物联网通讯连接失败: {e}")
                        
                except Exception as e:
                    print(f"❌ 物联网通讯连接异常: {e}")
            
            # 启动后台线程
            import threading
            mqtt_thread = threading.Thread(target=run_mqtt_connection, daemon=True)
            mqtt_thread.start()
            
        except Exception as e:
            print(f"❌ 物联网通讯连接启动失败: {e}")
    
    def save_log(self, u, a):  # 保存对话日志
        if self.dev_mode:
            return  # 开发者模式不写日志
        d = datetime.now().strftime('%Y-%m-%d')
        t = datetime.now().strftime('%H:%M:%S')
        
        # 确保日志目录存在
        log_dir = str(config.system.log_dir)  # 统一为字符串路径 #
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"已创建日志目录: {log_dir}")
        
        # 保存对话日志
        log_file = os.path.join(log_dir, f"{d}.log")  # 组合日志文件路径 #
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{t}] 用户: {u}\n")
                f.write(f"[{t}] {AI_NAME}: {a}\n")
                f.write("-" * 50 + "\n")
        except Exception as e:
            logger.error(f"保存日志失败: {e}")

    def _format_services_for_prompt(self, available_services: dict, intent_analysis: dict = None) -> str:
        """格式化可用服务列表为prompt字符串，MCP服务和Agent服务分开，包含具体调用格式"""
        mcp_services = available_services.get("mcp_services", [])
        agent_services = available_services.get("agent_services", [])
        
        # 获取本地城市信息和当前时间
        local_city = "未知城市"
        current_time = ""
        try:
            # 从WeatherTimeAgent获取本地城市信息
            from mcpserver.agent_weather_time.agent_weather_time import WeatherTimeTool
            weather_tool = WeatherTimeTool()
            local_city = getattr(weather_tool, '_local_city', '未知城市') or '未知城市'
            
            # 获取当前时间
            from datetime import datetime
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"[DEBUG] 获取本地信息失败: {e}")
        
        # 格式化MCP服务列表，包含具体调用格式
        mcp_list = []
        for service in mcp_services:
            name = service.get("name", "")
            description = service.get("description", "")
            display_name = service.get("display_name", name)
            tools = service.get("available_tools", [])
            
            # 展示name+displayName
            if description:
                mcp_list.append(f"- {name}: {description}")
            else:
                mcp_list.append(f"- {name}")
            
            # 为每个工具显示具体调用格式
            if tools:
                for tool in tools:
                    tool_name = tool.get('name', '')
                    tool_desc = tool.get('description', '')
                    tool_example = tool.get('example', '')
                    
                    if tool_name and tool_example:
                        # 解析示例JSON，提取参数
                        try:
                            import json
                            example_data = json.loads(tool_example)
                            params = []
                            for key, value in example_data.items():
                                if key != 'tool_name':
                                    params.append(f"{key}: {value}")  # 不再需要对天气进行特殊处理
                            
                            # 构建调用格式
                            format_str = f"  {tool_name}: ｛\n"
                            format_str += f"    \"agentType\": \"mcp\",\n"
                            format_str += f"    \"service_name\": \"{name}\",\n"
                            format_str += f"    \"tool_name\": \"{tool_name}\",\n"
                            for param in params:
                                # 将中文参数名转换为英文
                                param_key, param_value = param.split(': ', 1)
                                format_str += f"    \"{param_key}\": \"{param_value}\",\n"
                            format_str += f"  ｝\n"
                            
                            mcp_list.append(format_str)
                        except:
                            # 如果JSON解析失败，使用简单格式
                            mcp_list.append(f"  {tool_name}: 使用tool_name参数调用")
        
        # 格式化Agent服务列表
        agent_list = []
        
        # 1. 添加handoff服务
        for service in agent_services:
            name = service.get("name", "")
            description = service.get("description", "")
            tool_name = service.get("tool_name", "agent")
            display_name = service.get("display_name", name)
            # 展示name+displayName
            if description:
                agent_list.append(f"- {name}(工具名: {tool_name}): {description}")
            else:
                agent_list.append(f"- {name}(工具名: {tool_name})")
        
        # 2. 直接从AgentManager获取已注册的Agent
        try:
            from agentserver.core.agent_manager import get_agent_manager
            agent_manager = get_agent_manager()
            agent_manager_agents = agent_manager.get_available_agents()
            
            for agent in agent_manager_agents:
                name = agent.get("name", "")
                base_name = agent.get("base_name", "")
                description = agent.get("description", "")
                
                # 展示格式：base_name: 描述
                if description:
                    agent_list.append(f"- {base_name}: {description}")
                else:
                    agent_list.append(f"- {base_name}")
                    
        except Exception as e:
            # 如果AgentManager不可用，静默处理
            pass
        
        # 添加本地信息说明
        local_info = f"\n\n【当前环境信息】\n- 本地城市: {local_city}\n- 当前时间: {current_time}\n\n【使用说明】\n- 天气/时间查询时，请使用上述本地城市信息作为city参数\n- 所有时间相关查询都基于当前系统时间"
        
        # 添加意图分析结果（如果有）
        intent_info = ""
        if intent_analysis and intent_analysis.get("has_tasks", False):
            tasks = intent_analysis.get("tasks", [])
            priority = intent_analysis.get("priority", "medium")
            reason = intent_analysis.get("reason", "")
            
            intent_info = f"\n\n【意图分析结果】\n- 检测到 {len(tasks)} 个潜在任务 (优先级: {priority})\n- 分析原因: {reason}\n"
            if tasks:
                intent_info += "- 建议优先处理的任务:\n"
                for i, task in enumerate(tasks, 1):
                    intent_info += f"  {i}. {task}\n"
            intent_info += "\n【重要】如果用户请求与上述任务相关，请优先使用工具调用来执行任务，而不是仅提供建议。"
        
        # 返回格式化的服务列表
        result = {
            "available_mcp_services": "\n".join(mcp_list) + local_info + intent_info if mcp_list else "无" + local_info + intent_info,
            "available_agent_services": "\n".join(agent_list) if agent_list else "无"
        }
        
        return result

    async def process(self, u, is_voice_input=False):  # 添加is_voice_input参数
        try:
            # 开发者模式优先判断
            if u.strip().lower() == "#devmode":
                self.dev_mode = not self.dev_mode  # 切换模式
                status = "进入" if self.dev_mode else "退出"
                yield (AI_NAME, f"已{status}开发者模式")
                return

            # 只在语音输入时显示处理提示
            if is_voice_input:
                print(f"开始处理用户输入：{now()}")  # 语音转文本结束，开始处理
            
            # 异步启动意图分析（使用Agent Server）
            intent_analysis_task = None
            if not self.dev_mode and self.agent_server_client:  # 开发者模式跳过意图分析
                try:
                    # 构建分析用的消息格式
                    analysis_messages = []
                    for msg in self.messages[-5:]:  # 只分析最近5条消息
                        analysis_messages.append({
                            "role": msg.get("role", "user"),
                            "content": msg.get("content", "")
                        })
                    # 添加当前用户消息
                    analysis_messages.append({
                        "role": "user", 
                        "content": u
                    })
                    
                    # 异步启动意图分析（通过Agent Server）
                    intent_analysis_task = asyncio.create_task(
                        self._call_agent_server_analyze(analysis_messages, "main_session")
                    )
                    print(f"🧠 启动意图分析：{now()}")
                except Exception as e:
                    logger.debug(f"意图分析启动失败: {e}")
                    intent_analysis_task = None
                     
            # 获取过滤后的服务列表
            available_services = self.mcp.get_available_services_filtered()
            
            # 检查意图分析是否完成
            intent_analysis = None
            if intent_analysis_task and intent_analysis_task.done():
                try:
                    intent_analysis = intent_analysis_task.result()
                    print(f"🧠 意图分析完成：{now()}")
                    if intent_analysis.get("has_tasks", False):
                        tasks = intent_analysis.get("tasks", [])
                        print(f"   发现 {len(tasks)} 个潜在任务")
                except Exception as e:
                    logger.debug(f"获取意图分析结果失败: {e}")
            
            # 生成可用服务片段（已不再拼接能力摘要，信息来源于最新意图分析）
            # 生成系统提示词（不再注入服务占位符）
            system_prompt = get_prompt("naga_system_prompt", ai_name=AI_NAME)
            
            # 使用消息管理器统一的消息拼接逻辑（UI界面使用）
            from apiserver.message_manager import message_manager
            msgs = message_manager.build_conversation_messages_from_memory(
                memory_messages=self.messages,
                system_prompt=system_prompt,
                current_message=u,
                max_history_rounds=config.api.max_history_rounds
            )

            print(f"GTP请求发送：{now()}")  # AI请求前
            # 流式处理：实时检测工具调用，使用统一的工具调用循环
            try:
                # 导入流式文本切割器（不再解析或执行工具） # 保持纯聊天流式
                from apiserver.streaming_tool_extractor import StreamingToolCallExtractor
                
                tool_extractor = StreamingToolCallExtractor(self.mcp)  # 仅用于TTS分句 #
                
                # 用于累积前端显示的纯文本（不包含工具调用） #
                display_text = ""
                
                # 设置回调函数（仅文本块） #
                def on_text_chunk(text: str, chunk_type: str):
                    if chunk_type == "chunk":
                        nonlocal display_text
                        display_text += text
                        return (AI_NAME, text)
                    return None
                
                tool_extractor.set_callbacks(on_text_chunk=on_text_chunk)
                
                # 调用LLM API - 流式模式（仅聊天） #
                resp = await self.async_client.chat.completions.create(
                    model=config.api.model,
                    messages=msgs,
                    temperature=config.api.temperature,
                    max_tokens=config.api.max_tokens,
                    stream=True
                )
                
                # 处理流式响应 #
                async for chunk in resp:
                    try:
                        delta = getattr(chunk.choices[0], 'delta', None) if chunk.choices else None
                        if delta is not None:
                            logger.info("openai.delta: %r", getattr(delta, 'content', None))
                    except Exception:
                        pass

                    if (chunk.choices and 
                        len(chunk.choices) > 0 and 
                        hasattr(chunk.choices[0], 'delta') and 
                        chunk.choices[0].delta.content):
                        content = chunk.choices[0].delta.content
                        await tool_extractor.process_text_chunk(content)
                        # 将文本块直接推送前端 #
                        yield (AI_NAME, content)
                
                # 完成处理 #
                await tool_extractor.finish_processing()
                
                # 等待意图分析完成（最多等待2秒） #
                if intent_analysis_task and not intent_analysis_task.done():
                    try:
                        await asyncio.wait_for(intent_analysis_task, timeout=2.0)
                        final_intent_analysis = intent_analysis_task.result()
                        if final_intent_analysis.get("has_tasks", False):
                            tasks = final_intent_analysis.get("tasks", [])
                            print(f"🧠 意图分析最终结果：发现 {len(tasks)} 个潜在任务")
                    except asyncio.TimeoutError:
                        print(f"🧠 意图分析超时，继续处理")
                    except Exception as e:
                        logger.debug(f"等待意图分析完成失败: {e}")
                
                # 保存对话历史（使用前端显示的纯文本）
                print(f"[DEBUG] 最终display_text长度: {len(display_text)}")
                print(f"[DEBUG] 最终display_text内容: {display_text[:200]}...")
                self.messages += [{"role": "user", "content": u}, {"role": "assistant", "content": display_text}]
                self.save_log(u, display_text)
                
                # GRAG记忆存储（开发者模式不写入）- 使用前端显示的纯文本
                if self.memory_manager and not self.dev_mode:
                    try:
                        # 使用前端显示的纯文本进行五元组提取
                        await self.memory_manager.add_conversation_memory(u, display_text)
                    except Exception as e:
                        logger.error(f"GRAG记忆存储失败: {e}")
                
            except Exception as e:
                print(f"工具调用循环失败: {e}")
                # 区分API错误和MCP错误
                if "API" in str(e) or "api" in str(e) or "HTTP" in str(e) or "连接" in str(e):
                    yield (AI_NAME, f"[API调用异常]: {e}")
                else:
                    yield (AI_NAME, f"[MCP服务异常]: {e}")
                return

            return
        except Exception as e:
            import sys
            import traceback
            traceback.print_exc(file=sys.stderr)
            # 区分API错误和MCP错误
            if "API" in str(e) or "api" in str(e) or "HTTP" in str(e) or "连接" in str(e):
                yield (AI_NAME, f"[API调用异常]: {e}")
            else:
                yield (AI_NAME, f"[MCP服务异常]: {e}")
            return

    async def get_response(self, prompt: str, temperature: float = 0.7) -> str:
        """为树状思考系统等提供API调用接口""" # 统一接口
        try:
            response = await self.async_client.chat.completions.create(
                model=config.api.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=config.api.max_tokens
            )
            return response.choices[0].message.content
        except RuntimeError as e:
            if "handler is closed" in str(e):
                logger.debug(f"忽略连接关闭异常，重新创建客户端: {e}")
                # 重新创建客户端并重试
                self.async_client = AsyncOpenAI(api_key=config.api.api_key, base_url=config.api.base_url.rstrip('/') + '/')
                response = await self.async_client.chat.completions.create(
                    model=config.api.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=config.api.max_tokens
                )
                return response.choices[0].message.content
            else:
                logger.error(f"API调用失败: {e}")
                return f"API调用出错: {str(e)}"
        except Exception as e:
            logger.error(f"API调用失败: {e}")
            return f"API调用出错: {str(e)}"

async def process_user_message(s,msg):
    if config.system.voice_enabled and not msg: #无文本输入时启动语音识别
        async for text in s.voice.stt_stream():
            if text:
                msg=text
                break
        return await s.process(msg, is_voice_input=True)  # 语音输入
    return await s.process(msg, is_voice_input=False)  # 文字输入
