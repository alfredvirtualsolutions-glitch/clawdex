// Surface 7 — Settings: COSMIC-style appearance controls (accent + roundness +
// theme). Choices apply live via CSS variables and persist to localStorage.

import { useEffect, useState } from 'react'
import { Check, Play, Plug } from 'lucide-react'
import { ACCENTS, ROUNDS } from '../lib/theme'
import { api } from '../lib/api'
import { Card, SectionTitle, Badge } from '../components/ui'
import { useAppStore } from '../store/useAppStore'

interface Provider { name: string; agent: string; purpose: string; env: string; configured: boolean }

export function Settings() {
  const { accent, setAccent, round, setRound, theme, toggleTheme } = useAppStore()
  const [providers, setProviders] = useState<Provider[]>([])
  useEffect(() => { api.providers().then((r) => setProviders(r.providers)).catch(() => {}) }, [])

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Card>
        <SectionTitle>Accent color</SectionTitle>
        <p className="muted mb-4 text-sm">COSMIC-style accent palette. Applies across the whole interface instantly.</p>
        <div className="flex flex-wrap gap-3">
          {ACCENTS.map((a) => (
            <button
              key={a.key}
              onClick={() => setAccent(a.key)}
              className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-sm font-medium transition ${
                accent === a.key ? 'border-brand-500 ring-2 ring-brand-500/40' : 'border-slate-200 hover:bg-slate-100 dark:border-slate-800 dark:hover:bg-slate-800'
              }`}
            >
              <span className="h-5 w-5 rounded-full" style={{ background: a.base }} />
              {a.name}
              {accent === a.key && <Check size={14} className="text-brand-600" />}
            </button>
          ))}
        </div>
      </Card>

      <Card>
        <SectionTitle>Corner roundness</SectionTitle>
        <p className="muted mb-4 text-sm">COSMIC ships three corner styles. Pick how rounded surfaces should be.</p>
        <div className="inline-flex rounded-xl border border-slate-200 p-1 dark:border-slate-800">
          {ROUNDS.map((r) => (
            <button
              key={r.key}
              onClick={() => setRound(r.key)}
              className={`px-5 py-2 text-sm font-medium transition ${
                round === r.key ? 'bg-brand-600 text-white' : 'muted hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
              style={{ borderRadius: r.xl }}
            >
              {r.name}
            </button>
          ))}
        </div>
      </Card>

      <Card>
        <SectionTitle>Theme</SectionTitle>
        <div className="flex items-center gap-3">
          <button
            onClick={toggleTheme}
            className="rounded-full bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
          >
            Switch to {theme === 'dark' ? 'light' : 'dark'}
          </button>
          <span className="muted text-sm">Currently {theme}. Follows your OS by default.</span>
        </div>
      </Card>

      <Card>
        <SectionTitle icon={<Plug size={18} className="text-brand-600" />}>Integrations</SectionTitle>
        <p className="muted mb-4 text-sm">
          Providers behind the agents. Add each key to your <code className="mono">.env</code> file; status reflects what's configured on the server.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="muted border-b border-slate-200 text-xs uppercase tracking-wide dark:border-slate-800">
                <th className="px-3 py-2 font-medium">Provider</th>
                <th className="px-3 py-2 font-medium">Agent</th>
                <th className="px-3 py-2 font-medium">Purpose</th>
                <th className="px-3 py-2 font-medium">Env var</th>
                <th className="px-3 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {providers.map((p) => (
                <tr key={p.name}>
                  <td className="px-3 py-2 font-medium capitalize">{p.name}</td>
                  <td className="muted px-3 py-2">{p.agent}</td>
                  <td className="muted px-3 py-2">{p.purpose}</td>
                  <td className="px-3 py-2 font-mono text-xs">{p.env || '—'}</td>
                  <td className="px-3 py-2">
                    <Badge tone={p.configured ? 'valid' : undefined}>{p.configured ? 'connected' : 'not set'}</Badge>
                  </td>
                </tr>
              ))}
              {providers.length === 0 && (
                <tr><td colSpan={5} className="muted px-3 py-6 text-center text-sm">Start the backend to see provider status.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Live preview of the current tokens */}
      <Card>
        <SectionTitle>Preview</SectionTitle>
        <div className="flex flex-wrap items-center gap-3">
          <button className="flex items-center gap-1.5 rounded-full bg-brand-600 px-4 py-1.5 text-sm font-medium text-white">
            <Play size={15} /> Run cycle
          </button>
          <span className="rounded-xl border border-slate-200 px-3 py-1.5 text-sm dark:border-slate-800">Card surface</span>
          <Badge>Accent badge</Badge>
          <Badge tone="Hot">Hot</Badge>
          <Badge tone="valid">Valid</Badge>
          <div className="h-8 w-8 rounded-2xl bg-brand-500" />
        </div>
      </Card>
    </div>
  )
}
