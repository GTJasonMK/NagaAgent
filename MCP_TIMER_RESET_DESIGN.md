# MCP调用后重置ProactiveVision计时器 - 设计文档

## 问题场景

### 重复分析问题
```
时间线：
00:00 - 用户问AI："看一下右边是什么"
00:01 - AI调用screen_vision MCP → 截图+分析（耗时3秒）
00:04 - AI分析完成，回复用户
00:05 - ProactiveVision定时器触发（假设间隔30秒）
00:06 - ProactiveVision调用screen_vision → 重复分析同一屏幕！❌
```

### 资源浪费
- **重复截图** - 同一屏幕截图2次
- **重复AI分析** - 同一内容分析2次（成本高！）
- **用户体验差** - AI刚看过又主动提醒相同内容

### 典型场景
1. 用户："帮我看看这个错误"
2. AI调用screen_vision分析
3. 几秒后ProactiveVision也触发 → 重复分析

---

## 解决方案

### 核心思路
**当AI主动调用screen_vision MCP时，重置ProactiveVision的检查计时器，延迟下次检查。**

### 流程设计

```
┌─────────────┐
│   用户请求   │ "看一下右边"
└──────┬──────┘
       │
       v
┌─────────────┐
│  AI调用MCP  │ screen_vision
└──────┬──────┘
       │
       v
┌─────────────────────────┐
│   MCP Server /call      │
│   service=screen_vision │
└──────┬──────────────────┘
       │
       ├──────────────────────────────┐
       │                              │
       v                              v
┌─────────────┐              ┌──────────────────┐
│ 执行截图分析 │              │  异步通知Agent   │
└──────┬──────┘              │  重置PV计时器    │
       │                     └──────────────────┘
       v                              │
┌─────────────┐                       v
│  返回结果   │              ┌──────────────────┐
└─────────────┘              │ ProactiveVision  │
                             │ _last_check_time │
                             │ = time.time()    │
                             └──────────────────┘
                                      │
                                      v
                             下次检查延迟30秒 ✅
```

---

## 实现细节

### 1. ProactiveVision Scheduler 添加重置方法

**文件：** `agentserver/proactive_vision/scheduler.py`

```python
def reset_check_timer(self, reason: str = "external_trigger"):
    """重置检查计时器，延迟下次检查

    当外部触发screen_vision调用时（如AI主动调用），应重置计时器避免重复分析。

    Args:
        reason: 重置原因，用于日志记录
    """
    self._last_check_time = time.time()
    logger.info(
        f"[ProactiveVision] 检查计时器已重置 (原因: {reason})，"
        f"下次检查将在{self.config.check_interval_seconds}秒后"
    )
```

**作用：**
- 更新 `_last_check_time` 为当前时间
- 导致 `_should_check_now()` 判断未到间隔时间，跳过检查

---

### 2. Agent Server 添加重置API

**文件：** `agentserver/agent_server.py`

**端点：** `POST /proactive_vision/reset_timer`

```python
@app.post("/proactive_vision/reset_timer")
async def reset_proactive_vision_timer(payload: Dict[str, Any]):
    """重置ProactiveVision检查计时器（由MCP Server调用）

    当AI主动调用screen_vision MCP时，MCP Server会调用此API重置计时器，
    避免ProactiveVision短时间内重复分析同一屏幕。

    Args:
        payload: {"reason": "mcp_call_screen_vision"}
    """
    try:
        reason = payload.get("reason", "external_trigger")

        if Modules.proactive_scheduler:
            Modules.proactive_scheduler.reset_check_timer(reason)
            return {
                "success": True,
                "message": "计时器已重置",
                "reason": reason,
            }
        else:
            return {
                "success": False,
                "error": "ProactiveVision调度器未初始化",
            }
    except Exception as e:
        logger.error(f"重置ProactiveVision计时器失败: {e}")
        return {"success": False, "error": str(e)}
```

**调用者：** MCP Server

---

### 3. MCP Server 调用后通知

**文件：** `mcpserver/mcp_server.py`

**修改点：** `/call` 端点

