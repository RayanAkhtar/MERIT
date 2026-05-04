import React from 'react';

interface AuditSourceCardProps {
  sd: any;
  j: number;
}

const AuditSourceCard: React.FC<AuditSourceCardProps> = ({ sd, j }) => {
  const isPenalty = sd.score < 0;
  const isBridge = sd.is_semantic_bridge;
  
  let cardStyles = 'bg-zinc-50 dark:bg-zinc-900/50 border-zinc-100 dark:border-zinc-800';
  let textStyles = 'text-indigo-500 dark:text-indigo-400';
  let label = `${sd.source} Signal`;

  if (isPenalty) {
    cardStyles = 'bg-rose-500/5 border-rose-500/20';
    textStyles = 'text-rose-500 flex items-center gap-1.5';
    label = `Penalty: ${sd.source}`;
  } else if (isBridge) {
    cardStyles = 'bg-amber-500/5 border-amber-500/20';
    textStyles = 'text-amber-600 dark:text-amber-500 flex items-center gap-1.5';
    label = `Semantic Bridge: ${sd.source}`;
  }

  return (
    <div key={j} className={`p-3 rounded-lg border flex flex-col gap-1 ${cardStyles}`}>
      <span className={`text-[10px] font-black uppercase tracking-widest ${textStyles}`}>
        {isPenalty && (
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )}
        {isBridge && (
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        )}
        {label}
      </span>
      <p className={`text-xs leading-tight italic ${isPenalty ? 'text-rose-700 dark:text-rose-400 font-bold' : (isBridge ? 'text-amber-800 dark:text-amber-400' : 'text-zinc-800 dark:text-zinc-200')}`}>"{sd.explanation}"</p>
      {isPenalty && (
        <div className="mt-1 flex items-center gap-1.5">
          <span className="text-[9px] font-black text-rose-500 bg-rose-500/10 px-1.5 py-0.5 rounded border border-rose-500/20 uppercase tracking-tighter">
            Reduction: {(sd.score * 100).toFixed(0)}%
          </span>
        </div>
      )}
    </div>
  );
};

export default AuditSourceCard;
