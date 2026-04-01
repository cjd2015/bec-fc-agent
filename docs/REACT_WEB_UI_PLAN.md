# BEC Agent Web UI - React 18 技术方案

**版本:** 2.0  
**更新日期:** 2026-03-30  
**技术栈:** React 18 + TypeScript

---

## 1. 技术选型

### 核心框架

| 技术 | 版本 | 说明 |
|------|------|------|
| **Vue** | 3.4+ | UI 框架 |
| **TypeScript** | 5.0+ | 类型系统 |
| **Vite** | 5.0+ | 构建工具 |

### 状态管理

| 技术 | 版本 | 说明 |
|------|------|------|
| **Zustand + React Query** | 2.1+ | Vue 官方状态管理 |

### UI 组件库

| 技术 | 版本 | 说明 |
|------|------|------|
| **Ant Design** | 2.5+ | 企业级 UI 组件库 |
| **Ant Design Icons** | 2.3+ | 图标库 |

### 路由

| 技术 | 版本 | 说明 |
|------|------|------|
| **Vue Router** | 4.2+ | 路由管理 |

### HTTP 客户端

| 技术 | 版本 | 说明 |
|------|------|------|
| **Axios** | 1.6+ | HTTP 客户端 |
| **dayjs** | 1.11+ | 日期处理 |

---

## 2. 项目目录结构

```
frontend/
├── public/                      # 静态资源
│   └── vite.svg
├── src/
│   ├── api/                     # API 客户端
│   │   ├── index.ts             # Axios 实例配置
│   │   └── agent.ts             # Agent API
│   ├── components/              # 公共组件
│   │   └── Layout/              # 布局组件
│   │       └── index.react
│   ├── pages/                   # 页面组件
│   │   ├── agents/              # Agent 管理
│   │   │   ├── AgentList.react    # 列表页
│   │   │   ├── AgentForm.react    # 表单页
│   │   │   ├── AgentDetail.react  # 详情页
│   │   │   └── AgentVersions.react # 版本管理页
│   │   ├── knowledge/           # 知识库
│   │   ├── chat/                # 对话测试
│   │   └── tasks/               # 任务管理
│   ├── stores/                  # Zustand + React Query Stores
│   │   └── agent.ts             # Agent Store
│   ├── types/                   # TypeScript 类型
│   │   └── agent.ts             # Agent 类型
│   ├── router/                  # 路由配置
│   │   └── index.ts
│   ├── App.react                  # 根组件
│   ├── main.ts                  # 入口文件
│   ├── index.css                # 全局样式
│   └── vite-env.d.ts            # Vite 类型声明
├── .eslintrc.cjs                # ESLint 配置
├── .prettierrc                  # Prettier 配置
├── index.html
├── package.json
├── tsconfig.json                # TypeScript 配置
└── vite.config.ts               # Vite 配置
```

---

## 3. 核心代码示例

### 3.1 TypeScript 类型定义

```typescript
// src/types/agent.ts
export interface Agent {
  id: number
  name: string
  description?: string
  icon?: string
  provider: string
  model: string
  model_variant: string
  temperature: number
  max_tokens: number
  system_prompt?: string
  knowledge_base_ids: number[]
  status: 'draft' | 'active' | 'inactive' | 'archived'
  version: number
  total_conversations: number
  total_messages: number
  avg_rating: number
  created_at: string
  updated_at: string
}

export interface AgentVersion {
  id: number;
  agent_id: number;
  version: number;
  snapshot: Agent;
  change_summary?: string;
  change_details?: Record<string, any>;
  operator_name?: string;
  created_at: string;
  is_rollback_target: boolean;
}

export interface AgentOperationLog {
  id: number;
  agent_id: number;
  operation_type: 'create' | 'update' | 'delete' | 'rollback' | 'publish';
  operation_name: string;
  before_snapshot?: Agent;
  after_snapshot?: Agent;
  changes?: Record<string, any>;
  operator_name?: string;
  status: 'success' | 'failed';
  can_rollback: boolean;
  created_at: string;
}
```

### 3.2 API 客户端

```typescript
// src/api/index.ts
import axios from 'axios';

export const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 统一错误处理
    return Promise.reject(error);
  }
);
```

```typescript
// src/api/agent.ts
import { api } from './index';
import type { Agent, AgentVersion, AgentOperationLog } from '@/types/agent';

export const agentApi = {
  // 获取列表
  list: (params?: { status?: string }) => 
    api.get<Agent[]>('/agent', { params }),
  
  // 获取详情
  get: (id: number) => 
    api.get<Agent>(`/agent/${id}`),
  
  // 创建
  create: (data: Partial<Agent>) => 
    api.post<Agent>('/agent', data),
  
  // 更新
  update: (id: number, data: Partial<Agent>) => 
    api.put<Agent>(`/agent/${id}`, data),
  
  // 删除
  delete: (id: number) => 
    api.delete(`/agent/${id}`),
  
  // 恢复
  restore: (id: number) => 
    api.post(`/agent/${id}/restore`),
  
  // 版本历史
  getVersions: (id: number, params?: { limit?: number }) => 
    api.get<AgentVersion[]>(`/agent/${id}/versions`, { params }),
  
  // 回滚
  rollback: (agentId: number, versionId: number) => 
    api.post(`/agent/${agentId}/rollback/${versionId}`),
  
  // 操作日志
  getOperations: (id: number, params?: { limit?: number }) => 
    api.get<AgentOperationLog[]>(`/agent/${id}/operations`, { params }),
};
```

