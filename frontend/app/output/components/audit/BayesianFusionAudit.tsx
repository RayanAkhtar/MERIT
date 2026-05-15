import { AuditItem } from '@/types/audit';

interface BayesianFusionAuditProps {
  item: AuditItem;
  isBlindMode?: boolean;
}

const BayesianFusionAudit: React.FC<BayesianFusionAuditProps> = ({ item, isBlindMode }) => {
  if (item.alpha === undefined) return null;

  return (
    <div className="space-y-2">
      <div className="pt-2 space-y-2">
        
        <div className="flex justify-between items-center text-xs font-black text-indigo-300 uppercase tracking-[0.15em] border-b border-indigo-500/20 pb-2 mb-1">
          <span>Phase 2: Bayesian Evidence Fusion</span>
        </div>

        <div className="flex justify-between items-center text-[11px] font-mono py-2.5 bg-indigo-500/10 px-3 rounded-lg border border-indigo-500/20 mb-4">
          <span className="text-zinc-400 font-bold uppercase tracking-wider">Starting Prior (Uniform)</span>
          <span className="text-indigo-300 font-black">α=0.10, β=0.10</span>
        </div>
      </div>
      
      <div className="space-y-4">
        {(item.source_details || []).map((sd: any, idx: number) => {
          const trust = sd.trust || 0.5;
          const strength = sd.score || 0;
          const isNeg = strength < 0;
          const absStrength = Math.abs(strength);
          
          const alphaInc = !isNeg ? (absStrength * trust) : (1 - trust) * 0.05;
          const betaInc = !isNeg ? (1 - absStrength) * trust : (absStrength * trust);

          return (
            <div key={`p2-${idx}`} className="flex justify-between items-center py-4 border-b border-white/5 ml-2 border-l-2 border-indigo-500/30 pl-4 bg-white/[0.02] rounded-r-xl">
              <div className="flex flex-col gap-2">
                <span className="text-sm font-black text-white tracking-tight">{sd.source} Aggregation</span>
                <div className="flex flex-col gap-1">
                  <span className="text-[11px] text-zinc-400 font-mono leading-none">
                    Δα = {absStrength.toFixed(2)} (Str) × {trust.toFixed(2)} (Tr) = <span className="text-indigo-300 font-bold">{alphaInc.toFixed(2)}</span>
                  </span>
                  <span className="text-[11px] text-zinc-400 font-mono leading-none">
                    Δβ = (1.0 - {absStrength.toFixed(2)}) × {trust.toFixed(2)} = <span className="text-indigo-300 font-bold">{betaInc.toFixed(2)}</span>
                  </span>
                </div>
              </div>
              <div className="text-right flex flex-col gap-1 pr-2">
                {alphaInc > 0 && <span className="text-xs font-black text-emerald-400 uppercase tracking-tighter">+α({alphaInc.toFixed(2)})</span>}
                {betaInc > 0 && <span className="text-xs font-black text-rose-400 uppercase tracking-tighter">+β({betaInc.toFixed(2)})</span>}
              </div>
            </div>
          );
        })}

        {/* Shapley Values */}
        {item.impact_attribution && Object.keys(item.impact_attribution).length > 0 && (
          <div className="pt-4 space-y-3 px-1">
            <div className="flex justify-between items-center text-xs font-black text-indigo-300 uppercase tracking-[0.15em] border-b border-indigo-500/20 pb-2 mb-1">
              <span>Final Attribution: Source Impact</span>
            </div>
            <div className="space-y-2">
              {(Object.entries(item.impact_attribution || {}) as [string, number][])
                .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
                .map(([src, val], idx) => {
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-[10px] font-mono px-1">
                      <span className="text-zinc-400">{src}</span>
                      <span className={`${val >= 0 ? 'text-emerald-400' : 'text-rose-400'} font-bold`}>
                        {val >= 0 ? '+' : ''}{(val * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${val >= 0 ? 'bg-emerald-500/50' : 'bg-rose-500/50'}`} 
                        style={{ width: `${Math.min(100, Math.abs(val * 100))}%` }}
                      />
                    </div>
                  </div>
                );
              })}
              <p className="text-[9px] text-zinc-500 italic mt-2">
                * Calculated via Shapley Values (Cooperative Game Theory) to isolate marginal contribution per source.
              </p>
            </div>
          </div>
        )}
        <div className="pt-2 flex justify-between items-center bg-white/5 px-2 py-1.5 rounded border border-white/5">
          <div className="text-xs font-bold text-zinc-500 uppercase tracking-tight">Final Aggregated State:</div>
          <div className="text-sm font-mono font-bold text-white bg-indigo-500/30 px-2 py-0.5 rounded border border-indigo-500/20">
            α={item.alpha?.toFixed(2)}, β={item.beta?.toFixed(2)}
          </div>
        </div>

        {item.confidence_label && (
          <div className="pt-4 space-y-3">
            <div className="flex justify-between items-center text-xs font-black text-indigo-300 uppercase tracking-[0.15em] border-b border-indigo-500/20 pb-2 mb-1">
              <span>Phase 3: Confidence Audit</span>
            </div>
            <div className="p-4 rounded-xl bg-indigo-500/5 border border-indigo-500/10 space-y-3 shadow-inner">
              <div className="flex flex-col items-center py-2 bg-black/20 rounded-lg border border-white/5">
                <div className="text-[10px] font-mono text-indigo-400 mb-1 uppercase tracking-widest font-bold">Uncertainty Calculation (σ)</div>
                <div className="text-xs font-mono text-zinc-300">
                  σ = √[ (α·β) / ((α+β)² · (α+β+1)) ] = <span className="text-white font-black underline decoration-indigo-500/50">{(item.uncertainty || 0).toFixed(3)}</span>
                </div>
              </div>
              <div className="flex gap-2 items-center p-2 rounded bg-white/5 border border-white/5">
                <div className={`w-2 h-2 rounded-full animate-pulse ${item.confidence_label === 'High Confidence' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : item.confidence_label === 'Medium Confidence' ? 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]' : 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]'}`} />
                <div className="flex-1">
                  <div className="text-[10px] font-black uppercase text-white leading-none mb-1 tracking-tight">{item.confidence_label}</div>
                  <p className="text-[10px] text-zinc-400 italic leading-tight">
                    {item.confidence_reason || "Calculated based on standard deviation of fused evidence."}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {item.influence !== undefined && (
          <div className="pt-4 space-y-3">
            <div className="flex justify-between items-center text-xs font-black text-indigo-300 uppercase tracking-[0.15em] border-b border-indigo-500/20 pb-2 mb-1">
              <span>Phase 4: Weighted Contribution</span>
            </div>
            <div className="p-4 rounded-xl bg-indigo-500/5 border border-indigo-500/10 space-y-3 shadow-inner text-center">
               <div className="text-[10px] font-mono text-indigo-400 mb-1 uppercase tracking-widest font-bold">Contribution Calculation</div>
               <div className="text-sm font-mono text-zinc-300">
                 {item.score.toFixed(2)} (Score) × {item.influence.toFixed(1)} (Influence) = <span className="text-white font-black underline decoration-indigo-500/50">{(item.score * item.influence).toFixed(2)}</span>
               </div>
               <p className="text-[9px] text-zinc-500 italic">
                 This value is then summed with other active requirements to find the final alignment average.
               </p>
            </div>
          </div>
        )}

        <div className="p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-[10px] font-mono text-indigo-200">
          <div className="flex justify-between mb-1 opacity-60">
            <span>Score Formula:</span>
            <span>α / (α + β)</span>
          </div>
          <div className="flex justify-between font-bold text-indigo-100">
            <span>Calculation:</span>
            <span>{item.alpha?.toFixed(2)} / {((item.alpha || 0) + (item.beta || 0)).toFixed(2)} = <span className="text-white text-xs">{((item.score || 0) * 100).toFixed(0)}%</span></span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BayesianFusionAudit;
