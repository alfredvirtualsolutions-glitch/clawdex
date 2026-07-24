// Surface 4 — Approvals: the human-in-the-loop review queue. Hot leads and
// flagged records require a human decision before outreach can proceed.

import { useEffect, useState } from 'react'
import { Check, X, ShieldCheck } from 'lucide-react'
import { api } from '../lib/api'
import type { Approval } from '../lib/types'
import { Card, Badge, EmptyState } from '../components/ui'

export function Approvals() {
  const [items, setItems] = useState<Approval[]>([])
  const [busy, setBusy] = useState<string | null>(null)

  const load = () => api.approvals('pending').then((r) => setItems(r.approvals)).catch(() => {})
  useEffect(() => { load() }, [])

  async function decide(id: string, decision: 'approved' | 'rejected') {
    setBusy(id)
    try {
      await api.decideApproval(id, decision)
      setItems((s) => s.filter((a) => a.id !== id))
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <Card>
        <div className="flex items-center gap-2 text-sm">
          <ShieldCheck size={18} className="text-emerald-600" />
          <span>Human approvals before actions. Suppression, compliance, and financial review always override automation.</span>
        </div>
      </Card>

      {items.length === 0 && <Card><EmptyState>No pending approvals. 🎉</EmptyState></Card>}

      {items.map((a) => (
        <Card key={a.id}>
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <Badge tone="Hot">{a.record_type}</Badge>
                <span className="font-semibold">{a.title}</span>
              </div>
              <p className="muted mt-1 text-sm">{a.reason}</p>
              <div className="muted mt-2 text-xs">Requested by {a.requested_by} · {new Date(a.created_at).toLocaleString()}</div>
            </div>
            <div className="flex shrink-0 gap-2">
              <button
                onClick={() => decide(a.id, 'approved')}
                disabled={busy === a.id}
                className="flex items-center gap-1 rounded-lg bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                <Check size={15} /> Approve
              </button>
              <button
                onClick={() => decide(a.id, 'rejected')}
                disabled={busy === a.id}
                className="flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                <X size={15} /> Reject
              </button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}
