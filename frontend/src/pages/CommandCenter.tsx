// Surface 1 — Command Center: KPIs, live activity, pipeline health, principles.

import { useEffect, useState } from 'react'
import { Activity, ShieldCheck } from 'lucide-react'
import {
  BarChart, Bar, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid, Cell,
} from 'recharts'
import { api } from '../lib/api'
import type { Counts, Lead, RunEvent } from '../lib/types'
import { Card, SectionTitle, Stat, Badge, EmptyState } from '../components/ui'
import { useAppStore } from '../store/useAppStore'

export function CommandCenter() {
  const [counts, setCounts] = useState<Counts | null>(null)
  const [principles, setPrinciples] = useState<string[]>([])
  const [leads, setLeads] = useState<Lead[]>([])
  const liveRuns = useAppStore((s) => s.liveRuns)
  const [seedRuns, setSeedRuns] = useState<RunEvent[]>([])

  useEffect(() => {
    api.overview().then((o) => { setCounts(o.counts); setPrinciples(o.operating_principles); setSeedRuns(o.recent_runs) }).catch(() => {})
    api.leads().then((r) => setLeads(r.leads)).catch(() => {})
  }, [])

  const runs = [...liveRuns, ...seedRuns].slice(0, 14)
  const classes = ['Hot', 'Moderate', 'Nurture']
  const colors: Record<string, string> = { Hot: '#e11d48', Moderate: '#f59e0b', Nurture: '#0ea5e9' }
  const chart = classes.map((c) => ({ name: c, count: leads.filter((l) => l.classification === c).length }))

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
        <Stat label="Active campaigns" value={counts?.campaigns_active ?? '—'} accent="brand" />
        <Stat label="Signals" value={counts?.signals ?? '—'} sub={`${counts?.signals_verified ?? 0} verified`} accent="teal" />
        <Stat label="Leads" value={counts?.leads ?? '—'} accent="violet" />
        <Stat label="Hot leads" value={counts?.leads_hot ?? '—'} accent="red" />
        <Stat label="Approvals" value={counts?.approvals_pending ?? '—'} sub="awaiting human" accent="amber" />
        <Stat label="Runs logged" value={counts?.runs ?? '—'} accent="green" />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <SectionTitle icon={<Activity size={18} className="text-brand-600" />}>Live activity</SectionTitle>
          <div className="max-h-80 space-y-2 overflow-y-auto">
            {runs.length === 0 && <EmptyState>No activity yet — click “Run cycle”.</EmptyState>}
            {runs.map((r) => (
              <div key={r.id} className="flex items-start gap-3 rounded-lg border border-slate-100 px-3 py-2 dark:border-slate-800">
                <Badge tone={r.status}>{r.agent_key}</Badge>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm">{r.detail}</div>
                  <div className="muted text-[11px]">{r.division} · {r.action} · {new Date(r.created_at).toLocaleTimeString()}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <SectionTitle>Lead classification</SectionTitle>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.4} />
              <XAxis dataKey="name" fontSize={12} stroke="#94a3b8" />
              <YAxis allowDecimals={false} fontSize={12} stroke="#94a3b8" />
              <Tooltip cursor={{ fill: 'transparent' }} />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {chart.map((e) => <Cell key={e.name} fill={colors[e.name]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card>
        <SectionTitle icon={<ShieldCheck size={18} className="text-emerald-600" />}>Operating principles</SectionTitle>
        <div className="flex flex-wrap gap-2">
          {principles.map((p) => <Badge key={p} tone="valid">{p}</Badge>)}
        </div>
      </Card>
    </div>
  )
}
