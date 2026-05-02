'use client';

interface ScoringAuditProps {
  candidate: any;
}

export default function ScoringAudit({ candidate }: ScoringAuditProps) {
  const sortedMetrics = Object.entries(candidate.fullMetrics || {})
    .sort(([, a]: [string, any], [, b]: [string, any]) => {
      if (a.score === 0 && b.score !== 0) return 1;
      if (a.score !== 0 && b.score === 0) return -1;
      return 0;
    });

  return (
    <div className="space-y-8 animate-in slide-in-from-right-4 duration-300 max-w-3xl mx-auto pb-12">
      <div className="p-8 bg-zinc-900 rounded-2xl border border-zinc-800 shadow-2xl relative overflow-hidden">
        <h4 className="text-[10px] font-black uppercase tracking-widest text-indigo-400 mb-6">Global Scoring Algorithm</h4>
        <div className="space-y-6">
          <div className="bg-black/40 p-6 rounded-xl border border-white/5 font-mono overflow-x-auto">
            <div className="text-indigo-400 text-xs uppercase font-black mb-4 tracking-widest flex items-center gap-2">
              Contribution Sum (Final Aggregation)
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-8 text-white text-xl md:text-2xl font-light tracking-tight pb-8 border-b border-white/10">
              {sortedMetrics.map(([key, m]: [string, any], i, arr) => {
                const totalW = candidate.calculation_summary?.total_weight || 1;
                const weightedPoints = m.score * m.weight;
                return (
                  <div key={key} className="flex items-center gap-2 group/eq relative pt-6">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 text-[10px] font-black text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">#{i + 1}</div>
                    <div className="flex flex-col items-center">
                      <span className="text-indigo-400 font-bold border-b-2 border-white/20 pb-0.5 px-1">{weightedPoints.toFixed(2)}</span>
                      <span className="text-xs text-zinc-400 pt-1">{totalW.toFixed(2)}</span>
                    </div>
                    {i < arr.length - 1 && <span className="text-zinc-600 font-black text-lg mx-2">+</span>}
                  </div>
                );
              })}
              <span className="text-indigo-500 mx-4 font-black text-2xl">=</span>
              <div className="flex flex-col items-center justify-center px-6 py-3 rounded-2xl border-2 border-indigo-500/50 bg-indigo-500/5 relative group/result">
                <span className="font-black text-white text-4xl tracking-tighter">{(candidate.total_score * 100).toFixed(0)}%</span>
              </div>
            </div>
            <div className="mt-8 space-y-4">
              <h5 className="text-[10px] font-black uppercase text-zinc-400 tracking-widest">Detailed Manual Audit Trail</h5>
              <div className="grid grid-cols-1 gap-4">
                {sortedMetrics.map(([key, m]: [string, any], i) => {
                  const totalW = candidate.calculation_summary?.total_weight || 1;
                  const contribution = (m.score * m.weight) / totalW;
                  return (
                    <div key={key} className="flex justify-between items-start text-sm group/row hover:bg-white/5 p-2 rounded-lg transition-colors">
                      <span className="flex items-start gap-3 text-zinc-100 font-medium max-w-[60%]">
                        <span className="text-indigo-400 font-black text-[10px] mt-1 bg-indigo-500/10 w-6 h-6 rounded flex items-center justify-center border border-indigo-500/20 shrink-0">#{i + 1}</span>
                        <span>{m.name} contribution</span>
                      </span>
                      <span className="font-mono text-right">
                        <div className="text-zinc-400 text-xs mb-1 italic">({m.score.toFixed(2)} × {m.weight.toFixed(2)}) / {totalW.toFixed(2)}</div>
                        <div className="text-indigo-400 font-black text-base">= {contribution.toFixed(3)}</div>
                      </span>
                    </div>
                  );
                })}
              </div>
              <div className="pt-6 border-t border-white/10 flex justify-between items-center text-lg font-black text-white">
                Σ <span className="font-mono text-indigo-400 bg-indigo-500/10 px-4 py-2 rounded-xl border border-indigo-500/30">{candidate.total_score.toFixed(3)} ({(candidate.total_score * 100).toFixed(1)}%)</span>
              </div>
            </div>
          </div>
        </div>
        <p className="text-sm text-zinc-400 font-medium leading-relaxed italic border-l-2 border-indigo-500 pl-4 mt-6">{candidate.calculation_summary?.logic}</p>
      </div>
      <div className="space-y-4">
        {sortedMetrics.map(([key, m]: [string, any]) => (
          <div key={key} id={`formula-${key}`} className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm group/formula hover:border-indigo-500 transition-all">
            <div className="flex justify-between items-start mb-4">
              <h5 className="font-bold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">{m.name}</h5>
              <div className="flex items-center gap-3 text-xs font-black">
                <span className="text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 px-2 py-1 rounded">Score: {(m.score * 100).toFixed(0)}%</span>
                <span className="text-zinc-500 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 px-2 py-1 rounded">Weight: {m.weight.toFixed(2)}</span>
              </div>
            </div>
            <div className="space-y-4">
              {m.technical_formula && (
                <div className="p-4 bg-indigo-500/10 rounded-xl border border-indigo-500/20">
                  <span className="text-[8px] font-black uppercase text-indigo-500 block mb-1">Numerical Audit</span>
                  <div className="font-mono text-sm text-indigo-600 dark:text-indigo-400 font-bold">{m.technical_formula}</div>
                </div>
              )}
              <div className="p-4 bg-zinc-50 dark:bg-black/40 rounded-xl font-mono text-xs border border-zinc-100 dark:border-zinc-800 text-zinc-600 dark:text-zinc-300 italic">Logic Variable: {m.formula}</div>
              {m.improvements && m.improvements.length > 0 && (
                <div className="p-4 bg-amber-50/50 dark:bg-amber-900/10 rounded-xl border border-amber-200/50 dark:border-amber-700/30">
                  <span className="text-[10px] font-black uppercase text-amber-600 dark:text-amber-500 block mb-3 tracking-widest">How to maximise this score</span>
                  <ul className="space-y-2">
                    {m.improvements.filter(Boolean).map((imp: any, idx: number) => (
                      <li key={idx} className="flex gap-2 text-xs text-zinc-700 dark:text-zinc-300 font-medium leading-relaxed">
                        <span className="text-amber-500 shrink-0 mt-0.5">•</span>
                        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 w-full">
                          <span className="flex-1">{imp?.text || imp}</span>
                          {imp.variables && imp.variables.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1 sm:mt-0 shrink-0">
                              {imp.variables.map((v: string, vIdx: number) => (
                                <span key={vIdx} className="text-[9px] font-mono font-bold text-amber-700/80 dark:text-amber-500/80 bg-amber-200/50 dark:bg-amber-900/50 px-1.5 py-0.5 rounded border border-amber-300/30 dark:border-amber-700/30 uppercase tracking-wider">
                                  {v}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