### 3.3 Zustand Store

```typescript
// src/stores/agentStore.ts
import { create } from 'zustand';
import { agentApi } from '@/api/agent';
import type { Agent, AgentVersion } from '@/types/agent';

interface AgentState {
  agents: Agent[];
  currentAgent: Agent | null;
  versions: AgentVersion[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchAgents: (params?: { status?: string }) => Promise<void>;
  fetchAgent: (id: number) => Promise<void>;
  createAgent: (data: Partial<Agent>) => Promise<Agent>;
  updateAgent: (id: number, data: Partial<Agent>) => Promise<void>;
  deleteAgent: (id: number) => Promise<void>;
  fetchVersions: (id: number) => Promise<void>;
  rollbackToVersion: (agentId: number, versionId: number) => Promise<void>;
  clearCurrentAgent: () => void;
}

export const useAgentStore = create<AgentState>((set, get) => ({
  agents: [],
  currentAgent: null,
  versions: [],
  loading: false,
  error: null,
  
  fetchAgents: async (params) => {
    set({ loading: true, error: null });
    try {
      const agents = await agentApi.list(params);
      set({ agents, loading: false });
    } catch (error) {
      set({ error: '获取列表失败', loading: false });
      throw error;
    }
  },
  
  fetchAgent: async (id) => {
    set({ loading: true, error: null });
    try {
      const agent = await agentApi.get(id);
      set({ currentAgent: agent, loading: false });
    } catch (error) {
      set({ error: '获取详情失败', loading: false });
      throw error;
    }
  },
  
  createAgent: async (data) => {
    const agent = await agentApi.create(data);
    await get().fetchAgents();
    return agent;
  },
  
  updateAgent: async (id, data) => {
    await agentApi.update(id, data);
    await get().fetchAgent(id);
  },
  
  deleteAgent: async (id) => {
    await agentApi.delete(id);
    await get().fetchAgents();
  },
  
  fetchVersions: async (id) => {
    const versions = await agentApi.getVersions(id);
    set({ versions });
  },
  
  rollbackToVersion: async (agentId, versionId) => {
    await agentApi.rollback(agentId, versionId);
    await get().fetchAgent(agentId);
    await get().fetchVersions(agentId);
  },
  
  clearCurrentAgent: () => set({ currentAgent: null }),
}));
```

### 3.4 自定义 Hooks

```typescript
// src/hooks/useAgent.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentApi } from '@/api/agent';

export function useAgents(params?: { status?: string }) {
  return useQuery({
    queryKey: ['agents', params],
    queryFn: () => agentApi.list(params),
  });
}

export function useAgent(id: number) {
  return useQuery({
    queryKey: ['agent', id],
    queryFn: () => agentApi.get(id),
    enabled: !!id,
  });
}

export function useCreateAgent() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: any) => agentApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
}

export function useUpdateAgent(id: number) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: any) => agentApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent', id] });
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
}

export function useAgentVersions(agentId: number) {
  return useQuery({
    queryKey: ['agent-versions', agentId],
    queryFn: () => agentApi.getVersions(agentId),
    enabled: !!agentId,
  });
}

export function useRollback(agentId: number) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (versionId: number) => 
      agentApi.rollback(agentId, versionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent', agentId] });
      queryClient.invalidateQueries({ queryKey: ['agent-versions', agentId] });
    },
  });
}
```

### 3.5 页面组件示例

