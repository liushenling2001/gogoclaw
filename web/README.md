# GogoClaw Web UI

GogoClaw 的 Web 管理界面和智能对话界面。

## 功能特性

### 配置管理后台
- ✅ API Key 配置 (OpenAI / Anthropic / Google / Ollama)
- ✅ 模型选择 (provider + model_name)
- ✅ 渠道开关 (Telegram / Discord / 飞书 / 钉钉 / WhatsApp)
- ✅ 高级设置 (temperature, max_tokens, sandbox, tools)

### 智能助理聊天界面
- ✅ 对话列表 (左侧边栏)
- ✅ 聊天窗口 (右侧)
- ✅ 消息类型支持 (文本/代码/图片)
- ✅ 工具调用可视化 (显示正在使用的工具)
- ✅ 打字机效果 (流式响应)
- ✅ Markdown 渲染
- ✅ 代码高亮

## 技术栈

- **前端**: Vue 3 (CDN 版本) + Element Plus
- **后端**: FastAPI
- **实时通信**: WebSocket
- **Markdown**: marked.js
- **代码高亮**: Prism.js

## 快速启动

### 方式一：直接运行 (推荐)

```bash
cd /home/22607104_wy/openclaw/workspace/gogoclaw/web
python server.py
```

访问：http://localhost:18790

### 方式二：使用 Uvicorn

```bash
cd /home/22607104_wy/openclaw/workspace/gogoclaw/web
uvicorn server:app --host 0.0.0.0 --port 18790 --reload
```

### 方式三：集成到 GogoClaw Gateway

将 Web UI 作为 Gateway 的子路由挂载。

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 前端页面 |
| GET | `/health` | 健康检查 |
| GET | `/api/config` | 获取配置 |
| PUT | `/api/config` | 更新配置 |
| GET | `/api/config/models` | 获取模型列表 |
| POST | `/api/config/test` | 测试 API Key |
| GET | `/api/channels` | 获取渠道列表 |
| WS | `/ws` | WebSocket 实时通信 |

## 配置保存

配置保存到 `~/.gogoclaw/gogoclaw.json`

## 开发说明

### 前端架构

单文件架构 (Single File Architecture):
- `index.html` - 包含所有前端代码
- Vue 3 + Element Plus 通过 CDN 加载
- 无需构建步骤，开箱即用

### 后端架构

- `server.py` - FastAPI 应用
- 提供 REST API 和 WebSocket 服务
- 与 GogoClaw 配置系统集成

### 扩展开发

如需更复杂的功能，可以:
1. 拆分为标准 Vue 项目 (使用 Vite)
2. 添加 TypeScript 支持
3. 集成更多 UI 组件

## 注意事项

1. **WebSocket 端口**: 默认 18790 (与 Gateway 的 16888 区分)
2. **CORS**: 已配置允许所有来源 (生产环境应限制)
3. **API Key 安全**: 配置保存在本地，注意保护
4. **生产部署**: 建议使用 Nginx 反向代理 + HTTPS

## 截图

配置管理界面:
- API Key 配置表单
- 模型选择下拉框
- 渠道开关切换
- 高级设置滑块

聊天界面:
- 左侧对话列表
- 右侧聊天窗口
- 底部输入框
- 工具调用指示器

---

**版本**: 1.0.0  
**作者**: GogoClaw Team
