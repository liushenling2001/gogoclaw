# GogoClaw 智能体系统 - 需求规格说明书

## 1. 项目概述

### 1.1 项目背景

基于 OpenClaw 的架构设计理念，设计一个更加开放的 Python 版智能体系统。OpenClaw 是一个个人 AI 助手平台，采用调度中心架构，核心包括网关(Gateway)和智能体(Agent)两大模块。

### 1.2 项目目标

构建一个开放的个人 AI 助手基础设施，实现：
- 跨平台消息统一接入（WhatsApp、Telegram、Discord、飞书、钉钉等）
- 本地化的对话管理和记忆系统
- 安全的工具执行沙箱
- 可扩展的插件体系
- 完全的数据主权控制

### 1.3 核心特性

| 特性 | 描述 |
|------|------|
| 多渠道接入 | 支持多种聊天平台的适配器 |
| 本地部署 | 所有数据存储在用户设备上 |
| 工具执行 | 支持命令行、浏览器、文件操作等 |
| 记忆系统 | 向量搜索 + 关键词匹配的混合记忆 |
| 安全沙箱 | Docker 隔离的工具执行环境 |
| 插件扩展 | 渠道、记忆、工具、模型提供商的插件化 |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         消息来源                                  │
│   WhatsApp │ Telegram │ Discord │ 飞书 │ 钉钉 │ Web UI │ CLI    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Gateway (网关层)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ WebSocket   │  │ 消息路由     │  │ 访问控制    │            │
│  │ 服务器       │  │             │  │             │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Agent (智能体层)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ 会话管理     │  │ 上下文组装   │  │ 模型调用    │            │
│  │             │  │             │  │             │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ 工具执行     │  │ 状态管理    │  │ 多Agent路由 │            │
│  │             │  │             │  │             │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│    Memory (记忆层)       │    │   Tools (工具层)         │
│  ┌─────────────────────┐│    │  ┌─────────────────────┐│
│  │ SQLite + Vector Store││    │  │ Docker 沙箱执行     ││
│  │ 混合搜索             ││    │  │ 命令行/浏览器/文件  ││
│  └─────────────────────┘│    │  └─────────────────────┘│
└─────────────────────────┘    └─────────────────────────┘
```

### 2.2 技术选型

| 组件 | 技术栈 | 说明 |
|------|--------|------|
| WebSocket | FastAPI + websockets | 高性能异步网关 |
| Agent 引擎 | LangChain/LangGraph | 模型调用和工具执行 |
| 消息路由 | 自研 | 统一消息协议 |
| 数据存储 | SQLite + Qdrant/Chroma | 结构化 + 向量存储 |
| 工具沙箱 | Docker SDK | 容器化隔离执行 |
| 配置管理 | Pydantic Settings | 类型安全的配置 |
| 插件系统 | Pluggy | 动态加载扩展 |

---

## 3. 功能需求

### 3.1 网关模块 (Gateway)

#### 3.1.1 WebSocket 服务器
- 默认绑定 127.0.0.1:18789
- 支持 WebSocket 长连接
- 消息格式校验（JSON Schema）
- 事件驱动而非轮询

#### 3.1.2 消息路由
- 根据来源确定会话类型
- 支持多 Agent 实例路由
- 消息幂等性处理（Idempotency Key）

#### 3.1.3 访问控制
- 白名单机制
- DM 配对审批
- 群聊 @提及策略

### 3.2 智能体模块 (Agent)

#### 3.2.1 会话管理
- 主会话 (main): 最高权限
- DM 会话 (dm:channel:id): 沙箱隔离
- 群聊会话 (group:channel:id): 沙箱隔离
- 会话状态持久化

#### 3.2.2 上下文组装
- 加载会话历史
- 读取配置文件拼装 System Prompt
- 记忆语义搜索

#### 3.2.3 工具执行循环
- 拦截工具调用请求
- 沙箱环境执行
- 结果实时反馈给模型

### 3.3 渠道适配器 (Channel Adapter)

#### 3.3.1 内置适配器
- Telegram Bot
- Discord Bot
- Web UI (浏览器)

#### 3.3.2 适配器职责
- 身份验证 (Token/QR)
- 消息解析 (Inbound)
- 消息格式化 (Outbound)
- 访问控制

### 3.4 记忆系统 (Memory)

#### 3.4.1 存储结构
- SQLite: 结构化数据
- Vector Store: 向量嵌入

#### 3.4.2 混合搜索
- 向量相似度 (语义)
- BM25 (关键词)

#### 3.4.3 记忆文件
- MEMORY.md: 长期记忆
- memory/YYYY-MM-DD.md: 每日笔记

### 3.5 工具系统 (Tools)

#### 3.5.1 内置工具
- Command: 执行命令行
- Browser: 浏览器操作
- File: 文件读写
- Editor: 文件编辑

#### 3.5.2 工具沙箱
- Docker 容器隔离
- 网络访问控制
- 资源限制

### 3.6 控制界面

#### 3.6.1 Web UI
- 聊天界面
- 配置管理
- 会话查看

#### 3.6.2 CLI
- 启动网关
- 发送消息
- 健康检查

---

## 4. 数据模型

### 4.1 消息协议

```python
class Message(BaseModel):
    id: str                          # 消息唯一ID
    session_id: str                 # 会话ID
    role: Literal["user", "assistant", "system", "tool"]
    content: str                    # 消息内容
    channel: str                    # 来源渠道
    metadata: Dict[str, Any]        # 额外元数据
    timestamp: datetime              # 时间戳
    idempotency_key: Optional[str]  # 幂等键
