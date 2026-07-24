// Frontend Services Layer — API Client.
// Talks to the Agent OS backend. In dev, Vite proxies /api to :8787.

import type {
  Approval, Campaign, Catalog, Counts, Lead, Outreach, RunEvent, Signal,
} from './types'

const BASE = import.meta.env.VITE_API_BASE ?? ''

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`)
  return res.json() as Promise<T>
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`)
  return res.json() as Promise<T>
}

export const api = {
  catalog: () => get<Catalog>('/api/catalog'),
  overview: () => get<{ counts: Counts; recent_runs: RunEvent[]; operating_principles: string[] }>('/api/overview'),
  campaigns: () => get<{ campaigns: Campaign[] }>('/api/campaigns'),
  signals: (campaignId?: string) =>
    get<{ signals: Signal[] }>(`/api/signals${campaignId ? `?campaign_id=${campaignId}` : ''}`),
  leads: (opts?: { campaignId?: string; classification?: string }) => {
    const q = new URLSearchParams()
    if (opts?.campaignId) q.set('campaign_id', opts.campaignId)
    if (opts?.classification) q.set('classification', opts.classification)
    const s = q.toString()
    return get<{ leads: Lead[] }>(`/api/leads${s ? `?${s}` : ''}`)
  },
  outreach: () => get<{ outreach: Outreach[] }>('/api/outreach'),
  approvals: (status = 'pending') => get<{ approvals: Approval[] }>(`/api/approvals?status=${status}`),
  decideApproval: (id: string, decision: 'approved' | 'rejected') =>
    post<{ approval: Approval }>(`/api/approvals/${id}/decision`, { decision }),
  runs: (limit = 100) => get<{ runs: RunEvent[] }>(`/api/runs?limit=${limit}`),
  runCycle: (campaignId?: string) =>
    post<{ status: string; campaign_id: string }>('/api/orchestrator/run-cycle', { campaign_id: campaignId }),
}
