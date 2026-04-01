import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentApi } from '@/api/agent'
import type { AgentCreateRequest, AgentUpdateRequest } from '@/types/agent'

export function useAgents(params?: { status?: string }) {
  return useQuery({
    queryKey: ['agents', params],
    queryFn: () => agentApi.list(params),
  })
}

export function useAgent(id?: number) {
  return useQuery({
    queryKey: ['agent', id],
    queryFn: () => agentApi.get(id!),
    enabled: !!id,
  })
}

export function useCreateAgent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: AgentCreateRequest) => agentApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
    },
  })
}

export function useUpdateAgent(id: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: AgentUpdateRequest) => agentApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent', id] })
      queryClient.invalidateQueries({ queryKey: ['agents'] })
    },
  })
}

export function useDeleteAgent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => agentApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
    },
  })
}

export function useRestoreAgent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => agentApi.restore(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
    },
  })
}

export function useAgentVersions(agentId?: number) {
  return useQuery({
    queryKey: ['agent-versions', agentId],
    queryFn: () => agentApi.getVersions(agentId!),
    enabled: !!agentId,
  })
}

export function useRollback(agentId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (versionId: number) => agentApi.rollback(agentId, versionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent', agentId] })
      queryClient.invalidateQueries({ queryKey: ['agent-versions', agentId] })
    },
  })
}

export function useAgentOperations(agentId?: number) {
  return useQuery({
    queryKey: ['agent-operations', agentId],
    queryFn: () => agentApi.getOperations(agentId!),
    enabled: !!agentId,
  })
}
