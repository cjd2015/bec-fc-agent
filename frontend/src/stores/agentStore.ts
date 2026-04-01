import { create } from 'zustand'
import { agentApi } from '@/api/agent'
import type { Agent, AgentVersion, AgentCreateRequest, AgentUpdateRequest } from '@/types/agent'

interface AgentState {
  agents: Agent[]
  currentAgent: Agent | null
  versions: AgentVersion[]
  loading: boolean
  error: string | null

  fetchAgents: (params?: { status?: string }) => Promise<void>
  fetchAgent: (id: number) => Promise<void>
  createAgent: (data: AgentCreateRequest) => Promise<Agent>
  updateAgent: (id: number, data: AgentUpdateRequest) => Promise<void>
  deleteAgent: (id: number) => Promise<void>
  restoreAgent: (id: number) => Promise<void>
  fetchVersions: (id: number) => Promise<void>
  rollbackToVersion: (agentId: number, versionId: number) => Promise<void>
  clearCurrentAgent: () => void
  clearError: () => void
}

export const useAgentStore = create<AgentState>((set, get) => ({
  agents: [],
  currentAgent: null,
  versions: [],
  loading: false,
  error: null,

  fetchAgents: async (params) => {
    set({ loading: true, error: null })
    try {
      const data = await agentApi.list(params)
      set({ agents: data, loading: false })
    } catch (e) {
      set({ error: (e as Error).message, loading: false })
      throw e
    }
  },

  fetchAgent: async (id) => {
    set({ loading: true, error: null })
    try {
      const data = await agentApi.get(id)
      set({ currentAgent: data, loading: false })
      return data
    } catch (e) {
      set({ error: (e as Error).message, loading: false })
      throw e
    }
  },

  createAgent: async (data) => {
    const agent = await agentApi.create(data)
    await get().fetchAgents()
    return agent
  },

  updateAgent: async (id, data) => {
    await agentApi.update(id, data)
    await get().fetchAgent(id)
  },

  deleteAgent: async (id) => {
    await agentApi.delete(id)
    await get().fetchAgents()
  },

  restoreAgent: async (id) => {
    await agentApi.restore(id)
    await get().fetchAgents()
  },

  fetchVersions: async (id) => {
    const data = await agentApi.getVersions(id)
    set({ versions: data })
    return data
  },

  rollbackToVersion: async (agentId, versionId) => {
    await agentApi.rollback(agentId, versionId)
    await get().fetchAgent(agentId)
    await get().fetchVersions(agentId)
  },

  clearCurrentAgent: () => set({ currentAgent: null }),
  clearError: () => set({ error: null }),
}))
