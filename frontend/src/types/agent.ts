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
  id: number
  agent_id: number
  version: number
  snapshot: Partial<Agent>
  change_summary?: string
  change_details?: Record<string, any>
  operator_name?: string
  created_at: string
  is_rollback_target: boolean
}

export interface AgentOperationLog {
  id: number
  agent_id: number
  operation_type: 'create' | 'update' | 'delete' | 'rollback' | 'publish'
  operation_name: string
  before_snapshot?: Partial<Agent>
  after_snapshot?: Partial<Agent>
  changes?: Record<string, any>
  operator_name?: string
  ip_address?: string
  status: 'success' | 'failed'
  error_message?: string
  can_rollback: boolean
  created_at: string
}

export interface AgentCreateRequest {
  name: string
  description?: string
  icon?: string
  provider?: string
  model?: string
  model_variant?: string
  temperature?: number
  max_tokens?: number
  system_prompt?: string
  knowledge_base_ids?: number[]
}

export interface AgentUpdateRequest extends Partial<AgentCreateRequest> {
  create_version?: boolean
  change_summary?: string
}
