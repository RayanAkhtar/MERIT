'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function PastResultsPage() {
  const router = useRouter();
  
  // Mock data for the UI
  const [pastRuns, setPastRuns] = useState([
    {
      id: 'abc',
      configName: 'Senior ML Engineer Sourcing',
      runDate: 'Mar 26, 2026, 10:45 AM',
      status: 'UP_TO_DATE',
      candidatesEvaluated: 12,
      topCandidate: 'Alice Johnson (Score: 94%)'
    },
    {
      id: 'def456',
      configName: 'Summer DS Interns - Fair',
      runDate: 'Mar 25, 2026, 14:20 PM',
      status: 'OUT_OF_DATE',
      candidatesEvaluated: 45,
      topCandidate: 'Bob Smith (Score: 89%)'
    },
    {
      id: 'ghi789',
      configName: 'React Urgent Hire Filter',
      runDate: 'Mar 24, 2026, 09:15 AM',
      status: 'UP_TO_DATE',
      candidatesEvaluated: 104,
      topCandidate: 'Charlie Davis (Score: 97%)'
    },
    {
      id: 'jkl012',
      configName: 'Backend Go Engineer',
      runDate: 'Pending extraction...',
      status: 'GENERATING',
      candidatesEvaluated: 88,
      topCandidate: 'Calculating...'
    }
  ]);

  const handleRegenerate = (e: React.MouseEvent, runId: string) => {
    e.stopPropagation(); // Don't navigate when clicking the button
    
    // Set status to generating
    setPastRuns(prev => prev.map(r => r.id === runId ? { ...r, status: 'GENERATING' } : r));
    
    // Mock generation delay correctly resetting it
    setTimeout(() => {
       setPastRuns(prev => prev.map(r => r.id === runId ? { 
           ...r, 
           status: 'UP_TO_DATE', 
           runDate: 'Just now',
           candidatesEvaluated: Math.floor(Math.random() * 50) + r.candidatesEvaluated // simulate modified number logic
       } : r));
    }, 3000);
  };

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 px-4 py-8 md:py-12">
      <div className="max-w-5xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 tracking-tight">Past Results History</h1>
          <p className="mt-2 text-zinc-600 dark:text-zinc-400">
            View historical matching runs, review AI evaluations, and navigate to detailed candidate reports.
          </p>
        </div>

        <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden flex flex-col">
          <div className="p-4 md:p-6 flex-1">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-4 border-b border-zinc-200 dark:border-zinc-800 pb-2">
              Execution Logs
            </h2>

            <div className="space-y-3">
              {pastRuns.map((run) => (
                <div 
                  key={run.id}
                  onClick={() => {
                    // Prevent navigation if generating
                    if (run.status !== 'GENERATING') {
                      router.push(`/past-results/${run.id}`)
                    }
                  }}
                  className={`
                    group relative flex flex-col sm:flex-row items-center justify-between p-4 border rounded-lg transition-all
                    ${run.status === 'GENERATING' 
                       ? 'cursor-wait border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/30 opacity-80'
                       : 'cursor-pointer border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/50 hover:bg-white dark:hover:bg-zinc-900 hover:border-indigo-400 dark:hover:border-indigo-600 hover:shadow-md'
                    }
                  `}
                >
                  <div className="flex-1 w-full flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6">
                    <div className="flex-[1.5]">
                      <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
                        {run.configName}
                      </h3>
                      <div className="text-xs text-zinc-500 dark:text-zinc-400 mt-1 flex flex-wrap items-center gap-2">
                         <span>Run: {run.runDate}</span>
                         <span className="text-zinc-300 dark:text-zinc-700">|</span>
                         <span className="font-mono text-[10px] text-zinc-400">ID: {run.id}</span>
                      </div>
                    </div>
                    
                    <div className="flex-[1] flex flex-col gap-1 w-full sm:w-auto">
                      {run.status === 'UP_TO_DATE' && (
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-green-700 dark:text-green-400 w-fit">
                          <span className="flex items-center justify-center w-4 h-4 rounded bg-green-100 dark:bg-green-900/40">
                             <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                          </span>
                          Up to Date
                        </div>
                      )}
                      {run.status === 'OUT_OF_DATE' && (
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-700 dark:text-amber-500 w-fit">
                          <span className="flex items-center justify-center w-4 h-4 rounded bg-amber-100 dark:bg-amber-900/40">
                             <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                          </span>
                          Out of Date
                        </div>
                      )}
                      {run.status === 'GENERATING' && (
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-700 dark:text-indigo-400 w-fit">
                          <span className="flex items-center justify-center w-4 h-4 rounded bg-indigo-100 dark:bg-indigo-900/40">
                             <svg className="w-3 h-3 animate-spin origin-center" fill="none" viewBox="0 0 24 24">
                               <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                               <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                             </svg>
                          </span>
                          Generating...
                        </div>
                      )}
                      
                      <div className="text-[11px] font-medium text-zinc-500 dark:text-zinc-400 mt-1">
                         Evaluated <span className="font-bold text-zinc-700 dark:text-zinc-300">{run.candidatesEvaluated} CVs</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4 sm:mt-0 sm:ml-6 pl-0 sm:pl-6 border-t sm:border-t-0 sm:border-l border-zinc-200 dark:border-zinc-800 w-full sm:w-auto flex flex-col sm:flex-row items-center gap-3 shrink-0 justify-end pt-4 sm:pt-0">
                    
                    {run.status === 'OUT_OF_DATE' && (
                       <button
                         onClick={(e) => handleRegenerate(e, run.id)}
                         className="flex items-center justify-center px-4 py-1.5 text-[11px] font-bold uppercase tracking-wider bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 rounded shadow-sm hover:border-indigo-400 hover:text-indigo-600 dark:hover:border-indigo-500 dark:hover:text-indigo-400 transition-colors w-full sm:w-auto z-10"
                       >
                         <svg className="w-3 h-3 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                         Regenerate
                       </button>
                    )}

                    {run.status === 'GENERATING' ? (
                       <div className="flex items-center text-sm font-semibold text-zinc-400 dark:text-zinc-500 cursor-not-allowed w-full sm:w-auto justify-center sm:justify-start">
                         Processing data
                       </div>
                    ) : (
                       <div className="flex items-center text-sm font-semibold text-indigo-600 dark:text-indigo-400 group-hover:text-indigo-800 dark:group-hover:text-indigo-300 transition-colors w-full sm:w-auto justify-center sm:justify-start">
                         View Report
                         <svg className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                         </svg>
                       </div>
                    )}

                  </div>
                </div>
              ))}
            </div>

          </div>
        </div>
      </div>
    </main>
  );
}
