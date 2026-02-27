"""
Proactive Vision 调度器
负责定时截图和任务编排
"""

import asyncio
import time
import logging
from datetime import datetime, time as dt_time
from typing import Optional

from .config import ProactiveVisionConfig

logger = logging.getLogger(__name__)


class ProactiveVisionScheduler:
    """主动视觉调度器"""

    def __init__(self, config: ProactiveVisionConfig):
        self.config = config
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._last_check_time = 0.0
        self._last_user_activity_time = time.time()
        self._window_mode: str = "classic"  # 窗口模式：classic/ball/compact/full
        self._paused_by_mode = False  # 是否因为窗口模式而暂停

    async def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("[ProactiveVision] 调度器已在运行")
            return

        self._running = True
        self._task = asyncio.create_task(self._schedule_loop())
        logger.info(f"[ProactiveVision] 调度器已启动 (间隔: {self.config.check_interval_seconds}s)")

    async def stop(self):
        """停止调度器"""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("[ProactiveVision] 调度器已停止")

    def update_user_activity(self):
        """更新用户活动时间（由对话接口调用）"""
        self._last_user_activity_time = time.time()
        logger.debug("[ProactiveVision] 用户活动时间已更新")

    def reset_check_timer(self, reason: str = "external_trigger"):
        """重置检查计时器，延迟下次检查

        当外部触发screen_vision调用时（如AI主动调用），应重置计时器避免重复分析。

        Args:
            reason: 重置原因，用于日志记录
        """
        self._last_check_time = time.time()
        logger.info(f"[ProactiveVision] 检查计时器已重置 (原因: {reason})，下次检查将在{self.config.check_interval_seconds}秒后")

    def set_window_mode(self, mode: str):
        """设置窗口模式（由前端API调用）

        Args:
            mode: 窗口模式 - classic(主界面)/ball(悬浮球)/compact(紧凑)/full(完整)
        """
        old_mode = self._window_mode
        self._window_mode = mode

        # 判断是否需要暂停/恢复
        is_floating = mode in ("ball", "compact", "full")
        old_is_floating = old_mode in ("ball", "compact", "full")

        if is_floating and not old_is_floating:
            self._paused_by_mode = False
            logger.info(f"[ProactiveVision] 进入悬浮球模式 ({mode})，ProactiveVision已启用")
        elif not is_floating and old_is_floating:
            self._paused_by_mode = True
            logger.info(f"[ProactiveVision] 退出悬浮球模式 -> {mode}，ProactiveVision已暂停")

        if old_mode != mode:
            logger.debug(f"[ProactiveVision] 窗口模式切换: {old_mode} -> {mode}")

    async def _schedule_loop(self):
        """主调度循环"""
        while self._running:
            try:
                # 检查是否应该执行
                if not self._should_check_now():
                    await asyncio.sleep(1)
                    continue

                # 执行检查
                self._last_check_time = time.time()
                await self._perform_check()

                # 等待下一次检查
                await asyncio.sleep(self.config.check_interval_seconds)

            except asyncio.CancelledError:
                logger.info("[ProactiveVision] 调度循环被取消")
                break
            except Exception as e:
                logger.error(f"[ProactiveVision] 调度循环异常: {e}", exc_info=True)
                await asyncio.sleep(5)

    def _should_check_now(self) -> bool:
        """判断是否应该立即执行检查"""
        # 检查总开关
        if not self.config.enabled:
            return False

        # 检查窗口模式（只在悬浮球模式下运行）
        if self._paused_by_mode or self._window_mode == "classic":
            return False

        # 检查频率限制
        elapsed = time.time() - self._last_check_time
        if elapsed < 1.0 / self.config.max_fps:
            return False

        # 检查静默时段
        if self._is_in_quiet_hours():
            return False

        # 检查用户活跃度
        if self.config.pause_on_user_inactive:
            inactive_duration = time.time() - self._last_user_activity_time
            if inactive_duration > self.config.inactive_threshold_minutes * 60:
                return False

        return True

    def _is_in_quiet_hours(self) -> bool:
        """检查是否在静默时段"""
        if not self.config.quiet_hours_start or not self.config.quiet_hours_end:
            return False

        try:
            now = datetime.now().time()
            start = dt_time.fromisoformat(self.config.quiet_hours_start)
            end = dt_time.fromisoformat(self.config.quiet_hours_end)

            if start < end:
                return start <= now <= end
            else:  # 跨越午夜
                return now >= start or now <= end
        except ValueError:
            logger.error(f"[ProactiveVision] 静默时间格式错误: {self.config.quiet_hours_start} - {self.config.quiet_hours_end}")
            return False

    async def _perform_check(self):
        """执行一次屏幕检查"""
        try:
            from .analyzer import get_proactive_analyzer
            analyzer = get_proactive_analyzer()
            await analyzer.analyze_screen()
        except Exception as e:
            logger.error(f"[ProactiveVision] 屏幕检查失败: {e}", exc_info=True)


# 全局单例
_scheduler: Optional[ProactiveVisionScheduler] = None


def get_proactive_scheduler() -> Optional[ProactiveVisionScheduler]:
    """获取调度器单例"""
    return _scheduler


def create_proactive_scheduler(config: ProactiveVisionConfig) -> ProactiveVisionScheduler:
    """创建并注册调度器单例（同步版本，不推荐直接使用）

    警告：此函数不会停止旧调度器，可能导致内存泄漏。
    推荐使用 replace_proactive_scheduler_async() 进行线程安全的替换。
    """
    global _scheduler
    if _scheduler is not None:
        logger.warning("[ProactiveVision] 调度器已存在，将被替换（旧调度器未停止，可能导致资源泄漏）")

    _scheduler = ProactiveVisionScheduler(config)
    return _scheduler


# asyncio锁，保护调度器替换操作
_scheduler_lock: Optional[asyncio.Lock] = None


def _get_scheduler_lock() -> asyncio.Lock:
    """获取调度器锁（延迟创建，避免事件循环未就绪）"""
    global _scheduler_lock
    if _scheduler_lock is None:
        _scheduler_lock = asyncio.Lock()
    return _scheduler_lock


async def replace_proactive_scheduler_async(config: ProactiveVisionConfig) -> ProactiveVisionScheduler:
    """线程安全地替换调度器（推荐使用）

    此函数会：
    1. 停止旧调度器
    2. 创建新调度器
    3. 返回新调度器（但不自动启动，由调用者决定）

    Args:
        config: 新配置

    Returns:
        新调度器实例
    """
    global _scheduler

    lock = _get_scheduler_lock()
    async with lock:
        old_scheduler = _scheduler
        was_running = old_scheduler._running if old_scheduler else False

        # 停止旧调度器
        if old_scheduler is not None:
            logger.info("[ProactiveVision] 停止旧调度器...")
            await old_scheduler.stop()

        # 创建新调度器
        _scheduler = ProactiveVisionScheduler(config)
        logger.info(f"[ProactiveVision] 已创建新调度器 (was_running={was_running})")

        return _scheduler
