"""
GogoClaw 网关模块 - WebSocket 服务器
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, Set, Callable
from datetime import datetime
from dataclasses import dataclass, field

import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from gogoclaw.gateway.protocol import (
    Message, 
    MessageRequest, 
    MessageResponse,
    StreamChunk,
    Event,
    SessionInfo,
)
from gogoclaw.gateway.router import MessageRouter, SessionResolver
from gogoclaw.gateway.security import AccessControl
from gogoclaw.config.settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class Connection:
    """WebSocket 连接"""
    conn_id: str
    websocket: WebSocket
    device_id: str
    is_local: bool = True
    subscribed_events: Set[str] = field(default_factory=set)
    session_id: Optional[str] = None


class ConnectionManager:
    """连接管理器"""
    
    def __init__(self):
        self._connections: Dict[str, Connection] = {}
        self._sessions: Dict[str, Set[str]] = {}  # session_id -> set of conn_ids
        
    async def connect(self, conn: Connection):
        """建立连接"""
        self._connections[conn.conn_id] = conn
        logger.info(f"Client connected: {conn.conn_id} (local={conn.is_local})")
        
    def disconnect(self, conn_id: str):
        """断开连接"""
        conn = self._connections.pop(conn_id, None)
        if conn and conn.session_id:
            self._sessions[conn.session_id].discard(conn_id)
        logger.info(f"Client disconnected: {conn_id}")
        
    async def send_message(self, conn_id: str, message: Message):
        """发送消息到客户端"""
        conn = self._connections.get(conn_id)
        if conn:
            await conn.websocket.send_json(message.model_dump(mode="json"))
            
    async def send_event(self, conn_id: str, event: Event):
        """发送事件到客户端"""
        conn = self._connections.get(conn_id)
        if conn:
            await conn.websocket.send_json({
                "type": "event",
                "data": event.model_dump(mode="json")
            })
            
    async def broadcast_to_session(self, session_id: str, message: Message):
        """向会话的所有连接广播消息"""
        conn_ids = self._sessions.get(session_id, set())
        for conn_id in conn_ids:
            await self.send_message(conn_id, message)
            
    def join_session(self, conn_id: str, session_id: str):
        """连接加入会话"""
        conn = self._connections.get(conn_id)
        if conn:
            conn.session_id = session_id
            if session_id not in self._sessions:
                self._sessions[session_id] = set()
            self._sessions[session_id].add(conn_id)
            
    def leave_session(self, conn_id: str):
        """连接离开会话"""
        conn = self._connections.get(conn_id)
        if conn and conn.session_id:
            self._sessions[conn.session_id].discard(conn_id)
            conn.session_id = None


class GatewayServer:
    """网关服务器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.access_control = AccessControl()
        self.router = MessageRouter(self.access_control)
        self.connection_manager = ConnectionManager()
        self._app: Optional[FastAPI] = None
        self._ws_task: Optional[asyncio.Task] = None
        
    @property
    def app(self) -> FastAPI:
        if self._app is None:
            self._app = self._create_app()
        return self._app
        
    def _create_app(self) -> FastAPI:
        """创建 FastAPI 应用"""
        app = FastAPI(title="GogoClaw Gateway")
        
        @app.get("/")
        async def root():
            return {"status": "ok", "service": "gogoclaw-gateway"}
            
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
            
        @app.websocket("/ws")
        async def websocket_endpoint(
            websocket: WebSocket,
            device_id: Optional[str] = Query(None),
            token: Optional[str] = Query(None)
        ):
            await self._handle_websocket(websocket, device_id, token)
            
        @app.get("/api/sessions")
        async def list_sessions(agent_id: Optional[str] = None):
            sessions = self.router.list_sessions(agent_id)
            return {"sessions": [s.model_dump(mode="json") for s in sessions]}
            
        @app.get("/api/sessions/{session_id}")
        async def get_session(session_id: str):
            info = self.router.get_session_info(session_id)
            return info.model_dump(mode="json")
            
        return app
        
    async def _handle_websocket(
        self, 
        websocket: WebSocket, 
        device_id: Optional[str],
        token: Optional[str]
    ):
        """处理 WebSocket 连接"""
        # 接受连接
        await websocket.accept()
        
        # 生成连接ID
        conn_id = str(uuid.uuid4())
        
        # 简单验证
        is_local = True  # TODO: 实现更复杂的验证
        
        # 创建连接对象
        conn = Connection(
            conn_id=conn_id,
            websocket=websocket,
            device_id=device_id or "unknown",
            is_local=is_local
        )
        
        # 注册连接
        await self.connection_manager.connect(conn)
        
        try:
            # 处理消息循环
            while True:
                data = await websocket.receive_text()
                await self._process_message(conn, data)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {conn_id}")
        finally:
            self.connection_manager.disconnect(conn_id)
            
    async def _process_message(self, conn: Connection, data: str):
        """处理接收到的消息"""
        try:
            # 解析 JSON
            payload = json.loads(data)
            msg_type = payload.get("type", "message")
            
            if msg_type == "message":
                await self._handle_chat_message(conn, payload)
            elif msg_type == "subscribe":
                await self._handle_subscribe(conn, payload)
            elif msg_type == "ping":
                await conn.websocket.send_json({"type": "pong"})
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            await conn.websocket.send_json({
                "type": "error",
                "error": "Invalid JSON"
            })
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await conn.websocket.send_json({
                "type": "error",
                "error": str(e)
            })
            
    async def _handle_chat_message(self, conn: Connection, payload: Dict):
        """处理聊天消息"""
        # 创建请求
        request = MessageRequest(
            session_id=payload.get("session_id", f"agent:main:{conn.device_id}:dm:{conn.device_id}"),
            content=payload.get("content", ""),
            channel=payload.get("channel", "webui"),
            metadata=payload.get("metadata", {})
        )
        
        if not request.content:
            return
            
        # 加入会话
        self.connection_manager.join_session(conn.conn_id, request.session_id)
        
        # 调用 Agent 处理
        try:
            response = await self.router.handle_message(request)
            
            # 发送响应
            await conn.websocket.send_json({
                "type": "message",
                "data": response.model_dump(mode="json")
            })
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await conn.websocket.send_json({
                "type": "error",
                "error": str(e)
            })
            
    async def _handle_subscribe(self, conn: Connection, payload: Dict):
        """处理订阅"""
        events = payload.get("events", [])
        conn.subscribed_events.update(events)
        await conn.websocket.send_json({
            "type": "subscribed",
            "events": list(conn.subscribed_events)
        })
        
    def register_agent_handler(self, agent_id: str, handler):
        """注册 Agent 处理器"""
        self.router.register_handler(agent_id, handler)
        
    async def start(self):
        """启动服务器"""
        import uvicorn
        config = uvicorn.Config(
            self.app,
            host=self.settings.gateway.host,
            port=self.settings.gateway.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    def run(self):
        """运行服务器 (同步)"""
        import uvicorn
        uvicorn.run(
            self.app,
            host=self.settings.gateway.host,
            port=self.settings.gateway.port,
            log_level="debug" if self.settings.debug else "info"
        )