```python
@app.post("/call")
async def call_tool(req: ToolCallRequest):
    """调用单个MCP工具 - 同步返回结果"""
    from mcpserver.mcp_manager import get_mcp_manager
    manager = get_mcp_manager()

    tool_call = {
        "service_name": req.service_name,
        "tool_name": req.tool_name,
        "message": req.message,
        **req.params
    }

    try:
        result = await manager.unified_call(req.service_name, tool_call)

        # ✅ 如果调用的是screen_vision，通知ProactiveVision重置计时器
        if req.service_name == "screen_vision":
            asyncio.create_task(_notify_proactive_vision_reset())

        return {"status": "ok", "result": result}
    except Exception as e:
        logger.error(f"[MCP Server] 工具调用失败: service={req.service_name}, error={e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**通知函数：**
```python
async def _notify_proactive_vision_reset():
    """通知ProactiveVision重置检查计时器

    当AI主动调用screen_vision时，通知ProactiveVision延迟下次检查，
    避免短时间内重复分析同一屏幕。
    """
    try:
        import httpx
        from system.config import get_server_port

        agent_port = get_server_port("agent_server")
        url = f"http://127.0.0.1:{agent_port}/proactive_vision/reset_timer"

        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(url, json={"reason": "mcp_call_screen_vision"})
            if resp.status_code == 200:
                result = resp.json()
                if result.get("success"):
                    logger.debug("[MCP Server] 已通知ProactiveVision重置计时器")
                else:
                    logger.debug(f"[MCP Server] ProactiveVision重置失败: {result.get('error')}")
            else:
                logger.debug(f"[MCP Server] ProactiveVision通知失败: HTTP {resp.status_code}")
    except Exception as e:
        # 静默失败，不影响主流程
        logger.debug(f"[MCP Server] ProactiveVision通知异常（忽略）: {e}")
```

**特性：**
- 异步通知（不阻塞MCP调用返回）
- 静默失败（通知失败不影响screen_vision调用）
- 超时保护（3秒超时）
- Debug级别日志（不干扰主日志）

---

## 效果验证

### 场景1：AI调用screen_vision后

**时间线（优化后）：**
```
00:00 - 用户："看一下右边"
00:01 - AI调用screen_vision → 截图+分析
00:01 - MCP Server通知Agent Server重置计时器 ✅
00:04 - AI回复用户
00:05 - ProactiveVision检查：距离上次重置仅4秒 < 30秒 → 跳过 ✅
00:31 - ProactiveVision检查：距离重置30秒 → 执行检查
```

**日志：**
```
[MCP Server] 已通知ProactiveVision重置计时器
[ProactiveVision] 检查计时器已重置 (原因: mcp_call_screen_vision)，下次检查将在30秒后
```

---

### 场景2：连续多次AI调用

**时间线：**
```
00:00 - AI调用screen_vision #1 → 重置计时器
00:10 - AI调用screen_vision #2 → 再次重置计时器 ✅
00:20 - AI调用screen_vision #3 → 再次重置计时器 ✅
00:50 - ProactiveVision检查：距离最后一次重置30秒 → 执行
```

**效果：** 频繁AI调用期间，ProactiveVision一直延迟，避免冲突 ✅

---

### 场景3：ProactiveVision未启用

**行为：**
```python
# Agent Server API
if Modules.proactive_scheduler:
    # 重置计时器
else:
    return {"success": False, "error": "调度器未初始化"}
