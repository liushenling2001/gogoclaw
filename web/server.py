"""
GogoClaw Web UI - FastAPI Backend Server

提供:
- 配置管理 API
- 静态文件服务
- WebSocket 实时通信
"""
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field, asdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn

logger = logging.getLogger(__name__)

# ==================== 数据模型 ====================

class ModelConfig(BaseModel):
    """模型配置"""
    provider: str = "openai"
    model_name: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096

class ChannelConfig(BaseModel):
    """渠道配置"""
    enabled: bool = False
    whitelist: List[str] = Field(default_factory=list)
    dm_policy: str = "pairing"
    group_policy: str = "mentioned"

class AgentConfig(BaseModel):
    """智能体配置"""
    agent_id: str = "main"
    name: str = "GogoClaw"
    model: ModelConfig = Field(default_factory=ModelConfig)
    tools: List[str] = Field(default_factory=lambda: ["command", "browser", "file"])
    system_prompt: str = "You are GogoClaw, a helpful AI assistant."
    sandbox_enabled: bool = True
    memory_enabled: bool = True
    channels: Dict[str, ChannelConfig] = Field(default_factory=dict)

class ConfigResponse(BaseModel):
    """配置响应"""
    agents: Dict[str, AgentConfig]
    gateway: Dict[str, Any]
    memory: Dict[str, Any]
    
class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    agent_id: str = "main"
    model: Optional[ModelConfig] = None
    channels: Optional[Dict[str, ChannelConfig]] = None
    tools: Optional[List[str]] = None
    sandbox_enabled: Optional[bool] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    
class ModelInfo(BaseModel):
    """模型信息"""
    provider: str
    model_name: str
    display_name: str
    
class TestKeyRequest(BaseModel):
    """测试 API Key 请求"""
    provider: str
    api_key: str
    model_name: Optional[str] = None
    base_url: Optional[str] = None
    
class TestKeyResponse(BaseModel):
    """测试 API Key 响应"""
    success: bool
    message: str
    model_info: Optional[str] = None

# ==================== 配置管理 ====================

CONFIG_DIR = Path.home() / ".gogoclaw"
CONFIG_FILE = CONFIG_DIR / "gogoclaw.json"

