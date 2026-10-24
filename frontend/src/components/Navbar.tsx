import React from 'react';
import { ShieldCheck, Activity, User as UserIcon, LogOut, Terminal, Zap } from 'lucide-react';
import { User } from '../types';

interface NavbarProps {
  user: User | null;
  onOpenAuth: () => void;
  onLogout: () => void;
  isWsConnected: boolean;
  autoRecoveryEnabled: boolean;
  onToggleAutoRecovery: () => void;
  onOpenSimulation: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  user,
  onOpenAuth,
  onLogout,
  isWsConnected,
  autoRecoveryEnabled,
  onToggleAutoRecovery,
  onOpenSimulation,
}) => {
  return (
    <header className="h-16 bg-[#0B1222] border-b border-[#1B2945] px-6 flex items-center justify-between z-30 sticky top-0">
      {/* Brand & Identity */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold tracking-tight text-white">Self-Healing Cloud</h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              Autonomic v1.0
            </span>
          </div>
          <p className="text-xs text-slate-400">AI-Powered Continuous Incident Detection & Auto-Remediation</p>
        </div>
      </div>

      {/* Control Actions & User Session */}
      <div className="flex items-center space-x-4">
        {/* Real-Time WebSocket Telemetry Pill */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-[#142038] border border-[#233659] text-xs">
          <span className={`w-2 h-2 rounded-full ${isWsConnected ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]' : 'bg-amber-400'}`} />
          <span className="text-slate-300 font-medium">{isWsConnected ? 'Telemetry Live' : 'Connecting...'}</span>
        </div>

        {/* Global Auto-Recovery Toggle Button */}
        <button
          onClick={onToggleAutoRecovery}
          title="Toggle Global Autonomous Remediation"
          className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
            autoRecoveryEnabled
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20'
              : 'bg-amber-500/10 text-amber-400 border-amber-500/30 hover:bg-amber-500/20'
          }`}
        >
          <Zap className="w-3.5 h-3.5" />
          <span>{autoRecoveryEnabled ? 'Auto-Healing: Active' : 'Auto-Healing: Paused'}</span>
        </button>

        {/* Fault Injection Button */}
        <button
          onClick={onOpenSimulation}
          className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-semibold transition-all shadow-[0_0_15px_rgba(6,182,212,0.15)]"
        >
          <Terminal className="w-3.5 h-3.5" />
          <span>Simulate Failure</span>
        </button>

        {/* User Account Controls */}
        {user ? (
          <div className="flex items-center space-x-3 pl-3 border-l border-[#1B2945]">
            <div className="text-right">
              <div className="text-xs font-semibold text-slate-200">{user.username}</div>
              <div className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider">{user.role}</div>
            </div>
            <button
              onClick={onLogout}
              title="Sign Out"
              className="w-8 h-8 rounded-lg bg-[#142038] hover:bg-[#1B2B4A] border border-[#233659] text-slate-400 hover:text-rose-400 flex items-center justify-center transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <button
            onClick={onOpenAuth}
            className="flex items-center space-x-2 px-4 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs transition-colors shadow-[0_0_15px_rgba(6,182,212,0.3)]"
          >
            <UserIcon className="w-3.5 h-3.5" />
            <span>Sign In</span>
          </button>
        )}
      </div>
    </header>
  );
};
