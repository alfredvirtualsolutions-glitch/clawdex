// Surface 3 — Agent Builder: browse the 26-agent registry by division, inspect
// role, authority level, tasks, and guardrails.

import { useEffect, useMemo, useState } from 'react'
import { Bot, ShieldAlert, ListChecks } from 'lucide-react'
import { api } from '../lib/api'
import type { Agent, Catalog } from '../lib/types'
import { Card, Badge } from '../components/ui'
import { useAppStore } from '../store/useAppStore'

export function AgentBuilder() {
  const catalog = useAppStore((s) => s.catalog)
  const [local, setLocal] = useState<Catalog | null>(null)
  const [selected, setSelected] = useState<Agent | null>(null)

  useEffect(() => { if (!catalog) api.catalog().then(setLocal).catch(() => {}) }, [catalog])
  const cat = catalog ?? local

  const byDivision = useMemo(() => {
    const m: Record<string, Agent[]> = {}
    cat?.agents.forEach((a) => { (m[a.division] ??= []).push(a) })
    return m
  }, [cat])

  const active = selected ?? cat?.agents[0] ?? null

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <div className="space-y-5">
        {cat && Object.entries(byDivision).map(([div, agents]) => (
          <div key={div}>
            <div className="mb-2 flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full" style={{ background: cat.divisions[div]?.color }} />
              <h3 className="text-sm font-semibold">{cat.divisions[div]?.name} Division</h3>
              <span className="muted text-xs">({agents.length})</span>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {agents.map((a) => (
                <button
                  key={a.key}
                  onClick={() => setSelected(a)}
                  className={`card p-4 text-left transition hover:shadow-md ${active?.key === a.key ? 'ring-2 ring-brand-500' : ''}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Bot size={16} style={{ color: a.division_color }} />
                      <span className="font-semibold">{a.name}</span>
                    </div>
                    <Badge>L{a.authority}</Badge>
                  </div>
                  <div className="muted mt-1 text-xs">{a.role}</div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {active && (
        <Card className="h-fit lg:sticky lg:top-24">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg text-white" style={{ background: active.division_color }}>
              <Bot size={20} />
            </div>
            <div>
              <div className="text-lg font-semibold">{active.name}</div>
              <div className="muted text-xs">{active.role}</div>
            </div>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <Badge>{active.division_name}</Badge>
            <Badge tone="valid">Authority {active.authority} · {active.authority_name}</Badge>
          </div>
          <p className="mt-3 text-sm">{active.summary}</p>

          <div className="mt-4">
            <div className="mb-1 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide muted">
              <ListChecks size={14} /> Main tasks
            </div>
            <ul className="list-disc space-y-1 pl-5 text-sm">
              {active.tasks.map((t) => <li key={t}>{t}</li>)}
            </ul>
          </div>

          {active.guardrails.length > 0 && (
            <div className="mt-4 rounded-lg bg-rose-50 p-3 dark:bg-rose-500/10">
              <div className="mb-1 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-rose-600">
                <ShieldAlert size={14} /> Guardrails
              </div>
              <ul className="list-disc space-y-1 pl-5 text-sm text-rose-700 dark:text-rose-300">
                {active.guardrails.map((g) => <li key={g}>{g}</li>)}
              </ul>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
