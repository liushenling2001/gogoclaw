"""
GogoClaw 渠道适配器 - 钉钉 (DingTalk)
支持 webhook 模式和轮询模式，支持群聊/私聊区分
"""
from typing import Dict, Any, Optional
import logging
import asyncio
import hashlib
import hmac
import base64
import json
import time
from urllib.parse import quote

import aiohttp

from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage

logger = logging.getLogger(__name__)


class DingTalkConfig(ChannelConfig):
    """钉钉渠道配置"""
    app_key: Optional[str] = None
    app_secret: Optional[str] = None
    agent_id: Optional[str] = None
    webhook_secret: Optional[str] = None
    webhook_url: Optional[str] = None
    bot_code: Optional[str] = None
    polling_enabled: bool = False
    polling_interval: int = 30


class DingTalkAdapter(ChannelAdapter):
    """钉钉适配器"""
    
    API_BASE = "https://oapi.dingtalk.com"
    
    def __init__(self, config: DingTalkConfig):
        super().__init__(ChannelType.DINGTALK, config)
        self.config: DingTalkConfig = config
        self._access_token: Optional[str] = None
        self._token_expire: float = 0
        self._polling = False
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def start(self):
        """启动钉钉适配器"""
        if not self.config.app_key or not self.config.app_secret:
            raise ValueError("钉钉 app_key 和 app_secret 必须配置")
            
        self._session = aiohttp.ClientSession()
        
        # 获取 access_token
        await self._refresh_token()
        
        # 获取 agent info
        try:
            agent_info = await self._get_agent_info()
            logger.info(f"钉钉适配器已启动：{agent_info.get('name', 'Unknown')}")
        except Exception as e:
            logger.warning(f"获取 agent 信息失败：{e}")
        
        # 启动轮询（如果启用）
        if self.config.polling_enabled:
            self._polling = True
            asyncio.create_task(self._polling_loop())
            
        logger.info("钉钉适配器启动完成")
        
    async def stop(self):
        """停止钉钉适配器"""
        self._polling = False
        if self._session:
            await self._session.close()
        logger.info("钉钉适配器已停止")
        
    async def _refresh_token(self):
        """刷新 access_token"""
        if time.time() < self._token_expire - 300:
            return
            
        url = f"{self.API_BASE}/gettoken"
        params = {
            "appkey": self.config.app_key,
            "appsecret": self.config.app_secret
        }
        
        async with self._session.get(url, params=params) as resp:
            result = await resp.json()
            if result.get("errcode") != 0:
                raise Exception(f"获取 token 失败：{result.get('errmsg')}")
                
            self._access_token = result["access_token"]
            self._token_expire = time.time() + result.get("expires_in", 7200)
            logger.debug("钉钉 access_token 已刷新")
            
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Dict = None,
        params: Dict = None
    ) -> Dict:
        """发送 API 请求"""
        await self._refresh_token()
        
        url = f"{self.API_BASE}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if params is None:
            params = {}
        params["access_token"] = self._access_token
        
        async with self._session.request(method, url, json=data, params=params, headers=headers) as resp:
            result = await resp.json()
            if result.get("errcode") != 0:
                raise Exception(f"钉钉 API 错误 {result.get('errcode')}: {result.get('errmsg')}")
            return result
            
    async def _polling_loop(self):
        """轮询消息"""
        while self._polling:
            try:
                messages = await self._get_callback_messages()
                for msg in messages:
                    await self._handle_message_event(msg)
            except Exception as e:
                logger.error(f"钉钉轮询错误：{e}")
                
            await asyncio.sleep(self.config.polling_interval)
            
    async def _get_callback_messages(self) -> list:
        """获取回调消息（简化实现）"""
        # 钉钉的消息轮询需要通过事件订阅，这里简化处理
        # 实际使用建议使用 webhook 模式
        return []
        
    async def handle_webhook(self, payload: Dict) -> Dict:
        """处理 webhook 请求"""
        # 验证签名
        if not self._verify_signature(payload):
            logger.warning("钉钉 webhook 签名验证失败")
            return {"code": 401, "msg": "Invalid signature"}
            
        # 处理事件
        event_type = payload.get("eventType", "")
        
        if event_type == "bot_message":
            # 机器人消息
            chat_type = payload.get("chatType", "p2p")
            message = payload.get("text", {}).get("content", "")
            
            # 解析消息
            channel_msg = self._parse_message(payload)
            
            # 检查权限
            allowed, reason = self.check_access(channel_msg)
            if not allowed:
                logger.info(f"钉钉消息被拒绝：{reason}")
                return {"code": 0, "msg": "success"}
                
            # 处理消息
            await self.handle_message(channel_msg)
            
        return {"code": 0, "msg": "success"}
        
    def _verify_signature(self, payload: Dict) -> bool:
        """验证 webhook 签名"""
        if not self.config.webhook_secret:
            return True  # 未配置 secret 时跳过验证
            
        # 钉钉 webhook 签名验证
        timestamp = payload.get("timestamp", "")
        sign = payload.get("sign", "")
        
        # 计算签名
        string_to_sign = timestamp + "\n" + self.config.webhook_secret
        hmac_code = hmac.new(
            self.config.webhook_secret.encode(),
            string_to_sign.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        calculated = quote(base64.b64encode(hmac_code), safe="")
        
        return sign == calculated
        
    def _parse_message(self, payload: Dict) -> ChannelMessage:
        """解析钉钉消息"""
        conversation_id = payload.get("conversationId", "")
        sender_id = payload.get("senderId", "")
        sender_name = payload.get("senderNick", "Unknown")
        
        # 获取消息内容
        content = payload.get("text", {}).get("content", "")
        
        # 判断是否是群聊
        chat_type = payload.get("chatType", "p2p")
        is_group = chat_type == "group"
        group_id = conversation_id if is_group else None
        
        # 检查是否 @bot
        is_mentioned = payload.get("isAtAll", False) or payload.get("isAtMe", False)
        if not is_mentioned and is_group:
            # 检查消息内容中是否 @bot
            if self.config.bot_code and f"@{self.config.bot_code}" in content:
                is_mentioned = True
                
        return ChannelMessage(
            message_id=payload.get("messageId", conversation_id + "_" + sender_id),
            channel="dingtalk",
            sender_id=sender_id,
            sender_name=sender_name,
            content=content,
            is_group=is_group,
            group_id=group_id,
            is_mentioned=is_mentioned,
            metadata={
                "conversation_id": conversation_id,
                "chat_type": chat_type,
                "robot_code": self.config.bot_code,
                "raw_payload": payload
            }
        )
        
    def format_message(self, content: str, message_type: str = "text") -> Dict[str, Any]:
        """格式化消息用于发送"""
        if message_type == "text":
            return {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
        elif message_type == "markdown":
            return {
                "msgtype": "markdown",
                "markdown": {
                    "title": "消息",
                    "text": content
                }
            }
        elif message_type == "link":
            return {
                "msgtype": "link",
                "link": content  # 已经是 dict
            }
        elif message_type == "action_card":
            return {
                "msgtype": "actionCard",
                "actionCard": content  # 已经是 dict
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
        is_group = metadata.get("is_group", False)
        
        formatted = self.format_message(content, message_type)
        
        if is_group:
            # 发送群消息
            await self._send_group_message(receiver_id, formatted)
        else:
            # 发送私聊消息
            await self._send_private_message(receiver_id, formatted)
            
        logger.debug(f"钉钉消息已发送：{receiver_id}")
        
    async def _send_group_message(self, chat_id: str, message: Dict):
        """发送群消息"""
        # 使用机器人 webhook 发送群消息
        if self.config.webhook_url:
            webhook_url = self.config.webhook_url
            if self.config.webhook_secret:
                # 添加签名
                timestamp = str(round(time.time() * 1000))
                sign = self._generate_webhook_sign(timestamp)
                webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
                
            async with self._session.post(webhook_url, json=message) as resp:
                result = await resp.json()
                if result.get("errcode") != 0:
                    raise Exception(f"发送群消息失败：{result.get('errmsg')}")
        else:
            # 使用 API 发送
            await self._request("POST", "/topapi/message/send_to_chat", {
                "agent_id": self.config.agent_id,
                "chatid": chat_id,
                "msgtype": message["msgtype"],
                message["msgtype"]: message[message["msgtype"]]
            })
            
    async def _send_private_message(self, user_id: str, message: Dict):
        """发送私聊消息"""
        await self._request("POST", "/topapi/message/send", {
            "agent_id": self.config.agent_id,
            "userid": user_id,
            "msgtype": message["msgtype"],
            message["msgtype"]: message[message["msgtype"]]
        })
        
    def _generate_webhook_sign(self, timestamp: str) -> str:
        """生成 webhook 签名"""
        string_to_sign = timestamp + "\n" + self.config.webhook_secret
        hmac_code = hmac.new(
            self.config.webhook_secret.encode(),
            string_to_sign.encode(),
            digestmod=hashlib.sha256
        ).digest()
        return quote(base64.b64encode(hmac_code), safe="")
        
    async def send_typing(self, receiver_id: str):
        """发送正在输入状态（钉钉不支持）"""
        # 钉钉 API 不支持 typing 状态
        pass
        
    async def _get_agent_info(self) -> Dict:
        """获取 agent 信息"""
        return await self._request("GET", "/agent/get_agent", {
            "agent_id": self.config.agent_id
        })
