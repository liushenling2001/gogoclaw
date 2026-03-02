"""
GogoClaw 配置管理模块
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class ChannelConfig(BaseSettings):
    """渠道配置"""
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore"
    )
    enabled: bool = True
    whitelist: List[str] = Field(default_factory=list)
    dm_policy: str = "pairing"  # pairing, open, deny
    group_policy: str = "mentioned"  # mentioned, always, deny
    group_whitelist: List[str] = Field(default_factory=list)


class ModelConfig(BaseSettings):
    """模型配置"""
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore"
    )
    provider: str = "openai"  # openai, anthropic, google, ollama
    model_name: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


class AgentConfig(BaseSettings):
    """智能体配置"""
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore"
    )
    agent_id: str = "main"
    name: str = "GogoClaw"
    model: ModelConfig = Field(default_factory=ModelConfig)
    tools: List[str] = Field(default_factory=lambda: ["command", "browser", "file"])
    system_prompt: str = "You are GogoClaw, a helpful AI assistant."
    sandbox_enabled: bool = True
    memory_enabled: bool = True
    channels: Dict[str, ChannelConfig] = Field(default_factory=dict)


class GatewayConfig(BaseSettings):
    """网关配置"""
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore"
    )
    host: str = "127.0.0.1"
    port: int = 16888
    auth_enabled: bool = False
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])


class MemoryConfig(BaseSettings):
    """记忆配置"""
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore"
    )
    provider: str = "sqlite"  # sqlite, qdrant, chroma
    vector_enabled: bool = True
    embedding_model: str = "text-embedding-3-small"
    similarity_top_k: int = 5


class Settings(BaseSettings):
    """GogoClaw 全局设置"""
    model_config = SettingsConfigDict(
        env_prefix="GOGOCLAW_",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore"
    )
    
    # 路径配置
    home_dir: Path = Field(default_factory=lambda: Path.home() / ".gogoclaw")
    config_file: Optional[Path] = None
    
    # 网关配置
    gateway: GatewayConfig = Field(default_factory=GatewayConfig)
    
    # 智能体配置
    agents: Dict[str, AgentConfig] = Field(default_factory=lambda: {"main": AgentConfig()})
    
    # 记忆配置
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    
    # 调试模式
    debug: bool = False
    
    def load_from_file(self, config_path: Path) -> None:
        """从 JSON5 配置文件加载"""
        if not config_path.exists():
            return
            
        with open(config_path, "r", encoding="utf-8") as f:
            # 简单处理 JSON5 (支持注释和尾随逗号)
            content = f.read()
            # 移除注释
            import re
            content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            # 处理尾随逗号
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            
            data = json.loads(content)
            
        if "gateway" in data:
            self.gateway = GatewayConfig(**data["gateway"])
        if "agents" in data:
            self.agents = {k: AgentConfig(**v) for k, v in data["agents"].items()}
        if "memory" in data:
            self.memory = MemoryConfig(**data["memory"])


# 全局设置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局设置单例"""
    global _settings
    if _settings is None:
        _settings = Settings()
        
        # 尝试加载配置文件
        config_file = _settings.home_dir / "gogoclaw.json"
        if config_file.exists():
            _settings.load_from_file(config_file)
    
    return _settings


def init_settings(**kwargs) -> Settings:
    """初始化设置"""
    global _settings
    _settings = Settings(**kwargs)
    return _settings
