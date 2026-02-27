"""
Proactive Vision System - 主动屏幕识别系统

让AI能够主动观察屏幕状态，在检测到特定条件时主动与用户对话。
"""

from .scheduler import (
    ProactiveVisionScheduler,
    get_proactive_scheduler,
    create_proactive_scheduler,
    replace_proactive_scheduler_async,
)
from .analyzer import ProactiveVisionAnalyzer, get_proactive_analyzer, create_proactive_analyzer
from .trigger import ProactiveVisionTrigger, get_proactive_trigger, create_proactive_trigger
from .config import ProactiveVisionConfig, TriggerRule
from .config_loader import load_proactive_config, save_proactive_config

__all__ = [
    "ProactiveVisionScheduler",
    "ProactiveVisionAnalyzer",
    "ProactiveVisionTrigger",
    "ProactiveVisionConfig",
    "TriggerRule",
    "get_proactive_scheduler",
    "get_proactive_analyzer",
    "get_proactive_trigger",
    "create_proactive_scheduler",
    "create_proactive_analyzer",
    "create_proactive_trigger",
    "replace_proactive_scheduler_async",
    "load_proactive_config",
    "save_proactive_config",
]
