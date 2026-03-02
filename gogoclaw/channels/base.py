"""
GogoClaw 渠道适配器模块 - 基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ChannelType(Enum):
    """渠道类型"""
    TELEGRAM = "telegram"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"
    FEISHU = "feishu"
    DINGTALK = "dingtalk"
    WEBUI = "webui"


@dataclass
class ChannelMessage:
    """渠道消息"""
    message_id: str
    channel: str
    sender_id: str
    sender_name: str
    content: str
    is_group: bool = False
    group_id: Optional[str] = None
    is_mentioned: bool = False  # 是否 @ 提到 bot
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
            
    @property
    def platform(self) -> str:
        """获取平台名称"""
        return self.channel


@dataclass
class ChannelConfig:
    """渠道配置"""
    enabled: bool = True
    token: Optional[str] = None
    api_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    whitelist: list[str] = None
    dm_policy: str = "pairing"  # pairing, open, deny
    group_policy: str = "mentioned"  # mentioned, always, deny
    group_whitelist: list[str] = None
    
    def __post_init__(self):
        if self.whitelist is None:
            self.whitelist = []
        if self.group_whitelist is None:
            self.group_whitelist = []


class ChannelAdapter(ABC):
    """渠道适配器基类"""
    
    def __init__(self, channel_type: ChannelType, config: ChannelConfig):
        self.channel_type = channel_type
        self.config = config
        self._message_handler: Optional[Callable] = None
        
    @abstractmethod
    async def start(self):
        """启动适配器"""
        pass
        
    @abstractmethod
    async def stop(self):
        """停止适配器"""
        pass
        
    @abstractmethod
    async def send_message(
        self, 
        receiver_id: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """发送消息"""
        pass
        
    @abstractmethod
    async def send_typing(self, receiver_id: str):
        """发送正在输入状态"""
        pass
        
    def set_message_handler(self, handler: Callable[[ChannelMessage], Awaitable[None]]):
        """设置消息处理器"""
        self._message_handler = handler
        
    async def handle_message(self, message: ChannelMessage):
        """处理收到的消息"""
        if self._message_handler:
            await self._message_handler(message)
            
    def parse_message(self, raw_message: Dict[str, Any]) -> ChannelMessage:
        """解析原始消息 - 子类实现"""
        raise NotImplementedError
        
    def format_message(self, content: str) -> Dict[str, Any]:
        """格式化消息用于发送 - 子类实现"""
        raise NotImplementedError
        
    def check_access(self, message: ChannelMessage) -> tuple[bool, str]:
        """检查访问权限"""
        # 检查白名单
        if message.sender_id in self.config.whitelist:
            return True, "whitelist"
            
        # 检查私聊策略
        if not message.is_group:
            if self.config.dm_policy == "open":
                return True, "dm_open"
            elif self.config.dm_policy == "deny":
                return False, "dm_deny"
            return False, "dm_pairing"
            
        # 检查群策略
        if message.group_id in self.config.group_whitelist:
            return True, "group_whitelist"
            
        if self.config.group_policy == "always":
            return True, "group_always"
        elif self.config.group_policy == "deny":
            return False, "group_deny"
        elif self.config.group_policy == "mentioned":
            if message.is_mentioned:
                return True, "group_mentioned"
            return False, "group_not_mentioned"
            
        return False, "unknown"


class WebUIAdapter(ChannelAdapter):
    """Web UI 适配器"""
    
    def __init__(self, config: ChannelConfig = None):
        super().__init__(ChannelType.WEBUI, config or ChannelConfig())
        
    async def start(self):
        logger.info("WebUI adapter started")
        
    async def stop(self):
        logger.info("WebUI adapter stopped")
        
    async def send_message(self, receiver_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """WebUI 通过 WebSocket 发送"""
        # 由 Gateway 处理
        pass
        
    async def send_typing(self, receiver_id: str):
        """发送正在输入"""
        # 由 Gateway 处理
        pass
