// Frontend Services Layer — WebSocket / SSE Client.
// Provides real-time run visibility with auto-reconnect.

import type { WsMessage } from './types'

type Listener = (msg: WsMessage) => void

export class RunSocket {
  private ws: WebSocket | null = null
  private listeners = new Set<Listener>()
  private reconnectTimer: number | null = null
  private closed = false

  constructor(private readonly url: string) {}

  connect() {
    this.closed = false
    try {
      this.ws = new WebSocket(this.url)
      this.ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data) as WsMessage
          this.listeners.forEach((l) => l(msg))
        } catch {
          /* ignore malformed */
        }
      }
      this.ws.onclose = () => this.scheduleReconnect()
      this.ws.onerror = () => this.ws?.close()
    } catch {
      this.scheduleReconnect()
    }
  }

  private scheduleReconnect() {
    if (this.closed || this.reconnectTimer) return
    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null
      this.connect()
    }, 2000)
  }

  onMessage(l: Listener) {
    this.listeners.add(l)
    return () => this.listeners.delete(l)
  }

  close() {
    this.closed = true
    this.ws?.close()
  }
}

export function wsUrl(): string {
  const base = import.meta.env.VITE_WS_BASE
  if (base) return base
  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${location.host}/ws`
}
