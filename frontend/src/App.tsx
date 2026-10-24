import React, { useState, useEffect } from 'react';
import {
  Server,
  Activity,
  AlertTriangle,
  RotateCcw,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Layers,
  Sparkles,
  RefreshCw,
  Terminal,
  ExternalLink
} from 'lucide-react';
import { Navbar } from './components/Navbar';
import { Sidebar, TabType } from './components/Sidebar';
import { MetricCard } from './components/MetricCard';
import { LiveClusterChart } from './components/LiveClusterChart';
import { ServiceCard } from './components/ServiceCard';
import { SimulationModal } from './components/SimulationModal';
import { AuthModal } from './components/AuthModal';
import { api } from './services/api';
import { wsClient } from './services/websocket';
import {
  DashboardSummary,
  Service,
  Incident,
  RecoveryPolicy,
  RecoveryExecution,
  User,
  MetricSample,
  FailureType
} from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [user, setUser] = useState<User | null>(null);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [recoveryHistory, setRecoveryHistory] = useState<RecoveryExecution[]>([]);
  const [recoveryPolicies, setRecoveryPolicies] = useState<RecoveryPolicy[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [clusterMetricsSamples, setClusterMetricsSamples] = useState<MetricSample[]>([]);

  // Modals & Controls
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isSimOpen, setIsSimOpen] = useState(false);
  const [simServiceId, setSimServiceId] = useState<number | undefined>(undefined);
  const [isWsConnected, setIsWsConnected] = useState(false);
  const [autoRecovery, setAutoRecovery] = useState(true);
  const [loadingAction, setLoadingAction] = useState(false);

  // Initial Fetch & Auth Check
  useEffect(() => {
    const init = async () => {
      // Check existing token
      if (api.getToken()) {
        try {
          const me = await api.getMe();
          setUser(me);
        } catch (e) {
          api.logout();
        }
      }
      await refreshAllData();
    };

    init();

    // Start WebSocket
    wsClient.connect();
    const unsubscribe = wsClient.subscribe((data) => {
      setIsWsConnected(true);
      if (data.type === 'TELEMETRY_UPDATE') {
        // Sync real-time updates into state
        refreshAllData();
      }
    });

    // Fallback polling interval (5 seconds)
    const interval = setInterval(() => {
      refreshAllData();
    }, 5000);

    return () => {
      unsubscribe();
      clearInterval(interval);
    };
  }, []);

  const refreshAllData = async () => {
    try {
      const [sumData, srvData, incData, recData, polData] = await Promise.all([
        api.getDashboardSummary().catch(() => null),
        api.getServices().catch(() => ({ total: 0, services: [] })),
        api.getIncidents().catch(() => ({ total: 0, active_count: 0, incidents: [] })),
        api.getRecoveryHistory().catch(() => ({ total: 0, success_rate_percent: 100, executions: [] })),
        api.getRecoveryPolicies().catch(() => [])
      ]);

      if (sumData) setSummary(sumData);
      if (srvData) setServices(srvData.services);
      if (incData) setIncidents(incData.incidents);
      if (recData) setRecoveryHistory(recData.executions);
      if (polData) setRecoveryPolicies(polData);

      // Fetch primary service metric sample history for chart
      if (srvData && srvData.services.length > 0) {
        const primaryService = srvData.services[0];
        const mData = await api.getServiceMetrics(primaryService.id, 25).catch(() => null);
        if (mData) {
          setClusterMetricsSamples(mData.samples);
        }
      }
    } catch (err) {
      console.error('Error fetching cluster telemetry:', err);
    }
  };

  const handleExecuteAction = async (serviceId: number, action: string) => {
    setLoadingAction(true);
    try {
      await api.executeServiceAction(serviceId, action);
      await refreshAllData();
    } catch (err: any) {
      alert(`Action failed: ${err.message}`);
    } finally {
      setLoadingAction(false);
    }
  };

  const handleInjectFault = async (serviceId: number, failureType: FailureType, duration: number) => {
    await api.injectFault(serviceId, failureType, duration);
    await refreshAllData();
  };

  const handleResetSimulation = async (serviceId: number) => {
    await api.resetSimulation(serviceId);
    await refreshAllData();
  };

  const handleResolveIncident = async (incidentId: number) => {
    try {
      await api.resolveIncident(incidentId);
      await refreshAllData();
    } catch (err: any) {
      alert(`Could not resolve incident: ${err.message}`);
    }
  };

  const handleLogin = async (u: string, p: string) => {
    const res = await api.login(u, p);
    setUser(res.user);
    await refreshAllData();
  };

  const handleRegister = async (u: string, e: string, p: string) => {
    const res = await api.register(u, e, p);
    setUser(res.user);
    await refreshAllData();
  };

  const handleLogout = () => {
    api.logout();
    setUser(null);
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#070C18] text-slate-100">
      {/* Top Navbar */}
      <Navbar
        user={user}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
        isWsConnected={isWsConnected}
        autoRecoveryEnabled={autoRecovery}
        onToggleAutoRecovery={() => setAutoRecovery(!autoRecovery)}
        onOpenSimulation={() => {
          setSimServiceId(undefined);
          setIsSimOpen(true);
        }}
      />

      {/* Main App Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Operations Navigation */}
        <Sidebar
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          activeIncidentsCount={summary?.active_incidents_count || 0}
        />

        {/* Dynamic Center Work Area */}
        <main className="flex-1 overflow-y-auto p-8 space-y-6">
          {/* TAB 1: OVERVIEW DASHBOARD */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Active Incident Warning Alert */}
              {summary && summary.active_incidents_count > 0 && (
                <div className="bg-gradient-to-r from-rose-500/20 via-rose-500/10 to-transparent border border-rose-500/40 rounded-2xl p-4 flex items-center justify-between shadow-[0_0_20px_rgba(244,63,94,0.15)]">
                  <div className="flex items-center space-x-3.5">
                    <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400">
                      <AlertTriangle className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white">
                        {summary.active_incidents_count} Active Health Incident{summary.active_incidents_count > 1 ? 's' : ''} Detected
                      </h4>
                      <p className="text-xs text-rose-300/80">
                        Autonomic healing engine is currently mitigating unhealthy service containers.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setActiveTab('incidents')}
                    className="px-3.5 py-1.5 rounded-xl bg-rose-500 hover:bg-rose-400 text-slate-950 text-xs font-bold transition-colors"
                  >
                    View Incidents
                  </button>
                </div>
              )}

              {/* Key Operational Metric Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                  title="Monitored Services"
                  value={summary?.total_services || services.length}
                  subtitle={`${summary?.health_breakdown.healthy || 0} Healthy, ${summary?.health_breakdown.degraded || 0} Degraded`}
                  icon={Server}
                  variant="cyan"
                />
                <MetricCard
                  title="Cluster CPU Average"
                  value={`${summary?.cluster_metrics.average_cpu_percent || 0}%`}
                  subtitle="Average utilization across active nodes"
                  icon={Activity}
                  variant="emerald"
                />
                <MetricCard
                  title="Average Latency"
                  value={`${summary?.cluster_metrics.average_latency_ms || 0}ms`}
                  subtitle={`Error Rate: ${summary?.cluster_metrics.overall_error_rate_percent || 0}%`}
                  icon={Clock}
                  variant="blue"
                />
                <MetricCard
                  title="Recovery Success Rate"
                  value={`${summary?.recovery_success_rate_percent || 100}%`}
                  subtitle={`${summary?.total_recoveries_count || 0} autonomous actions logged`}
                  icon={RotateCcw}
                  variant="amber"
                />
              </div>

              {/* Charts & Graphs */}
              <div className="grid grid-cols-1 gap-6">
                <LiveClusterChart
                  samples={clusterMetricsSamples}
                  title="Cluster Telemetry Stream (CPU & Memory Utilization)"
                />
              </div>

              {/* Monitored Microservices Grid */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-base font-bold text-white tracking-tight">Cloud Microservices & Containers</h3>
                    <p className="text-xs text-slate-400">Continuous health monitoring, failure counts, and recovery controls</p>
                  </div>
                  <button
                    onClick={refreshAllData}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#142038] hover:bg-[#1B2B4A] border border-[#233659] text-xs text-slate-300 font-medium transition-colors"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Refresh</span>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {services.map((service) => (
                    <ServiceCard
                      key={service.id}
                      service={service}
                      onExecuteAction={handleExecuteAction}
                      onSimulate={(id) => {
                        setSimServiceId(id);
                        setIsSimOpen(true);
                      }}
                      isLoading={loadingAction}
                    />
                  ))}
                </div>
              </div>

              {/* Recent Recovery Actions Feed */}
              <div className="bg-[#142038] border border-[#233659] rounded-2xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-bold text-white">Recent Autonomic Recovery Actions</h3>
                    <p className="text-xs text-slate-400">Audit trail of automated and manual recovery attempts</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('recovery')}
                    className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold"
                  >
                    View All &rarr;
                  </button>
                </div>

                <div className="divide-y divide-[#1F2E4D]">
                  {recoveryHistory.slice(0, 5).map((rec) => (
                    <div key={rec.id} className="py-3 flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                          <RotateCcw className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <div className="font-semibold text-white">
                            Action: <span className="uppercase text-cyan-400">{rec.action}</span> on {rec.service_name || `Service #${rec.service_id}`}
                          </div>
                          <div className="text-[11px] text-slate-400">{rec.execution_log}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                          {rec.status}
                        </span>
                        <div className="text-[10px] text-slate-500 mt-1">
                          {new Date(rec.started_at).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}
                  {recoveryHistory.length === 0 && (
                    <div className="py-6 text-center text-xs text-slate-500">
                      No automated recovery executions logged yet. Inject a fault in the Simulation Lab to test self-healing!
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: MONITORED SERVICES */}
          {activeTab === 'services' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-white">Monitored Cloud Services</h2>
                  <p className="text-xs text-slate-400">Service topology, container health probes, and alert thresholds</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {services.map((service) => (
                  <ServiceCard
                    key={service.id}
                    service={service}
                    onExecuteAction={handleExecuteAction}
                    onSimulate={(id) => {
                      setSimServiceId(id);
                      setIsSimOpen(true);
                    }}
                    isLoading={loadingAction}
                  />
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: SIMULATION LAB */}
          {activeTab === 'simulation' && (
            <div className="space-y-6">
              <div className="bg-[#142038] border border-[#233659] rounded-2xl p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-lg font-bold text-white flex items-center space-x-2">
                      <Terminal className="w-5 h-5 text-rose-400" />
                      <span>Simulation & Chaos Engineering Lab</span>
                    </h2>
                    <p className="text-xs text-slate-400 mt-1 leading-relaxed max-w-2xl">
                      Inject deterministic cloud failures (CPU spikes, memory leaks, latency degradation, 500 error storms, container termination) to observe the closed-loop autonomic healing engine detect, validate, and safely restore services.
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setSimServiceId(undefined);
                      setIsSimOpen(true);
                    }}
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-rose-500 to-amber-500 hover:from-rose-600 hover:to-amber-600 text-slate-950 text-xs font-bold shadow-[0_0_15px_rgba(244,63,94,0.3)] transition-all"
                  >
                    Open Fault Injector
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
                  {services.map((s) => (
                    <div key={s.id} className="p-4 rounded-xl bg-[#0B1222] border border-[#1B2945]">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-white text-xs">{s.name}</span>
                        <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                          s.status === 'healthy' ? 'text-emerald-400 bg-emerald-500/10' : 'text-rose-400 bg-rose-500/10'
                        }`}>
                          {s.status}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400 mb-3">
                        Container: <code className="text-slate-300">{s.container_id}</code>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            setSimServiceId(s.id);
                            setIsSimOpen(true);
                          }}
                          className="flex-1 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 text-xs font-semibold"
                        >
                          Inject Failure
                        </button>
                        <button
                          onClick={() => handleResetSimulation(s.id)}
                          className="py-1.5 px-3 rounded-lg bg-[#142038] hover:bg-[#1B2B4A] border border-[#233659] text-xs text-slate-400"
                        >
                          Reset
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: INCIDENTS & ROOT CAUSES */}
          {activeTab === 'incidents' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-white">Incidents & Root Cause Analysis</h2>
                <p className="text-xs text-slate-400">Tracked failure events, metric evidence, and mitigation states</p>
              </div>

              <div className="bg-[#142038] border border-[#233659] rounded-2xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0F182B] text-slate-400 uppercase tracking-wider text-[10px] border-b border-[#233659]">
                    <tr>
                      <th className="px-5 py-3">Incident</th>
                      <th className="px-5 py-3">Service</th>
                      <th className="px-5 py-3">Severity</th>
                      <th className="px-5 py-3">Suspected Root Cause</th>
                      <th className="px-5 py-3">Status</th>
                      <th className="px-5 py-3">Detected Time</th>
                      <th className="px-5 py-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1F2E4D]">
                    {incidents.map((inc) => (
                      <tr key={inc.id} className="hover:bg-[#1B2B4A]/50 transition-colors">
                        <td className="px-5 py-3.5 font-bold text-white">{inc.title}</td>
                        <td className="px-5 py-3.5 text-slate-300 font-mono text-[11px]">{inc.service_name || inc.service_id}</td>
                        <td className="px-5 py-3.5">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            inc.severity === 'critical' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          }`}>
                            {inc.severity}
                          </span>
                        </td>
                        <td className="px-5 py-3.5 text-slate-300">{inc.suspected_root_cause}</td>
                        <td className="px-5 py-3.5">
                          <span className="font-semibold text-cyan-400 uppercase text-[10px]">{inc.status}</span>
                        </td>
                        <td className="px-5 py-3.5 text-slate-400 text-[11px]">{new Date(inc.detection_time).toLocaleTimeString()}</td>
                        <td className="px-5 py-3.5 text-right">
                          {inc.status !== 'resolved' && (
                            <button
                              onClick={() => handleResolveIncident(inc.id)}
                              className="px-2.5 py-1 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-semibold"
                            >
                              Resolve
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                    {incidents.length === 0 && (
                      <tr>
                        <td colSpan={7} className="px-5 py-8 text-center text-slate-500 text-xs">
                          No active or historical incidents recorded.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 5: RECOVERY ACTIONS & POLICIES */}
          {activeTab === 'recovery' && (
            <div className="space-y-6">
              {/* Policies Configuration */}
              <div className="bg-[#142038] border border-[#233659] rounded-2xl p-5">
                <h3 className="text-sm font-bold text-white mb-1">Configured Autonomic Recovery Policies</h3>
                <p className="text-xs text-slate-400 mb-4">Self-healing trigger conditions, retry thresholds, and cooldown timers</p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {recoveryPolicies.map((pol) => (
                    <div key={pol.id} className="p-3.5 rounded-xl bg-[#0B1222] border border-[#1B2945] text-xs">
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="font-bold text-white">{pol.name}</span>
                        <span className="text-[10px] uppercase font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded">
                          {pol.action_type}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 mb-2 leading-snug">{pol.description}</p>
                      <div className="flex justify-between text-[10px] text-slate-500 pt-2 border-t border-[#1F2E4D]">
                        <span>Retries: {pol.max_retries}</span>
                        <span>Cooldown: {pol.cooldown_seconds}s</span>
                        <span className="text-emerald-400 font-semibold">{pol.is_enabled ? 'Active' : 'Disabled'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Execution History */}
              <div className="bg-[#142038] border border-[#233659] rounded-2xl p-5">
                <h3 className="text-sm font-bold text-white mb-1">Recovery Execution Log</h3>
                <p className="text-xs text-slate-400 mb-4">Before and after health state verification records</p>

                <div className="divide-y divide-[#1F2E4D]">
                  {recoveryHistory.map((rec) => (
                    <div key={rec.id} className="py-3 flex items-center justify-between text-xs">
                      <div>
                        <div className="font-semibold text-white">
                          Action: <span className="uppercase text-cyan-400">{rec.action}</span> on {rec.service_name || `Service #${rec.service_id}`}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">{rec.execution_log}</div>
                        <div className="text-[10px] text-slate-500 mt-1">
                          Health Transition: <span className="text-rose-400">{rec.pre_health_status}</span> &rarr; <span className="text-emerald-400">{rec.post_health_status}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                          {rec.status}
                        </span>
                        <div className="text-[10px] text-slate-500 mt-1">
                          {new Date(rec.started_at).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                  {recoveryHistory.length === 0 && (
                    <div className="py-6 text-center text-xs text-slate-500">
                      No automated recovery executions logged yet.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: AUDIT TRAIL */}
          {activeTab === 'audit' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-white">Immutable Audit Trail</h2>
                <p className="text-xs text-slate-400">Append-only log of all operator actions, recovery executions, and policy adjustments</p>
              </div>

              <div className="bg-[#142038] border border-[#233659] rounded-2xl p-5">
                <button
                  onClick={async () => {
                    const res = await api.getAuditLogs().catch(() => ({ total: 0, logs: [] }));
                    setAuditLogs(res.logs);
                  }}
                  className="px-3 py-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs font-semibold mb-4"
                >
                  Load Latest Audit Logs
                </button>

                <div className="divide-y divide-[#1F2E4D]">
                  {auditLogs.map((log) => (
                    <div key={log.id} className="py-3 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-bold text-white font-mono">{log.action}</span>
                        <span className="text-slate-400 ml-2">Entity: {log.entity_type}:{log.entity_id}</span>
                        <div className="text-[11px] text-slate-500 mt-0.5 font-mono">
                          {JSON.stringify(log.details)}
                        </div>
                      </div>
                      <div className="text-right text-[10px] text-slate-400">
                        <div>{new Date(log.created_at).toLocaleString()}</div>
                        <div className="text-slate-500">{log.ip_address}</div>
                      </div>
                    </div>
                  ))}
                  {auditLogs.length === 0 && (
                    <div className="py-6 text-center text-xs text-slate-500">
                      Click 'Load Latest Audit Logs' to display historical immutable records.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Simulation Modal */}
      <SimulationModal
        isOpen={isSimOpen}
        onClose={() => setIsSimOpen(false)}
        services={services}
        selectedServiceId={simServiceId}
        onInject={handleInjectFault}
        onReset={handleResetSimulation}
      />

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onLogin={handleLogin}
        onRegister={handleRegister}
      />
    </div>
  );
};
