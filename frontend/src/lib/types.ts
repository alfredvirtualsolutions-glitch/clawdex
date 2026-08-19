// Shared types mirroring the Agent OS backend payloads.

export interface Agent {
  key: string
  name: string
  role: string
  division: string
  division_name: string
  division_color: string
  authority: number
  authority_name: string
  summary: string
  tasks: string[]
  guardrails: string[]
}

export interface PipelineEdge { source: string; destination: string; label: string }

export interface Catalog {
  divisions: Record<string, { name: string; color: string }>
  authority_levels: Record<string, { name: string; can: string }>
  agents: Agent[]
  signal_flow: string[]
  lead_flow: string[]
  outreach_flow: string[]
  failure_states: string[]
  pipeline: PipelineEdge[]
  handoff_contract: string[]
  operating_principles: string[]
}

export interface Counts {
  campaigns: number; campaigns_active: number
  signals: number; signals_verified: number
  leads: number; leads_hot: number
  outreach: number; approvals_pending: number; runs: number
}

export interface Campaign {
  id: string; name: string; advisor_name: string; advisor_license_states: string
  target_state: string; target_profession: string; target_retirement_system: string
  minimum_signal_score: number; status: string; created_at: string
}

export interface Signal {
  id: string; campaign_id: string; signal_type: string; title: string; summary: string
  state: string; source_url: string; signal_date: string; status: string; score: number
  discovered_by: string; created_at: string
}

export interface Lead {
  id: string; campaign_id: string; signal_id: string; full_name: string; job_title: string
  organization_name: string; professional_email: string; state: string; email_status: string
  identity_status: string; score: number; classification: string; status: string; created_at: string
}

export interface Outreach {
  id: string; campaign_id: string; lead_id: string; subject: string; body: string
  status: string; provider: string; created_at: string
}

export interface Approval {
  id: string; campaign_id: string; record_type: string; record_id: string; title: string
  reason: string; requested_by: string; status: string; created_at: string
}

export interface RunEvent {
  id: string; campaign_id: string; agent_key: string; division: string; action: string
  record_type: string; record_id: string; status: string; detail: string; created_at: string
}

export interface WsMessage {
  type: 'hello' | 'run' | 'cycle_start' | 'cycle_complete'
  counts?: Counts
  campaign_id?: string
  [k: string]: unknown
}
