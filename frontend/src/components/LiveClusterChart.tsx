import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import { MetricSample } from '../types';

interface LiveClusterChartProps {
  samples: MetricSample[];
  title?: string;
}

export const LiveClusterChart: React.FC<LiveClusterChartProps> = ({ samples, title = "Cluster Resource Trends (Live)" }) => {
  const chartData = samples.map((s) => ({
    time: new Date(s.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    cpu: s.cpu_percent,
    memory: s.memory_percent,
    latency: s.latency_ms,
    errors: s.error_rate_percent,
  }));

  return (
    <div className="bg-[#142038] border border-[#233659] rounded-2xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-white tracking-tight">{title}</h3>
          <p className="text-xs text-slate-400">Continuous CPU and Memory utilization with latency metrics</p>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 text-cyan-400">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span>CPU (%)</span>
          </div>
          <div className="flex items-center space-x-1.5 text-blue-400">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-400"></span>
            <span>Memory (%)</span>
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="memGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F2E4D" />
            <XAxis dataKey="time" stroke="#64748B" fontSize={11} tickLine={false} />
            <YAxis stroke="#64748B" fontSize={11} domain={[0, 100]} tickLine={false} unit="%" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0F182B',
                borderColor: '#233659',
                borderRadius: '0.75rem',
                fontSize: '12px',
                color: '#F8FAFC'
              }}
            />
            <Area
              type="monotone"
              dataKey="cpu"
              name="CPU Utilization"
              stroke="#06B6D4"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#cpuGradient)"
            />
            <Area
              type="monotone"
              dataKey="memory"
              name="Memory Usage"
              stroke="#3B82F6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#memGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
