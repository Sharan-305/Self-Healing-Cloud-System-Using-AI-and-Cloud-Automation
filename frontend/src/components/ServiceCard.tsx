import React from 'react';
import { RotateCcw, Play, Square, Layers, Sparkles, Activity } from 'lucide-react';
import { Service, ServiceStatus } from '../types';

interface ServiceCardProps {
  service: Service;
  onExecuteAction: (serviceId: number, action: string) => void;
  onSimulate: (serviceId: number) => void;
  isLoading?: boolean;
}

export const ServiceCard: React.FC<ServiceCardProps> = ({
  service,
  onExecuteAction,
  onSimulate,
  isLoading
}) => {
  const statusConfig: Record<ServiceStatus, { label: string; badge: string; dot: string }> = {
    healthy: {
      label: 'Healthy',
      badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      dot: 'bg-emerald-400'
    },
    degraded: {
      label: 'Degraded',
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      dot: 'bg-amber-400'
    },
    unhealthy: {
      label: 'Unhealthy',
      badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      dot: 'bg-rose-400'
    },
    recovering: {
      label: 'Auto-Healing',
      badge: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 healing-pulse',
      dot: 'bg-cyan-400'
    },
    stopped: {
      label: 'Stopped',
      badge: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
      dot: 'bg-slate-400'
    }
  };

  const status = statusConfig[service.status] || statusConfig.healthy;

  return (
    <div className={`bg-[#142038] border rounded-2xl p-5 transition-all ${
      service.status === 'unhealthy' 
        ? 'border-rose-500/50 shadow-[0_0_20px_rgba(239,68,68,0.15)]' 
        : service.status === 'recovering'
        ? 'border-cyan-500/50 shadow-[0_0_20px_rgba(6,182,212,0.15)]'
        : 'border-[#233659] hover:border-[#2C4472]'
    }`}>
      {/* Top Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center space-x-2">
            <h4 className="font-bold text-white tracking-tight">{service.name}</h4>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#0B1222] text-slate-400 border border-[#1B2945]">
              {service.container_id || 'container'}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">{service.description || service.service_type}</p>
        </div>
        <div className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${status.badge}`}>
          <span className={`w-2 h-2 rounded-full ${status.dot}`}></span>
          <span>{status.label}</span>
        </div>
      </div>

      {/* Metrics Row & Thresholds */}
      <div className="grid grid-cols-2 gap-3 my-4 p-3 rounded-xl bg-[#0B1222] border border-[#1B2945] text-xs">
        <div>
          <span className="text-slate-400 block text-[11px]">Thresholds</span>
          <span className="font-semibold text-slate-200">
            CPU &gt; {service.cpu_threshold_percent}% | RAM &gt; {service.memory_threshold_percent}%
          </span>
        </div>
        <div>
          <span className="text-slate-400 block text-[11px]">Consecutive Failures</span>
          <span className={`font-semibold ${service.consecutive_failures > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {service.consecutive_failures} / {service.max_consecutive_failures} (Max)
          </span>
        </div>
      </div>

      {/* Control Actions */}
      <div className="flex items-center justify-between pt-3 border-t border-[#1F2E4D]">
        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => onExecuteAction(service.id, 'restart')}
            disabled={isLoading}
            title="Safe Restart Container"
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-[#0F182B] hover:bg-cyan-500/10 hover:text-cyan-400 border border-[#233659] text-xs text-slate-300 font-medium transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Restart</span>
          </button>
          <button
            onClick={() => onExecuteAction(service.id, 'clear_cache')}
            disabled={isLoading}
            title="Purge Memory Cache"
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-[#0F182B] hover:bg-blue-500/10 hover:text-blue-400 border border-[#233659] text-xs text-slate-300 font-medium transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Cache Purge</span>
          </button>
          <button
            onClick={() => onExecuteAction(service.id, 'scale_up')}
            disabled={isLoading}
            title="Scale Replica"
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-[#0F182B] hover:bg-emerald-500/10 hover:text-emerald-400 border border-[#233659] text-xs text-slate-300 font-medium transition-colors"
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Scale</span>
          </button>
        </div>

        <button
          onClick={() => onSimulate(service.id)}
          className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 text-xs font-semibold transition-colors"
        >
          <Activity className="w-3.5 h-3.5" />
          <span>Inject Fault</span>
        </button>
      </div>
    </div>
  );
};
