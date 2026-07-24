// Presentation / Component Layer — reusable primitives (Cards, Badges, Stats, Table).

import type { ReactNode } from 'react'

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`card p-5 ${className}`}>{children}</div>
}

export function SectionTitle({ children, icon }: { children: ReactNode; icon?: ReactNode }) {
  return (
    <div className="mb-4 flex items-center gap-2">
      {icon}
      <h3 className="text-base font-semibold">{children}</h3>
    </div>
  )
}

export function Stat({ label, value, sub, accent = 'brand' }:
  { label: string; value: ReactNode; sub?: string; accent?: string }) {
  const ring: Record<string, string> = {
    brand: 'text-brand-600', green: 'text-emerald-600', amber: 'text-amber-600',
    violet: 'text-violet-600', teal: 'text-teal-600', red: 'text-rose-600',
  }
  return (
    <Card>
      <div className="muted text-xs font-medium uppercase tracking-wide">{label}</div>
      <div className={`mt-1 text-3xl font-bold ${ring[accent] ?? ring.brand}`}>{value}</div>
      {sub && <div className="muted mt-1 text-xs">{sub}</div>}
    </Card>
  )
}

const TONES: Record<string, string> = {
  Hot: 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300',
  Moderate: 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300',
  Nurture: 'bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300',
  valid: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300',
  catch_all: 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300',
  risky: 'bg-orange-100 text-orange-700 dark:bg-orange-500/15 dark:text-orange-300',
  unknown: 'bg-slate-100 text-slate-600 dark:bg-slate-700/40 dark:text-slate-300',
  active: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300',
  paused: 'bg-slate-100 text-slate-600 dark:bg-slate-700/40 dark:text-slate-300',
  pending: 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300',
  ok: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300',
}

export function Badge({ children, tone }: { children: ReactNode; tone?: string }) {
  const cls = (tone && TONES[tone]) || 'bg-brand-100 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300'
  return <span className={`pill ${cls}`}>{children}</span>
}

export function Table({ head, children }: { head: string[]; children: ReactNode }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="muted border-b border-slate-200 text-xs uppercase tracking-wide dark:border-slate-800">
            {head.map((h) => <th key={h} className="whitespace-nowrap px-3 py-2 font-medium">{h}</th>)}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">{children}</tbody>
      </table>
    </div>
  )
}

export function EmptyState({ children }: { children: ReactNode }) {
  return <div className="muted py-10 text-center text-sm">{children}</div>
}
