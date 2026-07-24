// State & Client Logic Layer — global app store (Zustand).
// Holds catalog, theme, live run log, and connection status.

import { create } from 'zustand'
import type { Catalog, RunEvent, WsMessage } from '../lib/types'

type Theme = 'light' | 'dark'

interface AppState {
  theme: Theme
  toggleTheme: () => void
  catalog: Catalog | null
  setCatalog: (c: Catalog) => void
  liveRuns: RunEvent[]
  cycleRunning: boolean
  connected: boolean
  setConnected: (v: boolean) => void
  ingest: (msg: WsMessage) => void
}

const initialTheme: Theme =
  (localStorage.getItem('vbs-theme') as Theme) ||
  (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')

function applyTheme(t: Theme) {
  document.documentElement.classList.toggle('dark', t === 'dark')
  localStorage.setItem('vbs-theme', t)
}
applyTheme(initialTheme)

export const useAppStore = create<AppState>((set) => ({
  theme: initialTheme,
  toggleTheme: () =>
    set((s) => {
      const theme = s.theme === 'dark' ? 'light' : 'dark'
      applyTheme(theme)
      return { theme }
    }),
  catalog: null,
  setCatalog: (c) => set({ catalog: c }),
  liveRuns: [],
  cycleRunning: false,
  connected: false,
  setConnected: (v) => set({ connected: v }),
  ingest: (msg) =>
    set((s) => {
      if (msg.type === 'run') {
        return { liveRuns: [msg as unknown as RunEvent, ...s.liveRuns].slice(0, 200) }
      }
      if (msg.type === 'cycle_start') return { cycleRunning: true }
      if (msg.type === 'cycle_complete') return { cycleRunning: false }
      return {}
    }),
}))
