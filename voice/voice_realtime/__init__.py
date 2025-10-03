#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
实时语音模块 (Refactored)
支持多种语音服务提供商的实时语音交互

版本: 2.0.0
重构日期: 2024-09-30
"""

# 版本信息
__version__ = "2.0.0"
__author__ = "NagaAgent Team"

# 导入核心组件
from .core.voice_client_factory import VoiceClientFactory
from .core.base_client import BaseVoiceClient
from .core.audio_manager import AudioManager
from .core.state_manager import StateManager, ConversationState

# 导入适配器
from .adapters.qwen_adapter import QwenVoiceClientAdapter
from .adapters.openai_adapter import OpenAIVoiceClientAdapter

# 注册默认适配器
VoiceClientFactory.register('qwen', QwenVoiceClientAdapter)
VoiceClientFactory.register('openai', OpenAIVoiceClientAdapter)

# 导出公共接口
__all__ = [
    'VoiceClientFactory',
    'BaseVoiceClient',
    'AudioManager',
    'StateManager',
    'ConversationState',
    'QwenVoiceClientAdapter',
    'OpenAIVoiceClientAdapter',
]

# 简化的创建函数
def create_voice_client(provider='qwen', api_key=None, **kwargs):
    """
    快速创建语音客户端

    参数:
        provider: 提供商名称 ('qwen', 'openai')
        api_key: API密钥
        **kwargs: 其他参数

    返回:
        BaseVoiceClient: 语音客户端实例
    """
    return VoiceClientFactory.create(
        provider=provider,
        api_key=api_key,
        **kwargs
    )