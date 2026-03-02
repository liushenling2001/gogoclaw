# GogoClaw - 开放的智能体系统

> 让每个开发者都能轻松构建和部署 AI 智能体

## 简介

GogoClaw 是一个开源的 AI 智能体系统，支持连接多种大语言模型和主流通讯渠道，让你能够快速构建自己的 AI 助手。

### 核心特性

- 🌐 **多模型支持** - 支持国内外 7+ 家主流模型服务商
- 💬 **多渠道接入** - Telegram、Discord、飞书、钉钉、WhatsApp
- 🔧 **工具系统** - 内置命令执行、文件操作、网页抓取等工具
- 🧠 **记忆系统** - 支持短期和长期记忆，让 AI 更懂你
- 🔒 **安全沙箱** - 可选的 Docker 沙箱模式，安全执行命令
- 🎛️ **Web UI** - 直观的配置管理后台和聊天界面
- 📦 **易于部署** - 支持 Windows、Ubuntu、macOS

## 快速开始

### 安装步骤

#### Windows

```bash
# 1. 安装 Python 3.10+
# 从 python.org 下载并安装

# 2. 克隆项目
git clone https://github.com/your-org/gogoclaw.git
cd gogoclaw

# 3. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 4. 安装依赖
pip install -e .

# 5. 配置环境变量
# 复制 .env.example 到 .env 并填写你的 API Key
```

#### Ubuntu/Debian

```bash
# 1. 安装 Python 3.10+
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# 2. 克隆项目
git clone https://github.com/your-org/gogoclaw.git
cd gogoclaw

# 3. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 4. 安装依赖
pip install -e .

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写你的 API Key
```

#### macOS

```bash
# 1. 安装 Python 3.10+
brew install python@3.10

# 2. 克隆项目
git clone https://github.com/your-org/gogoclaw.git
cd gogoclaw

# 3. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 4. 安装依赖
pip install -e .

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写你的 API Key
```

### 配置说明

编辑 `.env` 文件配置你的 API Key：

```bash
# 模型配置
GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER=openai
GOGOCLAW_AGENTS__MAIN__MODEL__MODEL_NAME=gpt-4o
GOGOCLAW_AGENTS__MAIN__MODEL__API_KEY=sk-your-api-key

# 网关配置
GOGOCLAW_GATEWAY__HOST=127.0.0.1
GOGOCLAW_GATEWAY__PORT=18789

# 渠道配置
GOGOCLAW_AGENTS__MAIN__CHANNELS__TELEGRAM__TOKEN=your-telegram-bot-token
```

### 启动方式

```bash
# 开发模式（自动重载）
python -m gogoclaw.gateway.server --reload

# 生产模式
python -m gogoclaw.gateway.server

# 使用 CLI
gogoclaw start

# 查看帮助
gogoclaw --help
```

启动后访问 http://localhost:18789 打开 Web UI。

## 支持的模型服务商

### 国内模型

| 服务商 | 配置项 | 示例模型 |
|--------|--------|----------|
| 阿里 DashScope | `dashscope` / `aliyun` | qwen-plus |
| 智谱 AI | `zhipu` / `glm` | glm-4 |
| Kimi (月之暗面) | `kimi` / `moonshot` | moonshot-v1-8k |
| Ollama (本地) | `ollama` | llama3.2 |

### 国际模型

| 服务商 | 配置项 | 示例模型 |
|--------|--------|----------|
| OpenAI | `openai` | gpt-4o |
| Anthropic | `anthropic` / `claude` | claude-3-5-sonnet-20241022 |
| Google | `google` / `gemini` | gemini-1.5-pro |

## 支持的渠道

| 渠道 | 状态 | 配置说明 |
|------|------|----------|
| Telegram | ✅ 已实现 | 需要 Bot Token |
| Discord | ✅ 已实现 | 需要 Bot Token |
| 飞书 | ✅ 已实现 | 需要 App ID 和 Secret |
| 钉钉 | ✅ 已实现 | 需要 AppKey 和 AppSecret |
| WhatsApp | ✅ 已实现 | 需要 Business API |
| Web UI | ✅ 已实现 | 内置，无需配置 |

## Web UI 使用指南

### 配置管理后台

访问 http://localhost:18789/admin 进入管理后台：

- **模型配置** - 切换模型服务商、调整参数
- **渠道管理** - 启用/禁用渠道、配置白名单
- **会话管理** - 查看和管理活跃会话
- **日志查看** - 实时查看系统日志

