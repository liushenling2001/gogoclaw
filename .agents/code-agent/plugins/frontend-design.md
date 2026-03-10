# OpenCode 前端设计插件推荐

## 🎨 推荐插件

### 1. **Excalidraw** - 手绘风格设计工具

**用途**：快速绘制 UI 草图、流程图、架构图

**安装**：
```bash
# 作为依赖安装
npm install -D @excalidraw/excalidraw

# 或在浏览器中使用
https://excalidraw.com
```

**OpenCode 集成**：
```javascript
// opencode.config.js
module.exports = {
  plugins: [
    {
      name: 'excalidraw',
      enabled: true,
      config: {
        outputDir: './designs',
        format: 'svg'
      }
    }
  ]
}
```

**使用示例**：
```
@OpenCode 请用 Excalidraw 绘制一个登录页面的线框图，包含：
- 邮箱输入框
- 密码输入框
- 登录按钮
- 忘记密码链接
- 注册链接
```

---

### 2. **Storybook** - UI 组件开发环境

**用途**：独立开发和测试 React/Vue/Angular 组件

**安装**：
```bash
# React 项目
npx storybook@latest init

# 自动检测项目类型并安装
npx storybook@latest init --type react
```

**OpenCode 集成**：
```javascript
// .storybook/main.js
module.exports = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-a11y' // 无障碍检查
  ],
  framework: {
    name: '@storybook/react-vite',
    options: {}
  }
}
```

**使用示例**：
```
@OpenCode 请为 Button 组件创建 Storybook 故事，包含：
- 主要按钮
- 次要按钮
- 禁用状态
- 加载状态
- 不同尺寸（small, medium, large）
```

---

### 3. **Tailwind CSS + Headless UI** - 实用优先 CSS 框架

**用途**：快速构建响应式 UI

**安装**：
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 安装 Headless UI（无样式组件）
npm install @headlessui/react @heroicons/react
```

**配置**：
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8'
        }
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ]
}
```

**使用示例**：
```
@OpenCode 请用 Tailwind CSS 设计一个现代化的卡片组件，包含：
- 圆角边框
- 阴影效果
- hover 动画
- 响应式布局
- 支持暗色模式
```

---

### 4. **Figma Plugin (OpenCode Bridge)** - 设计稿转代码

**用途**：将 Figma 设计稿自动转换为 React/Vue 代码

**安装**：
1. 在 Figma 社区搜索 "OpenCode Bridge"
2. 安装插件
3. 在 OpenCode 配置中添加 API 密钥

**配置**：
```javascript
// opencode.config.js
module.exports = {
  plugins: {
    figma: {
      enabled: true,
      apiKey: 'YOUR_FIGMA_API_KEY',
      fileKey: 'YOUR_FILE_KEY',
      outputDir: './src/components/from-figma'
    }
  }
}
```

**使用示例**：
```
@OpenCode 请将 Figma 设计稿中的登录页面转换为 React 组件：
- Figma 文件链接：https://figma.com/file/xxx
- 使用 Tailwind CSS
- 支持响应式
- 添加表单验证
```

---

### 5. **Chromatic** - 视觉回归测试

**用途**：自动检测 UI 变化，防止视觉 bug

**安装**：
```bash
npm install -D chromatic
npx chromatic --project-token=YOUR_PROJECT_TOKEN
```

**配置**：
```yaml
# .github/workflows/chromatic.yml
name: 'Chromatic'
on: push
jobs:
  chromatic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: chromaui/action@v1
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
```

**使用示例**：
```
@OpenCode 请为所有 UI 组件配置 Chromatic 视觉回归测试：
- 设置 GitHub Actions 工作流
- 配置 Storybook
- 添加基准截图
- 设置 PR 检查
```

---

### 6. **CSS Modules + PostCSS** - 组件级 CSS 隔离

**用途**：避免 CSS 命名冲突，支持 CSS 特性

**安装**：
```bash
npm install -D postcss postcss-preset-env css-modules
```

**配置**：
```javascript
// postcss.config.js
module.exports = {
  plugins: [
    'postcss-import',
    'postcss-preset-env',
    'postcss-nesting',
    'autoprefixer'
  ]
}
```

**使用示例**：
```
@OpenCode 请用 CSS Modules 创建一个响应式导航栏：
- 移动端汉堡菜单
- 桌面端水平导航
- 平滑过渡动画
- 支持键盘导航
```

---

### 7. **Vite + Plugin Visualizer** - 构建分析和优化

**用途**：分析打包体积，优化性能

**安装**：
```bash
npm install -D rollup-plugin-visualizer
```

**配置**：
```javascript
// vite.config.js
import { visualizer } from 'rollup-plugin-visualizer'

export default {
  plugins: [
    visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ]
}
```

**使用示例**：
```
@OpenCode 请分析项目的打包体积，并给出优化建议：
- 识别最大的依赖
- 建议代码分割点
- 配置懒加载
- 优化图片资源
```

---

## 🛠️ OpenCode 前端设计工作流

### 步骤 1：需求分析

```
@OpenCode 我需要设计一个电商网站的商品详情页，包含：
- 商品图片画廊
- 商品信息（名称、价格、描述）
- 规格选择（颜色、尺寸）
- 加入购物车按钮
- 用户评价

请输出：
1. 功能列表
2. 技术选型建议
3. 预计开发时间
```

### 步骤 2：原型设计

```
@OpenCode 请用 Excalidraw 绘制商品详情页的线框图：
- 移动端优先
- 考虑平板和桌面端适配
- 标注关键交互点
```

