import React from 'react';

interface TemporalDecayAuditProps {
  item: any;
}

const TemporalDecayAudit: React.FC<TemporalDecayAuditProps> = ({ item }) => {
  if (!item.temporal_formula) return null;

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center text-[10px] font-black text-indigo-400/80 uppercase tracking-widest border-b border-indigo-500/10 pb-1">
        <span>Phase 0: Temporal Decay Analysis</span>
      </div>
      <div className="p-4 rounded-xl bg-gradient-to-br from-indigo-500/10 to-transparent border border-indigo-500/20 shadow-inner space-y-3">
        <div className="flex flex-col items-center py-3 bg-black/20 rounded-lg border border-white/5">
          <div className="text-lg font-serif text-indigo-100 italic tracking-wide">
            S<sub className="text-[10px] not-italic opacity-60">decay</sub> = S<sub className="text-[10px] not-italic opacity-60">base</sub> · e<sup className="text-xs not-italic">-λΔt</sup>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="flex flex-col p-2 bg-indigo-500/5 rounded border border-indigo-500/10">
            <span className="text-[9px] uppercase text-zinc-500 font-bold mb-1">Decay Constant (λ)</span>
            <span className="text-xs font-mono text-indigo-300">{item.temporal_params?.lambda}</span>
          </div>
          <div className="flex flex-col p-2 bg-indigo-500/5 rounded border border-indigo-500/10">
            <span className="text-[9px] uppercase text-zinc-500 font-bold mb-1">Temporal Delta (Δt)</span>
            <span className="text-xs font-mono text-indigo-300">{item.temporal_params?.delta_t} years</span>
          </div>
        </div>
        <div className="pt-2 border-t border-indigo-500/10 flex justify-between items-center bg-white/5 px-2 py-1 rounded">
          <span className="text-[10px] text-zinc-500 font-mono uppercase font-bold">Substitution:</span>
          <span className="text-sm font-mono text-indigo-300">
            e<sup>-{item.temporal_params?.lambda}·{item.temporal_params?.delta_t}</sup> = <span className="text-white font-black underline decoration-indigo-500/50">{(item.temporal_params?.weight || 0).toFixed(2)}</span>
          </span>
        </div>
        <p className="text-[10px] text-zinc-400 leading-relaxed text-center px-2">
          Skills stay fresh (1.0) if used recently. This multiplier drops as the "center" of your activity moves further into the past.
        </p>
      </div>
    </div>
  );
};

export default TemporalDecayAudit;
