import React from 'react';
import { LayoutDashboard, Server, AlertTriangle, RotateCcw, Terminal, FileText } from 'lucide-react';

export type TabType = 'overview' | 'services' | 'simulation' | 'incidents' | 'recovery' | 'audit';

interface SidebarProps {
  activeTab: TabType;
  onSelectTab: (tab: TabType) => void;
  activeIncidentsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab, activeIncidentsCount }) => {
  const menuItems = [
    { id: 'overview' as TabType, label: 'Overview Dashboard', icon: LayoutDashboard },
    { id: 'services' as TabType, label: 'Monitored Services', icon: Server },
    { id: 'simulation' as TabType, label: 'Simulation Lab', icon: Terminal, highlight: true },
    { id: 'incidents' as TabType, label: 'Incidents & Alerts', icon: AlertTriangle, badge: activeIncidentsCount },
    { id: 'recovery' as TabType, label: 'Recovery & Policies', icon: RotateCcw },
    { id: 'audit' as TabType, label: 'Audit Trail', icon: FileText },
  ];

  return (
    <aside className="w-64 bg-[#0B1222] border-r border-[#1B2945] flex flex-col justify-between p-4 flex-shrink-0">
      <nav className="space-y-1.5">
        <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">
          Operations Center
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.1)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#142038]'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/40">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Engine Status Card */}
      <div className="p-3.5 rounded-xl bg-[#0F182B] border border-[#1B2945] text-xs">
        <div className="flex items-center justify-between mb-2">
          <span className="text-slate-400 font-medium">Orchestrator Mode</span>
          <span className="text-[10px] uppercase font-bold text-emerald-400">Autonomous</span>
        </div>
        <p className="text-[11px] text-slate-500 leading-relaxed">
          Closed-loop health probes active. Failing probes trigger auto-restart and scale policies within bounds.
        </p>
      </div>
    </aside>
  );
};
