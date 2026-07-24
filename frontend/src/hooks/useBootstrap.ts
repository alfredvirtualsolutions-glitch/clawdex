// Loads the catalog and opens the live run WebSocket once, app-wide.

import { useEffect } from 'react'
import { api } from '../lib/api'
import { RunSocket, wsUrl } from '../lib/ws'
import { useAppStore } from '../store/useAppStore'

export function useBootstrap() {
  const { setCatalog, ingest, setConnected } = useAppStore()

  useEffect(() => {
    api.catalog().then(setCatalog).catch(() => {})

    const sock = new RunSocket(wsUrl())
    const off = sock.onMessage((msg) => {
      ingest(msg)
      if (msg.type === 'hello') setConnected(true)
    })
    sock.connect()
    setConnected(true)

    return () => {
      off()
      sock.close()
      setConnected(false)
    }
  }, [setCatalog, ingest, setConnected])
}
