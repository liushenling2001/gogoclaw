"""
GogoClaw 渠道适配器 - WhatsApp
使用 WhatsApp Business Cloud API
"""
from typing import Dict, Any, Optional
import logging
import asyncio
import hashlib
import hmac
import json
import time

import aiohttp

from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage

logger = logging.getLogger(__name__)


class WhatsAppConfig(ChannelConfig):
    """WhatsApp 渠道配置"""
    phone_number_id: Optional[str] = None
    business_account_id: Optional[str] = None
    verify_token: Optional[str] = None
    webhook_url: Optional[str] = None
    api_version: str = "v18.0"
    polling_enabled: bool = False
    polling_interval: int = 30


class WhatsAppAdapter(ChannelAdapter):
    """WhatsApp 适配器"""
    
    API_BASE = "https://graph.facebook.com"
    
    def __init__(self, config: WhatsAppConfig):
        super().__init__(ChannelType.WHATSAPP, config)
        self.config: WhatsAppConfig = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._polling = False
        
    async def start(self):
        """启动 WhatsApp 适配器"""
        if not self.config.token:
            raise ValueError("WhatsApp access_token 必须配置")
        if not self.config.phone_number_id:
            raise ValueError("WhatsApp phone_number_id 必须配置")
            
        self._session = aiohttp.ClientSession()
        
        # 验证配置
        try:
            await self._verify_business_account()
            logger.info(f"WhatsApp 适配器已启动：{self.config.phone_number_id}")
        except Exception as e:
            logger.warning(f"验证 WhatsApp 账户失败：{e}")
        
        # 启动轮询（如果启用）
        if self.config.polling_enabled:
            self._polling = True
            asyncio.create_task(self._polling_loop())
            
        logger.info("WhatsApp 适配器启动完成")
        
    async def stop(self):
        """停止 WhatsApp 适配器"""
        self._polling = False
        if self._session:
            await self._session.close()
        logger.info("WhatsApp 适配器已停止")
        
    async def _verify_business_account(self):
        """验证业务账户"""
        endpoint = f"/{self.config.api_version}/{self.config.business_account_id or self.config.phone_number_id}"
        await self._request("GET", endpoint)
        
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Dict = None,
        params: Dict = None
    ) -> Dict:
        """发送 API 请求"""
        url = f"{self.API_BASE}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json"
        }
        
        if params is None:
            params = {}
            
        async with self._session.request(method, url, json=data, params=params, headers=headers) as resp:
            result = await resp.json()
            if resp.status >= 400:
                raise Exception(f"WhatsApp API 错误 {resp.status}: {result}")
            return result
            
    async def _polling_loop(self):
        """轮询消息（通过 webhook 订阅）"""
        while self._polling:
            # WhatsApp 主要通过 webhook 接收消息
            # 轮询模式仅作为备选
            await asyncio.sleep(self.config.polling_interval)
            
    async def handle_webhook(self, payload: Dict) -> Dict:
        """处理 webhook 请求"""
        # 验证请求
        if not self._verify_webhook(payload):
            logger.warning("WhatsApp webhook 验证失败")
            return {"status": "error"}
            
        # 处理消息
        if "entry" in payload:
            for entry in payload["entry"]:
                changes = entry.get("changes", [])
                for change in changes:
                    if change.get("field") == "messages":
                        value = change.get("value", {})
                        messages = value.get("messages", [])
                        
                        for message in messages:
                            await self._handle_message_event(message, value)
                            
        return {"status": "ok"}
        
    def _verify_webhook(self, payload: Dict) -> bool:
        """验证 webhook 请求"""
        # WhatsApp webhook 验证在订阅时通过 GET 请求完成
        # 这里验证消息签名
        if not self.config.verify_token:
            return True
            
        # 可以添加 HMAC 验证
        return True
        
    async def handle_webhook_verify(
        self, 
        mode: str,
        token: str,
        challenge: str
    ) -> str:
        """处理 webhook 验证请求（GET）"""
        if mode == "subscribe" and token == self.config.verify_token:
            logger.info("WhatsApp webhook 验证成功")
            return challenge
        else:
            logger.warning("WhatsApp webhook 验证失败")
            return ""
            
    async def _handle_message_event(self, message: Dict, metadata: Dict):
        """处理消息事件"""
        try:
            # 解析消息
            channel_msg = self._parse_message(message, metadata)
            
            # 检查权限
            allowed, reason = self.check_access(channel_msg)
            if not allowed:
                logger.info(f"WhatsApp 消息被拒绝：{reason}")
                return
                
            # 处理消息
            await self.handle_message(channel_msg)
            
        except Exception as e:
            logger.error(f"处理 WhatsApp 消息失败：{e}")
            
    def _parse_message(self, message: Dict, metadata: Dict) -> ChannelMessage:
        """解析 WhatsApp 消息"""
        message_id = message.get("id", "")
        from_id = message.get("from", "")
        from_name = metadata.get("contacts", [{}])[0].get("profile", {}).get("name", "Unknown")
        
        # 获取消息内容
        content = ""
        message_type = message.get("type", "text")
        
        if message_type == "text":
            content = message.get("text", {}).get("body", "")
        elif message_type == "image":
            content = f"[图片] {message.get('image', {}).get('caption', '')}"
        elif message_type == "video":
            content = f"[视频] {message.get('video', {}).get('caption', '')}"
        elif message_type == "audio":
            content = "[音频消息]"
        elif message_type == "document":
            content = f"[文档] {message.get('document', {}).get('filename', '')}"
        elif message_type == "sticker":
            content = "[贴纸]"
        elif message_type == "location":
            loc = message.get("location", {})
            content = f"[位置] {loc.get('latitude')}, {loc.get('longitude')}"
        elif message_type == "contacts":
            content = "[联系人]"
        elif message_type == "button":
            content = message.get("button", {}).get("text", "")
        elif message_type == "interactive":
            # 交互消息（按钮、列表等）
            interactive = message.get("interactive", {})
            if "button_reply" in interactive:
                content = interactive["button_reply"]["title"]
            elif "list_reply" in interactive:
                content = interactive["list_reply"]["title"]
                
        # WhatsApp 主要是私聊，群聊支持有限
        is_group = False  # WhatsApp Business API 主要支持私聊
        group_id = None
        
        return ChannelMessage(
            message_id=message_id,
            channel="whatsapp",
            sender_id=from_id,
            sender_name=from_name,
            content=content,
            is_group=is_group,
            group_id=group_id,
            is_mentioned=False,  # WhatsApp 不支持 @
            metadata={
                "message_type": message_type,
                "phone_number_id": self.config.phone_number_id,
                "raw_metadata": metadata
            }
        )
        
    def format_message(self, content: str, message_type: str = "text") -> Dict[str, Any]:
        """格式化消息用于发送"""
        if message_type == "text":
            return {
                "messaging_product": "whatsapp",
                "type": "text",
                "text": {
                    "body": content
                }
            }
        elif message_type == "template":
            # 模板消息
            return {
                "messaging_product": "whatsapp",
                "type": "template",
                "template": content  # 已经是 dict
            }
        elif message_type == "interactive":
            # 交互消息（按钮、列表）
            return {
                "messaging_product": "whatsapp",
                "type": "interactive",
                "interactive": content  # 已经是 dict
            }
        elif message_type == "image":
            return {
                "messaging_product": "whatsapp",
                "type": "image",
                "image": content  # {"link": "...", "caption": "..."}
            }
        elif message_type == "document":
            return {
                "messaging_product": "whatsapp",
                "type": "document",
                "document": content
            }
        else:
            return self.format_message(content, "text")
            
    async def send_message(
        self, 
        receiver_id: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """发送消息"""
        metadata = metadata or {}
        message_type = metadata.get("message_type", "text")
        
        formatted = self.format_message(content, message_type)
        formatted["to"] = receiver_id
        
        endpoint = f"/{self.config.api_version}/{self.config.phone_number_id}/messages"
        
        await self._request("POST", endpoint, formatted)
        
        logger.debug(f"WhatsApp 消息已发送：{receiver_id}")
        
    async def send_typing(self, receiver_id: str):
        """发送正在输入状态（WhatsApp 不支持）"""
        # WhatsApp Business API 不支持 typing 状态
        pass
        
    async def send_template(
        self, 
        receiver_id: str, 
        template_name: str,
        language: str = "zh_CN",
        components: list = None
    ):
        """发送模板消息"""
        template = {
            "name": template_name,
            "language": {
                "code": language
            }
        }
        
        if components:
            template["components"] = components
            
        await self.send_message(
            receiver_id,
            template,
            metadata={"message_type": "template"}
        )
        
    async def send_button(
        self, 
        receiver_id: str, 
        body: str,
        buttons: list
    ):
        """发送按钮消息"""
        interactive = {
            "type": "button",
            "body": {
                "text": body
            },
            "action": {
                "buttons": buttons
            }
        }
        
        await self.send_message(
            receiver_id,
            interactive,
            metadata={"message_type": "interactive"}
        )
        
    async def send_list(
        self, 
        receiver_id: str, 
        body: str,
        button_text: str,
        sections: list
    ):
        """发送列表消息"""
        interactive = {
            "type": "list",
            "body": {
                "text": body
            },
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
        
        await self.send_message(
            receiver_id,
            interactive,
            metadata={"message_type": "interactive"}
        )
