# ProactiveVision 线程安全和并发问题深度排查

## 问题1：❌ 缺失create_*工厂函数导出（已修复）

### 问题
```python
# agent_server.py:287-291
from agentserver.proactive_vision import (
    load_proactive_config,
    create_proactive_scheduler,  # ❌ 未在__init__.py导出
    create_proactive_analyzer,   # ❌ 未在__init__.py导出
    create_proactive_trigger,    # ❌ 未在__init__.py导出
)
```

### 后果
- ImportError导致agent_server启动失败
- ProactiveVision完全无法初始化

### 修复
✅ 已在`__init__.py`添加导出：
```python
from .scheduler import create_proactive_scheduler
from .analyzer import create_proactive_analyzer
from .trigger import create_proactive_trigger
```

---

## 问题2：⚠️ 全局单例的线程安全问题

### 当前实现
```python
# scheduler.py
_scheduler: Optional[ProactiveVisionScheduler] = None

def create_proactive_scheduler(config: ProactiveVisionConfig) -> ProactiveVisionScheduler:
    global _scheduler
    if _scheduler is not None:
        logger.warning("[ProactiveVision] 调度器已存在，将被替换")
    _scheduler = ProactiveVisionScheduler(config)
    return _scheduler
```

### 潜在问题

#### 2.1 竞态条件（Race Condition）
**场景：** 配置更新时并发访问
```python
# agent_server.py:1667-1673
await Modules.proactive_scheduler.stop()  # Thread A: 停止旧调度器
# ⚠️ 此时另一个请求可能正在访问 _scheduler
create_proactive_scheduler(new_config)   # Thread A: 替换全局单例
```

**后果：**
- Thread B可能访问到已停止但未替换的调度器
- Thread B可能在替换过程中访问到None

**概率：** 低（FastAPI单进程，但async并发）

#### 2.2 内存泄漏风险
**问题：** 旧调度器被替换但未正确清理
```python
if _scheduler is not None:
    logger.warning("[ProactiveVision] 调度器已存在，将被替换")
    # ❌ 没有调用 await _scheduler.stop()
    # ❌ 旧调度器的asyncio.Task可能仍在运行
```

**后果：**
- 旧的`_schedule_loop` Task仍在后台运行
- 多个调度器同时执行屏幕检查
- 内存和CPU占用累积

**概率：** 高（每次配置更新都会发生）

### 修复方案

#### 方案A：线程锁（不推荐 - async不兼容）
```python
import threading
_lock = threading.Lock()  # ❌ 不适用于asyncio
```

#### 方案B：asyncio锁 + 优雅替换（推荐）
```python
_scheduler_lock = asyncio.Lock()

async def replace_proactive_scheduler(config: ProactiveVisionConfig) -> ProactiveVisionScheduler:
    """线程安全地替换调度器"""
    global _scheduler

    async with _scheduler_lock:
        old_scheduler = _scheduler

        # 停止旧调度器
        if old_scheduler is not None:
            await old_scheduler.stop()

        # 创建新调度器
        _scheduler = ProactiveVisionScheduler(config)

        return _scheduler
```

---

## 问题3：⚠️ asyncio.Task生命周期管理

### 当前实现
```python
# scheduler.py:34
self._task = asyncio.create_task(self._schedule_loop())
```

### 潜在问题

#### 3.1 Task未正确取消
```python
async def stop(self):
    self._running = False
    if self._task:
        self._task.cancel()
        try:
            await self._task  # ⚠️ 等待取消完成
        except asyncio.CancelledError:
            pass  # ✅ 正确处理
```

**分析：** ✅ 当前实现正确，有try-except处理CancelledError

#### 3.2 Task异常未捕获导致僵死
```python
# scheduler.py:72-77
except asyncio.CancelledError:
    logger.info("[ProactiveVision] 调度循环被取消")
    break
except Exception as e:
    logger.error(f"[ProactiveVision] 调度循环异常: {e}", exc_info=True)
    await asyncio.sleep(5)  # ✅ 异常后等待5秒重试
```