```

**效果：** 返回失败，但不影响MCP调用（静默失败）✅

---

## 优势分析

### 1. 资源节省
- **避免重复截图** - 节省~50ms/次
- **避免重复AI分析** - 节省~3秒和API成本
- **减少系统负载** - 减少CPU/GPU占用

### 2. 用户体验
- **避免重复通知** - AI刚分析过，不会立即主动提醒相同内容
- **更智能的触发** - ProactiveVision与AI协同工作

### 3. 实现优雅
- **异步通知** - 不阻塞MCP调用
- **静默失败** - 通知失败不影响主流程
- **低耦合** - MCP Server和ProactiveVision松耦合
- **可扩展** - 未来可支持其他MCP工具触发重置

---

## 边缘情况处理

### 情况1：Agent Server未启动
**现象：** MCP Server通知失败（连接拒绝）
**处理：** 静默失败，记录debug日志
**影响：** 无，screen_vision正常返回

### 情况2：ProactiveVision未启用
**现象：** API返回 `{"success": false, "error": "调度器未初始化"}`
**处理：** MCP Server记录debug日志
**影响：** 无

### 情况3：通知超时
**现象：** httpx.TimeoutException（3秒超时）
**处理：** 捕获异常，记录debug日志
**影响：** 无

### 情况4：AI调用非screen_vision工具
**现象：** `req.service_name != "screen_vision"`
**处理：** 不触发通知
**影响：** 无

---

## 性能影响

### MCP Server增加的开销
- **异步HTTP请求** - 不阻塞返回，开销可忽略
- **超时时间** - 3秒（实际通常<10ms）
- **内存占用** - 一个异步Task，可忽略

### Agent Server增加的开销
- **API处理** - 简单的时间戳更新，<1ms
- **内存占用** - 无额外占用

### 总体评估
**性能影响：可忽略（<1%）**

---

## 测试建议

### 单元测试
```python
# 测试计时器重置
def test_reset_check_timer():
    scheduler = ProactiveVisionScheduler(config)
    initial_time = scheduler._last_check_time

    time.sleep(1)
    scheduler.reset_check_timer("test")

    assert scheduler._last_check_time > initial_time
```

### 集成测试
```bash
# 1. 启动所有服务
python -m mcpserver.mcp_server &
python -m agentserver.agent_server &

# 2. 调用screen_vision
curl -X POST http://127.0.0.1:8003/call \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "screen_vision",
    "tool_name": "look_screen",
    "message": "测试"
  }'

# 3. 检查日志
# 预期：
# [MCP Server] 已通知ProactiveVision重置计时器
# [ProactiveVision] 检查计时器已重置 (原因: mcp_call_screen_vision)
```

### E2E测试
```
1. 启用ProactiveVision（间隔30秒）
2. 用户问AI："看一下屏幕"
3. AI调用screen_vision
4. 等待5秒
5. 检查：ProactiveVision未触发（因为计时器被重置）✅
6. 等待25秒（总共30秒）
7. 检查：ProactiveVision触发检查 ✅
```

---

## 未来扩展

### 1. 支持其他MCP工具
```python
# 可配置哪些MCP调用会重置计时器
RESET_TRIGGER_TOOLS = ["screen_vision", "other_vision_tool"]

if req.service_name in RESET_TRIGGER_TOOLS:
    asyncio.create_task(_notify_proactive_vision_reset())
```

### 2. 智能延迟策略
```python
# 根据调用频率动态调整延迟时间
if recent_calls > 3:
    delay = 60  # 频繁调用，延迟更久
else:
    delay = 30  # 正常延迟
```

### 3. 通知其他系统
```python
# 重置计时器时，可以触发其他事件
def reset_check_timer(self, reason: str):
    self._last_check_time = time.time()
    # 触发自定义钩子
    self._on_timer_reset(reason)
```

---

## 总结

### 已实现功能
✅ MCP Server调用screen_vision时异步通知Agent Server
✅ Agent Server重置ProactiveVision检查计时器
✅ 静默失败机制，不影响主流程
✅ 完整的日志记录

### 解决的问题
✅ AI调用screen_vision后，避免ProactiveVision短时间内重复分析
✅ 节省资源（截图、AI分析成本）
✅ 改善用户体验（避免重复通知）

### 代码质量
✅ 低耦合设计（MCP Server和ProactiveVision解耦）
✅ 异步非阻塞（不影响MCP调用性能）
✅ 健壮的错误处理（静默失败）
✅ 清晰的日志（便于调试）

### 下一步
1. 部署测试（验证实际效果）
2. 监控日志（观察重置频率）
3. 用户反馈（确认体验改善）

---

**文档版本：** 1.0
**实现状态：** ✅ 已完成
**测试状态：** 待验证
