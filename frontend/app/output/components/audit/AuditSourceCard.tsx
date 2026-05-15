import { SourceDetail } from '@/types/audit';

interface AuditSourceCardProps {
  sd: SourceDetail;
  j: number;
}

const AuditSourceCard: React.FC<AuditSourceCardProps> = ({ sd, j }) => {
  const isPenalty = (sd.score || 0) < 0;
  const isBridge = sd.is_semantic_bridge;
  
  let cardStyles = 'bg-zinc-50 dark:bg-zinc-900/50 border-zinc-100 dark:border-zinc-800';
  let textStyles = 'text-indigo-500 dark:text-indigo-400';
  let label = `${sd.source} Signal`;

  if (isPenalty) {
    const isIntegrity = sd.source?.includes('INTEGRITY');
    cardStyles = isIntegrity ? 'bg-amber-500/5 border-amber-500/20' : 'bg-rose-500/5 border-rose-500/20';
    textStyles = `${isIntegrity ? 'text-amber-500' : 'text-rose-500'} flex items-center gap-1.5`;
    label = `Penalty: ${sd.source}`;
  } else if (isBridge) {
    cardStyles = 'bg-fuchsia-500/5 border-fuchsia-500/20';
    textStyles = 'text-fuchsia-600 dark:text-fuchsia-400 flex items-center gap-1.5';
    label = `Semantic Bridge: ${sd.source}`;
  }

  return (
    <div key={j} className={`p-3 rounded-lg border flex flex-col gap-1 relative group ${cardStyles}`}>
      <span className={`text-[10px] font-black uppercase tracking-widest ${textStyles}`}>
        {isPenalty && (
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )}
        {isBridge && (
          <>
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {/* Semantic Tooltip */}
            <div className="absolute bottom-full left-0 mb-3 w-64 p-4 bg-zinc-900/95 dark:bg-zinc-800/95 backdrop-blur-md text-white text-[10px] rounded-2xl opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none z-50 shadow-[0_20px_50px_rgba(0,0,0,0.5)] border border-fuchsia-500/30 leading-relaxed translate-y-2 group-hover:translate-y-0 normal-case font-medium">
              <div className="absolute -bottom-1.5 left-4 w-3 h-3 bg-zinc-900 dark:bg-zinc-800 border-r border-b border-fuchsia-500/30 rotate-45" />
              <p className="font-black text-fuchsia-400 uppercase tracking-[0.2em] text-[9px] mb-2 pb-2 border-b border-white/5">Intelligence Signal</p>
              <p className="opacity-90">
                This is a <b className="text-fuchsia-300 font-bold">Semantic Bridge</b>. The system used natural language processing to infer this skill through contextual similarity, even though the specific term was not explicitly found in this data source.
              </p>
            </div>
          </>
        )}
        {label}
      </span>
      <p className={`text-xs leading-tight italic ${isPenalty ? (sd.source?.includes('INTEGRITY') ? 'text-amber-700 dark:text-amber-400 font-bold' : 'text-rose-700 dark:text-rose-400 font-bold') : (isBridge ? 'text-fuchsia-800 dark:text-fuchsia-400' : 'text-zinc-800 dark:text-zinc-200')}`}>"{sd.explanation}"</p>
      {isPenalty && (
        <div className="mt-1 flex items-center gap-1.5">
          <span className={`text-[9px] font-black ${sd.source?.includes('INTEGRITY') ? 'text-amber-500 bg-amber-500/10 border-amber-500/20' : 'text-rose-500 bg-rose-500/10 border-rose-500/20'} px-1.5 py-0.5 rounded border uppercase tracking-tighter`}>
            Reduction: {((sd.score || 0) * 100).toFixed(0)}%
          </span>
        </div>
      )}
    </div>
  );
};

export default AuditSourceCard;
