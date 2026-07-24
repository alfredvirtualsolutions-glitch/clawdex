import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import './index.css'
import 'reactflow/dist/style.css'
import { LayoutShell } from './components/LayoutShell'
import { CommandCenter } from './pages/CommandCenter'
import { WorkflowCanvas } from './pages/WorkflowCanvas'
import { AgentBuilder } from './pages/AgentBuilder'
import { Approvals } from './pages/Approvals'
import { LeadsSignals } from './pages/LeadsSignals'
import { RunHistory } from './pages/RunHistory'
import { useBootstrap } from './hooks/useBootstrap'

function App() {
  useBootstrap()
  return (
    <BrowserRouter>
      <LayoutShell>
        <Routes>
          <Route path="/" element={<CommandCenter />} />
          <Route path="/workflow" element={<WorkflowCanvas />} />
          <Route path="/agents" element={<AgentBuilder />} />
          <Route path="/approvals" element={<Approvals />} />
          <Route path="/leads" element={<LeadsSignals />} />
          <Route path="/runs" element={<RunHistory />} />
        </Routes>
      </LayoutShell>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
