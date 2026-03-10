# 代码模板库

## 📁 目录结构

```
templates/
├── web/
│   ├── react-component/     # React 组件模板
│   ├── express-route/       # Express 路由模板
│   └── api-response/        # API 响应格式模板
├── database/
│   ├── mysql-schema/        # MySQL 建表模板
│   ├── mongodb-model/       # MongoDB 模型模板
│   └── redis-config/        # Redis 配置模板
├── python/
│   ├── flask-app/           # Flask 应用模板
│   ├── django-model/        # Django 模型模板
│   └── fastapi-endpoint/    # FastAPI 端点模板
├── javascript/
│   ├── nodejs-module/       # Node.js 模块模板
│   ├── typescript-class/    # TypeScript 类模板
│   └── jest-test/           # Jest 测试模板
└── docs/
    ├── README.md            # 项目说明模板
    ├── API.md               # API 文档模板
    └── CHANGELOG.md         # 变更日志模板
```

---

## 🌐 Web 开发模板

### React 组件模板

```jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import styles from './ComponentName.module.css';

/**
 * ComponentName 组件
 * 
 * @description [组件功能描述]
 * @example
 * <ComponentName 
 *   prop1="value1"
 *   prop2={value2}
 *   onEvent={handleEvent}
 * />
 */
const ComponentName = ({ prop1, prop2, onEvent }) => {
  // State
  const [state, setState] = useState(initialValue);
  
  // Effects
  useEffect(() => {
    // 副作用逻辑
    return () => {
      // 清理函数
    };
  }, [dependencies]);
  
  // Handlers
  const handleAction = () => {
    // 事件处理逻辑
    onEvent?.(data);
  };
  
  // Render
  return (
    <div className={styles.container}>
      {/* 组件内容 */}
    </div>
  );
};

ComponentName.propTypes = {
  prop1: PropTypes.string.isRequired,
  prop2: PropTypes.object,
  onEvent: PropTypes.func
};

ComponentName.defaultProps = {
  prop2: {},
  onEvent: undefined
};

export default ComponentName;
```

---

### Express 路由模板

```javascript
const express = require('express');
const router = express.Router();
const { body, param, query, validationResult } = require('express-validator');
const Controller = require('../controllers/ControllerName');

/**
 * @route   GET/POST/PUT/DELETE /api/resource
 * @desc    [功能描述]
 * @access  Private/Public
 */

// GET /api/resource - 获取资源列表
router.get(
  '/',
  [
    query('page').optional().isInt({ min: 1 }),
    query('limit').optional().isInt({ min: 1, max: 100 })
  ],
  async (req, res, next) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }
      
      const result = await Controller.list(req.query);
      res.json(result);
    } catch (error) {
      next(error);
    }
  }
);

// POST /api/resource - 创建资源
router.post(
  '/',
  [
    body('field1').notEmpty().withMessage('field1 是必填项'),
    body('field2').isEmail().withMessage('请输入有效的邮箱地址')
  ],
  async (req, res, next) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }
      
      const result = await Controller.create(req.body);
      res.status(201).json(result);
    } catch (error) {
      next(error);
    }
  }
);

module.exports = router;
```

---

## 🗄️ 数据库模板

### MySQL 建表模板

```sql
-- ============================================
-- 表名：table_name
-- 描述：[表功能描述]
-- 创建时间：2026-03-10
-- ============================================

CREATE TABLE IF NOT EXISTS `table_name` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  
  -- 业务字段
  `name` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '名称',
  `description` TEXT COMMENT '描述',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1-启用 0-禁用',
  
  -- 时间字段
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` TIMESTAMP NULL DEFAULT NULL COMMENT '删除时间',
  
  -- 索引字段
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`name`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
  
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表描述';
```

---

## 🐍 Python 模板

### FastAPI 端点模板

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/resource", tags=["resource"])

# Request/Response Models
class ResourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    email: EmailStr

class ResourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Endpoints
@router.get("/", response_model=List[ResourceResponse])
async def list_resources(
    skip: int = 0,
    limit: int = 100,
    # db: Session = Depends(get_db)
):
    """
    获取资源列表
    
    - **skip**: 跳过记录数
    - **limit**: 返回记录数上限
    """
    # TODO: 实现数据库查询
    return []

@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource: ResourceCreate,
    # db: Session = Depends(get_db)
):
    """
    创建新资源
    
    - **name**: 资源名称（必填）
    - **description**: 资源描述（可选）
    - **email**: 联系邮箱（必填）
    """
    # TODO: 实现数据库插入
    return ResourceResponse(
        id=1,
        name=resource.name,
        description=resource.description,
        created_at=datetime.now()
    )

@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    # db: Session = Depends(get_db)
):
    """
    获取指定资源
    
    - **resource_id**: 资源 ID
    """
    # TODO: 实现数据库查询
    return ResourceResponse(
        id=resource_id,
        name="Example",
        description=None,
        created_at=datetime.now()
    )
```

---

## 📄 文档模板

### README.md 模板

```markdown
# 项目名称

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## 📖 项目简介

[简要描述项目的功能和用途]

## ✨ 特性

- [特性 1]
- [特性 2]
- [特性 3]

## 🚀 快速开始

### 安装

```bash
npm install package-name
# 或
pip install package-name
```

### 使用

```javascript
// 代码示例
const example = require('package-name');
example.doSomething();
```

## 📚 API 文档

详见 [API.md](./docs/API.md)

## 🧪 测试

```bash
npm test
# 或
pytest
```

## 📦 依赖

- [依赖 1]
- [依赖 2]

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 许可证

MIT License
```

---

*模板库版本：v1.0*
*创建时间：2026 年 3 月 10 日*
