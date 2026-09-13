# 校园二手交易与智能议价助手

一个面向高校学生的二手闲置交易平台，内置 **AI 智能议价、AI 帮写文案、AI 智能估价** 三大 AI 能力。前后端分离，覆盖「注册登录 → 发布商品 → 搜索筛选 → 议价沟通 → 下单成交 → 评价」完整业务闭环。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + TypeScript + Vite 7 + Ant Design Vue 4 + Pinia 3 + Tailwind CSS 3 |
| 后端 | Python 3.12 + FastAPI + Tortoise ORM（异步）+ Pydantic v2 |
| 数据库 | MySQL 8.0（aiomysql 驱动，10 张关联表） |
| 认证 | JWT Bearer Token（python-jose + bcrypt） |
| AI | OpenAI 兼容大模型 API（可配 Key），无 Key 时自动降级为本地规则策略 |
| 脚手架 | 基于 orbai-tech 的 fastapi / vue 官方模板二次开发 |

## 项目结构

```
校园二手交易与智能议价助手/
├── backend/                     # FastAPI 后端
│   ├── main.py                  # 启动入口（uvicorn）
│   ├── config.yaml              # 本地开发配置（MySQL/JWT/LLM）
│   ├── config-test.yaml         # 测试配置
│   ├── pyproject.toml           # 依赖（uv 管理）
│   ├── scripts/seed.py          # 种子数据脚本
│   ├── tests/                   # 业务链路测试
│   └── application/
│       ├── apis/                # 路由层：user/category/goods/favorite/bargain/order/review/message/report/ai
│       ├── service/             # 业务服务层（议价/订单状态机、AI 服务）
│       ├── common/              # 配置/模型(10表)/统一响应/异常/JWT/依赖注入
│       └── core/                # 数据库/Redis/LLM 客户端/生命周期
└── frontend/                    # Vue3 前端
    └── src/
        ├── common/apis/         # 各领域 API 封装
        ├── common/types/        # TS 类型定义
        ├── stores/              # Pinia（用户登录态）
        ├── views/layouts/       # storefront 前台布局 / admin 后台布局
        └── views/pages/         # 前台页面 + admin 后台页面
```

## 数据库设计（10 张关联表）

`user`（用户）、`category`（分类）、`product`（商品）、`favorite`（收藏）、`bargain_record`（议价记录）、`orders`（订单）、`review`（评价）、`message`（消息）、`report`（举报）、`browse_history`（浏览历史）。

关联关系：user 1→N product/orders/favorite/review/message/report；category 1→N product；product 1→N bargain_record/favorite/orders/browse_history；orders 1→1 review。

## 快速开始

### 前置要求
- Node.js ≥ 24.18
- Python 3.12（推荐用 [uv](https://docs.astral.sh/uv/) 管理，仓库已含 uv.lock）
- 本机 MySQL 8.0，root 密码 `123456`（或在 `backend/config.yaml` 中修改）

### 1. 初始化数据库
```sql
CREATE DATABASE IF NOT EXISTS campus_market DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 一键启动（推荐）
在项目根目录执行，自动同时启动后端(8001)与前端(5174)：
```bash
python start.py            # 启动前后端；加 --seed 可先初始化示例数据
python start.py --backend  # 只启动后端
python start.py --frontend # 只启动前端
```
- 前台访问：http://localhost:5174
- 后台管理：http://localhost:5174/admin
- 后端接口文档：http://127.0.0.1:8001/api/docs

### 3. 手动分开启动（可选）
```bash
# 后端
cd backend
uv sync
uv run uvicorn main:app --host 127.0.0.1 --port 8001

# 前端（另开终端）
cd frontend
npm install
npm run dev    # 已在 vite.config.ts 固定端口 5174，并代理 /api 到 8001
```
> 注意：本项目前端固定为 **5174** 端口。若本机 5173 上有其他脚手架 demo 前端在运行，请以 5174 为准，避免登错系统。

### 默认账号
| 角色 | 用户名 | 密码 | 说明 |
|---|---|---|---|
| 管理员 | admin | 123456 | 后台 http://localhost:5174/admin |
| 卖家 | student1 | 123456 | 昵称：林晚晴 |
| 买家 | student2 | 123456 | 昵称：陈屿 |

### 开启真实 AI（可选）
默认无 Key 时 AI 走本地规则策略，功能仍可完整演示。配置大模型 Key 后即用真实模型：

```bash
# Windows PowerShell
$env:LLM_API_KEY="sk-你的key"
$env:LLM_API_BASE="https://api.openai.com/v1"   # 或通义/DeepSeek 兼容地址
$env:LLM_MODEL="gpt-4o-mini"
cd backend; uv run uvicorn main:app --port 8000
```

## 核心功能

- **商品**：发布（多图上传）、瀑布流列表、关键词搜索、分类/价格/成色筛选、最新/价格/热度排序、详情（浏览量、相关推荐）、编辑/下架
- **AI 能力**：发布页一键「AI 帮写」标题与描述、「AI 估价」给出建议价与区间；议价中心「AI 助手」给出还价话术与建议成交价
- **议价**：买家出价 → 卖家接受/拒绝/还价 的状态机；议价被接受后可按成交价一键下单
- **订单**：下单 → 付款 → 发货 → 确认收货 全流程状态流转，支持取消（自动恢复商品在售）
- **其他**：收藏、站内私信（会话/未读）、评价（关联订单、评分+标签）、举报、个人中心（资料/头像/我的商品/收到的评价）
- **后台管理**：数据概览、商品/订单/举报/用户/分类管理

## 接口规范
- 统一前缀 `/api`，RESTful 风格
- 统一响应 `{ code, message, data }`，分页结构 `{ list, total, page, page_size }`
- Pydantic 严格参数校验 + 全局异常处理 + 统一业务错误码

## 测试
```bash
cd backend
uv run pytest tests/test_business_flow.py -q
```
该测试覆盖完整业务闭环：注册→登录→发布→搜索→收藏→议价→下单→付款→发货→收货→评价→AI 能力。

## 原创性设计（毕设亮点）
1. **议价状态机**：买家/卖家轮流出价的有限状态流转，自主设计
2. **智能估价规则模型**：品类贬值曲线 × 成色系数 × 使用年限 的基础价 + LLM 微调的混合策略
3. **信用分体系**：基于交易与评价累积的用户信用
4. **AI 降级架构**：LLM 客户端与本地规则策略双通道，保证演示鲁棒性