def get_config_path() -> Path:
    """获取配置文件路径"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_FILE

def load_config() -> Dict[str, Any]:
    """加载配置"""
    config_file = get_config_path()
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置失败：{e}")
    
    # 返回默认配置
    return {
        "gateway": {
            "host": "127.0.0.1",
            "port": 16888,
            "auth_enabled": False,
            "cors_origins": ["*"]
        },
        "agents": {
            "main": {
                "agent_id": "main",
                "name": "GogoClaw",
                "model": {
                    "provider": "openai",
                    "model_name": "gpt-4o",
                    "api_key": None,
                    "base_url": None,
                    "temperature": 0.7,
                    "max_tokens": 4096
                },
                "tools": ["command", "browser", "file"],
                "system_prompt": "You are GogoClaw, a helpful AI assistant.",
                "sandbox_enabled": True,
                "memory_enabled": True,
                "channels": {}
            }
        },
        "memory": {
            "provider": "sqlite",
            "vector_enabled": True,
            "embedding_model": "text-embedding-3-small",
            "similarity_top_k": 5
        }
    }

def save_config(config: Dict[str, Any]) -> bool:
    """保存配置"""
    try:
        config_file = get_config_path()
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"保存配置失败：{e}")
        return False

# ==================== FastAPI 应用 ====================

app = FastAPI(title="GogoClaw Web UI", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件目录
web_dir = Path(__file__).parent

@app.get("/")
async def root():
    """根路径 - 返回前端页面"""
    index_file = web_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"status": "ok", "service": "gogoclaw-webui"}

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/config")
async def get_config():
    """获取当前配置"""
    config = load_config()
    return config

@app.put("/api/config")
async def update_config(request: ConfigUpdateRequest):
    """更新配置"""
    config = load_config()
    
    if request.agent_id not in config.get("agents", {}):
        # 创建新的 agent 配置
        config["agents"][request.agent_id] = {
            "agent_id": request.agent_id,
            "name": "GogoClaw",
            "model": {},
            "tools": ["command", "browser", "file"],
            "sandbox_enabled": True
        }
    
    agent = config["agents"][request.agent_id]
    
    # 更新模型配置
    if request.model:
        if "model" not in agent:
            agent["model"] = {}
        model_data = request.model.model_dump(exclude_unset=True)
        agent["model"].update(model_data)
    
    # 更新高级设置
    if request.temperature is not None:
        if "model" not in agent:
            agent["model"] = {}
        agent["model"]["temperature"] = request.temperature
    if request.max_tokens is not None:
        if "model" not in agent:
            agent["model"] = {}
        agent["model"]["max_tokens"] = request.max_tokens
    if request.sandbox_enabled is not None:
        agent["sandbox_enabled"] = request.sandbox_enabled
    if request.tools:
        agent["tools"] = request.tools
    if request.channels:
        if "channels" not in agent:
            agent["channels"] = {}
        for channel_id, channel_config in request.channels.items():
            if channel_id in agent["channels"]:
                agent["channels"][channel_id]["enabled"] = channel_config.enabled
            else:
                agent["channels"][channel_id] = channel_config.model_dump()
    
    # 保存配置
    if save_config(config):
        return {"status": "success", "message": "配置已更新"}
    else:
        raise HTTPException(status_code=500, detail="保存配置失败")

@app.get("/api/config/models")
async def get_available_models():
    """获取可用模型列表"""
    models = [
        # OpenAI
        {"provider": "openai", "model_name": "gpt-4o", "display_name": "GPT-4o"},
        {"provider": "openai", "model_name": "gpt-4o-mini", "display_name": "GPT-4o Mini"},
        {"provider": "openai", "model_name": "gpt-4-turbo", "display_name": "GPT-4 Turbo"},
        {"provider": "openai", "model_name": "gpt-3.5-turbo", "display_name": "GPT-3.5 Turbo"},
        
        # Anthropic
        {"provider": "anthropic", "model_name": "claude-sonnet-4-20250514", "display_name": "Claude Sonnet 4"},
        {"provider": "anthropic", "model_name": "claude-3-5-sonnet-20241022", "display_name": "Claude 3.5 Sonnet"},
        {"provider": "anthropic", "model_name": "claude-3-opus-20240229", "display_name": "Claude 3 Opus"},
        
        # Google
        {"provider": "google", "model_name": "gemini-2.0-flash", "display_name": "Gemini 2.0 Flash"},
        {"provider": "google", "model_name": "gemini-1.5-pro", "display_name": "Gemini 1.5 Pro"},
        
        # Ollama (本地)
        {"provider": "ollama", "model_name": "qwen2.5:7b", "display_name": "Qwen 2.5 7B"},
        {"provider": "ollama", "model_name": "llama3.1:8b", "display_name": "Llama 3.1 8B"},
        {"provider": "ollama", "model_name": "deepseek-r1:8b", "display_name": "DeepSeek R1 8B"},
    ]
    
    return {"models": models}

@app.post("/api/config/test")
async def test_api_key(request: TestKeyRequest):
    """测试 API Key 有效性"""
    try:
        if not request.api_key or len(request.api_key) < 10:
            return TestKeyResponse(
                success=False,
                message="API Key 格式不正确"
            ).model_dump()
        
        if request.provider == "openai":
            if request.api_key.startswith("sk-"):
                return TestKeyResponse(
                    success=True,
                    message="OpenAI API Key 格式正确",
                    model_info=request.model_name or "gpt-4o"
                ).model_dump()
            else:
                return TestKeyResponse(
                    success=False,
                    message="OpenAI API Key 应以 sk- 开头"
                ).model_dump()
        
        elif request.provider == "anthropic":
            if request.api_key.startswith("sk-ant-"):
                return TestKeyResponse(
                    success=True,
                    message="Anthropic API Key 格式正确",
                    model_info=request.model_name or "claude-sonnet-4-20250514"
                ).model_dump()
            else:
                return TestKeyResponse(
                    success=False,
                    message="Anthropic API Key 应以 sk-ant- 开头"
                ).model_dump()
        
        elif request.provider == "google":
            if len(request.api_key) > 20:
                return TestKeyResponse(
                    success=True,
                    message="Google API Key 格式正确",
                    model_info=request.model_name or "gemini-2.0-flash"
                ).model_dump()
            else:
                return TestKeyResponse(
                    success=False,
                    message="Google API Key 长度不足"
                ).model_dump()
        
        elif request.provider == "ollama":
            return TestKeyResponse(
                success=True,
                message="Ollama 本地部署，无需 API Key",
                model_info=request.model_name or "qwen2.5:7b"
            ).model_dump()
        
        else:
            return TestKeyResponse(
                success=True,
                message=f"{request.provider} API Key 格式验证通过",
                model_info=request.model_name
            ).model_dump()
            
    except Exception as e:
        return TestKeyResponse(
            success=False,
            message=f"测试失败：{str(e)}"
        ).model_dump()

@app.get("/api/channels")
async def get_channels():
    """获取可用渠道列表"""
    channels = [
        {"id": "telegram", "name": "Telegram", "enabled": False},
        {"id": "discord", "name": "Discord", "enabled": False},
        {"id": "feishu", "name": "飞书", "enabled": False},
        {"id": "dingtalk", "name": "钉钉", "enabled": False},
        {"id": "whatsapp", "name": "WhatsApp", "enabled": False},
    ]
    return {"channels": channels}

# ==================== WebSocket 处理 ====================

class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client connected: {client_id}")
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client disconnected: {client_id}")
            
    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: str = Query("default")):
    """WebSocket 实时通信端点"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type", "message")
                
                if msg_type == "chat":
                    await handle_chat_message(message, websocket)
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
    except WebSocketDisconnect:
        manager.disconnect(client_id)

async def handle_chat_message(message: dict, websocket: WebSocket):
    """处理聊天消息"""
    content = message.get("content", "")
    session_id = message.get("session_id", "default")
    
    await websocket.send_json({
        "type": "message_received",
        "session_id": session_id
    })
    
    await websocket.send_json({
        "type": "tool_call",
        "tool": "thinking",
        "status": "processing",
        "message": "正在思考..."
    })
    
    await asyncio.sleep(1)
    
    response_text = f"收到您的消息：{content}\n\n这是一个演示响应。实际部署时将调用 GogoClaw Agent 处理。"
    
    await websocket.send_json({
        "type": "stream_start",
        "session_id": session_id
    })
    
    for i in range(0, len(response_text), 10):
        chunk = response_text[i:i+10]
        await websocket.send_json({
            "type": "stream_chunk",
            "content": chunk
        })
        await asyncio.sleep(0.05)
    
    await websocket.send_json({
        "type": "stream_end",
        "session_id": session_id
    })

# ==================== 启动 ====================

def run_server(host: str = "0.0.0.0", port: int = 16889, reload: bool = False):
    """运行服务器"""
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_server(host="0.0.0.0", port=16889, reload=True)
