import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: string;
  variant?: 'cyan' | 'emerald' | 'amber' | 'rose' | 'blue';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = 'cyan'
}) => {
  const variantStyles = {
    cyan: 'border-cyan-500/20 text-cyan-400 bg-cyan-500/5',
    emerald: 'border-emerald-500/20 text-emerald-400 bg-emerald-500/5',
    amber: 'border-amber-500/20 text-amber-400 bg-amber-500/5',
    rose: 'border-rose-500/20 text-rose-400 bg-rose-500/5',
    blue: 'border-blue-500/20 text-blue-400 bg-blue-500/5',
  };

  return (
    <div className="bg-[#142038] border border-[#233659] rounded-2xl p-5 hover:border-[#2C4472] transition-all">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</span>
        <div className={`w-9 h-9 rounded-xl border flex items-center justify-center ${variantStyles[variant]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="flex items-baseline space-x-2">
        <div className="text-2xl font-bold tracking-tight text-white">{value}</div>
        {trend && (
          <span className="text-xs font-semibold text-emerald-400">
            {trend}
          </span>
        )}
      </div>
      {subtitle && <div className="text-xs text-slate-400 mt-1">{subtitle}</div>}
    </div>
  );
};
