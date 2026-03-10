# OpenCode 调用技能

## 📌 技能说明

本技能用于调用 OpenCode 完成代码生成、修改、重构等编程任务。

## 🛠️ 工具调用

### 1. 使用 OpenCode CLI

```bash
# 生成代码
opencode generate --prompt "实现一个 XXX 功能"

# 修改代码
opencode edit --file path/to/file.js --prompt "添加 XXX 功能"

# 代码审查
opencode review --file path/to/file.js
```

### 2. 使用 OpenCode API

```javascript
// 通过 API 调用
const response = await fetch('http://localhost:PORT/api/opencode', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'generate',
    prompt: '实现一个 XXX 功能',
    language: 'javascript'
  })
});
```

## 📋 使用场景

### 代码生成

```
任务：实现一个用户登录功能
调用：opencode generate --prompt "实现用户登录功能，包含密码加密、token 生成"
输出：完整的登录模块代码
```

### 代码修改

```
任务：为现有函数添加错误处理
调用：opencode edit --file auth.js --prompt "添加 try-catch 错误处理"
输出：修改后的代码
```

### 代码重构

```
任务：优化代码结构
调用：opencode refactor --file main.js --prompt "提取公共函数，减少重复代码"
输出：重构后的代码
```

### 代码审查

```
任务：检查代码质量问题
调用：opencode review --file api.js
输出：问题列表和改进建议
```

## 📝 最佳实践

1. **明确需求**：prompt 要具体，包含功能要求、输入输出、边界条件
2. **分步实现**：复杂功能拆分成小任务，逐步完成
3. **及时验证**：生成代码后立即测试，确保功能正常
4. **保留上下文**：相关代码文件一起提交，保持完整性

## ⚠️ 注意事项

1. **代码审查**：OpenCode 生成的代码必须人工审查
2. **安全检查**：检查是否有安全漏洞（SQL 注入、XSS 等）
3. **性能考虑**：生成代码可能不是最优解，需要优化
4. **依赖确认**：新增依赖需确认许可和兼容性

## 🔗 相关资源

- OpenCode 文档：https://opencode.ai/docs
- 示例代码：/home/22607104_wy/openclaw/workspace/.agents/code-agent/templates/

---

*技能版本：v1.0*
*最后更新：2026 年 3 月 10 日*
