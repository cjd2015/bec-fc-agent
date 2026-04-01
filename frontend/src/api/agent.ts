import { api } from './index'
import type {
  Agent,
  AgentVersion,
  AgentOperationLog,
  AgentCreateRequest,
  AgentUpdateRequest,
} from '@/types/agent'

export const agentApi = {
  list: (params?: { status?: string; limit?: number; offset?: number }) =>
    api.get<Agent[]>('/agent', { params }),

  get: (id: number) => api.get<Agent>(`/agent/${id}`),

  create: (data: AgentCreateRequest) => api.post<Agent>('/agent', data),

  update: (id: number, data: AgentUpdateRequest) => api.put<Agent>(`/agent/${id}`, data),

  delete: (id: number) => api.delete(`/agent/${id}`),

  restore: (id: number) => api.post(`/agent/${id}/restore`),

  getVersions: (id: number, params?: { limit?: number }) =>
    api.get<AgentVersion[]>(`/agent/${id}/versions`, { params }),

  getVersion: (agentId: number, versionId: number) =>
    api.get<AgentVersion>(`/agent/${agentId}/versions/${versionId}`),

  rollback: (agentId: number, versionId: number) =>
    api.post(`/agent/${agentId}/rollback/${versionId}`),

  getOperations: (id: number, params?: { limit?: number }) =>
    api.get<AgentOperationLog[]>(`/agent/${id}/operations`, { params }),

  getOperationDetail: (agentId: number, operationId: number) =>
    api.get<AgentOperationLog>(`/agent/${agentId}/operations/${operationId}`),
}