**分析：** ✅ 有异常处理和重试机制

#### 3.3 多次start()导致Task泄漏
```python
async def start(self):
    if self._running:
        logger.warning("[ProactiveVision] 调度器已在运行")
        return  # ✅ 防止重复启动

    self._running = True
    self._task = asyncio.create_task(self._schedule_loop())
```

**分析：** ✅ 有防护检查

---

## 问题4：⚠️ 截图提供者的进程安全

### 问题
```python
# analyzer.py:_capture_screenshot
from guide_engine.screenshot_provider import get_screenshot_provider
screenshot_provider = get_screenshot_provider()
screenshot_result = screenshot_provider.capture_data_url()
```

### 潜在问题

#### 4.1 mss库的线程安全性
mss库使用系统级截图API（Win32/X11/Quartz），部分实现**不是线程安全**的。

**Windows (mss):**
```python
with mss.mss() as sct:
    shot = sct.grab(monitor)
```
- Win32 API **不保证线程安全**
- 多个线程同时调用可能导致截图损坏或崩溃

**后果：**
- 如果ProactiveVision和用户手动触发screen_vision同时执行
- 可能导致截图数据损坏或程序崩溃

**概率：** 中等（取决于用户操作频率）

#### 4.2 临时文件冲突
部分截图后端（scrot、screencapture）使用临时文件：
```python
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
    tmp_path = tmp.name
subprocess.run(["scrot", tmp_path], ...)
```

**问题：** ✅ 使用NamedTemporaryFile，文件名唯一，无冲突

### 修复方案

#### 方案A：全局截图锁（推荐）
```python
# screenshot_provider.py
_screenshot_lock = asyncio.Lock()

class ScreenshotProvider:
    async def capture_data_url_async(self, monitor_index: int | None = None):
        async with _screenshot_lock:
            # 同步代码在线程池中执行
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.capture_data_url, monitor_index)
```

#### 方案B：ProactiveVision专用截图实例（简单但效率低）
```python
# analyzer.py
self._screenshot_provider = ScreenshotProvider()  # 每个analyzer独立实例
```

---

## 问题5：⚠️ HTTP客户端的资源泄漏

### 当前实现
```python
# analyzer.py:269
async with httpx.AsyncClient(timeout=30.0) as client:
    resp = await client.post(url, json=payload)
```

### 分析
✅ **正确使用async with** - 客户端会自动关闭连接

### 潜在优化
每次创建新客户端有开销，可以复用：
```python
class ProactiveVisionAnalyzer:
    def __init__(self, config):
        self._http_client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        await self._http_client.aclose()
```

**权衡：**
- 优点：减少连接开销
- 缺点：需要在scheduler停止时调用close()

**建议：** 当前实现可接受，除非性能测试发现瓶颈

---

## 问题6：⚠️ 配置热更新的原子性

### 当前流程
```python
# agent_server.py:1661-1680
was_running = Modules.proactive_scheduler._running

# 1. 停止旧调度器
await Modules.proactive_scheduler.stop()

# 2. 重新创建（⚠️ 期间服务不可用）
create_proactive_analyzer(new_config)
Modules.proactive_scheduler = create_proactive_scheduler(new_config)

# 3. 启动新调度器
await Modules.proactive_scheduler.start()
```

### 潜在问题

#### 6.1 配置更新期间服务中断
**时间窗口：** stop() + create() + start() ≈ 1-2秒
**影响：** 期间所有ProactiveVision API返回错误或过期数据

#### 6.2 更新失败回滚不完整
```python
except Exception as e:
    # 尝试恢复旧配置
    old_config = load_proactive_config()  # ❌ 这里加载的是新配置（已保存）
    create_proactive_analyzer(old_config)
```

