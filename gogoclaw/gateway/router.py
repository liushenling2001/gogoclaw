"""
GogoClaw 网关模块 - 消息路由
"""
from typing import Optional, Dict, Any, Callable, Awaitable
from dataclasses import dataclass
import logging

from gogoclaw.gateway.protocol import Message, MessageRequest, SessionInfo
from gogoclaw.gateway.security import AccessControl

logger = logging.getLogger(__name__)


@dataclass
class RouteRule:
    """路由规则"""
    channel: str
    pattern: str  # 会话ID模式
    agent_id: str
    priority: int = 0


class SessionResolver:
    """会话解析器"""
    
    @staticmethod
    def resolve_session_id(
        channel: str,
        sender: str,
        is_group: bool = False,
        group_id: Optional[str] = None,
        agent_id: str = "main"
    ) -> str:
        """
        解析会话ID
        
        规则:
        - 自己发的私聊: agent:<agentId>:main
        - 别人的私聊: agent:<agentId>:<channel>:dm:<id>
        - 群聊: agent:<agentId>:<channel>:group:<id>
        """
        if not is_group:
            # 私聊
            if sender == "self":
                return f"agent:{agent_id}:main"
            else:
                return f"agent:{agent_id}:{channel}:dm:{sender}"
        else:
            # 群聊
            return f"agent:{agent_id}:{channel}:group:{group_id}"
            
    @staticmethod
    def get_trust_level(session_id: str) -> str:
        """获取会话信任级别"""
        parts = session_id.split(":")
        
        if ":main" in session_id:
            return "main"
        elif ":dm:" in session_id:
            return "dm"
        elif ":group:" in session_id:
            return "group"
            
        return "dm"  # 默认沙箱隔离
        
    @staticmethod
    def parse_session(session_id: str) -> Dict[str, str]:
        """解析会话ID"""
        parts = session_id.split(":")
        result = {
            "prefix": parts[0] if parts else "",
            "agent_id": parts[1] if len(parts) > 1 else "main",
        }
        
        if ":main" in session_id:
            result["type"] = "main"
        elif ":dm:" in session_id:
            result["type"] = "dm"
            result["channel"] = parts[2] if len(parts) > 2 else "unknown"
            result["sender"] = parts[3] if len(parts) > 3 else ""
        elif ":group:" in session_id:
            result["type"] = "group"
            result["channel"] = parts[2] if len(parts) > 2 else "unknown"
            result["group_id"] = parts[3] if len(parts) > 3 else ""
            
        return result


class MessageRouter:
    """消息路由器"""
    
    def __init__(self, access_control: AccessControl):
        self.access_control = access_control
        self.session_resolver = SessionResolver()
        self._routes: Dict[str, RouteRule] = {}
        self._handlers: Dict[str, Callable[[MessageRequest], Awaitable[Message]]] = {}
        
    def register_route(self, rule: RouteRule):
        """注册路由规则"""
        key = f"{rule.channel}:{rule.pattern}"
        self._routes[key] = rule
        logger.info(f"Registered route: {key} -> {rule.agent_id}")
        
    def register_handler(self, agent_id: str, handler: Callable[[MessageRequest], Awaitable[Message]]):
        """注册消息处理器"""
        self._handlers[agent_id] = handler
        
    def route_message(self, request: MessageRequest) -> Optional[str]:
        """路由消息到正确的 Agent"""
        # 解析会话获取 agent_id
        parsed = self.session_resolver.parse_session(request.session_id)
        agent_id = parsed.get("agent_id", "main")
        
        # 检查是否有对应的处理器
        if agent_id in self._handlers:
            return agent_id
            
        # 默认返回 main
        return "main"
        
    async def handle_message(self, request: MessageRequest) -> Message:
        """处理消息"""
        # 路由到正确的 Agent
        agent_id = self.route_message(request)
        
        # 获取处理器
        handler = self._handlers.get(agent_id)
        if not handler:
            raise ValueError(f"No handler for agent: {agent_id}")
            
        # 调用处理器
        return await handler(request)
        
    def get_session_info(self, session_id: str) -> SessionInfo:
        """获取会话信息"""
        parsed = self.session_resolver.parse_session(session_id)
        trust_level = self.session_resolver.get_trust_level(session_id)
        
        return SessionInfo(
            session_id=session_id,
            agent_id=parsed.get("agent_id", "main"),
            channel=parsed.get("channel", "unknown"),
            trust_level=trust_level,
            created_at=datetime.now(),  # TODO: 从存储加载
            last_active=datetime.now(),
        )
        
    def list_sessions(self, agent_id: Optional[str] = None) -> list[SessionInfo]:
        """列出所有会话"""
        # TODO: 从存储加载
        return []
