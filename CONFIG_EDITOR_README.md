# 🦎 OpenClaw 配置编辑器 - 便携版

一个**单文件、零依赖、跨平台**的 OpenClaw 可视化配置工具！

## ✨ 核心特点

### 🚀 便携性 MAX
- **单文件** - 只有一个 HTML 文件，无需安装任何依赖
- **纯前端** - 不需要服务器，浏览器直接打开
- **跨平台** - Windows、macOS、Linux 通用
- **离线使用** - 完全本地运行，无需联网
- **数据安全** - 所有数据在本地，不会上传

### 🎯 功能完整
- ✅ 模型提供商管理
- ✅ Gateway 配置
- ✅ 消息通道配置（飞书、钉钉、QQBot）
- ✅ 代理设置
- ✅ 工具配置
- ✅ JSON 实时预览
- ✅ 配置备份下载

## 📥 使用方式

### 方式 1：直接双击打开
```bash
# 找到文件，双击打开
openclaw-config-editor.html
```

### 方式 2：浏览器打开
```bash
# macOS/Linux
open openclaw-config-editor.html

# Windows
start openclaw-config-editor.html
```

### 方式 3：拖拽到浏览器
直接将 `openclaw-config-editor.html` 拖拽到任意现代浏览器窗口

## 🎓 使用教程

### 第一步：加载配置
1. 点击 **"📂 打开配置文件"**
2. 选择 `~/.openclaw/openclaw.json`
3. 或者 **直接拖拽文件到虚线框区域**

> 💡 首次使用可点击 **"🔄 加载默认配置"**

### 第二步：编辑配置
切换到不同选项卡修改配置：

#### 🤖 模型配置
- 添加/删除模型提供商
- 配置 Base URL（API 地址）
- 配置 API Key
- 查看模型数量

#### 👤 代理设置
- **工作目录** - Agent 运行目录
- **主模型** - 格式：`提供商 ID/模型 ID`
- **并发数** - 控制同时运行的任务数
- **压缩模式** - 控制上下文压缩策略

#### 🌐 Gateway
- **端口** - 默认 18789
- **绑定模式** - 仅本地/所有接口
- **认证模式** - Token 认证/无认证
- **Token** - Dashboard 访问凭证

#### 📱 消息通道
- **飞书** - App ID、App Secret
- **钉钉** - Client ID、Client Secret
- **QQBot** - App ID、Client Secret

#### 🔧 工具
- 工具配置文件选择
- 网页搜索开关
- 网页抓取开关

#### 📄 JSON 预览
- 实时查看完整配置 JSON
- 一键复制 JSON 内容

### 第三步：保存配置
1. 点击 **"💾 保存配置"**
2. 浏览器会下载 `openclaw.json`
3. 将文件复制到 `~/.openclaw/` 目录
4. 运行 `openclaw gateway restart` 重启生效

## 📁 配置文件位置

### Linux/macOS
```bash
~/.openclaw/openclaw.json
# 或完整路径
/home/用户名/.openclaw/openclaw.json
```

### Windows
```
C:\Users\用户名\.openclaw\openclaw.json
```

### 替换命令
```bash
# macOS/Linux
cp ~/Downloads/openclaw.json ~/.openclaw/openclaw.json
openclaw gateway restart

# Windows (PowerShell)
Copy-Item ~\Downloads\openclaw.json ~\.openclaw\openclaw.json
openclaw gateway restart
```

## 💡 实用技巧

### 快速备份配置
点击 **"⬇️ 下载备份"** 会下载带日期的备份文件：
```
openclaw-backup-2026-03-01.json
```

### 快速复制配置
点击 **"📋 复制 JSON"** 可直接复制配置到剪贴板，方便：
- 通过聊天工具分享给同事
- 粘贴到版本控制系统
- 快速迁移到其他机器

### 拖拽加载
直接将 `openclaw.json` 文件拖拽到页面的虚线框区域，快速加载配置！

### 实时预览
切换到 **"📄 JSON 预览"** 选项卡，实时查看当前配置的完整 JSON 表示。

## 🔧 常见配置示例

### 添加新模型提供商
1. 切换到 **"🤖 模型配置"**
2. 点击 **"➕ 添加提供商"**
3. 输入提供商 ID（如：`deepseek`）
4. 填写 Base URL（如：`https://api.deepseek.com/v1`）
5. 填写 API Key
6. 保存配置

### 修改 Gateway 端口
1. 切换到 **"🌐 Gateway"**
2. 修改 **"端口"** 字段
3. 保存配置并重启

### 启用飞书消息
1. 切换到 **"📱 消息通道"**
2. 飞书配置 -> 启用：**是**
3. 填写 App ID 和 App Secret
4. 保存配置并重启

## ⚠️ 注意事项

### 安全提示
- ⚠️ **不要分享包含 API Key 的配置**
- ⚠️ **定期备份配置文件**
- ⚠️ **Token 建议至少 20 位随机字符**

### 修改后必须重启
```bash
openclaw gateway restart
```

### 格式校验
- 工具会自动校验 JSON 格式
- 错误会弹出提示
- 可在 JSON 预览中检查

## 🆘 故障排除

### 配置不生效？
1. 确认文件已替换到正确位置
2. 确认已重启 Gateway
3. 检查 Gateway 日志：`openclaw gateway status`

### 模型无法使用？
1. 检查模型 ID 格式：`提供商 ID/模型 ID`
2. 检查 API Key 是否正确
3. 检查 Base URL 是否正确

### Gateway 无法启动？
1. 检查端口是否被占用
2. 检查配置文件 JSON 格式
3. 查看错误日志

## 📊 配置结构说明

```json
{
  "models": {
    "providers": {
      "提供商 ID": {
        "baseUrl": "API 地址",
        "apiKey": "API 密钥",
        "api": "API 类型",
        "models": [...]
      }
    }
  },
  "agents": {
    "defaults": {
      "workspace": "工作目录",
      "model": { "primary": "主模型" },
      "maxConcurrent": 并发数
    }
  },
  "gateway": {
    "port": 端口,
    "bind": "绑定模式",
    "auth": { "mode": "认证模式", "token": "Token" }
  },
  "channels": {
    "feishu": { "enabled": 是否启用, "appId": "", "appSecret": "" },
    "dingtalk-connector": { ... },
    "qqbot": { ... }
  }
}
```

## 🌟 与其他工具对比

| 特性 | 配置编辑器 | 手动编辑 | VS Code |
|------|-----------|---------|---------|
| 无需安装 | ✅ | ✅ | ❌ |
| 可视化界面 | ✅ | ❌ | ❌ |
| 格式校验 | ✅ | ❌ | ⚠️ |
| 拖拽加载 | ✅ | ❌ | ❌ |
| 一键备份 | ✅ | ❌ | ❌ |
| 跨平台 | ✅ | ✅ | ✅ |
| 离线使用 | ✅ | ✅ | ✅ |

## 📞 反馈与建议

如有问题或建议，欢迎反馈！

---

**版本**: 1.0.0 (便携版)  
**最后更新**: 2026-03-01  
**文件大小**: ~35KB  
**兼容性**: 所有现代浏览器（Chrome、Firefox、Safari、Edge）
