# GogoClaw API 文档

## 基础信息

- **Base URL**: `http://localhost:18789`
- **认证方式**: Bearer Token (可选，取决于配置)
- **内容类型**: `application/json`
- **字符编码**: `UTF-8`

### 认证

如果启用了认证，需要在请求头中添加：

```
Authorization: Bearer <your-token>
```

## 端点列表

### 配置管理

#### GET /api/config

获取当前配置。

**请求示例**:
```bash
curl http://localhost:18789/api/config
```

**响应示例**:
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
      "sandbox_enabled": true,
      "memory_enabled": true
    }
  },
  "memory": {
    "provider": "sqlite",
    "vector_enabled": true
  }
}
```

---

#### PUT /api/config

更新配置。

**请求示例**:
```bash
curl -X PUT http://localhost:18789/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "agents": {
      "main": {
        "model": {
          "provider": "anthropic",
          "model_name": "claude-3-5-sonnet-20241022"
        }
      }
    }
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "Configuration updated"
}
```

---

#### POST /api/config/test

测试配置（如测试模型连接）。

**请求示例**:
```bash
curl -X POST http://localhost:18789/api/config/test \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "api_key": "sk-test123"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "Connection successful",
  "latency_ms": 234
}
```

---

### 会话管理

#### GET /api/sessions

获取所有活跃会话。

**请求示例**:
```bash
curl http://localhost:18789/api/sessions
```

**响应示例**:
```json
{
  "sessions": [
    {
      "session_id": "agent:main:telegram:dm:123456",
      "agent_id": "main",
      "channel": "telegram",
      "trust_level": "dm",
      "created_at": "2024-01-01T10:00:00Z",
      "last_activity": "2024-01-01T10:30:00Z",
      "message_count": 15
    }
  ]
}
```

---

#### POST /api/sessions

创建新会话。

**请求示例**:
```bash
curl -X POST http://localhost:18789/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "main",
    "channel": "webui"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "session_id": "agent:main:webui:dm:abc123"
}
```

---

#### DELETE /api/sessions/{id}

删除指定会话。

**请求示例**:
```bash
curl -X DELETE http://localhost:18789/api/sessions/agent:main:webui:dm:abc123
```

**响应示例**:
```json
{
  "success": true,
  "message": "Session deleted"
}
```

---

#### GET /api/sessions/{id}/history

获取会话历史消息。

**请求示例**:
```bash
curl http://localhost:18789/api/sessions/agent:main:webui:dm:abc123/history
```

**响应示例**:
```json
{
  "session_id": "agent:main:webui:dm:abc123",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-01T10:00:00Z"
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "Hi there! How can I help?",
      "timestamp": "2024-01-01T10:00:01Z"
    }
  ]
}
```

---

### 消息

#### POST /api/message

发送消息并获取响应。

**请求示例**:
```bash
curl -X POST http://localhost:18789/api/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "agent:main:webui:dm:abc123",
    "content": "What is the weather today?",
    "channel": "webui"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": {
    "id": "msg-3",
    "session_id": "agent:main:webui:dm:abc123",
    "role": "assistant",
    "content": "I don't have access to real-time weather data. You can check a weather website for current conditions.",
    "timestamp": "2024-01-01T10:01:00Z"
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "Session not found"
  }
}
```

---

### WebSocket

#### WS /ws

WebSocket 连接，用于实时消息推送。

**连接示例**:
```javascript
const ws = new WebSocket('ws://localhost:18789/ws');

