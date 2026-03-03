# LIMS Lite - 化学实验数据管理平台

一个简化版的实验室信息管理系统（LIMS），用于管理化学品、实验反应和结果数据。

## 🚀 技术栈

- **前端**: Vue 3 + Vite + Element Plus
- **后端**: Python FastAPI
- **数据库**: SQLite (轻量级，适合开发和测试)
- **API**: RESTful

## 📋 核心功能

### 1. 化学品管理
- ✅ 新增/编辑/删除化学品信息
- ✅ 字段：名称、CAS 号、分子式、分子量、危险品分类、存储条件、库存量
- ✅ 按名称或 CAS 号搜索化学品

### 2. 实验反应管理
- ✅ 创建新实验
- ✅ 关联使用的化学品清单（用量）
- ✅ 实验参数：温度、时间、压力、气氛等
- ✅ 实验状态：进行中/已完成/失败

### 3. 实验结果
- ✅ 产物信息：产率、纯度、外观描述
- ✅ 分析数据：NMR, IR, MS 等谱图数据录入
- ✅ 实验笔记：文字描述、备注

### 4. 基础搜索和展示
- ✅ 化学品列表页面（带搜索）
- ✅ 实验历史记录
- ✅ 实验详情查看

## 🎯 快速开始

### 方式一：Docker Compose（推荐）

1. **确保已安装 Docker 和 Docker Compose**

2. **启动服务**
   ```bash
   cd chemical-lims-demo
   docker-compose up -d
   ```

3. **访问应用**
   - 前端：http://localhost
   - API 文档：http://localhost:8000/docs
   - 健康检查：http://localhost:health

4. **初始化示例数据（可选）**
   ```bash
   docker exec lims-backend python init_data.py
   ```

### 方式二：本地开发

#### 后端启动

```bash
cd backend

# 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 开发模式运行
npm run dev
```

5. **访问应用**
   - 前端：http://localhost:5173
   - API 文档：http://localhost:8000/docs

## 📁 项目结构

```
chemical-lims-demo/
├── backend/                    # FastAPI 后端
│   ├── main.py                # 主应用文件
│   ├── models.py              # SQLAlchemy 模型
│   ├── schemas.py             # Pydantic 数据模式
│   ├── database.py            # 数据库配置
│   ├── init_data.py           # 示例数据初始化脚本
│   ├── requirements.txt       # Python 依赖
│   └── Dockerfile
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   │   ├── ChemicalsPage.vue    # 化学品管理页
│   │   │   ├── ExperimentsPage.vue  # 实验列表页
│   │   │   ├── ExperimentForm.vue   # 实验表单页
│   │   │   └── ExperimentDetail.vue # 实验详情页
│   │   ├── components/        # 通用组件
│   │   │   └── Layout.vue
│   │   ├── router.js          # 路由配置
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 入口文件
│   ├── vite.config.js         # Vite 配置
│   ├── package.json           # Node 依赖
│   └── Dockerfile
├── docker-compose.yml         # Docker Compose 配置
└── README.md                  # 项目说明文档
```

## 🔌 API 接口

### 化学品 API
- `GET /api/chemicals` - 获取化学品列表（支持分页、搜索）
- `POST /api/chemicals` - 创建化学品
- `GET /api/chemicals/{id}` - 获取单个化学品
- `PUT /api/chemicals/{id}` - 更新化学品
- `DELETE /api/chemicals/{id}` - 删除化学品

### 实验 API
- `GET /api/experiments` - 获取实验列表（支持分页、搜索、状态过滤）
- `POST /api/experiments` - 创建实验
- `GET /api/experiments/{id}` - 获取单个实验详情
- `PUT /api/experiments/{id}` - 更新实验
- `DELETE /api/experiments/{id}` - 删除实验
- `POST /api/experiments/{id}/results` - 创建实验结果
- `PATCH /api/experiments/{id}/results` - 更新实验结果

完整的 API 文档请访问：http://localhost:8000/docs

## 📝 使用说明

### 添加化学品
1. 进入"化学品管理"页面
2. 点击"新增化学品"按钮
3. 填写化学品信息并提交
4. 支持的字段包括：名称、CAS 号、分子式、分子量、危险品分类、存储条件、库存量

### 创建实验
1. 进入"实验记录"页面
2. 点击"新建实验"按钮
3. 填写实验基本信息（名称、状态）
4. 设置实验参数（温度、时间、压力、气氛）
5. 从下拉框选择使用的试剂及用量
6. （可选）直接录入实验结果
7. 提交保存

### 查看实验详情
1. 在实验列表中点击任意实验的"详情"按钮
2. 可查看所有实验参数、使用的试剂、以及实验结果
3. 可以点击"编辑"按钮修改实验信息

## 🗄️ 数据库说明

本系统使用 SQLite 数据库，数据存储在 `backend/data/lims.db`

表结构：
- **chemicals**: 化学品信息表
- **experiments**: 实验信息表
- **experiment_reagents**: 实验与试剂关联表（多对多）
- **experiment_results**: 实验结果表

## 🔧 开发提示

### 环境变量
- 前端 `.env`: 配置 API 地址 `VITE_API_BASE_URL=http://localhost:8000`

### CORS 配置
默认允许来自 `http://localhost:5173` 的前端访问

### 数据验证
- 所有必填字段都有验证
- 数值范围限制（如产率、纯度在 0-100% 之间）
- CAS 号唯一性检查

## ⚠️ 注意事项

1. 生产环境建议使用 PostgreSQL 或其他生产级数据库
2. 如需修改数据库类型，请更新 `models.py` 中的 DATABASE_URL
3. 建议定期备份数据库文件
4. HTTPS 和认证功能需根据实际需求添加

## 📦 示例数据

运行以下命令可加载示例数据：
```bash
docker exec lims-backend python init_data.py
```

包含 8 个常用化学品作为示例。

## 🛠️ 后续扩展方向

- [ ] 用户管理和权限控制
- [ ] 谱图数据文件上传
- [ ] 高级统计分析图表
- [ ] 实验模板功能
- [ ] 化学品库存预警
- [ ] 导出报告（PDF/Excel）
- [ ] 集成 LDAP/SSO

## 📄 License

MIT License

---

Made with ❤️ for laboratory management
