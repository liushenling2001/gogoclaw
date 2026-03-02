"""
GogoClaw CLI - 命令行工具
"""
import asyncio
import sys
import logging
from pathlib import Path
import click
import json

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from gogoclaw.config.settings import Settings, get_settings, init_settings
from gogoclaw.gateway.server import GatewayServer
from gogoclaw.agent.engine import AgentEngine, AgentConfig
from gogoclaw.memory.store import MemoryStore


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """GogoClaw - 开放的智能体系统"""
    pass


@cli.command()
@click.option("--host", default="127.0.0.1", help="绑定地址")
@click.option("--port", default=16888, help="绑定端口")
@click.option("--config", type=click.Path(), help="配置文件路径")
def gateway(host: str, port: int, config: str):
    """启动网关服务器"""
    click.echo(f"Starting GogoClaw Gateway on {host}:{port}...")
    
    # 初始化设置
    settings = init_settings()
    settings.gateway.host = host
    settings.gateway.port = port
    
    if config:
        settings.load_from_file(Path(config))
        
    # 创建并启动网关
    gateway_server = GatewayServer()
    
    try:
        gateway_server.run()
    except KeyboardInterrupt:
        click.echo("\nGateway stopped.")


@cli.command()
@click.option("--message", "-m", required=True, help="发送的消息")
@click.option("--session", "-s", default="agent:main:webui:dm:cli", help="会话ID")
@click.option("--agent", "-a", default="main", help="Agent ID")
def message(message: str, session: str, agent: str):
    """发送消息到 Agent"""
    click.echo(f"Sending message to {agent}...")
    
    # TODO: 实现通过 CLI 发送消息
    click.echo("This feature is not yet implemented.")


@cli.command()
def doctor():
    """运行健康检查"""
    click.echo("Running GogoClaw health check...")
    
    # 检查配置
    settings = get_settings()
    click.echo(f"✓ Config loaded: {settings.home_dir}")
    
    # 检查目录
    if settings.home_dir.exists():
        click.echo(f"✓ Home directory exists: {settings.home_dir}")
    else:
        click.echo(f"✗ Home directory not found: {settings.home_dir}")
        
    # 检查端口
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', settings.gateway.port))
    sock.close()
    
    if result == 0:
        click.echo(f"✗ Port {settings.gateway.port} is in use")
    else:
        click.echo(f"✓ Port {settings.gateway.port} is available")
        
    click.echo("\nHealth check complete.")


@cli.command()
@click.option("--provider", type=click.Choice(["openai", "anthropic", "google", "ollama"]), help="模型提供商")
@click.option("--model", help="模型名称")
@click.option("--api-key", help="API Key")
def config(provider: str, model: str, api_key: str):
    """显示或修改配置"""
    settings = get_settings()
    
    click.echo("Current configuration:")
    click.echo(json.dumps({
        "gateway": {
            "host": settings.gateway.host,
            "port": settings.gateway.port
        },
        "agents": {
            name: {
                "model": {
                    "provider": agent.model.provider,
                    "model_name": agent.model.model_name
                }
            }
            for name, agent in settings.agents.items()
        }
    }, indent=2))


@cli.command()
def init():
    """初始化 GogoClaw 配置"""
    home_dir = Path.home() / ".gogoclaw"
    
    # 创建目录
    home_dir.mkdir(parents=True, exist_ok=True)
    (home_dir / "sessions").mkdir(exist_ok=True)
    (home_dir / "memory").mkdir(exist_ok=True)
    (home_dir / "workspace").mkdir(exist_ok=True)
    
    # 创建默认配置文件
    config_file = home_dir / "gogoclaw.json"
    if not config_file.exists():
        default_config = {
            "gateway": {
                "host": "127.0.0.1",
                "port": 16888,
                "auth_enabled": False
            },
            "agents": {
                "main": {
                    "agent_id": "main",
                    "name": "GogoClaw",
                    "model": {
                        "provider": "openai",
                        "model_name": "gpt-4o",
                        "api_key": ""  # TODO: 从环境变量读取
                    },
                    "system_prompt": "You are GogoClaw, a helpful AI assistant.",
                    "tools": ["command", "file", "browser"],
                    "sandbox_enabled": True,
                    "memory_enabled": True,
                    "channels": {}
                }
            },
            "memory": {
                "provider": "sqlite",
                "vector_enabled": True,
                "embedding_model": "text-embedding-3-small"
            }
        }
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
            
    click.echo(f"GogoClaw initialized at: {home_dir}")
    click.echo("\nNext steps:")
    click.echo("1. Set your API key: export OPENAI_API_KEY=your_key")
    click.echo("2. Start gateway: gogoclaw gateway")


@cli.command()
def version():
    """显示版本信息"""
    from gogoclaw import __version__
    click.echo(f"GogoClaw {__version__}")


if __name__ == "__main__":
    cli()
