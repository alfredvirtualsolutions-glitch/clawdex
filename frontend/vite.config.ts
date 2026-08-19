import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Local-first dev server. API + WebSocket are proxied to the Agent OS backend
// (python -m juan_os.agent_os on :8787) so the frontend can talk to it in dev.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8787', changeOrigin: true },
      '/ws': { target: 'ws://127.0.0.1:8787', ws: true },
    },
  },
})
