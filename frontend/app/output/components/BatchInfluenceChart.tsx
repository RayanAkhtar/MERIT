'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface BatchInfluenceChartProps {
  data: {
    CV: number;
    GitHub: number;
    LinkedIn: number;
  };
}

export default function BatchInfluenceChart({ data }: BatchInfluenceChartProps) {
  const chartData = [
    { name: 'CV Evidence', value: data.CV, color: '#6366f1' },
    { name: 'GitHub Verification', value: data.GitHub, color: '#10b981' },
    { name: 'LinkedIn Presence', value: data.LinkedIn, color: '#f59e0b' }
  ].filter(d => d.value > 0);

  const total = chartData.reduce((acc, curr) => acc + curr.value, 0);

  return (
    <div className="flex flex-col sm:flex-row items-center gap-6 p-4 bg-zinc-50 dark:bg-zinc-800/40 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-inner group transition-all hover:bg-white dark:hover:bg-zinc-800 transition-colors">
      <div className="h-[120px] w-[120px] shrink-0 relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={35}
              outerRadius={50}
              paddingAngle={4}
              dataKey="value"
              stroke="none"
              animationDuration={1500}
              animationBegin={200}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} className="opacity-80 hover:opacity-100 transition-opacity" />
              ))}
            </Pie>
            <Tooltip 
              wrapperStyle={{ zIndex: 100 }}
              content={({ active, payload }: any) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="bg-zinc-900 text-white text-[10px] px-2 py-1 rounded shadow-xl font-bold uppercase tracking-widest border border-white/10 relative z-[110]">
                      {d.name}: {((d.value / total) * 100).toFixed(1)}%
                    </div>
                  );
                }
                return null;
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
          <div className="text-[10px] font-black text-zinc-400 uppercase tracking-widest opacity-40">XAI</div>
        </div>
      </div>

      <div className="space-y-3 flex-1 min-w-[180px]">
        <div className="space-y-1">
          <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500">Batch Source Influence</h4>
          <p className="text-[11px] font-bold text-zinc-400 leading-tight">Marginal contribution averaged across {chartData.length} sources</p>
        </div>
        
        <div className="space-y-2">
          {chartData.sort((a, b) => b.value - a.value).map((item) => (
            <div key={item.name} className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-[10px] font-black text-zinc-600 dark:text-zinc-300 uppercase tracking-tight">{item.name}</span>
              </div>
              <span className="text-[11px] font-mono font-bold text-zinc-900 dark:text-zinc-100">
                {((item.value / total) * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
