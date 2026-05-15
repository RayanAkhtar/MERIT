import { MetricAudit, StuffingAudit } from '@/types/audit';

interface ScoringAuditProps {
  candidate: any;
  onMetricClick?: (key: string) => void;
  isBlindMode?: boolean;
}

export default function ScoringAudit({ candidate, onMetricClick, isBlindMode }: ScoringAuditProps) {
  console.log("DEBUG [ScoringAudit]: calculation_summary ->", candidate.calculation_summary);
  const sortedMetrics = (Object.entries(candidate.fullMetrics || {}) as [string, MetricAudit][])
    .sort(([, a], [, b]) => {
      if (a.score === 0 && (b.score || 0) !== 0) return 1;
      if ((a.score || 0) !== 0 && b.score === 0) return -1;
      return 0;
    });

  return (
    <div className="space-y-8 animate-in slide-in-from-right-4 duration-300 max-w-3xl mx-auto pb-12">
      {/* Identity Integrity Audit */}
      {candidate.calculation_summary?.identity_audit_details && (
        <div className={`p-8 rounded-2xl border-2 shadow-xl relative overflow-hidden group/identity animate-in zoom-in-95 duration-500 ${
          candidate.calculation_summary.identity_penalty > 0 
            ? 'bg-indigo-500/5 border-indigo-500/20' 
            : 'bg-emerald-500/5 border-emerald-500/10 mb-8'
        }`}>
          <div className={`absolute -top-12 -right-12 w-32 h-32 rounded-full blur-3xl transition-all duration-700 ${
            candidate.calculation_summary.identity_penalty > 0 ? 'bg-indigo-500/10' : 'bg-emerald-500/10'
          }`} />
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-xl border ${
              candidate.calculation_summary.identity_penalty > 0 
                ? 'bg-indigo-500/20 border-indigo-500/30' 
                : 'bg-emerald-500/20 border-emerald-500/30'
            }`}>
              <svg className={`w-6 h-6 ${candidate.calculation_summary.identity_penalty > 0 ? 'text-indigo-500' : 'text-emerald-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <h4 className={`text-[10px] font-black uppercase tracking-[0.2em] ${candidate.calculation_summary.identity_penalty > 0 ? 'text-indigo-500' : 'text-emerald-500'}`}>
                    Squatter Integrity Audit: {candidate.calculation_summary.identity_penalty > 0 ? 'Mismatch Detected' : 'Verified'}
                  </h4>
                  {candidate.calculation_summary.identity_penalty > 0 && (
                    <span className="px-1.5 py-0.5 bg-rose-500 text-white text-[8px] font-black rounded uppercase tracking-widest animate-pulse">Critical Flag</span>
                  )}
                </div>
                <div className={`px-2 py-1 rounded text-[10px] font-black ${candidate.calculation_summary.identity_penalty > 0 ? 'bg-indigo-500/10 text-indigo-500' : 'bg-emerald-500/10 text-emerald-500'}`}>
                  {candidate.calculation_summary.identity_audit_details.similarity}% Match
                </div>
              </div>
              
              {candidate.calculation_summary.identity_penalty > 0 ? (
                <>
                  <p className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-6 leading-relaxed">
                    The squatter audit found a significant mismatch (Confidence: {candidate.calculation_summary.identity_audit_details.similarity}%). 
                    A "Squatter Penalty" of <span className="text-indigo-500 font-black">{(candidate.calculation_summary.identity_penalty * 100).toFixed(0)}%</span> has been applied.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                      <p className="text-[9px] font-black text-zinc-400 uppercase tracking-widest mb-1">Name on CV</p>
                      <p className="text-sm font-black text-zinc-800 dark:text-zinc-200">
                        {isBlindMode ? "Redacted (Identity Mask Active)" : (candidate.calculation_summary.identity_audit_details?.cv_name || "---")}
                      </p>
                    </div>
                    <div className="p-4 bg-indigo-500/5 rounded-xl border border-indigo-500/20 shadow-sm">
                      <p className="text-[9px] font-black text-indigo-400 uppercase tracking-widest mb-1">Social Profile Owner</p>
                      <p className="text-sm font-black text-indigo-600 dark:text-indigo-400">
                        {isBlindMode ? "Redacted (Identity Mask Active)" : (candidate.calculation_summary.identity_audit_details?.profile_name || "---")}
                      </p>
                    </div>
                  </div>
                </>
              ) : (
                <p className="text-xs font-bold text-zinc-500 dark:text-zinc-400">
                  Identity consistency confirmed. Signal from <span className="text-emerald-500 uppercase tracking-tight font-black">{isBlindMode ? "Verified Source" : candidate.calculation_summary.identity_audit_details.profile_name}</span> has been successfully linked to <span className="text-emerald-500 uppercase tracking-tight font-black">{isBlindMode ? "Candidate" : candidate.name}</span>.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Integrity Audit: Keyword Stuffing */}
      {(candidate.integrity_penalty > 0 || candidate.calculation_summary?.integrity_penalty > 0) && (candidate.calculation_summary?.stuffing_audit?.length > 0) && (
        <div className="p-8 bg-amber-500/5 rounded-2xl border-2 border-amber-500/20 shadow-xl relative overflow-hidden group/penalty animate-in zoom-in-95 duration-500">
          <div className="absolute -top-12 -right-12 w-32 h-32 bg-amber-500/10 rounded-full blur-3xl group-hover/penalty:bg-amber-500/20 transition-all duration-700" />
          <div className="flex items-start gap-4">
            <div className="p-3 bg-amber-500/20 rounded-xl border border-amber-500/30">
              <svg className="w-6 h-6 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-amber-500 mb-2">Integrity Audit: Keyword Stuffing Detected</h4>
              <p className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4">
                The scoring engine detected unnatural repetition of buzzwords in the CV. 
                An integrity penalty of <span className="text-amber-500">{(candidate.calculation_summary.integrity_penalty * 100).toFixed(0)}%</span> was subtracted from the final score.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {(candidate.calculation_summary.stuffing_audit || []).map((audit: StuffingAudit, i: number) => (
                  <div key={i} className="p-2.5 bg-amber-500/5 rounded-lg border border-amber-500/10 flex justify-between items-center text-xs">
                    <span className="font-bold text-amber-600 dark:text-amber-500">{audit.term}</span>
                    <span className="text-[10px] font-black text-amber-500/80 uppercase tracking-widest">{audit.count}x / {audit.density} density</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="p-8 bg-zinc-900 rounded-2xl border border-zinc-800 shadow-2xl relative overflow-hidden">
        <h4 className="text-[10px] font-black uppercase tracking-widest text-indigo-400 mb-6">Global Scoring Algorithm</h4>
        <div className="space-y-6">
          <div className="bg-black/40 p-6 rounded-xl border border-white/5 font-mono overflow-x-auto">
            <div className="text-indigo-400 text-xs uppercase font-black mb-4 tracking-widest flex items-center gap-2">
              Contribution Sum (Final Aggregation)
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-8 text-white text-xl md:text-2xl font-light tracking-tight pb-8 border-b border-white/10">
              {sortedMetrics.map(([key, m], i, arr) => {
                const totalW = candidate.calculation_summary?.total_weight || 1;
                const weightedPoints = (m.score || 0) * (m.weight || 0);
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
                {sortedMetrics.map(([key, m], i) => {
                  const totalW = candidate.calculation_summary?.total_weight || 1;
                  const contribution = ((m.score || 0) * (m.weight || 0)) / totalW;
                  return (
                    <div key={key} className="flex justify-between items-start text-sm group/row hover:bg-white/5 p-2 rounded-lg transition-colors">
                      <span className="flex items-start gap-3 text-zinc-100 font-medium max-w-[60%]">
                        <span className="text-indigo-400 font-black text-[10px] mt-1 bg-indigo-500/10 w-6 h-6 rounded flex items-center justify-center border border-indigo-500/20 shrink-0">#{i + 1}</span>
                        <span>{m.name} contribution</span>
                      </span>
                      <span className="font-mono text-right">
                        <div className="text-zinc-400 text-xs mb-1 italic">({(m.score || 0).toFixed(2)} × {(m.weight || 0).toFixed(2)}) / {totalW.toFixed(2)}</div>
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
        {sortedMetrics.map(([key, m]) => (
          <div 
            key={key} 
            id={`formula-${key}`} 
            onClick={() => onMetricClick?.(key)}
            className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm group/formula hover:border-indigo-500 transition-all cursor-pointer hover:shadow-lg active:scale-[0.99]"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex flex-col gap-1">
                <h5 className={`font-bold flex items-center gap-2 transition-colors ${m.integrity_penalty_applied ? 'text-amber-600 dark:text-amber-500' : 'text-zinc-900 dark:text-zinc-100 group-hover/formula:text-indigo-600'}`}>
                  {m.name}
                  {m.integrity_penalty_applied && (
                    <span className="flex items-center gap-1 text-[9px] font-black text-amber-500 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20 uppercase tracking-widest animate-pulse">
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Audit Flag
                    </span>
                  )}
                </h5>
              </div>
              <div className="flex items-center gap-3 text-xs font-black">
                <span className={`px-2 py-1 rounded flex items-center gap-2 ${m.integrity_penalty_applied ? 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/30 border border-amber-500/20' : 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30'}`}>
                  Score: {(m.score * 100).toFixed(0)}%
                </span>
                <span className="text-zinc-500 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 px-2 py-1 rounded">Weight: {(m.weight || 0).toFixed(2)}</span>
              </div>
            </div>
            <div className="space-y-4">
              {m.technical_formula && m.technical_formula.includes('α') && (
                <div className="p-4 bg-zinc-50 dark:bg-black/40 rounded-xl border border-zinc-100 dark:border-zinc-800">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-[10px] font-black uppercase text-zinc-400 tracking-widest">Statistical Audit Summary</span>
                    <span className="text-[9px] text-indigo-500 font-bold uppercase">Deep Audit available in sidebar</span>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="flex flex-col">
                      <span className="text-[9px] text-zinc-500 uppercase font-bold">Signal (α)</span>
                      <span className="text-sm font-mono font-bold text-zinc-900 dark:text-zinc-100">
                        {m.technical_formula.match(/α.*?=\s*([\d.]+)/)?.[1] || '---'}
                      </span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[9px] text-zinc-500 uppercase font-bold">Uncertainty (β)</span>
                      <span className="text-sm font-mono font-bold text-zinc-900 dark:text-zinc-100">
                        {m.technical_formula.match(/β.*?=\s*([\d.]+)/)?.[1] || '---'}
                      </span>
                    </div>
                    <div className="h-8 w-px bg-zinc-200 dark:bg-zinc-800 mx-2" />
                    <div className="flex flex-col">
                      <span className="text-[9px] text-indigo-500 uppercase font-bold">Fused Result</span>
                      <span className="text-sm font-mono font-black text-indigo-600 dark:text-indigo-400">
                        {(m.score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}
              
              {m.integrity_penalty_applied && (
                <div className="p-4 bg-amber-500/5 rounded-xl border border-amber-500/20 animate-in slide-in-from-top-2 duration-500">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="p-1.5 bg-amber-500/20 rounded-md">
                      <svg className="w-3.5 h-3.5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <span className="text-[10px] font-black uppercase tracking-widest text-amber-500">Anti-Gamer Penalty Applied</span>
                  </div>
                  <p className="text-xs text-amber-600 dark:text-amber-400 font-medium leading-relaxed">
                    The <span className="font-black underline decoration-amber-500/30 italic">CV Signal Strength</span> for this metric was reduced by <span className="font-black">{((m.integrity_penalty_value || 0) * 100).toFixed(0)}%</span> because the system detected keyword stuffing tactics. 
                    The natural repetition limit for <span className="font-bold">'{m.integrity_audit_details?.term}'</span> is <span className="font-bold">{m.integrity_audit_details?.limit}x</span>, 
                    but <span className="font-bold text-amber-700 dark:text-amber-300 underline decoration-amber-500/30">{m.integrity_audit_details?.count}x</span> occurrences were found in the CV. 
                    A penalty scale of <span className="font-bold">{((m.integrity_audit_details?.penalty_per || 0) * 100).toFixed(0)}%</span> per excess occurrence was applied to ensure the match remains authentic and not gamed.
                  </p>
                </div>
              )}

              <div className="p-4 bg-zinc-50 dark:bg-black/40 rounded-xl font-mono text-xs border border-zinc-100 dark:border-zinc-800 text-zinc-600 dark:text-zinc-300 italic">Logic Variable: {m.formula}</div>
              {(m.improvements?.length || 0) > 0 && (
                <div className="p-4 bg-amber-50/50 dark:bg-amber-900/10 rounded-xl border border-amber-200/50 dark:border-amber-700/30">
                  <span className="text-[10px] font-black uppercase text-amber-600 dark:text-amber-500 block mb-3 tracking-widest">How to maximise this score</span>
                  <ul className="space-y-2">
                    {m.improvements?.filter(Boolean).map((imp: any, idx: number) => (
                      <li key={idx} className="flex gap-2 text-xs text-zinc-700 dark:text-zinc-300 font-medium leading-relaxed">
                        <span className="text-amber-500 shrink-0 mt-0.5">•</span>
                        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 w-full">
                          <span className="flex-1">{imp?.text || imp}</span>
                          {(imp.variables?.length || 0) > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1 sm:mt-0 shrink-0">
                              {(imp.variables || []).map((v: string, vIdx: number) => (
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
