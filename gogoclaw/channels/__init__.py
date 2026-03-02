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
from gogoclaw.channels.telegram import TelegramAdapter, TelegramConfig
from gogoclaw.channels.discord import DiscordAdapter, DiscordConfig
from gogoclaw.channels.feishu import FeishuAdapter, FeishuConfig
from gogoclaw.channels.dingtalk import DingTalkAdapter, DingTalkConfig
from gogoclaw.channels.whatsapp import WhatsAppAdapter, WhatsAppConfig

__all__ = [
    "ChannelAdapter",
    "ChannelType", 
    "ChannelConfig",
    "ChannelMessage",
    "WebUIAdapter",
    # Telegram
    "TelegramAdapter",
    "TelegramConfig",
    # Discord
    "DiscordAdapter",
    "DiscordConfig",
    # Feishu
    "FeishuAdapter",
    "FeishuConfig",
    # DingTalk
    "DingTalkAdapter",
    "DingTalkConfig",
    # WhatsApp
    "WhatsAppAdapter",
    "WhatsAppConfig",
]
