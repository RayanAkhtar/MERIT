'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function PastResultsPage() {
  const router = useRouter();
  
  const [pastRuns, setPastRuns] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

  useEffect(() => {
    fetchSnapshots();
  }, []);

  const fetchSnapshots = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-past-results`);
      if (response.ok) {
        const data = await response.json();
        setPastRuns(data || []);
      }
    } catch (error) {
      console.error('Error fetching snapshots:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = (e: React.MouseEvent, configId: string) => {
    e.stopPropagation(); 
    router.push(`/output?config_id=${configId}`);
  };

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 px-4 py-8 md:py-12">
      <div className="max-w-5xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 tracking-tight">Execution History</h1>
          <p className="mt-2 text-zinc-600 dark:text-zinc-400">
            Review historical matching configurations and access their latest evaluation reports.
          </p>
        </div>

        <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden flex flex-col">
          <div className="p-4 md:p-6 flex-1">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-4 border-b border-zinc-200 dark:border-zinc-800 pb-2">
              Historical Match Logs
            </h2>

            <div className="space-y-3">
              {isLoading ? (
                <div className="p-12 text-center text-zinc-500 animate-pulse">
                   Synchronising match history...
                </div>
              ) : pastRuns.length === 0 ? (
                <div className="p-12 text-center text-zinc-400 italic">
                   No match history found.
                </div>
              ) : pastRuns.map((run) => (
                <div 
                  key={run.id}
                  onClick={() => router.push(`/output?config_id=${run.config_id}`)}
                  className="group relative flex flex-col sm:flex-row items-center justify-between p-4 border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/50 hover:bg-white dark:hover:bg-zinc-900 hover:border-indigo-400 dark:hover:border-indigo-600 hover:shadow-md cursor-pointer rounded-lg transition-all"
                >
                  <div className="flex-1 w-full flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6">
                    <div className="flex-[1.5]">
                      <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
                        {run.matching_configs?.name || "Deleted Config"}
                      </h3>
                      <div className="text-xs text-zinc-500 dark:text-zinc-400 mt-1 flex flex-wrap items-center gap-2">
                         <span>Run: {new Date(run.created_at).toLocaleString()}</span>
                         <span className="text-zinc-300 dark:text-zinc-700">|</span>
                         <span className="font-mono text-[10px] text-zinc-400 uppercase">Snapshot: {run.id.split('-')[0]}</span>
                      </div>
                    </div>
                    
                    <div className="flex-[1] flex flex-col gap-1 w-full sm:w-auto">
                      <div className="flex items-center gap-1.5 text-xs font-semibold text-green-700 dark:text-green-400 w-fit">
                        <span className="flex items-center justify-center w-4 h-4 rounded bg-green-100 dark:bg-green-900/40">
                           <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                        </span>
                        Top Match: {run.summary_data?.top_candidate} ({Math.round((run.summary_data?.top_score || 0) * 100)}%)
                      </div>
                      
                      <div className="text-[11px] font-medium text-zinc-500 dark:text-zinc-400 mt-1">
                         Analysed <span className="font-bold text-zinc-700 dark:text-zinc-300">{run.summary_data?.candidate_count || 0} candidates</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4 sm:mt-0 sm:ml-6 pl-0 sm:pl-6 border-t sm:border-t-0 sm:border-l border-zinc-200 dark:border-zinc-800 w-full sm:w-auto flex flex-col sm:flex-row items-center gap-3 shrink-0 justify-end pt-4 sm:pt-0">
                    
                     <button
                       onClick={(e) => handleRegenerate(e, run.config_id)}
                       className="flex items-center justify-center px-4 py-1.5 text-[11px] font-bold uppercase tracking-wider bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 rounded shadow-sm hover:border-indigo-400 hover:text-indigo-600 dark:hover:border-indigo-500 dark:hover:text-indigo-400 transition-colors w-full sm:w-auto z-10"
                     >
                       <svg className="w-3 h-3 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                       Refresh Match
                     </button>

                     <div className="flex items-center text-sm font-semibold text-indigo-600 dark:text-indigo-400 group-hover:text-indigo-800 dark:group-hover:text-indigo-300 transition-colors w-full sm:w-auto justify-center sm:justify-start">
                       View Report
                       <svg className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                       </svg>
                     </div>

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
