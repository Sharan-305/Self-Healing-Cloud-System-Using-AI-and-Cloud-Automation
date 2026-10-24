import React, { useState } from 'react';
import { Terminal, X, AlertTriangle, Flame, ShieldAlert, Cpu, HardDrive, Clock, ShieldCheck } from 'lucide-react';
import { Service, FailureType } from '../types';

interface SimulationModalProps {
  isOpen: boolean;
  onClose: () => void;
  services: Service[];
  selectedServiceId?: number;
  onInject: (serviceId: number, failureType: FailureType, duration: number) => Promise<void>;
  onReset: (serviceId: number) => Promise<void>;
}

export const SimulationModal: React.FC<SimulationModalProps> = ({
  isOpen,
  onClose,
  services,
  selectedServiceId,
  onInject,
  onReset
}) => {
  if (!isOpen) return null;

  const [targetId, setTargetId] = useState<number>(selectedServiceId || (services[0]?.id ?? 1));
  const [failureType, setFailureType] = useState<FailureType>('cpu_overload');
  const [duration, setDuration] = useState<number>(45);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const failureTypes = [
    {
      id: 'cpu_overload' as FailureType,
      name: 'CPU Overload (95%+)',
      desc: 'Simulates infinite compute loop or crypto spike. Triggers scale-up or process cycle.',
      icon: Cpu,
      color: 'text-amber-400 border-amber-500/30 bg-amber-500/10'
    },
    {
      id: 'memory_pressure' as FailureType,
      name: 'Memory Leak (95%+)',
      desc: 'Simulates uncollected heap buffers. Triggers memory cache purge or restart.',
      icon: HardDrive,
      color: 'text-rose-400 border-rose-500/30 bg-rose-500/10'
    },
    {
      id: 'high_latency' as FailureType,
      name: 'Thread Starvation / Latency Spike (1200ms+)',
      desc: 'Simulates hung database locks and slow I/O. Triggers graceful process recycling.',
      icon: Clock,
      color: 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10'
    },
    {
      id: 'http_500_errors' as FailureType,
      name: 'HTTP 500 Failure Storm (60%+ Error Rate)',
      desc: 'Simulates cascading runtime exceptions. Triggers container drain & recreation.',
      icon: AlertTriangle,
      color: 'text-rose-400 border-rose-500/30 bg-rose-500/10'
    },
    {
      id: 'container_crash' as FailureType,
      name: 'Dead Container Crash (SIGKILL / 0% CPU)',
      desc: 'Simulates container death. Health probe fails and triggers immediate auto-restart.',
      icon: Flame,
      color: 'text-rose-500 border-rose-500/40 bg-rose-500/15'
    }
  ];

  const handleInject = async () => {
    setLoading(true);
    setFeedback(null);
    try {
      await onInject(targetId, failureType, duration);
      setFeedback(`Fault '${failureType}' successfully injected! Watch the dashboard autonomic engine detect and heal it.`);
    } catch (err: any) {
      setFeedback(`Injection failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    setFeedback(null);
    try {
      await onReset(targetId);
      setFeedback('Simulation cleared. Service returned to normal telemetry baseline.');
    } catch (err: any) {
      setFeedback(`Reset failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-xl bg-[#0F182B] border border-[#233659] rounded-2xl shadow-2xl p-6 text-slate-100">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#1B2945]">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Simulation Lab — Fault Injection</h3>
              <p className="text-xs text-slate-400">Safely test autonomic self-healing detection & remediation</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Target Service Picker */}
        <div className="mt-5 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
              Target Microservice
            </label>
            <select
              value={targetId}
              onChange={(e) => setTargetId(Number(e.target.value))}
              className="w-full bg-[#142038] border border-[#233659] rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500"
            >
              {services.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.container_id || 'container'} - Status: {s.status})
                </option>
              ))}
            </select>
          </div>

          {/* Fault Category Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
              Failure Pattern
            </label>
            <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
              {failureTypes.map((item) => {
                const Icon = item.icon;
                const isSelected = failureType === item.id;
                return (
                  <div
                    key={item.id}
                    onClick={() => setFailureType(item.id)}
                    className={`p-3 rounded-xl border cursor-pointer transition-all flex items-start space-x-3 ${
                      isSelected
                        ? 'border-cyan-500 bg-cyan-500/10 shadow-[0_0_15px_rgba(6,182,212,0.15)]'
                        : 'border-[#1B2945] bg-[#142038] hover:border-[#2C4472]'
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-lg border flex items-center justify-center flex-shrink-0 ${item.color}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">{item.name}</div>
                      <div className="text-[11px] text-slate-400 leading-snug mt-0.5">{item.desc}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Duration Slider */}
          <div>
            <div className="flex justify-between text-xs text-slate-300 mb-1">
              <span>Fault Duration</span>
              <span className="font-bold text-cyan-400">{duration} seconds</span>
            </div>
            <input
              type="range"
              min={15}
              max={120}
              step={5}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="w-full accent-cyan-500 bg-[#142038] h-2 rounded-lg cursor-pointer"
            />
          </div>

          {feedback && (
            <div className="p-3 rounded-xl text-xs bg-[#142038] border border-cyan-500/30 text-cyan-300">
              {feedback}
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-5 mt-5 border-t border-[#1B2945]">
          <button
            onClick={handleReset}
            disabled={loading}
            className="px-4 py-2 rounded-xl bg-[#142038] hover:bg-[#1B2B4A] border border-[#233659] text-xs font-semibold text-slate-300 transition-colors"
          >
            Clear Active Fault
          </button>
          <div className="flex space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-[#142038] hover:bg-[#1B2B4A] border border-[#233659] text-xs font-semibold text-slate-400 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleInject}
              disabled={loading}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-rose-500 to-amber-500 hover:from-rose-600 hover:to-amber-600 text-slate-950 text-xs font-bold transition-all shadow-[0_0_15px_rgba(244,63,94,0.3)]"
            >
              {loading ? 'Injecting...' : 'Inject Fault Now'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
