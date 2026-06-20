import { AuditItem } from '@/types/audit';

interface TemporalDecayAuditProps {
  item: AuditItem;
  isBlindMode?: boolean;
}

const TemporalDecayAudit: React.FC<TemporalDecayAuditProps> = ({ item, isBlindMode }) => {
  if (!item.temporal_formula) return null;

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center text-sm font-black text-indigo-950 dark:text-indigo-200 uppercase tracking-[0.15em] border-b border-indigo-500/20 pb-2 mb-1">
        <span>Phase 0: Temporal Decay Analysis</span>
      </div>
      <div className="p-4 rounded-xl bg-gradient-to-br from-indigo-500/10 to-transparent border border-indigo-500/20 shadow-inner space-y-3">
        <div className="flex flex-col items-center py-3 bg-indigo-500/5 dark:bg-black/20 rounded-lg border border-indigo-500/10 dark:border-white/5">
          <div className="text-lg font-serif text-indigo-900 dark:text-indigo-100 italic tracking-wide">
            S<sub className="text-[10px] not-italic opacity-60">decay</sub> = S<sub className="text-[10px] not-italic opacity-60">base</sub> · e<sup className="text-xs not-italic">-λΔt</sup>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="flex flex-col p-2 bg-indigo-500/5 rounded border border-indigo-500/10">
            <span className="text-[11px] uppercase text-zinc-900 dark:text-zinc-300 font-bold mb-1">Decay Constant (λ)</span>
            <span className="text-sm font-mono text-indigo-950 dark:text-indigo-200">{item.temporal_params?.lambda}</span>
          </div>
          <div className="flex flex-col p-2 bg-indigo-500/5 rounded border border-indigo-500/10">
            <span className="text-[11px] uppercase text-zinc-900 dark:text-zinc-300 font-bold mb-1">Temporal Delta (Δt)</span>
            <span className="text-sm font-mono text-indigo-950 dark:text-indigo-200">{item.temporal_params?.delta_t} years</span>
          </div>
        </div>

        {item.temporal_params?.history && item.temporal_params.history.length > 0 && (
          <div className="mt-2 p-3 bg-indigo-500/5 dark:bg-black/20 rounded border border-indigo-500/10 dark:border-white/5 space-y-2">
            <div className="text-[11px] uppercase text-black dark:text-zinc-300 font-bold tracking-widest border-b border-indigo-500/10 dark:border-white/5 pb-1.5 mb-1.5">Δt Derivation (Volume Weighted)</div>
            <div className="space-y-1">
              {item.temporal_params.history.map((h: any, i: number) => (
                <div key={i} className="flex justify-between items-center text-xs font-mono text-zinc-900 dark:text-zinc-300">
                  <span>{h.year} Volume:</span>
                  <span className="text-indigo-950 dark:text-indigo-200">{h.volume} LOC</span>
                </div>
              ))}
            </div>
            <div className="border-t border-indigo-500/10 dark:border-white/5 pt-2 mt-2 pb-1 mb-1 text-xs font-mono text-black dark:text-zinc-300 flex flex-col gap-1 italic">
               <div className="flex justify-between items-center">
                 <span>Σ(Year × Vol) / Σ(Vol):</span>
                 <span>
                    {item.temporal_params.history.reduce((acc: number, h: any) => acc + (h.year * h.volume), 0).toLocaleString()} / {item.temporal_params.history.reduce((acc: number, h: any) => acc + h.volume, 0).toLocaleString()}
                 </span>
               </div>
            </div>
            <div className="border-t border-indigo-500/10 dark:border-white/5 pt-1.5 mt-1 text-xs font-mono text-black dark:text-zinc-300 flex flex-col gap-1.5">
              <div className="flex justify-between">
                <span>Effective Year (Weighted):</span>
                <span className="text-indigo-950 dark:text-indigo-200">{item.temporal_params.effective_year}</span>
              </div>
              <div className="flex justify-between">
                <span>Current Year:</span>
                <span className="text-indigo-950 dark:text-indigo-200">{item.temporal_params.current_year}</span>
              </div>
              <div className="flex justify-between font-bold mt-1">
                <span>Δt ({item.temporal_params.current_year} - {item.temporal_params.effective_year}):</span>
                <span className="text-indigo-950 dark:text-indigo-200">{item.temporal_params.delta_t} years</span>
              </div>
            </div>
          </div>
        )}
        <div className="pt-2 border-t border-indigo-500/10 flex justify-between items-center bg-indigo-500/5 dark:bg-white/5 px-2 py-1 rounded">
          <span className="text-xs text-black dark:text-zinc-300 font-mono uppercase font-bold">Substitution:</span>
          <span className="text-base font-mono text-indigo-950 dark:text-indigo-200">
            e<sup>-{item.temporal_params?.lambda || 0}·{item.temporal_params?.delta_t || 0}</sup> = <span className="text-zinc-900 dark:text-white font-black underline decoration-indigo-500/50">{(item.temporal_params?.weight || 0).toFixed(2)}</span>
          </span>
        </div>
        <p className="text-xs text-zinc-900 dark:text-zinc-300 leading-relaxed text-center px-2">
          Skills stay fresh (1.0) if used recently. This multiplier drops as the "center" of your activity moves further into the past.
        </p>
      </div>
    </div>
  );
};

export default TemporalDecayAudit;
