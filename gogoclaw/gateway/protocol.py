"""
GogoClaw 网关模块 - 消息协议定义
"""
from datetime import datetime
from typing import Optional, Dict, Any, Literal, List
from pydantic import BaseModel, Field
import uuid


class Message(BaseModel):
    """统一消息协议"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    channel: str = "webui"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    idempotency_key: Optional[str] = None
    
    # 工具调用相关
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class MessageRequest(BaseModel):
    """消息请求"""
    session_id: str
    content: str
    channel: str = "webui"
    idempotency_key: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    """消息响应"""
    message: Message
    status: Literal["success", "error"] = "success"
    error: Optional[str] = None


class StreamChunk(BaseModel):
    """流式响应块"""
    chunk: str
    done: bool = False
    message_id: str


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    agent_id: str
    channel: str
    trust_level: Literal["main", "dm", "group"]
    created_at: datetime
    last_active: datetime
    message_count: int = 0


class Event(BaseModel):
    """事件"""
    type: Literal["message", "typing", "reaction", "session_start", "session_end"]
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class ConfigRequest(BaseModel):
    """配置请求"""
    action: Literal["get", "set", "list_agents"]
    key: Optional[str] = None
    value: Any = None


class ConfigResponse(BaseModel):
    """配置响应"""
    success: bool
    data: Any = None
    error: Optional[str] = None
