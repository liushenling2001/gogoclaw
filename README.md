# GogoClaw

[English](./README.md) | [中文](./README_zh.md)

GogoClaw 是一个基于 OpenClaw 架构设计的开放式 Python 智能体系统。它是一个个人 AI 助手平台，数据完全存储在本地设备上，给你完全的数据控制权。

![Python Version](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)

## 特性

- 🌍 **多渠道接入** - 支持 Telegram、Discord、飞书、钉钉等多种聊天平台
- 🔒 **本地部署** - 所有数据存储在本地，保护隐私
- 🧠 **记忆系统** - 向量搜索 + 关键词匹配的混合记忆
- 🛡️ **安全沙箱** - Docker 隔离的工具执行环境
- 🔌 **插件体系** - 支持渠道、记忆、工具、模型提供商的插件化扩展
- 🎯 **完全控制** - 数据存储、AI 能力、访问权限全部由你掌控

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      消息来源                             │
│   Telegram │ Discord │ 飞书 │ 钉钉 │ Web UI │ CLI     │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Gateway (网关层)                       │
│  WebSocket 服务器 │ 消息路由 │ 访问控制                   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Agent (智能体层)                       │
│  会话管理 │ 上下文组装 │ 模型调用 │ 工具执行             │
└─────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│   Memory (记忆层)        │    │   Tools (工具层)         │
│  SQLite + Vector Store  │    │   Docker 沙箱执行       │
└─────────────────────────┘    └─────────────────────────┘
```

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/gogoclaw/gogoclaw.git
cd gogoclaw

# 安装依赖
pip install -e .

# 或者安装所有可选依赖
pip install -e ".[all]"
```

### 配置

```bash
# 初始化配置
gogoclaw init
```

然后编辑 `~/.gogoclaw/gogoclaw.json`：

```json
{
  "agents": {
    "main": {
      "model": {
        "provider": "openai",
        "model_name": "gpt-4o",
        "api_key": "your-api-key"
      }
    }
  }
}
```

### 启动

```bash
# 启动网关
gogoclaw gateway

# 或者指定端口
gogoclaw gateway --port 8080
```

现在可以访问 `http://127.0.0.1:18789` 使用 Web UI。

## 配置说明

### 环境变量

| 变量 | 描述 |
|------|------|
| `GOGOCLAW_HOME` | 配置目录 (默认: `~/.gogoclaw`) |
| `OPENAI_API_KEY` | OpenAI API Key |
| `ANTHROPIC_API_KEY` | Anthropic API Key |

### 配置文件

配置文件位于 `~/.gogoclaw/gogoclaw.json`：

```json
{
  "gateway": {
    "host": "127.0.0.1",
    "port": 18789,
    "auth_enabled": false
  },
  "agents": {
    "main": {
      "agent_id": "main",
      "name": "GogoClaw",
      "model": {
        "provider": "openai",
        "model_name": "gpt-4o"
      },
      "tools": ["command", "file", "browser"],
      "sandbox_enabled": true,
      "memory_enabled": true
    }
  },
  "memory": {
    "provider": "sqlite",
    "vector_enabled": true,
    "embedding_model": "text-embedding-3-small"
  }
}
```

## 工作空间

Agent 的工作空间位于 `~/.gogoclaw/workspace/`，可以放置以下配置文件：

| 文件 | 描述 |
|------|------|
| `AGENTS.md` | Agent 核心规则 |
| `SOUL.md` | Agent 人格和语气 |
| `TOOLS.md` | 工具使用备注 |
| `MEMORY.md` | 长期记忆 |
| `skills/` | 技能文件目录 |

## CLI 命令

```bash
# 启动网关
gogoclaw gateway

# 发送消息
gogoclaw message -m "Hello"

# 健康检查
gogoclaw doctor

# 查看/修改配置
gogoclaw config

# 初始化
gogoclaw init

# 版本
gogoclaw version
```

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black .
ruff check --fix .

# 类型检查
mypy .
```

## 路线图

- [ ] 完整的 Web UI
- [ ] 更多渠道适配器 (WhatsApp, 飞书, 钉钉)
- [ ] 向量存储支持 (Qdrant, Chroma)
- [ ] 语音交互
- [ ] 多 Agent 路由
- [ ] Canvas/A2UI 支持

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 参考

- [OpenClaw](https://github.com/obertyh/OpenClaw) - 原始项目
- [LangChain](https://github.com/langchain-ai/langchain) - 模型调用框架
- [FastAPI](https://github.com/tiangolo/fastapi) - Web 框架
