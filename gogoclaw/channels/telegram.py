"""
GogoClaw 渠道适配器 - Telegram
"""
from typing import Dict, Any, Optional
import logging

from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage

logger = logging.getLogger(__name__)


class TelegramAdapter(ChannelAdapter):
    """Telegram 适配器"""
    
    def __init__(self, config: ChannelConfig):
        super().__init__(ChannelType.TELEGRAM, config)
        self.api_url = "https://api.telegram.org"
        self._offset = 0
        self._polling = False
        
    async def start(self):
        """启动 Telegram Bot"""
        if not self.config.token:
            raise ValueError("Telegram bot token not configured")
            
        # 获取 bot info
        try:
            response = await self._make_request("getMe")
            logger.info(f"Telegram bot started: {response['result']['username']}")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            raise
            
        # 开始长轮询
        self._polling = True
        asyncio.create_task(self._polling_loop())
        
    async def stop(self):
        """停止 Telegram Bot"""
        self._polling = False
        logger.info("Telegram adapter stopped")
        
    async def _polling_loop(self):
        """长轮询循环"""
        while self._polling:
            try:
                updates = await self._get_updates()
                for update in updates:
                    await self._handle_update(update)
                    
                if updates:
                    self._offset = updates[-1]["update_id"] + 1
                    
            except Exception as e:
                logger.error(f"Polling error: {e}")
                await asyncio.sleep(5)
                
    async def _get_updates(self) -> list[Dict]:
        """获取更新"""
        url = f"{self.api_url}/bot{self.config.token}/getUpdates"
        params = {"offset": self._offset, "timeout": 30}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("result", [])
                return []
                
    async def _handle_update(self, update: Dict):
        """处理更新"""
        message = update.get("message")
        if not message:
            return
            
        # 解析消息
        channel_msg = self.parse_message(message)
        
        # 检查权限
        allowed, reason = self.check_access(channel_msg)
        if not allowed:
            logger.info(f"Message denied: {reason}")
            return
            
        # 处理消息
        await self.handle_message(channel_msg)
        
    def parse_message(self, raw_message: Dict) -> ChannelMessage:
        """解析 Telegram 消息"""
        chat = raw_message.get("chat", {})
        from_user = raw_message.get("from", {})
        
        message_id = str(raw_message.get("message_id", ""))
        sender_id = str(from_user.get("id", ""))
        sender_name = from_user.get("first_name", "") or from_user.get("username", "Unknown")
        
        # 获取文本内容
        content = ""
        if "text" in raw_message:
            content = raw_message["text"]
        elif "caption" in raw_message:
            content = raw_message["caption"]
            
        # 检查是否是群聊
        is_group = chat.get("type") == "group" or chat.get("type") == "supergroup"
        group_id = str(chat.get("id", "")) if is_group else None
        
        # 检查是否 @提到 bot
        is_mentioned = False
        if "entities" in raw_message:
            for entity in raw_message["entities"]:
                if entity.get("type") == "mention":
                    # 检查是否提到 bot username
                    pass
                    
        return ChannelMessage(
            message_id=message_id,
            channel="telegram",
            sender_id=sender_id,
            sender_name=sender_name,
            content=content,
            is_group=is_group,
            group_id=group_id,
            is_mentioned=is_mentioned,
            metadata=raw_message
        )
        
    def format_message(self, content: str) -> Dict[str, Any]:
        """格式化消息"""
        return {"text": content}
        
    async def send_message(
        self, 
        receiver_id: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """发送消息"""
        url = f"{self.api_url}/bot{self.config.token}/sendMessage"
        data = {
            "chat_id": receiver_id,
            "text": content,
            "parse_mode": "Markdown"
        }
        
        await self._make_request("sendMessage", data)
        
    async def send_typing(self, receiver_id: str):
        """发送正在输入"""
        url = f"{self.api_url}/bot{self.config.token}/sendChatAction"
        data = {
            "chat_id": receiver_id,
            "action": "typing"
        }
        
        await self._make_request("sendChatAction", data)
        
    async def _make_request(self, method: str, data: Dict = None) -> Dict:
        """发送 API 请求"""
        import aiohttp
        
        url = f"{self.api_url}/bot{self.config.token}/{method}"
        
        async with aiohttp.ClientSession() as session:
            if data:
                async with session.post(url, json=data) as resp:
                    result = await resp.json()
                    if not result.get("ok"):
                        raise Exception(result.get("description", "Unknown error"))
                    return result
            else:
                async with session.get(url) as resp:
                    result = await resp.json()
                    if not result.get("ok"):
                        raise Exception(result.get("description", "Unknown error"))
                    return result


import asyncio
import aiohttp
