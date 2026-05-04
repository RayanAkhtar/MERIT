import { motion, AnimatePresence } from 'framer-motion';
import { MetricAudit } from '@/types/audit';

interface WeightedAverageAuditProps {
  m: MetricAudit;
  expandedAudit: string | null;
}

const WeightedAverageAudit: React.FC<WeightedAverageAuditProps> = ({ m, expandedAudit }) => {
  if (!m.weighted_average_breakdown) return null;

  return (
    <AnimatePresence>
      {expandedAudit === `${m.name}-parent` && (
        <motion.div 
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="mt-4 pt-4 border-t border-slate-800 space-y-4"
        >
          <div className="space-y-4">
            <div className="flex justify-between items-center text-[10px] font-black text-indigo-400 uppercase tracking-widest border-b border-indigo-500/10 pb-1">
              <span>Phase 1: Active Requirement Scores</span>
            </div>
            <div className="grid grid-cols-1 gap-2">
              {(m.weighted_average_breakdown || []).map((wa: any, waIdx: number) => (
                <div key={waIdx} className="flex justify-between items-center text-[11px] font-mono p-2 bg-indigo-500/5 rounded border border-indigo-500/10">
                  <span className="text-zinc-400">{wa.name} Score:</span>
                  <span className="text-white font-bold">{Math.round((wa.score || 0) * 100)}%</span>
                </div>
              ))}
            </div>

            <div className="flex justify-between items-center text-[10px] font-black text-indigo-400 uppercase tracking-widest border-b border-indigo-500/10 pb-1 pt-2">
              <span>Phase 2: Priority Weighting</span>
            </div>
            <div className="grid grid-cols-1 gap-1">
              {(m.weighted_average_breakdown || []).map((wa: any, waIdx: number) => (
                <div key={waIdx} className="flex justify-between items-center text-[10px] font-mono px-2 py-1 opacity-80">
                  <span className="text-zinc-500">{wa.name}:</span>
                  <span className="text-indigo-300 italic">{(wa.score || 0).toFixed(2)} * {(wa.weight || 1).toFixed(1)} = {((wa.score || 0) * (wa.weight || 1)).toFixed(2)}</span>
                </div>
              ))}
            </div>

            <div className="flex justify-between items-center text-[10px] font-black text-indigo-400 uppercase tracking-widest border-b border-indigo-500/10 pb-1 pt-2">
              <span>Phase 3: Global Aggregation</span>
            </div>
            <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-center space-y-2">
               <div className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest font-bold">Sum(Weighted Scores) / Sum(Weights)</div>
                <div className="text-sm font-mono text-white font-black">
                  {(m.weighted_sum || 0).toFixed(2)} / {(m.total_weight || 1).toFixed(1)} = <span className="underline decoration-indigo-500">{Math.round((m.score || 0) * 100)}%</span>
                </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default WeightedAverageAudit;
