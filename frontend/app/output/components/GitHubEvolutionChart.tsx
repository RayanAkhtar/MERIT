'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface GitHubEvolutionChartProps {
  history: any[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const sortedData = [...payload]
      .filter((p: any) => p.value > 0)
      .sort((a: any, b: any) => b.value - a.value)
      .slice(0, 10);

    if (sortedData.length === 0) return null;

    return (
      <div className="bg-white/95 dark:bg-zinc-900/95 p-4 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-2xl backdrop-blur-md min-w-[160px] ring-1 ring-black/5">
        <p className="text-[10px] font-black mb-3 text-zinc-400 uppercase tracking-widest border-b border-zinc-100 dark:border-zinc-800 pb-2">{label}</p>
        <div className="space-y-2">
          {sortedData.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-6">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full shadow-sm" style={{ backgroundColor: entry.color }} />
                <span className="text-[10px] font-black text-zinc-700 dark:text-zinc-300">{entry.name}</span>
              </div>
              <span className="text-[10px] font-mono font-bold text-indigo-600 dark:text-indigo-400">
                {entry.value >= 1000 ? `${(entry.value / 1000).toFixed(1)}k` : entry.value}
              </span>
            </div>
          ))}
          {payload.length > 10 && (
            <div className="pt-1 text-[8px] text-zinc-400 italic text-center border-t border-zinc-100 dark:border-zinc-800 mt-2">
              + {payload.length - 10} other languages
            </div>
          )}
        </div>
      </div>
    );
  }
  return null;
};

export default function GitHubEvolutionChart({ history }: GitHubEvolutionChartProps) {
  if (!history || history.length === 0) return null;

  const languages = Object.keys(history[0]).filter(k => k !== 'year');
  const colors = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#a855f7', '#06b6d4', '#64748b', '#f97316'];

  return (
    <div className="p-8 bg-white dark:bg-[#09090b] border border-zinc-200 dark:border-zinc-800 rounded-3xl shadow-xl space-y-8">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-400">Language Evolution</h4>
          <p className="text-[11px] font-bold text-zinc-500">Temporal progression of verified code volume</p>
        </div>
        <div className="px-3 py-1 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-100 dark:border-indigo-800">
          <span className="text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest">
            {history[0].year} — {history[history.length - 1].year}
          </span>
        </div>
      </div>
      <div className="h-[320px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis dataKey="year" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} dy={10} />
            <YAxis 
              stroke="#94a3b8" 
              fontSize={9} 
              tickLine={false} 
              axisLine={false} 
              tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(1)}k` : v} 
            />
            <Tooltip 
              content={<CustomTooltip />}
              wrapperStyle={{ zIndex: 100 }}
              cursor={{ stroke: '#6366f1', strokeWidth: 1, strokeDasharray: '4 4' }}
            />
            <Legend 
              iconType="circle" 
              wrapperStyle={{ fontSize: '9px', fontWeight: 'bold', paddingTop: '30px' }} 
            />
            {languages.map((lang, idx) => (
              <Line 
                key={lang} 
                type="monotone" 
                dataKey={lang} 
                stroke={colors[idx % colors.length]} 
                strokeWidth={3} 
                dot={{ r: 4 }} 
                activeDot={{ r: 6 }} 
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
