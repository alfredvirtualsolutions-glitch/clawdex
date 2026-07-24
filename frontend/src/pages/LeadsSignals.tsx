// Surface 5 — Leads & Signals: the two evidence tables with status-flow context.

import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import type { Lead, Signal } from '../lib/types'
import { Card, SectionTitle, Table, Badge, EmptyState } from '../components/ui'

type Tab = 'signals' | 'leads'

export function LeadsSignals() {
  const [tab, setTab] = useState<Tab>('signals')
  const [signals, setSignals] = useState<Signal[]>([])
  const [leads, setLeads] = useState<Lead[]>([])

  useEffect(() => {
    api.signals().then((r) => setSignals(r.signals)).catch(() => {})
    api.leads().then((r) => setLeads(r.leads)).catch(() => {})
  }, [])

  return (
    <div className="space-y-4">
      <div className="inline-flex rounded-lg border border-slate-200 p-1 dark:border-slate-800">
        {(['signals', 'leads'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-md px-4 py-1.5 text-sm font-medium capitalize transition ${
              tab === t ? 'bg-brand-600 text-white' : 'muted hover:bg-slate-100 dark:hover:bg-slate-800'
            }`}
          >
            {t} ({t === 'signals' ? signals.length : leads.length})
          </button>
        ))}
      </div>

      {tab === 'signals' ? (
        <Card>
          <SectionTitle>Verified & candidate signals</SectionTitle>
          {signals.length === 0 ? <EmptyState>No signals.</EmptyState> : (
            <Table head={['Signal', 'Type', 'State', 'Found by', 'Score', 'Status', 'Date']}>
              {signals.map((s) => (
                <tr key={s.id}>
                  <td className="px-3 py-2">{s.title}</td>
                  <td className="px-3 py-2">{s.signal_type}</td>
                  <td className="px-3 py-2">{s.state}</td>
                  <td className="px-3 py-2 font-mono text-xs">{s.discovered_by}</td>
                  <td className="px-3 py-2 font-mono">{s.score}</td>
                  <td className="px-3 py-2"><Badge>{s.status}</Badge></td>
                  <td className="muted px-3 py-2 text-xs">{s.signal_date}</td>
                </tr>
              ))}
            </Table>
          )}
        </Card>
      ) : (
        <Card>
          <SectionTitle>Qualified leads</SectionTitle>
          {leads.length === 0 ? <EmptyState>No leads.</EmptyState> : (
            <Table head={['Name', 'Organization', 'Email', 'Email status', 'Identity', 'Score', 'Class']}>
              {leads.map((l) => (
                <tr key={l.id}>
                  <td className="px-3 py-2 font-medium">{l.full_name}</td>
                  <td className="px-3 py-2">{l.organization_name}</td>
                  <td className="px-3 py-2 font-mono text-xs">{l.professional_email}</td>
                  <td className="px-3 py-2"><Badge tone={l.email_status}>{l.email_status}</Badge></td>
                  <td className="muted px-3 py-2 text-xs">{l.identity_status}</td>
                  <td className="px-3 py-2 font-mono">{l.score}</td>
                  <td className="px-3 py-2"><Badge tone={l.classification}>{l.classification}</Badge></td>
                </tr>
              ))}
            </Table>
          )}
        </Card>
      )}
    </div>
  )
}