```

### 4.2 会话模型

```python
class Session(BaseModel):
    session_id: str                 # agent:agentId:main
    channel: str                    # 渠道
    trust_level: Literal["main", "dm", "group"]
    created_at: datetime
    last_active: datetime
    history: List[Message]
    metadata: Dict[str, Any]
```

### 4.3 配置模型

```python
class AgentConfig(BaseModel):
    agent_id: str
    model_provider: str
    model_name: str
    tools: List[str]
    system_prompt: str
    sandbox_enabled: bool
    channel_config: Dict[str, ChannelConfig]
```

---

## 5. 安全架构

### 5.1 网络安全
- 默认本地绑定 (127.0.0.1)
- 远程访问: SSH 隧道 / Tailscale

### 5.2 身份验证
- Token 认证
- 设备配对机制

### 5.3 渠道访问控制
- 白名单
- DM 配对审批
- 群聊策略

### 5.4 工具沙箱
- Docker 隔离
- 会话级沙箱边界
- 权限层级控制

---

## 6. 插件体系

### 6.1 插件类型

| 类型 | 描述 | 扩展点 |
|------|------|--------|
| Channel | 新聊天平台 | Adapter 类 |
| Memory | 新存储后端 | VectorStore |
| Tool | 自定义工具 | Tool 类 |
| Provider | 新模型商 | ChatModel |

### 6.2 插件目录
```
extensions/
├── channels/
│   └── feishu/
├── memories/
│   └── qdrant/
├── tools/
│   └── custom/
└── providers/
    └── ollama/
```

---

## 7. 项目结构

```
gogoclaw/
├── gogoclaw/                    # 核心包
│   ├── __init__.py
│   ├── gateway/                 # 网关模块
│   │   ├── __init__.py
│   │   ├── server.py            # WebSocket 服务器
│   │   ├── router.py            # 消息路由
│   │   └── security.py          # 访问控制
│   ├── agent/                   # 智能体模块
│   │   ├── __init__.py
│   │   ├── engine.py            # Agent 引擎
│   │   ├── session.py           # 会话管理
│   │   ├── context.py           # 上下文组装
│   │   └── tools.py             # 工具执行
│   ├── channels/               # 渠道适配器
│   │   ├── __init__.py
│   │   ├── base.py              # 适配器基类
│   │   ├── telegram.py
│   │   ├── discord.py
│   │   └── webui.py
│   ├── memory/                  # 记忆系统
│   │   ├── __init__.py
│   │   ├── store.py             # 记忆存储
│   │   └── search.py            # 混合搜索
│   ├── sandbox/                 # 沙箱模块
│   │   ├── __init__.py
│   │   └── docker.py           # Docker 沙箱
│   ├── config/                  # 配置管理
│   │   ├── __init__.py
│   │   └── settings.py
│   └── plugins/                # 插件系统
│       ├── __init__.py
│       └── loader.py
├── extensions/                  # 插件目录
├── ui/                          # Web UI
├── cli/                         # CLI 工具
├── tests/                       # 测试
├── pyproject.toml
└── README.md
```

---

## 8. 验收标准

### 8.1 功能验收
- [ ] WebSocket 服务器正常启动
- [ ] 支持多渠道消息接入
- [ ] Agent 能正确调用模型和工具
- [ ] 记忆系统能存储和检索
- [ ] 工具能在沙箱中执行

### 8.2 安全验收
- [ ] 未授权用户无法访问
- [ ] 沙箱有效隔离工具执行
- [ ] 敏感数据本地存储

### 8.3 性能验收
- [ ] 消息延迟 < 500ms
- [ ] 支持多并发连接
- [ ] 向量搜索 < 100ms
