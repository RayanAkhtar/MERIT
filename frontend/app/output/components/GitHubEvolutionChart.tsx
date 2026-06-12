'use client';

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface GitHubEvolutionChartProps {
  history: any[];
  priorityLanguages?: string[];
}

const baseLanguageColors: Record<string, string> = {
  'TypeScript': '#818cf8',
  'JavaScript': '#34d399',
  'Python': '#fbbf24',
  'TeX': '#f472b6',
  'Rust': '#c084fc',
  'Go': '#38bdf8',
  'Shell': '#fb923c',
  'HTML': '#60a5fa',
  'CSS': '#f87171',
  'C++': '#22d3ee',
  'SQL': '#a78bfa',
  'C#': '#fb7185',
  'Ruby': '#f43f5e',
  'Java': '#ef4444',
  'PHP': '#818cf8',
  'C': '#94a3b8',
  'Jupyter Notebook': '#fbbf24'
};

const getLangColor = (lang: string) => {
  const matchedKey = Object.keys(baseLanguageColors).find(
      k => k.toLowerCase() === lang.toLowerCase()
  );
  if (matchedKey) return baseLanguageColors[matchedKey];
  
  let hash = 0;
  for (let i = 0; i < lang.length; i++) {
      hash = lang.charCodeAt(i) + ((hash << 5) - hash);
  }
  const c = (hash & 0x00FFFFFF).toString(16).toUpperCase();
  return '#' + '00000'.substring(0, 6 - c.length) + c;
};

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
                <span className="text-[10px] font-black text-zinc-700 dark:text-zinc-300 uppercase tracking-widest">{entry.name}</span>
              </div>
              <span className="text-[10px] font-mono font-bold text-indigo-600 dark:text-indigo-400">
                {entry.value >= 1000 ? `${(entry.value / 1000).toFixed(1)}k` : entry.value} LINES
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