```typescript
// src/pages/agents/AgentList.tsx
import React, { useState } from 'react';
import { Table, Button, Tag, Space, Input, Select, Modal } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAgents, useDeleteAgent } from '@/hooks/useAgent';
import type { Agent } from '@/types/agent';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;

export const AgentList: React.FC = () => {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<string>();
  const { data: agents, isLoading, refetch } = useAgents({ status: statusFilter });
  const deleteMutation = useDeleteAgent();
  
  const columns: ColumnsType<Agent> = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 80,
    },
    {
      title: '名称',
      dataIndex: 'name',
      render: (_, record) => (
        <Space>
          <Avatar src={record.icon} icon={!record.icon && <UserOutlined />} />
          <span>{record.name}</span>
          <Tag color={record.status === 'active' ? 'green' : 'default'}>
            {getStatusText(record.status)}
          </Tag>
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      ellipsis: true,
    },
    {
      title: '模型',
      render: (_, record) => `${record.provider} / ${record.model}`,
    },
    {
      title: '版本',
      dataIndex: 'version',
      align: 'center',
    },
    {
      title: '对话数',
      dataIndex: 'total_conversations',
      align: 'center',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      render: (date) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      width: 280,
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            onClick={() => navigate(`/agents/${record.id}`)}
          >
            详情
          </Button>
          <Button 
            type="link" 
            onClick={() => navigate(`/agents/${record.id}/edit`)}
          >
            编辑
          </Button>
          <Button 
            type="link" 
            onClick={() => navigate(`/agents/${record.id}/versions`)}
          >
            版本
          </Button>
          <Button 
            type="link" 
            danger 
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];
  
  const handleDelete = (record: Agent) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除 Agent "${record.name}" 吗？`,
      onOk: async () => {
        await deleteMutation.mutateAsync(record.id);
        refetch();
      },
    });
  };
  
  return (
    <div className="agent-list">
      <div className="page-header">
        <h2>BEC Agent 管理</h2>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => navigate('/agents/create')}
        >
          创建 Agent
        </Button>
      </div>
      
      <Card className="filter-card">
        <Space>
          <Select
            placeholder="状态筛选"
            style={{ width: 150 }}
            onChange={setStatusFilter}
            allowClear
          >
            <Option value="draft">草稿</Option>
            <Option value="active">激活</Option>
            <Option value="inactive">停用</Option>
            <Option value="archived">归档</Option>
          </Select>
          <Search placeholder="搜索 Agent" onSearch={refetch} />
        </Space>
      </Card>
      
      <Table
        columns={columns}
        dataSource={agents}
        loading={isLoading}
        rowKey="id"
        onRow={(record) => ({
          onClick: () => navigate(`/agents/${record.id}`),
        })}
      />
    </div>
  );
};
```

---

## 4. 页面路由规划

```typescript
// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { AgentList } from '@/pages/agents/AgentList';
import { AgentForm } from '@/pages/agents/AgentForm';
import { AgentDetail } from '@/pages/agents/AgentDetail';
import { AgentVersions } from '@/pages/agents/AgentVersions';
// ... 其他页面

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/agents" replace />} />
          <Route path="agents" element={<AgentList />} />
          <Route path="agents/create" element={<AgentForm />} />
          <Route path="agents/:id" element={<AgentDetail />} />
          <Route path="agents/:id/edit" element={<AgentForm />} />
          <Route path="agents/:id/versions" element={<AgentVersions />} />
          <Route path="knowledge" element={<KnowledgeList />} />
          <Route path="chat" element={<Chat />} />
          <Route path="tasks" element={<TaskList />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 5. 开发计划

### 阶段 1：基础框架（1 天）

- [ ] 项目初始化（Vite + TypeScript）
- [ ] 安装依赖（Ant Design、Zustand、React Query 等）
- [ ] 配置 ESLint + Prettier
- [ ] 创建基础目录结构
- [ ] 配置路由

### 阶段 2：核心功能（2 天）

- [ ] API 客户端封装
- [ ] Zustand Store 实现
- [ ] 自定义 Hooks
- [ ] Layout 组件
- [ ] AgentList 页面
- [ ] AgentForm 页面
- [ ] AgentDetail 页面
- [ ] AgentVersions 页面

### 阶段 3：功能完善（1 天）

- [ ] 错误处理
- [ ] 加载状态
- [ ] 表单验证
- [ ] 删除确认
- [ ] 回滚确认对话框

### 阶段 4：其他页面（2 天）

- [ ] 知识库管理页面
- [ ] 对话测试页面
- [ ] 任务管理页面

---

## 6. 技术亮点

### 6.1 类型安全

- 完整的 TypeScript 类型定义
- API 响应类型推断
- 表单数据类型验证

### 6.2 状态管理

- **Zustand** - 客户端状态（轻量、简单）
- **React Query** - 服务端状态（缓存、重试、乐观更新）

### 6.3 组件化

- 公共组件复用
- 页面组件拆分
- 自定义 Hooks 封装业务逻辑

### 6.4 性能优化

- 路由懒加载
- 列表虚拟滚动（大数据量时）
- React Query 缓存策略

---

## 7. 代码规范

### ESLint 规则

```javascript
// .eslintrc.cjs
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:@typescript-eslint/recommended',
  ],
  rules: {
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
  },
};
```

### Prettier 配置

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

---

## 8. 构建部署

### 开发

```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```

### 生产构建

```bash
npm run build
# 输出到 dist/ 目录
```

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
```

---

## 9. 审核要点

### 请审核以下内容：

1. **技术选型是否合理？**
   - React 18 + TypeScript ✓
   - Zustand + React Query ✓
   - Ant Design 5 ✓

2. **目录结构是否清晰？**
   - API/Components/Hooks/Pages/Stores/Types 分离 ✓

3. **代码示例是否符合规范？**
   - TypeScript 类型定义 ✓
   - 自定义 Hooks 封装 ✓
   - 组件写法 ✓

4. **功能是否完整？**
   - CRUD 操作 ✓
   - 版本管理 ✓
   - 回滚功能 ✓
   - 操作日志 ✓

5. **是否有遗漏的功能？**
   - 批量操作？
   - 搜索功能？
   - 导出导入？

---

## 10. 下一步

**待确认事项：**

1. ✅ 技术选型确认
2. ⏳ 目录结构确认
3. ⏳ 功能优先级确认
4. ⏳ 开始实现

**请审核以上技术方案，确认无误后我将立即开始实现！**
