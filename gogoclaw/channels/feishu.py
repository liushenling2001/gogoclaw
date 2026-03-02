"""
GogoClaw 渠道适配器 - 飞书 (Feishu/Lark)
支持 webhook 模式和轮询模式，支持消息加解密和卡片消息
"""
from typing import Dict, Any, Optional, Callable, Awaitable
import logging
import asyncio
import hashlib
import base64
import hmac
import json
import time
from datetime import datetime

import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage

logger = logging.getLogger(__name__)


class FeishuConfig(ChannelConfig):
    """飞书渠道配置"""
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    verification_token: Optional[str] = None
    encrypt_key: Optional[str] = None
    bot_name: Optional[str] = None
    webhook_enabled: bool = True
    polling_enabled: bool = False
    polling_interval: int = 30


class FeishuAdapter(ChannelAdapter):
    """飞书适配器"""
    
    API_BASE = "https://open.feishu.cn/open-apis"
    
    def __init__(self, config: FeishuConfig):
        super().__init__(ChannelType.FEISHU, config)
        self.config: FeishuConfig = config
        self._access_token: Optional[str] = None
        self._token_expire: float = 0
        self._polling = False
        self._session: Optional[aiohttp.ClientSession] = None
        self._tenant_key: Optional[str] = None
        
    async def start(self):
        """启动飞书适配器"""
        if not self.config.app_id or not self.config.app_secret:
            raise ValueError("飞书 app_id 和 app_secret 必须配置")
            
        self._session = aiohttp.ClientSession()
        
        # 获取 access_token
        await self._refresh_token()
        
        # 获取 bot info
        try:
            bot_info = await self._request("GET", "/bot/v4/info")
            self._tenant_key = bot_info.get("data", {}).get("tenant_key")
            logger.info(f"飞书适配器已启动：{bot_info.get('data', {}).get('app_name', 'Unknown')}")
        except Exception as e:
            logger.warning(f"获取 bot 信息失败：{e}")
        
        # 启动轮询（如果启用）
        if self.config.polling_enabled:
            self._polling = True
            asyncio.create_task(self._polling_loop())
            
        logger.info("飞书适配器启动完成")
        
    async def stop(self):
        """停止飞书适配器"""
        self._polling = False
        if self._session:
            await self._session.close()
        logger.info("飞书适配器已停止")
        
    async def _refresh_token(self):
        """刷新 access_token"""
        if time.time() < self._token_expire - 300:  # 提前 5 分钟刷新
            return
            
        url = f"{self.API_BASE}/auth/v3/tenant_access_token/internal"
        data = {
            "app_id": self.config.app_id,
            "app_secret": self.config.app_secret
        }
        
        async with self._session.post(url, json=data) as resp:
            result = await resp.json()
            if result.get("code") != 0:
                raise Exception(f"获取 token 失败：{result.get('msg')}")
                
            self._access_token = result["tenant_access_token"]
            self._token_expire = time.time() + result.get("expire", 7200)
            logger.debug("飞书 access_token 已刷新")
            
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Dict = None,
        use_bot_token: bool = True
    ) -> Dict:
        """发送 API 请求"""
        await self._refresh_token()
        
        url = f"{self.API_BASE}{endpoint}"
        headers = {
            "Content-Type": "application/json"
        }
        
        if use_bot_token and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
            
        async with self._session.request(method, url, json=data, headers=headers) as resp:
            result = await resp.json()
            if result.get("code") != 0:
                raise Exception(f"飞书 API 错误 {result.get('code')}: {result.get('msg')}")
            return result
            
    async def _polling_loop(self):
        """轮询消息"""
        while self._polling:
            try:
                # 获取消息列表
                messages = await self._get_messages()
                for msg in messages:
                    await self._handle_message_event(msg)
            except Exception as e:
                logger.error(f"飞书轮询错误：{e}")
                
            await asyncio.sleep(self.config.polling_interval)
            
    async def _get_messages(self) -> list:
        """获取消息列表（简化实现）"""
        # 飞书的消息轮询需要通过事件订阅，这里简化处理
        # 实际使用建议使用 webhook 模式
        return []
        
    async def handle_webhook(self, payload: Dict) -> Dict:
        """处理 webhook 请求"""
        # 验证签名
        if not self._verify_signature(payload):
            logger.warning("飞书 webhook 签名验证失败")
            return {"code": 401, "msg": "Invalid signature"}
            
        # 处理挑战（challenge）
        if payload.get("type") == "url_verification":
            return {
                "challenge": payload.get("challenge"),
                "token": payload.get("token")
            }
            
        # 处理事件
        event = payload.get("event", {})
        event_type = payload.get("header", {}).get("event_type", "")
        
        if event_type == "im.message.receive_v1":
            await self._handle_message_event(event)
        elif event_type == "im.message.group_at_msg_v1":
            await self._handle_message_event(event)
            
        return {"code": 0, "msg": "success"}
        
    def _verify_signature(self, payload: Dict) -> bool:
        """验证 webhook 签名"""
        if not self.config.verification_token:
            return True  # 未配置 token 时跳过验证
            
        signature = payload.get("header", {}).get("signature", "")
        timestamp = payload.get("header", {}).get("timestamp", "")
        
        # 计算签名
        sign_str = timestamp + self.config.verification_token
        calculated = hashlib.sha256(sign_str.encode()).hexdigest()
        
        return signature == calculated
        
    def _decrypt_message(self, encrypted_data: str) -> Dict:
        """解密消息（AES-CBC）"""
        if not self.config.encrypt_key:
            return json.loads(encrypted_data)
            
        try:
            # 解码 base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # 提取 IV 和密文
            iv = encrypted_bytes[:16]
            ciphertext = encrypted_bytes[16:]
            
            # 解密
            key = base64.b64decode(self.config.encrypt_key)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
            
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"消息解密失败：{e}")
            return {}
            
    async def _handle_message_event(self, event: Dict):
        """处理消息事件"""
        try:
            message = event.get("message", {})
            sender = event.get("sender", {})
            
            # 解析消息
            channel_msg = self._parse_message(message, sender, event)
            
            # 检查权限
            allowed, reason = self.check_access(channel_msg)
            if not allowed:
                logger.info(f"飞书消息被拒绝：{reason}")
                return
                
            # 处理消息
            await self.handle_message(channel_msg)
            
        except Exception as e:
            logger.error(f"处理飞书消息失败：{e}")
            
    def _parse_message(
        self, 
        message: Dict, 
        sender: Dict,
        event: Dict
    ) -> ChannelMessage:
        """解析飞书消息"""
        message_id = message.get("message_id", "")
        sender_id = sender.get("sender_id", {}).get("union_id", "") or \
                    sender.get("sender_id", {}).get("user_id", "")
        sender_name = sender.get("sender_name", "Unknown")
        
        # 获取消息内容
        content = message.get("content", "")
        message_type = message.get("message_type", "text")
        
        # 解析不同消息类型
        if message_type == "text":
            content_data = json.loads(content) if content else {}
            content = content_data.get("text", "")
        elif message_type == "post":
            content_data = json.loads(content) if content else {}
            # 提取 post 消息的文本内容
            content = self._extract_post_content(content_data)
        elif message_type == "interactive":
            # 卡片消息
            content = f"[卡片消息] {message_id}"
            
        # 判断是否是群聊
        chat_type = message.get("chat_type", "p2p")
        is_group = chat_type == "group"
        chat_id = message.get("chat_id", "")
        group_id = chat_id if is_group else None
        
        # 检查是否 @bot
        is_mentioned = event.get("header", {}).get("event_type", "") == "im.message.group_at_msg_v1"
        if not is_mentioned and is_group:
            # 检查消息内容中是否 @bot
            if self.config.bot_name and f"@{self.config.bot_name}" in content:
                is_mentioned = True
                
        return ChannelMessage(
            message_id=message_id,
            channel="feishu",
            sender_id=sender_id,
            sender_name=sender_name,
            content=content,
            is_group=is_group,
            group_id=group_id,
            is_mentioned=is_mentioned,
            metadata={
                "message_type": message_type,
                "chat_id": chat_id,
                "tenant_key": self._tenant_key,
                "raw_event": event
            }
        )
        
    def _extract_post_content(self, content_data: Dict) -> str:
        """提取 post 消息的文本内容"""
        content_list = content_data.get("content", [])
        texts = []
        for item in content_list:
            if isinstance(item, list):
                for elem in item:
                    if elem.get("tag") == "text":
                        texts.append(elem.get("text", ""))
        return "\n".join(texts)
        
    def format_message(self, content: str, message_type: str = "text") -> Dict[str, Any]:
        """格式化消息用于发送"""
        if message_type == "text":
            return {
                "msg_type": "text",
                "content": json.dumps({"text": content})
            }
        elif message_type == "post":
            return {
                "msg_type": "post",
                "content": json.dumps({
                    "zh_cn": {
                        "title": "",
                        "content": [[{"tag": "text", "text": content}]]
                    }
                })
            }
        elif message_type == "interactive":
            # 卡片消息
            return {
                "msg_type": "interactive",
                "content": content  # 已经是 JSON 字符串
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
        
        # 判断是发送给用户还是群聊
        chat_type = metadata.get("chat_type", "p2p")
        receive_id = receiver_id
        
        # 获取 receive_id 类型
        id_type = metadata.get("id_type", "user_id")
        if metadata.get("is_group"):
            id_type = "chat_id"
            
        formatted = self.format_message(content, message_type)
        
        # 发送消息
        endpoint = f"/im/v1/messages?receive_id={receive_id}&msg_type={message_type}"
        
        # 根据 id_type 调整参数
        if id_type == "chat_id":
            endpoint = f"/im/v1/messages?receive_id={receive_id}&msg_type={message_type}"
        elif id_type == "user_id":
            endpoint = f"/im/v1/messages?receive_id={receive_id}&msg_type={message_type}"
            
        data = {
            "receive_id": receive_id,
            "msg_type": message_type,
            "content": formatted["content"]
        }
        
        # 使用不同的 API 端点
        if metadata.get("is_group"):
            # 群聊
            await self._request("POST", "/im/v1/messages", {
                "receive_id": receive_id,
                "msg_type": message_type,
                "content": formatted["content"]
            })
        else:
            # 私聊
            await self._request("POST", "/im/v1/messages", {
                "receive_id": receive_id,
                "msg_type": message_type,
                "content": formatted["content"]
            })
            
        logger.debug(f"飞书消息已发送：{receiver_id}")
        
    async def send_typing(self, receiver_id: str):
        """发送正在输入状态（飞书不支持）"""
        # 飞书 API 不支持 typing 状态
        pass
        
    async def send_card(
        self, 
        receiver_id: str, 
        card_content: Dict,
        is_group: bool = False
    ):
        """发送卡片消息"""
        await self.send_message(
            receiver_id,
            json.dumps(card_content),
            metadata={
                "message_type": "interactive",
                "is_group": is_group
            }
        )