export default function GitHubEvolutionChart({ history, priorityLanguages }: GitHubEvolutionChartProps) {
  const [hiddenLangs, setHiddenLangs] = React.useState<Set<string>>(new Set());

  const languages = React.useMemo(() => {
    if (!history || history.length === 0) return [];
    
    const volumeMap: Record<string, number> = {};
    history.forEach(entry => {
      Object.keys(entry).forEach(k => {
        if (k !== 'year') {
          volumeMap[k] = (volumeMap[k] || 0) + Number(entry[k] || 0);
        }
      });
    });

    const prioritySet = new Set((priorityLanguages || []).map(l => l.toLowerCase()));
    const allLangs = Object.keys(volumeMap);
    
    // Sort all languages by volume descending
    allLangs.sort((a, b) => volumeMap[b] - volumeMap[a]);

    const baseTop7 = allLangs.slice(0, 7);
    const finalSet = new Set(baseTop7);
    
    // Ensure all priority languages are included if they exist in history
    allLangs.forEach(lang => {
      if (prioritySet.has(lang.toLowerCase())) {
        finalSet.add(lang);
      }
    });

    // Render priority languages last so they draw on top (highest z-index in Recharts)
    return Array.from(finalSet).sort((a, b) => {
        const aP = prioritySet.has(a.toLowerCase());
        const bP = prioritySet.has(b.toLowerCase());
        if (aP && !bP) return 1;
        if (!aP && bP) return -1;
        // Keep relative volume order otherwise
        return volumeMap[b] - volumeMap[a];
    });
  }, [history, priorityLanguages]);

  // Years extraction and mapping
  const availableYears = React.useMemo(() => {
    if (!history) return [];
    return history.map(entry => entry.year).sort((a,b) => parseInt(a) - parseInt(b));
  }, [history]);

  const [minYearIdx, setMinYearIdx] = React.useState(0);
  const [maxYearIdx, setMaxYearIdx] = React.useState(0);
  const [lastActive, setLastActive] = React.useState<'min' | 'max'>('min');

  React.useEffect(() => {
    if (availableYears.length > 0) {
      setMinYearIdx(0);
      setMaxYearIdx(availableYears.length - 1);
    }
  }, [availableYears]);

  const filteredHistory = React.useMemo(() => {
    if (!history || availableYears.length === 0) return [];
    const minYear = availableYears[minYearIdx];
    const maxYear = availableYears[maxYearIdx];
    return history.filter(e => e.year >= minYear && e.year <= maxYear);
  }, [history, availableYears, minYearIdx, maxYearIdx]);

  const handleLegendClick = (o: any) => {
    const { dataKey } = o;
    setHiddenLangs((prev) => {
        const next = new Set(prev);
        if (next.has(dataKey)) {
            next.delete(dataKey);
        } else {
            next.add(dataKey);
        }
        return next;
    });
  };

  if (!history || history.length === 0) return null;

  return (
    <div className="p-8 bg-white dark:bg-[#09090b] border border-zinc-200 dark:border-zinc-800 rounded-3xl shadow-xl space-y-8">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-400">Language Evolution</h4>
          <p className="text-[11px] font-bold text-zinc-500">Temporal progression of verified code volume</p>
        </div>
      </div>
      
      {/* Time Range and Slider */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 p-6 rounded-2xl bg-zinc-50 dark:bg-zinc-900/30 border border-zinc-100 dark:border-zinc-800 shadow-inner">
          <div className="space-y-2">
              <span className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-400 dark:text-zinc-600">Time Range</span>
              <div className="flex items-center gap-4 text-zinc-900 dark:text-white font-black tracking-tighter text-2xl">
                  <span className="px-3 py-1.5 rounded-lg bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-indigo-600 dark:text-indigo-400">
                      {availableYears[minYearIdx] || '...'}
                  </span>
                  <span className="text-zinc-300 dark:text-zinc-700 opacity-50">—</span>
                  <span className="px-3 py-1.5 rounded-lg bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-indigo-600 dark:text-indigo-400">
                      {availableYears[maxYearIdx] || '...'}
                  </span>
              </div>
          </div>

          <div className="flex-1 max-w-md">
              <div className="space-y-4">
                  <div className="flex justify-between text-[9px] font-black text-zinc-400 dark:text-zinc-600 uppercase tracking-widest">
                      <span>Early History</span>
                      <span>Present Day</span>
                  </div>
                  <div className="relative h-2 bg-zinc-200 dark:bg-zinc-950 rounded-full flex items-center">
                      <style>{`
                          .range-slider-input::-webkit-slider-runnable-track { pointer-events: none; background: none; border: none; }
                          .range-slider-input::-webkit-slider-thumb { pointer-events: auto; }
                          .range-slider-input::-moz-range-track { pointer-events: none; background: none; border: none; }
                          .range-slider-input::-moz-range-thumb { pointer-events: auto; }
                      `}</style>
                      <div 
                          className="absolute h-full bg-indigo-500/20 dark:bg-indigo-500/30 rounded-full"
                          style={{ 
                              left: availableYears.length > 1 ? `${(minYearIdx / (availableYears.length - 1)) * 100}%` : '0%',
                              right: availableYears.length > 1 ? `${100 - (maxYearIdx / (availableYears.length - 1)) * 100}%` : '0%'
                          }}
                      />
                      <input 
                          type="range"
                          min={0}
                          max={Math.max(0, availableYears.length - 1)}
                          value={minYearIdx}
                          onMouseDown={() => setLastActive('min')}
                          onChange={(e) => setMinYearIdx(Math.min(parseInt(e.target.value), maxYearIdx))}
                          className={`range-slider-input absolute w-full appearance-none bg-transparent cursor-pointer h-1 accent-indigo-600 dark:accent-indigo-500 pointer-events-none ${lastActive === 'min' ? 'z-30' : 'z-20'}`}
                      />
                      <input 
                          type="range"
                          min={0}
                          max={Math.max(0, availableYears.length - 1)}
                          value={maxYearIdx}
                          onMouseDown={() => setLastActive('max')}
                          onChange={(e) => setMaxYearIdx(Math.max(parseInt(e.target.value), minYearIdx))}
                          className={`range-slider-input absolute w-full appearance-none bg-transparent cursor-pointer h-1 accent-indigo-600 dark:accent-indigo-500 pointer-events-none ${lastActive === 'max' ? 'z-30' : 'z-20'}`}
                      />
                  </div>
                  <p className="text-[8px] font-bold text-zinc-400 dark:text-zinc-500 italic text-center uppercase tracking-widest">
                      Drag handles to adjust analytical window
                  </p>
              </div>
          </div>
      </div>

      <div className="h-[400px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={filteredHistory} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis dataKey="year" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} dy={10} tick={{ fontWeight: 800, letterSpacing: '0.1em' }} />
            <YAxis 
              stroke="#94a3b8" 
              fontSize={9} 
              tickLine={false} 
              axisLine={false} 
              tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(1)}k` : v} 
              tick={{ fontWeight: 800 }}
            />
            <Tooltip 
              content={<CustomTooltip />}
              wrapperStyle={{ zIndex: 100 }}
              cursor={{ stroke: '#6366f1', strokeWidth: 1, strokeDasharray: '4 4' }}
            />
            <Legend 
                verticalAlign="top" 
                align="right" 
                iconSize={0}
                onClick={handleLegendClick}
                formatter={(value, entry: any) => {
                    const color = getLangColor(entry.dataKey);
                    const isHidden = hiddenLangs.has(entry.dataKey);
                    return (
                        <span className={`
                            inline-flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all duration-300 mx-1 mb-2
                            ${isHidden 
                                ? 'bg-zinc-100 dark:bg-zinc-900/20 border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-600 opacity-40 grayscale line-through' 
                                : 'bg-white dark:bg-zinc-900/80 border-zinc-200 dark:border-zinc-800 text-zinc-900 dark:text-zinc-300 hover:border-zinc-400 dark:hover:border-zinc-500 hover:scale-105 active:scale-95 shadow-lg dark:shadow-xl'}
                        `}>
                            <span className="w-1.5 h-1.5 rounded-full shadow-[0_0_8px_currentColor]" style={{ backgroundColor: color, color: color }} />
                            <span className="font-black tracking-widest uppercase text-[8px]">{value}</span>
                        </span>
                    );
                }}
                wrapperStyle={{ 
                    paddingBottom: '40px',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'flex-end',
                    flexWrap: 'wrap'
                }}
            />
            {languages.map((lang, idx) => (
              <Line 
                key={lang} 
                type="monotone" 
                dataKey={lang} 
                stroke={getLangColor(lang)} 
                strokeWidth={3} 
                dot={{ r: 4, strokeWidth: 2, fill: 'var(--tw-backgroundColor-white)' }} 
                activeDot={{ r: 6, strokeWidth: 0, fill: getLangColor(lang) }} 
                hide={hiddenLangs.has(lang)}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
