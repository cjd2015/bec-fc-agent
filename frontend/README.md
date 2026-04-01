# AI Agent Platform - Frontend

基于 React 18 + TypeScript 的 Web UI

## 技术栈

- **React 18** - UI 框架
- **TypeScript 5** - 类型系统
- **Vite 5** - 构建工具
- **Ant Design 5** - UI 组件库
- **Zustand** - 状态管理
- **React Query** - 服务端状态
- **React Router** - 路由管理
- **Axios** - HTTP 客户端

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

确保后端服务已启动（端口 8000）

```bash
npm run dev
```

访问 http://localhost:3000

### 3. 构建生产版本

```bash
npm run build
```

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 客户端
│   │   ├── index.ts      # Axios 实例
│   │   └── agent.ts      # Agent API
│   ├── components/       # 公共组件
│   │   └── Layout/       # 布局组件
│   ├── hooks/            # 自定义 Hooks
│   │   └── useAgent.ts   # Agent Hooks
│   ├── pages/            # 页面组件
│   │   └── agents/       # Agent 管理页面
│   ├── stores/           # Zustand Stores
│   │   └── agentStore.ts # Agent Store
│   ├── types/            # TypeScript 类型
│   │   └── agent.ts      # Agent 类型
│   ├── App.tsx           # 根组件
│   ├── main.tsx          # 入口文件
│   └── index.css         # 全局样式
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## 功能说明

### Agent 管理

#### 列表页 (`/agents`)
- 显示所有 Agent
- 状态筛选（草稿/激活/停用/归档）
- 搜索功能
- 快捷操作（详情/编辑/版本/删除）

#### 创建/编辑页 (`/agents/create`, `/agents/:id/edit`)
- 基本信息（名称/描述/图标）
- 模型配置（Provider/Model/Variant）
- 高级配置（温度/最大 Tokens）
- 系统提示词
- 知识库关联

#### 详情页 (`/agents/:id`)
- 完整信息展示
- 统计信息
- 最近操作
- 快捷操作

#### 版本管理页 (`/agents/:id/versions`)
- 版本历史时间线
- 版本预览
- 一键回滚（带确认对话框）

## API 集成

后端 API 地址：http://localhost:8000/api/v1

通过 Vite 代理配置，前端可以直接使用相对路径：

```typescript
import { agentApi } from '@/api/agent'

// 获取列表
const agents = await agentApi.list()

// 获取详情
const agent = await agentApi.get(1)

// 创建
const newAgent = await agentApi.create({ name: 'Agent' })

// 更新
await agentApi.update(1, { name: 'New Name' })

// 删除
await agentApi.delete(1)
```

## 状态管理

### Zustand Store

```typescript
import { useAgentStore } from '@/stores/agentStore'

const {
  agents,
  currentAgent,
  fetchAgents,
  fetchAgent,
  createAgent,
  updateAgent,
  deleteAgent,
} = useAgentStore()
```

### React Query Hooks

```typescript
import { useAgents, useAgent, useCreateAgent } from '@/hooks/useAgent'

// 获取列表
const { data: agents, isLoading } = useAgents()

// 获取详情
const { data: agent } = useAgent(1)

// 创建
const createMutation = useCreateAgent()
await createMutation.mutateAsync({ name: 'Agent' })
```

## 代码规范

### ESLint

```bash
npm run lint
```

### Prettier

```bash
npm run format
```

## 构建部署

### Docker 部署

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

## 开发计划

### 已完成
- ✅ 项目初始化
- ✅ Agent CRUD
- ✅ 版本管理
- ✅ 回滚功能

### 待完成
- ⏳ 知识库管理
- ⏳ 对话测试
- ⏳ 任务管理
- ⏳ 批量操作
- ⏳ 搜索优化
- ⏳ 权限控制

## 参考资料

- [React 文档](https://react.dev/)
- [TypeScript 文档](https://www.typescriptlang.org/)
- [Ant Design 文档](https://ant.design/)
- [Zustand 文档](https://zustand-demo.pmnd.rs/)
- [React Query 文档](https://tanstack.com/query)
- [Vite 文档](https://vitejs.dev/)
