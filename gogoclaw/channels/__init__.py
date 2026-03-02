"""
GogoClaw 渠道适配器模块
"""
from gogoclaw.channels.base import (
    ChannelAdapter,
    ChannelType,
    ChannelConfig,
    ChannelMessage,
    WebUIAdapter,
)
from gogoclaw.channels.telegram import TelegramAdapter
from gogoclaw.channels.discord import DiscordAdapter

__all__ = [
    "ChannelAdapter",
    "ChannelType", 
    "ChannelConfig",
    "ChannelMessage",
    "WebUIAdapter",
    "TelegramAdapter",
    "DiscordAdapter",
]
