// Presentation Layer — Layout Shell: Sidebar + Topbar + routed content.

import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Workflow, Bot, CheckSquare, Radio, History,
  Moon, Sun, Wifi, WifiOff, Play,
} from 'lucide-react'
import type { ReactNode } from 'react'
import { useAppStore } from '../store/useAppStore'
import { api } from '../lib/api'

const NAV = [
  { to: '/', label: 'Command Center', icon: LayoutDashboard, end: true },
  { to: '/workflow', label: 'Workflow Canvas', icon: Workflow },
  { to: '/agents', label: 'Agent Builder', icon: Bot },
  { to: '/approvals', label: 'Approvals', icon: CheckSquare },
  { to: '/leads', label: 'Leads & Signals', icon: Radio },
  { to: '/runs', label: 'Run History', icon: History },
]

function titleFor(path: string) {
  return NAV.find((n) => (n.end ? path === n.to : path.startsWith(n.to) && n.to !== '/'))?.label
    ?? 'Command Center'
}

export function LayoutShell({ children }: { children: ReactNode }) {
  const { theme, toggleTheme, connected, cycleRunning } = useAppStore()
  const loc = useLocation()

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-60 flex-col border-r border-slate-200 bg-white px-3 py-5 dark:border-slate-800 dark:bg-slate-900 lg:flex">
        <div className="mb-6 flex items-center gap-2 px-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 font-bold text-white">J</div>
          <div>
            <div className="text-sm font-semibold leading-tight">Juan OS</div>
            <div className="muted text-[11px] leading-tight">VBS Local Agent OS</div>
          </div>
        </div>
        <nav className="flex flex-col gap-1">
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? 'bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300'
                    : 'muted hover:bg-slate-100 dark:hover:bg-slate-800'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto rounded-lg border border-slate-200 p-3 text-xs dark:border-slate-800">
          <div className="flex items-center gap-2">
            {connected ? <Wifi size={14} className="text-emerald-500" /> : <WifiOff size={14} className="text-slate-400" />}
            <span className="muted">{connected ? 'Live · connected' : 'Offline'}</span>
          </div>
          <div className="muted mt-1">Local-first · human-in-the-loop</div>
        </div>
      </aside>

      {/* Main column */}
      <div className="flex min-w-0 flex-1 flex-col lg:pl-60">
        {/* Topbar */}
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white/80 px-6 py-3 backdrop-blur dark:border-slate-800 dark:bg-slate-900/80">
          <div>
            <h1 className="text-lg font-semibold">{titleFor(loc.pathname)}</h1>
            <p className="muted text-xs">Local-first AI operations assistant</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => api.runCycle().catch(() => {})}
              disabled={cycleRunning}
              className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-brand-700 disabled:opacity-50"
            >
              <Play size={15} /> {cycleRunning ? 'Running…' : 'Run cycle'}
            </button>
            <button
              onClick={toggleTheme}
              className="rounded-lg border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 dark:border-slate-800 dark:hover:bg-slate-800"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </button>
          </div>
        </header>

        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  )
}
