// Surface 6 — Run History: the audit timeline of agent actions (live + persisted).

import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import type { RunEvent } from '../lib/types'
import { Card, Badge, Table, EmptyState } from '../components/ui'
import { useAppStore } from '../store/useAppStore'

export function RunHistory() {
  const liveRuns = useAppStore((s) => s.liveRuns)
  const [persisted, setPersisted] = useState<RunEvent[]>([])

  useEffect(() => { api.runs(200).then((r) => setPersisted(r.runs)).catch(() => {}) }, [])

  // De-dup live + persisted by id, newest first.
  const seen = new Set<string>()
  const all = [...liveRuns, ...persisted].filter((r) => (seen.has(r.id) ? false : seen.add(r.id)))

  return (
    <Card>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-base font-semibold">Run history · audit timeline</h3>
        <span className="muted text-xs">{all.length} events</span>
      </div>
      {all.length === 0 ? <EmptyState>No runs recorded yet.</EmptyState> : (
        <Table head={['Time', 'Agent', 'Division', 'Action', 'Record', 'Status', 'Detail']}>
          {all.map((r) => (
            <tr key={r.id}>
              <td className="muted whitespace-nowrap px-3 py-2 text-xs">{new Date(r.created_at).toLocaleTimeString()}</td>
              <td className="px-3 py-2 font-medium">{r.agent_key}</td>
              <td className="muted px-3 py-2 text-xs">{r.division}</td>
              <td className="px-3 py-2 font-mono text-xs">{r.action}</td>
              <td className="muted px-3 py-2 text-xs">{r.record_type}</td>
              <td className="px-3 py-2"><Badge tone={r.status}>{r.status}</Badge></td>
              <td className="px-3 py-2">{r.detail}</td>
            </tr>
          ))}
        </Table>
      )}
    </Card>
  )
}
