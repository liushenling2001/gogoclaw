"""
GogoClaw 渠道适配器 - Discord
"""
from typing import Dict, Any, Optional
import logging
import asyncio
import aiohttp
import json

from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage

logger = logging.getLogger(__name__)


class DiscordAdapter(ChannelAdapter):
    """Discord 适配器"""
    
    def __init__(self, config: ChannelConfig):
        super().__init__(ChannelType.DISCORD, config)
        self.api_url = "https://discord.com/api/v10"
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws = None
        self._sequence = None
        self._heartbeat_task = None
        
    @property
    def headers(self) -> Dict[str, str]:
        """API 请求头"""
        return {
            "Authorization": f"Bot {self.config.token}",
            "Content-Type": "application/json"
        }
        
    async def start(self):
        """启动 Discord Bot"""
        if not self.config.token:
            raise ValueError("Discord bot token not configured")
            
        self._session = aiohttp.ClientSession(headers=self.headers)
        
        # 获取 gateway URL
        try:
            response = await self._request("GET", "/gateway")
            gateway_url = response["url"]
            logger.info(f"Discord bot started")
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
            raise
            
        # 连接 WebSocket
        await self._connect_ws(gateway_url + "?encoding=json&v=10")
        
    async def stop(self):
        """停止 Discord Bot"""
        if self._ws:
            await self._ws.close()
        if self._session:
            await self._session.close()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        logger.info("Discord adapter stopped")
        
    async def _connect_ws(self, url: str):
        """连接 WebSocket"""
        self._ws = await self._session.ws_connect(url)
        asyncio.create_task(self._ws_loop())
        
    async def _ws_loop(self):
        """WebSocket 消息循环"""
        async for msg in self._ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                await self._handle_ws_message(data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"WebSocket error: {msg.data}")
                
    async def _handle_ws_message(self, data: Dict):
        """处理 WebSocket 消息"""
        op = data.get("op")
        
        if op == 10:  # Hello
            # 开始心跳
            interval = data["d"]["heartbeat_interval"]
            asyncio.create_task(self._heartbeat(interval))
            
        elif op == 0:  # Dispatch
            event_type = data.get("t")
            event_data = data.get("d", {})
            self._sequence = data.get("s")
            
            if event_type == "MESSAGE_CREATE":
                await self._handle_message(event_data)
                
    async def _heartbeat(self, interval: int):
        """发送心跳"""
        while True:
            await asyncio.sleep(interval / 1000)
            await self._ws.send_json({"op": 1, "d": self._sequence})
            
    async def _handle_message(self, data: Dict):
        """处理消息事件"""
        channel_msg = self.parse_message(data)
        
        # 检查权限
        allowed, reason = self.check_access(channel_msg)
        if not allowed:
            logger.info(f"Message denied: {reason}")
            return
            
        await self.handle_message(channel_msg)
        
    def parse_message(self, raw_message: Dict) -> ChannelMessage:
        """解析 Discord 消息"""
        author = raw_message.get("author", {})
        
        message_id = str(raw_message.get("id", ""))
        sender_id = str(author.get("id", ""))
        sender_name = author.get("username", "Unknown")
        
        # 跳过 bot 消息
        if author.get("bot"):
            # 仍然返回，但标记为 bot
            pass
            
        # 获取文本内容
        content = raw_message.get("content", "")
        
        # 获取 channel 信息判断是否是群聊
        channel_id = str(raw_message.get("channel_id", ""))
        
        # Discord 没有明确的群ID，需要查 metadata
        # 简化处理: 检查消息是否在 guild 中
        is_group = "guild_id" in raw_message
        group_id = str(raw_message.get("guild_id", "")) if is_group else None
        
        # 检查是否 @提到 bot
        mentions = raw_message.get("mentions", [])
        is_mentioned = False
        # TODO: 检查是否 @了 bot
        
        return ChannelMessage(
            message_id=message_id,
            channel="discord",
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
        return {"content": content}
        
    async def send_message(
        self, 
        receiver_id: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """发送消息"""
        # receiver_id 可能是 channel_id 或 user_id (DM)
        channel_id = receiver_id
        
        await self._request(
            "POST", 
            f"/channels/{channel_id}/messages",
            {"content": content}
        )
        
    async def send_typing(self, receiver_id: str):
        """发送正在输入"""
        channel_id = receiver_id
        await self._request(
            "POST",
            f"/channels/{channel_id}/typing"
        )
        
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Dict = None
    ) -> Dict:
        """发送 API 请求"""
        url = f"{self.api_url}{endpoint}"
        
        async with self._session.request(method, url, json=data) as resp:
            if resp.status >= 400:
                text = await resp.text()
                raise Exception(f"Discord API error {resp.status}: {text}")
            if resp.status == 204:
                return {}
            return await resp.json()