ws.onopen = () => {
  console.log('Connected');
  // 发送消息
  ws.send(JSON.stringify({
    type: 'message',
    session_id: 'agent:main:webui:dm:abc123',
    content: 'Hello'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

**消息格式**:
```json
{
  "type": "message",
  "session_id": "xxx",
  "content": "Hello"
}
```

**响应格式**:
```json
{
  "type": "message",
  "message": {
    "id": "msg-1",
    "role": "assistant",
    "content": "Hi!"
  }
}
```

**其他事件类型**:
- `typing` - 正在输入
- `error` - 错误
- `session_created` - 会话创建
- `session_deleted` - 会话删除

---

### 渠道

#### GET /api/channels

获取所有可用渠道。

**请求示例**:
```bash
curl http://localhost:18789/api/channels
```

**响应示例**:
```json
{
  "channels": [
    {
      "name": "telegram",
      "enabled": true,
      "type": "messaging",
      "config": {
        "dm_policy": "pairing",
        "group_policy": "mentioned"
      }
    },
    {
      "name": "discord",
      "enabled": true,
      "type": "messaging"
    },
    {
      "name": "webui",
      "enabled": true,
      "type": "web"
    }
  ]
}
```

---

#### GET /api/channels/{name}/status

获取指定渠道状态。

**请求示例**:
```bash
curl http://localhost:18789/api/channels/telegram/status
```

**响应示例**:
```json
{
  "name": "telegram",
  "enabled": true,
  "connected": true,
  "bot_username": "MyBot",
  "webhook_url": "https://api.telegram.org/bot.../webhook"
}
```

---

### 工具

#### GET /api/tools

获取可用工具列表。

**请求示例**:
```bash
curl http://localhost:18789/api/tools
```

**响应示例**:
```json
{
  "tools": [
    {
      "name": "execute_command",
      "description": "Execute a shell command",
      "parameters": {
        "type": "object",
        "properties": {
          "command": {"type": "string"},
          "timeout": {"type": "integer"},
          "sandbox": {"type": "boolean"}
        },
        "required": ["command"]
      }
    },
    {
      "name": "read_file",
      "description": "Read file content",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {"type": "string"},
          "offset": {"type": "integer"},
          "limit": {"type": "integer"}
        },
        "required": ["path"]
      }
    }
  ]
}
```

---

### 记忆

#### GET /api/memory

搜索记忆。

**请求示例**:
```bash
curl "http://localhost:18789/api/memory?query=previous+conversation&limit=5"
```

**响应示例**:
```json
{
  "query": "previous conversation",
  "results": [
    {
      "id": "mem-1",
      "session_id": "agent:main:webui:dm:abc123",
      "role": "user",
      "content": "Remember to call me John",
      "timestamp": "2024-01-01T09:00:00Z",
      "similarity": 0.95
    }
  ]
}
```

---

#### DELETE /api/memory/{id}

删除指定记忆。

**请求示例**:
```bash
curl -X DELETE http://localhost:18789/api/memory/mem-1
```

**响应示例**:
```json
{
  "success": true,
  "message": "Memory deleted"
}
```

---

## 请求/响应示例

### 完整对话流程

```bash
# 1. 创建会话
SESSION=$(curl -s -X POST http://localhost:18789/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "main"}' | jq -r '.session_id')

# 2. 发送消息
curl -X POST http://localhost:18789/api/message \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION\",
    \"content\": \"Hello, who are you?\"
  }"

# 3. 获取历史
curl http://localhost:18789/api/sessions/$SESSION/history

# 4. 删除会话
curl -X DELETE http://localhost:18789/api/sessions/$SESSION
```

---

## 错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| `SUCCESS` | 200 | 成功 |
| `BAD_REQUEST` | 400 | 请求参数错误 |
| `UNAUTHORIZED` | 401 | 未授权 |
| `FORBIDDEN` | 403 | 禁止访问 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `METHOD_NOT_ALLOWED` | 405 | 方法不允许 |
| `CONFLICT` | 409 | 冲突（如会话已存在） |
| `TOO_MANY_REQUESTS` | 429 | 请求过于频繁 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 |

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Session not found",
    "details": {
      "session_id": "invalid-id"
    }
  }
}
```

---

## 速率限制

默认速率限制（可配置）：

- 消息发送：60 次/分钟
- 配置更新：10 次/分钟
- 其他 API：100 次/分钟

超过限制将返回 `429 Too Many Requests`。

---

## 版本信息

当前 API 版本：v1

API 版本通过 URL 路径或请求头指定：

```bash
# URL 路径
curl http://localhost:18789/api/v1/config

# 请求头
curl -H "Accept: application/vnd.gogoclaw.v1+json" \
  http://localhost:18789/api/config
```

---

**最后更新**: 2024-03-02