### 聊天界面

访问 http://localhost:18789 进入聊天界面：

- 直接输入消息与 AI 对话
- 支持 Markdown 格式
- 显示工具执行结果
- 支持多会话切换

## 高级用法

### 工具系统

GogoClaw 内置多种工具：

```python
# 执行命令
execute_command(command="ls -la", timeout=30)

# 读取文件
read_file(path="/path/to/file.txt", offset=0, limit=100)

# 写入文件
write_file(path="/path/to/file.txt", content="Hello")

# 列出目录
list_directory(path=".", include_hidden=False)

# 搜索记忆
search_memory(query="previous conversation", limit=5)

# 浏览器操作
browser_navigate(url="https://example.com", action="get_html")
```

### 沙箱模式

启用沙箱模式后，命令将在 Docker 容器中执行：

```bash
# 在配置中启用
GOGOCLAW_AGENTS__MAIN__SANDBOX_ENABLED=true

# 需要安装 Docker
docker --version
```

### 记忆系统

记忆系统让 AI 能够记住之前的对话：

```bash
# 启用记忆
GOGOCLAW_AGENTS__MAIN__MEMORY_ENABLED=true

# 配置记忆存储
GOGOCLAW_MEMORY__PROVIDER=sqlite  # 或 qdrant, chroma
GOGOCLAW_MEMORY__VECTOR_ENABLED=true
```

## API 文档

详细的 API 文档请查看 [docs/API.md](docs/API.md)

### 快速参考

```bash
# 获取配置
curl http://localhost:18789/api/config

# 更新配置
curl -X PUT http://localhost:18789/api/config \
  -H "Content-Type: application/json" \
  -d '{"gateway": {"port": 8080}}'

# 创建会话
curl -X POST http://localhost:18789/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "main"}'

# 发送消息
curl -X POST http://localhost:18789/api/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "xxx", "content": "Hello"}'
```

## 开发指南

### 项目结构

```
gogoclaw/
├── agent/          # 智能体核心
│   ├── engine.py   # 引擎
│   ├── tools.py    # 工具系统
│   └── session.py  # 会话管理
├── channels/       # 渠道适配器
│   ├── base.py     # 基类
│   ├── telegram.py
│   ├── discord.py
│   └── ...
├── config/         # 配置管理
├── gateway/        # 网关服务
├── memory/         # 记忆系统
├── sandbox/        # 沙箱实现
├── utils/          # 工具函数
└── web/            # Web UI
```

### 添加新模型服务商

1. 在 `gogoclaw/agent/model_client.py` 中创建新的客户端类：

```python
class NewProviderClient(BaseModelClient):
    def __init__(self, api_key: str, model: str = "default", **kwargs):
        self.api_key = api_key
        self.model = model
        
    async def chat(self, messages, tools=None, **kwargs) -> ModelResponse:
        # 实现 API 调用
        pass
```

2. 在 `create_model_client` 函数中注册：

```python
clients = {
    "newprovider": NewProviderClient,
    # ...
}
```

### 添加新渠道

1. 在 `gogoclaw/channels/` 中创建新的适配器：

```python
from gogoclaw.channels.base import ChannelAdapter, ChannelType

class NewChannelAdapter(ChannelAdapter):
    async def start(self):
        # 启动逻辑
        pass
        
    async def send_message(self, receiver_id, content, metadata=None):
        # 发送消息逻辑
        pass
```

2. 在渠道注册表中注册新适配器。

## 常见问题

### Q: 如何切换模型？

A: 修改 `.env` 文件中的 `GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER` 和 `MODEL_NAME`，然后重启服务。

### Q: 支持多个 Agent 吗？

A: 支持。在配置文件中添加多个 agent 配置即可。

### Q: 如何查看日志？

A: 日志输出到 `~/.gogoclaw/logs/` 目录，或在 Web UI 的管理后台查看。

### Q: 命令执行失败怎么办？

A: 检查沙箱模式是否启用，确认 Docker 是否正常运行。也可以临时禁用沙箱模式测试。

### Q: 支持流式输出吗？

A: 目前不支持，计划在未来版本中添加。

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

### 开发环境设置

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 代码格式化
black gogoclaw/
isort gogoclaw/

# 类型检查
mypy gogoclaw/
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**GogoClaw** - 让 AI 智能体触手可及 🚀
