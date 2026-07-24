// Surface 2 — Workflow Canvas: the agent command hierarchy as a live graph.
// Nodes are agents (grouped by division/authority); edges are the handoff pipeline.
// Nodes flash when a matching run event streams in over the WebSocket.

import { useEffect, useMemo, useState } from 'react'
import ReactFlow, {
  Background, Controls, MarkerType, type Edge, type Node,
} from 'reactflow'
import { api } from '../lib/api'
import type { Catalog } from '../lib/types'
import { useAppStore } from '../store/useAppStore'

const DIVISION_ORDER = ['command', 'signal', 'extraction', 'data', 'qualification', 'outreach', 'operations']

export function WorkflowCanvas() {
  const catalog = useAppStore((s) => s.catalog)
  const liveRuns = useAppStore((s) => s.liveRuns)
  const [local, setLocal] = useState<Catalog | null>(null)

  useEffect(() => { if (!catalog) api.catalog().then(setLocal).catch(() => {}) }, [catalog])
  const cat = catalog ?? local

  const lastActiveKey = liveRuns[0]?.agent_key

  const { nodes, edges } = useMemo(() => {
    if (!cat) return { nodes: [] as Node[], edges: [] as Edge[] }
    const colByDiv: Record<string, number> = {}
    DIVISION_ORDER.forEach((d, i) => (colByDiv[d] = i))
    const perDiv: Record<string, number> = {}

    const nodes: Node[] = cat.agents.map((a) => {
      const row = perDiv[a.division] ?? 0
      perDiv[a.division] = row + 1
      const active = a.key === lastActiveKey
      return {
        id: a.key,
        position: { x: colByDiv[a.division] * 210, y: row * 96 + 20 },
        data: { label: `${a.name}\n${a.role}` },
        style: {
          width: 176, padding: 8, borderRadius: 12, fontSize: 11,
          border: `2px solid ${active ? '#f59e0b' : a.division_color}`,
          background: active ? '#fffbeb' : 'white',
          color: '#0f172a', whiteSpace: 'pre-line', textAlign: 'center' as const,
          boxShadow: active ? '0 0 0 3px rgba(245,158,11,.25)' : '0 1px 2px rgba(0,0,0,.06)',
        },
      }
    })

    const edges: Edge[] = cat.pipeline.map((p, i) => ({
      id: `e${i}`,
      source: p.source,
      target: p.destination,
      animated: p.destination === lastActiveKey,
      style: { stroke: '#94a3b8', strokeWidth: 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#94a3b8' },
    }))
    return { nodes, edges }
  }, [cat, lastActiveKey])

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {DIVISION_ORDER.map((d) => cat && (
          <span key={d} className="pill" style={{ background: `${cat.divisions[d]?.color}22`, color: cat.divisions[d]?.color }}>
            {cat.divisions[d]?.name}
          </span>
        ))}
      </div>
      <div className="card" style={{ height: '72vh' }}>
        <ReactFlow nodes={nodes} edges={edges} fitView minZoom={0.3} proOptions={{ hideAttribution: true }}>
          <Background gap={16} color="#e2e8f0" />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
      <p className="muted text-xs">
        Columns = divisions · arrows = the handoff pipeline (Nova → Delta → Pathfinder → … → Oracle).
        A node highlights amber when its agent emits a run event. Trigger one with “Run cycle”.
      </p>
    </div>
  )
}
