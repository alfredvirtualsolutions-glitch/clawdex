'use client'

import { useState, useEffect } from 'react';
import { Activity, Workflow, Radio, TrendingUp, Shield, BarChart3, Users, Settings, FileText, Bell, HardDrive, Wrench, CheckCircle, Cpu } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = {
  purple: '#a855f7',
  cyan: '#06b6d4',
  green: '#22c55e',
  orange: '#f97316',
  red: '#ef4444',
  blue: '#3b82f6',
};

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [signals, setSignals] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeNav, setActiveNav] = useState('Overview');

  const fetchData = async () => {
    try {
      const [statsRes, workflowsRes, signalsRes, analyticsRes] = await Promise.all([
        fetch('/api/dashboard/stats'),
        fetch('/api/dashboard/workflows'),
        fetch('/api/dashboard/signals'),
        fetch('/api/dashboard/analytics'),
      ]);

      const statsData = await statsRes.json();
      const workflowsData = await workflowsRes.json();
      const signalsData = await signalsRes.json();
      const analyticsData = await analyticsRes.json();

      setStats(statsData);
      setWorkflows(workflowsData.workflows || []);
      setSignals(signalsData.signals || []);
      setAnalytics(analyticsData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { icon: Activity, label: 'Overview' },
    { icon: Workflow, label: 'Workflows' },
    { icon: Users, label: 'Agents' },
    { icon: Radio, label: 'Signals' },
    { icon: FileText, label: 'Leads' },
    { icon: Bell, label: 'Outreach' },
    { icon: HardDrive, label: 'Memory' },
    { icon: Settings, label: 'Settings' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a1a] flex items-center justify-center">
        <div className="text-cyan-400 text-xl animate-pulse">Initializing Juan OS...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a1a] text-gray-100">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-full w-64 glassmorphism border-r border-purple-500/20 z-50">
        {/* Logo */}
        <div className="p-6 flex items-center space-x-3">
          <div className="w-12 h-12 hexagon bg-gradient-to-br from-purple-500 to-cyan-500 neon-glow-purple flex items-center justify-center">
            <span className="text-2xl font-bold">J</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="px-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.label}
                onClick={() => setActiveNav(item.label)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                  activeNav === item.label
                    ? 'bg-purple-500/20 text-purple-400 neon-glow-purple'
                    : 'text-gray-400 hover:text-purple-400 hover:bg-purple-500/10'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* System Status */}
        <div className="absolute bottom-6 left-4 right-4">
          <div className="glassmorphism rounded-lg p-4 border border-green-500/30">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse neon-glow-green"></div>
              <span className="text-sm text-green-400">All Systems Operational</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64 p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-6xl font-bold text-gradient mb-2">Juan Operating System</h1>
          <p className="text-gray-400 text-lg">Neon-backed agent OS with tools, guardrails, chassis, and command UI.</p>
        </div>

        {/* Top Stats */}
        <div className="grid grid-cols-5 gap-4 mb-8">
          <StatCard
            title="Agents Online"
            value={stats?.agentsOnline || 0}
            icon={Users}
            color="purple"
          />
          <StatCard
            title="Workflows Running"
            value={stats?.workflowsRunning || 0}
            icon={Workflow}
            color="cyan"
          />
          <StatCard
            title="Signals Today"
            value={stats?.signalsToday || 0}
            icon={Radio}
            color="green"
          />
          <StatCard
            title="Success Rate"
            value={`${stats?.successRate || 0}%`}
            icon={TrendingUp}
            color="orange"
          />
          <StatCard
            title="System Health"
            value={stats?.systemHealth || 'Unknown'}
            icon={Shield}
            color={stats?.systemHealth === 'Excellent' ? 'green' : 'red'}
          />
        </div>

        {/* Main Panel - 3 Columns */}
        <div className="grid grid-cols-3 gap-6 mb-8">
          {/* Active Workflows */}
          <Card className="glassmorphism border-purple-500/20 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-purple-400">Active Workflows</h3>
              <Workflow className="w-5 h-5 text-purple-400" />
            </div>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {workflows.map((workflow) => (
                <div key={workflow.id} className="glassmorphism rounded-lg p-4 border border-cyan-500/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-200">{workflow.name}</span>
                    <Badge className={`text-xs ${
                      workflow.status === 'running' ? 'bg-green-500/20 text-green-400' :
                      workflow.status === 'completed' ? 'bg-blue-500/20 text-blue-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {workflow.status}
                    </Badge>
                  </div>
                  <Badge className="text-xs bg-purple-500/20 text-purple-400 mb-2">{workflow.type}</Badge>
                  <Progress value={workflow.progress} className="h-2" />
                  <span className="text-xs text-gray-400 mt-1">{workflow.progress}%</span>
                </div>
              ))}
              {workflows.length === 0 && (
                <p className="text-gray-500 text-sm">No active workflows</p>
              )}
            </div>
            <button className="mt-4 text-cyan-400 text-sm hover:text-cyan-300 transition-colors">
              View all workflows →
            </button>
          </Card>

          {/* Live Signal Feed */}
          <Card className="glassmorphism border-purple-500/20 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-cyan-400">Live Signal Feed</h3>
              <Radio className="w-5 h-5 text-cyan-400" />
            </div>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {signals.map((signal) => (
                <div key={signal.id} className="glassmorphism rounded-lg p-3 border border-purple-500/20">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-200 mb-1">{signal.title}</div>
                      <Badge className="text-xs bg-cyan-500/20 text-cyan-400">{signal.campaign}</Badge>
                    </div>
                    <Badge className={`text-xs ml-2 ${
                      signal.score === 'Hot' ? 'bg-orange-500/20 text-orange-400' :
                      signal.score === 'Moderate' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {signal.score === 'Hot' && '🔥 '}{signal.score}
                    </Badge>
                  </div>
                  <span className="text-xs text-gray-500 mt-1">{signal.timeAgo}</span>
                </div>
              ))}
              {signals.length === 0 && (
                <p className="text-gray-500 text-sm">No signals detected</p>
              )}
            </div>
            <button className="mt-4 text-cyan-400 text-sm hover:text-cyan-300 transition-colors">
              View all signals →
            </button>
          </Card>

          {/* Terminal */}
          <Card className="glassmorphism border-purple-500/20 p-6 font-mono">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-green-400">Terminal</h3>
              <Cpu className="w-5 h-5 text-green-400" />
            </div>
            <div className="bg-black/50 rounded-lg p-4 text-sm text-green-400">
              <div className="mb-2">
                <span className="text-cyan-400">juan@command</span>:<span className="text-blue-400">~</span>$ status
              </div>
              <div className="space-y-1 text-gray-300">
                <div>System    : <span className="text-green-400">Operational</span></div>
                <div>Agents    : <span className="text-purple-400">{stats?.agentsOnline || 0}</span> online</div>
                <div>Signals   : <span className="text-cyan-400">{stats?.signalsToday || 0}</span> today</div>
                <div>Leads     : <span className="text-yellow-400">{workflows.length}</span> total</div>
                <div>Uptime    : <span className="text-green-400">Live</span></div>
              </div>
              <div className="mt-4">
                <span className="text-cyan-400">juan@command</span>:<span className="text-blue-400">~</span>$ <span className="animate-pulse">_</span>
              </div>
            </div>
          </Card>
        </div>

        {/* Analytics Section */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          {/* Signals by Campaign */}
          <Card className="glassmorphism border-purple-500/20 p-6">
            <h3 className="text-lg font-bold text-purple-400 mb-4">Signals by Campaign</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={analytics?.signalsByCampaign || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="campaign" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #a855f7' }}
                />
                <Bar dataKey="count" fill={COLORS.purple} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Signal Classification */}
          <Card className="glassmorphism border-purple-500/20 p-6">
            <h3 className="text-lg font-bold text-cyan-400 mb-4">Signal Classification</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={analytics?.signalClassification || []}
                  dataKey="count"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  label
                >
                  {(analytics?.signalClassification || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={[
                      COLORS.orange,
                      COLORS.cyan,
                      COLORS.purple
                    ][index % 3]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #06b6d4' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </Card>

          {/* Leads Pipeline */}
          <Card className="glassmorphism border-purple-500/20 p-6">
            <h3 className="text-lg font-bold text-green-400 mb-4">Leads Pipeline</h3>
            <div className="space-y-3">
              <PipelineStep label="Signals" value={analytics?.leadsPipeline?.signals || 0} color="purple" />
              <PipelineStep label="Named" value={analytics?.leadsPipeline?.named || 0} color="cyan" />
              <PipelineStep label="Enriched" value={analytics?.leadsPipeline?.enriched || 0} color="green" />
              <PipelineStep label="Valid Email" value={analytics?.leadsPipeline?.valid_email || 0} color="orange" />
              <PipelineStep label="Contacted" value={analytics?.leadsPipeline?.contacted || 0} color="blue" />
            </div>
          </Card>

          {/* Daily Signal Trend */}
          <Card className="glassmorphism border-purple-500/20 p-6">
            <h3 className="text-lg font-bold text-orange-400 mb-4">Daily Signal Trend</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={analytics?.dailyTrend || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="date" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #f97316' }}
                />
                <Line type="monotone" dataKey="count" stroke={COLORS.orange} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Bottom Architecture Strip */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          <ArchitectureCard
            icon={HardDrive}
            title="Neon Database Backend"
            description="secure data layer, tables, signals, workflows"
            color="purple"
          />
          <ArchitectureCard
            icon={Wrench}
            title="Tools"
            description="connectors, scraping, enrichment, automation"
            color="cyan"
          />
          <ArchitectureCard
            icon={Shield}
            title="Guardrails"
            description="safety rules, permissions, validation, compliance"
            color="green"
          />
          <ArchitectureCard
            icon={Cpu}
            title="Chassis"
            description="orchestration engine, workflow runtime, scheduling, memory"
            color="orange"
          />
        </div>

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm">
          Built to orchestrate signal-driven workflows from search to action.
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon: Icon, color }) => {
  const colorClasses = {
    purple: 'border-purple-500/20 text-purple-400 neon-glow-purple',
    cyan: 'border-cyan-500/20 text-cyan-400 neon-glow-cyan',
    green: 'border-green-500/20 text-green-400 neon-glow-green',
    orange: 'border-orange-500/20 text-orange-400',
    red: 'border-red-500/20 text-red-400',
  };

  return (
    <Card className={`glassmorphism ${colorClasses[color]} p-6`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{title}</span>
        <Icon className="w-5 h-5" />
      </div>
      <div className="text-3xl font-bold">{value}</div>
    </Card>
  );
};

const PipelineStep = ({ label, value, color }) => {
  const colors = {
    purple: 'bg-purple-500',
    cyan: 'bg-cyan-500',
    green: 'bg-green-500',
    orange: 'bg-orange-500',
    blue: 'bg-blue-500',
  };

  return (
    <div className="flex items-center space-x-3">
      <div className={`w-3 h-3 rounded-full ${colors[color]}`}></div>
      <span className="text-sm text-gray-400 flex-1">{label}</span>
      <span className="text-sm font-bold text-gray-200">{value}</span>
    </div>
  );
};

const ArchitectureCard = ({ icon: Icon, title, description, color }) => {
  const colorClasses = {
    purple: 'border-purple-500/30 text-purple-400',
    cyan: 'border-cyan-500/30 text-cyan-400',
    green: 'border-green-500/30 text-green-400',
    orange: 'border-orange-500/30 text-orange-400',
  };

  return (
    <Card className={`glassmorphism ${colorClasses[color]} p-6 text-center`}>
      <div className="w-16 h-16 hexagon bg-gradient-to-br from-purple-500/20 to-cyan-500/20 flex items-center justify-center mx-auto mb-4">
        <Icon className="w-8 h-8" />
      </div>
      <h4 className="font-bold mb-2">{title}</h4>
      <p className="text-xs text-gray-400">{description}</p>
    </Card>
  );
};

function App() {
  return <Dashboard />;
}

export default App;