**问题：** `load_proactive_config()`加载的是**磁盘上的新配置**，而非旧配置！

### 修复方案
```python
# 1. 先备份旧配置（内存中）
old_config_backup = Modules.proactive_scheduler.config  # 从运行时对象获取

# 2. 更新
try:
    create_proactive_analyzer(new_config)
    Modules.proactive_scheduler = create_proactive_scheduler(new_config)
except Exception as e:
    # 3. 回滚到内存备份
    create_proactive_analyzer(old_config_backup)
    Modules.proactive_scheduler = create_proactive_scheduler(old_config_backup)
```

---

## 问题7：✅ WebSocket广播的并发安全

### 当前实现
```python
# websocket_manager.py
async def broadcast(self, message: Dict[str, Any], exclude_session: str = None):
    message_json = json.dumps(message, ensure_ascii=False)
    dead_connections = []

    for ws in list(self._global_connections):  # ✅ 使用list()创建副本
        try:
            await ws.send_text(message_json)
        except:
            dead_connections.append(ws)

    for ws in dead_connections:
        self._global_connections.discard(ws)  # ✅ 安全移除
```

### 分析
✅ **正确处理** - 迭代副本，安全移除失效连接

---

## 问题8：⚠️ 差异检测的内存占用

### 当前实现
```python
# analyzer.py
self._last_screenshot_hash: Optional[str] = None  # 仅16字节
```

### 分析
✅ **内存占用可忽略** - 仅存储hash字符串（16-64字节）

### 潜在优化
如果未来需要"对比相似度"而非"是否相同"：
```python
# 存储上次截图（可选）
if self.config.store_last_screenshot:
    self._last_screenshot_data = screenshot_data_url  # ⚠️ 可能~500KB
```

**建议：** 当前不存储截图数据，保持内存友好

---

## 问题9：⚠️ AI调用的超时和取消

### 当前实现
```python
# analyzer.py:269
async with httpx.AsyncClient(timeout=30.0) as client:
    resp = await client.post(url, json=payload)
```

### 潜在问题

#### 9.1 调度器停止时AI调用未取消
**场景：**
```
1. 调度器触发analyze_screen()
2. analyze_screen()调用AI（耗时3-5秒）
3. 用户触发stop()
4. ❌ AI调用仍在进行，未取消
```

**后果：**
- stop()需要等待AI调用完成
- 关闭延迟3-5秒

**修复方案：**
```python
# scheduler.py
async def stop(self):
    self._running = False
    if self._task:
        self._task.cancel()  # ✅ 会取消所有子任务（包括AI调用）
        try:
            await self._task
        except asyncio.CancelledError:
            pass
```

**分析：** ✅ Task.cancel()会传播取消信号，AI调用会收到CancelledError

#### 9.2 超时时间设置
- screen_vision调用：30秒
- trigger推送：3秒（WebSocket）、5秒（HTTP）

**分析：** ✅ 超时设置合理

---

## 问题10：⚠️ 日志并发写入

### 当前实现
```python
logger = logging.getLogger(__name__)
logger.info("[ProactiveVision] ...")
```

### 分析
✅ **Python logging模块是线程安全的** - 使用内部锁保护

---

## 总结：严重性分级

### 🔴 严重问题（必须修复）
1. **缺失create_*导出** - ✅ 已修复
2. **全局单例未停止旧调度器** - ❌ 必须修复（内存泄漏）
3. **配置回滚加载新配置** - ❌ 必须修复（回滚失败）

### 🟡 中等问题（建议修复）
4. **截图提供者线程安全** - 建议添加锁
5. **配置更新原子性** - 建议优化

### 🟢 轻微问题（可选优化）
6. **HTTP客户端复用** - 性能优化
7. **差异检测内存** - 已经很优秀

### ✅ 无问题
8. asyncio.Task生命周期管理
9. WebSocket广播并发安全
10. 日志线程安全
11. AI调用取消机制
