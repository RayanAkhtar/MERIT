'use client';

import { useParams, useRouter } from 'next/navigation';
import { useMemo, useState, useRef, useEffect } from 'react';

const availableSources = [
  { id: 'CV', label: 'CV', icon: (props: any) => <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg> },
  { id: 'GitHub', label: 'GitHub', icon: (props: any) => <svg {...props} fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg> },
  { id: 'LinkedIn', label: 'LinkedIn', icon: (props: any) => <svg {...props} fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg> },
];

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

export default function PastResultDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const id = typeof params?.id === 'string' ? params.id : 'unknown';

  const [rawResults, setRawResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [visibleColKeys, setVisibleColKeys] = useState<string[]>([]);
  const [sortConfig, setSortConfig] = useState<{ key: string, direction: 'asc' | 'desc' }>({ key: 'overallScore', direction: 'desc' });
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const [activeSources, setActiveSources] = useState<string[]>(['CV', 'GitHub', 'LinkedIn']);
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const sourcesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
      if (sourcesRef.current && !sourcesRef.current.contains(event.target as Node)) {
        setSourcesOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (id && id !== 'unknown') {
      fetchResults();
    }
  }, [id]);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/rank-candidates/${id}`);
      if (response.ok) {
        const data = await response.json();
        setRawResults(data);
        const firstCand = data.results[0];
        if (firstCand) {
           setVisibleColKeys(Object.keys(firstCand.metrics));
        }
      } else {
        const err = await response.json();
        setError(err.error || 'Failed to fetch historic ranking');
      }
    } catch (err) {
      setError('Connection to historic data failed.');
    } finally {
      setLoading(false);
    }
  };

  const allMetricsInfo = useMemo(() => {
    if (!rawResults || !rawResults.results[0]) return [];
    return Object.entries(rawResults.results[0].metrics).map(([key, m]: [string, any]) => ({
      key,
      label: m.name,
      weight: m.weight || 3,
      color: key === 'languages' ? 'text-blue-500 bg-blue-50 dark:bg-blue-900/20' : 
             key === 'technologies' ? 'text-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' :
             key === 'soft_skills' ? 'text-rose-500 bg-rose-50 dark:bg-rose-900/20' :
             'text-zinc-500 bg-zinc-50 dark:bg-zinc-800'
    }));
  }, [rawResults]);

  const candidates = useMemo(() => {
    if (!rawResults) return [];
    return rawResults.results.map((c: any) => {
      const scores: Record<string, number> = {};
      Object.entries(c.metrics).forEach(([key, m]: [string, any]) => {
        const sourcesUsed = m.sources_used || [];
        const isAnySourceActive = sourcesUsed.some((s: string) => activeSources.includes(s));
        scores[key] = isAnySourceActive ? Math.round(m.score * 100) : 0;
      });
      return {
        id: c.candidate_id,
        name: c.name,
        email: c.email,
        computedScores: scores,
        overallScore: Math.round(c.total_score * 100)
      };
    });
  }, [rawResults, activeSources]);

  const sortedCandidates = useMemo(() => {
    let sortable = [...candidates];
    sortable.sort((a, b) => {
      let aVal, bVal;
      if (sortConfig.key === 'overallScore') {
        aVal = a.overallScore; bVal = b.overallScore;
      } else if (sortConfig.key === 'name') {
        aVal = a.name; bVal = b.name;
      } else {
        aVal = a.computedScores[sortConfig.key]; bVal = b.computedScores[sortConfig.key];
      }
      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
    return sortable;
  }, [candidates, sortConfig]);

  const visibleMetrics = allMetricsInfo.filter(m => visibleColKeys.includes(m.key));
  const stats = { topCand: sortedCandidates[0] };

  if (loading) return <div className="p-20 text-center animate-pulse text-zinc-500">Loading History Report...</div>;
  if (error) return <div className="p-20 text-center text-red-500">{error}</div>;

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 px-4 py-8 md:py-12">
      <div className="max-w-[1400px] mx-auto space-y-8">
        
        <button onClick={() => router.push('/past-results')} className="flex items-center text-sm font-medium text-zinc-500 hover:text-indigo-600 group">
          <svg className="w-4 h-4 mr-1 group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
          Back to History
        </button>

        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-zinc-200 dark:border-zinc-800 pb-5 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 tracking-tight">Historic Match Review</h1>
            <p className="mt-2 text-zinc-500 font-mono text-xs">Run ID: {id}</p>
          </div>
          <div className="flex items-center gap-3">
             <span className="px-3 py-1.5 rounded-md text-xs font-bold bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700">Stored Analysis</span>
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">Configuration Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-5 shadow-sm">
               <p className="text-xs font-semibold uppercase text-zinc-500 mb-1">Top Performer</p>
               <h3 className="text-xl font-bold text-zinc-900 dark:text-zinc-50 truncate">{stats.topCand?.name || 'N/A'}</h3>
               <p className="mt-2 text-sm text-indigo-600 dark:text-indigo-400">Score: {stats.topCand?.overallScore || 0}%</p>
            </div>
            {allMetricsInfo.slice(0, 3).map(m => (
              <div key={m.key} className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-5 shadow-sm">
                 <p className="text-xs font-semibold uppercase text-zinc-500 mb-1">{m.label}</p>
                 <h3 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">{Math.round(candidates.reduce((acc, c) => acc + c.computedScores[m.key], 0) / candidates.length)}% <span className="text-xs font-normal">avg</span></h3>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4 pt-4">
          <div className="flex items-center justify-between">
             <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Match Leaderboard</h2>
             <div className="flex items-center gap-2">
                {/* Column toggle would go here, kept simpler for consistency */}
             </div>
          </div>
          <div className="bg-white dark:bg-zinc-900 shadow-sm border border-zinc-200 dark:border-zinc-800 rounded-xl overflow-x-auto">
             <table className="w-full text-left text-sm whitespace-nowrap">
               <thead className="bg-zinc-50 dark:bg-zinc-900/50 border-b border-zinc-200 dark:border-zinc-800 text-zinc-700 dark:text-zinc-300">
                 <tr>
                   <th className="px-5 py-4 font-semibold w-16 text-center border-r border-zinc-200 dark:border-zinc-800">#</th>
                   <th className="px-5 py-4 font-semibold min-w-[200px]">Candidate</th>
                   <th className="px-5 py-4 font-bold text-indigo-700 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/10 border-x border-zinc-200 dark:border-zinc-800 w-32">Total</th>
                   {visibleMetrics.map(m => <th key={m.key} className="px-4 py-4 font-semibold border-r border-zinc-100 dark:border-zinc-800/50">{m.label}</th>)}
                 </tr>
               </thead>
               <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/60">
                 {sortedCandidates.map((cand, idx) => (
                   <tr key={cand.id} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/30 transition-colors">
                     <td className="px-5 py-4 text-center text-zinc-400 border-r border-zinc-100 dark:border-zinc-800/60">{idx + 1}</td>
                     <td className="px-5 py-4">
                        <div className="flex flex-col">
                           <span className="font-bold text-zinc-900 dark:text-zinc-100 uppercase">{cand.name}</span>
                           <span className="text-[10px] text-zinc-500">{cand.email}</span>
                        </div>
                     </td>
                     <td className="px-5 py-4 bg-indigo-50/30 dark:bg-indigo-900/5 border-x border-zinc-100 dark:border-zinc-800/60">
                        <span className="text-base font-black text-indigo-600 dark:text-indigo-400">{cand.overallScore}%</span>
                     </td>
                     {visibleMetrics.map(m => <td key={m.key} className="px-4 py-4 font-mono text-sm border-r border-zinc-100 dark:border-zinc-800/30 last:border-0">{cand.computedScores[m.key]}%</td>)}
                   </tr>
                 ))}
               </tbody>
             </table>
          </div>
        </div>

      </div>
    </main>
  );
}