### 步骤 3：组件开发

```
@OpenCode 请基于设计稿创建 React 组件：
- 使用 TypeScript
- Tailwind CSS 样式
- 支持暗色模式
- 添加单元测试
```

### 步骤 4：Storybook 文档

```
@OpenCode 请为所有组件创建 Storybook 故事：
- 展示所有状态
- 添加交互测试
- 编写使用文档
```

### 步骤 5：性能优化

```
@OpenCode 请优化页面性能：
- 分析打包体积
- 配置代码分割
- 优化图片加载
- 添加骨架屏
```

### 步骤 6：测试部署

```
@OpenCode 请配置 CI/CD：
- 运行单元测试
- 视觉回归测试
- 自动部署到预览环境
```

---

## 📦 推荐技术栈组合

### 方案 A：快速原型（推荐新手）

```json
{
  "framework": "Vite + React",
  "styling": "Tailwind CSS",
  "components": "Headless UI",
  "icons": "Heroicons",
  "docs": "Storybook",
  "testing": "Vitest + React Testing Library"
}
```

**安装命令**：
```bash
npm create vite@latest my-app -- --template react
cd my-app
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install @headlessui/react @heroicons/react
npm install -D storybook @storybook/react-vite
npm install -D vitest @testing-library/react
```

---

### 方案 B：企业级（推荐大型项目）

```json
{
  "framework": "Next.js 14",
  "styling": "Tailwind CSS + CSS Modules",
  "components": "Radix UI",
  "state": "Zustand",
  "forms": "React Hook Form + Zod",
  "docs": "Storybook + Chromatic",
  "testing": "Playwright + Vitest"
}
```

**安装命令**：
```bash
npx create-next-app@latest my-app
cd my-app
npm install @radix-ui/react-*
npm install zustand
npm install react-hook-form @hookform/resolvers zod
npm install -D storybook @storybook/nextjs
npm install -D @chromatic-com/storybook
npm install -D playwright vitest
```

---

### 方案 C：设计驱动（推荐设计团队）

```json
{
  "design": "Figma",
  "bridge": "Figma to Code Plugin",
  "framework": "React",
  "styling": "Styled Components",
  "tokens": "Style Dictionary",
  "docs": "Zeroheight + Storybook"
}
```

---

## 🔧 OpenCode 配置模板

```javascript
// opencode.config.js
module.exports = {
  // 前端设计插件配置
  plugins: {
    // Excalidraw 草图
    excalidraw: {
      enabled: true,
      outputDir: './designs/sketches',
      format: 'svg'
    },
    
    // Storybook 集成
    storybook: {
      enabled: true,
      port: 6006,
      outputDir: './storybook-static'
    },
    
    // Tailwind CSS
    tailwind: {
      enabled: true,
      config: './tailwind.config.js',
      css: './src/styles/globals.css'
    },
    
    // 视觉回归测试
    chromatic: {
      enabled: true,
      projectToken: process.env.CHROMATIC_PROJECT_TOKEN
    },
    
    // 性能分析
    visualizer: {
      enabled: true,
      filename: 'dist/stats.html',
      open: true
    }
  },
  
  // 代码生成配置
  generate: {
    // 默认使用 TypeScript
    typescript: true,
    
    // 默认使用 Tailwind CSS
    styling: 'tailwind',
    
    // 组件模板
    componentTemplate: 'react-functional',
    
    // 自动生成测试
    autoTest: true,
    
    // 自动生成 Storybook 故事
    autoStory: true
  },
  
  // 设计系统配置
  designSystem: {
    // 从 Figma 导入设计令牌
    figma: {
      enabled: false,
      fileKey: '',
      apiKey: ''
    },
    
    // 设计令牌输出
    tokens: {
      output: './src/tokens',
      format: 'typescript'
    }
  }
}
```

---

## 📚 学习资源

### OpenCode 官方文档
- [OpenCode 文档](https://opencode.ai/docs)
- [插件开发指南](https://opencode.ai/docs/plugins)
- [自定义命令](https://opencode.ai/docs/commands)

### 前端设计资源
- [Tailwind CSS 官方文档](https://tailwindcss.com/docs)
- [Storybook 官方文档](https://storybook.js.org/docs)
- [Headless UI 组件库](https://headlessui.com)
- [Radix UI 无样式组件](https://www.radix-ui.com)
- [Figma 设计资源](https://figma.com/community)

### 性能优化
- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse 测试](https://pagespeed.web.dev/)
- [Bundle Phobia](https://bundlephobia.com) - 检查 npm 包体积

---

## 🎯 最佳实践

### 1. 设计先行
```
✅ 先用 Excalidraw 绘制线框图
✅ 与团队确认设计方向
✅ 再开始编码实现
```

### 2. 组件驱动
```
✅ 先开发基础组件（Button, Input, Card）
✅ 用 Storybook 文档化
✅ 组合基础组件构建页面
```

### 3. 测试保障
```
✅ 单元测试覆盖核心逻辑
✅ 视觉回归测试防止 UI bug
✅ E2E 测试关键用户流程
```

### 4. 性能优先
```
✅ 使用 Vite 快速开发
✅ 分析打包体积
✅ 配置代码分割
✅ 优化图片和字体
```

### 5. 文档同步
```
✅ 组件即文档（Storybook）
✅ 设计令牌集中管理
✅ API 文档自动生成
```

---

*文档版本：v1.0*
*创建时间：2026 年 3 月 10 日*
*适用于：OpenCode + React/Vue/Angular 项目*
