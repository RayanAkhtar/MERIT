'use client';

import { useParams, useRouter } from 'next/navigation';
import { useMemo, useState, useRef, useEffect } from 'react';

// Mock data for the UI
const allMetricsInfo = [
  { key: 'tech', label: 'Technical Depth', weight: 0.15, sources: ['cv', 'github'], color: 'text-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:text-blue-400 border-blue-200 dark:border-blue-800' },
  { key: 'experience', label: 'Domain Experience', weight: 0.15, sources: ['cv', 'linkedin'], color: 'text-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800' },
  { key: 'systemDesign', label: 'System Design', weight: 0.15, sources: ['cv'], color: 'text-purple-500 bg-purple-50 dark:bg-purple-900/20 dark:text-purple-400 border-purple-200 dark:border-purple-800' },
  { key: 'problemSolving', label: 'Problem Solving', weight: 0.15, sources: ['cv', 'github'], color: 'text-fuchsia-500 bg-fuchsia-50 dark:bg-fuchsia-900/20 dark:text-fuchsia-400 border-fuchsia-200 dark:border-fuchsia-800' },
  { key: 'communication', label: 'Communication', weight: 0.15, sources: ['cv', 'linkedin'], color: 'text-rose-500 bg-rose-50 dark:bg-rose-900/20 dark:text-rose-400 border-rose-200 dark:border-rose-800' },
  { key: 'cultureFit', label: 'Culture Fit', weight: 0.10, sources: ['linkedin'], color: 'text-orange-500 bg-orange-50 dark:bg-orange-900/20 dark:text-orange-400 border-orange-200 dark:border-orange-800' },
  { key: 'leadership', label: 'Leadership', weight: 0.05, sources: ['cv', 'linkedin'], color: 'text-teal-500 bg-teal-50 dark:bg-teal-900/20 dark:text-teal-400 border-teal-200 dark:border-teal-800' },
  { key: 'projectMgmt', label: 'Project Mgmt', weight: 0.05, sources: ['cv', 'linkedin'], color: 'text-cyan-500 bg-cyan-50 dark:bg-cyan-900/20 dark:text-cyan-400 border-cyan-200 dark:border-cyan-800' },
  { key: 'teamwork', label: 'Teamwork', weight: 0.05, sources: ['linkedin'], color: 'text-sky-500 bg-sky-50 dark:bg-sky-900/20 dark:text-sky-400 border-sky-200 dark:border-sky-800' },
];

const availableSources = [
  { id: 'cv', label: 'CV', icon: (props: any) => <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg> },
  { id: 'github', label: 'GitHub', icon: (props: any) => <svg {...props} fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg> },
  { id: 'linkedin', label: 'LinkedIn', icon: (props: any) => <svg {...props} fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg> },
];

export default function PastResultDetailsPage() {
  const params = useParams();
  const router = useRouter();
  
  const id = typeof params?.id === 'string' ? params.id : 'unknown';

  const [visibleColKeys, setVisibleColKeys] = useState<string[]>(() => allMetricsInfo.slice(0, 6).map(m => m.key));
  const [sortConfig, setSortConfig] = useState<{ key: string, direction: 'asc' | 'desc' }>({ key: 'overallScore', direction: 'desc' });
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const [includeHiddenInScore, setIncludeHiddenInScore] = useState(true);
  const [activeSources, setActiveSources] = useState<string[]>(['cv', 'github', 'linkedin']);
  
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

  const rawCandidates = useMemo(() => {
    const firstNames = ['James', 'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'William', 'Sophia', 'Lucas', 'Isabella', 'Mateo', 'Mia', 'Elijah', 'Charlotte', 'Logan'];
    const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez'];
    
    const generateScore = (base: number) => Math.floor(Math.random() * (100 - base)) + base;
    
    return Array.from({ length: 32 }).map((_, i) => {
      const scores: Record<string, Record<string, number>> = {};
      allMetricsInfo.forEach(m => {
        scores[m.key] = {};
        m.sources.forEach(s => {
          scores[m.key][s] = generateScore(m.key === 'cultureFit' || m.key === 'teamwork' ? 70 : 50);
        });
      });
      
      return {
        id: `cand_${i + 1}`,
        name: `${firstNames[Math.floor(Math.random() * firstNames.length)]} ${lastNames[Math.floor(Math.random() * lastNames.length)]}`,
        scores
      };
    });
  }, []);

  const visibleMetrics = useMemo(() => {
    return allMetricsInfo.filter(m => visibleColKeys.includes(m.key));
  }, [visibleColKeys]);

  const candidates = useMemo(() => {
    const usableMetrics = includeHiddenInScore ? allMetricsInfo : visibleMetrics;
    const weightSum = usableMetrics.reduce((sum, m) => sum + m.weight, 0);

    return rawCandidates.map(c => {
      let overallScore = 0;
      let computedScores: Record<string, number> = {};

      allMetricsInfo.forEach(m => {
        const activeSrcs = m.sources.filter(s => activeSources.includes(s));
        if (activeSrcs.length === 0) {
          computedScores[m.key] = 0;
        } else {
          let sum = 0;
          activeSrcs.forEach(s => sum += c.scores[m.key][s]);
          computedScores[m.key] = Math.round(sum / activeSrcs.length);
        }
      });

      usableMetrics.forEach(m => {
         overallScore += (computedScores[m.key] * m.weight);
      });
      
      if (weightSum > 0) {
        overallScore = overallScore / weightSum;
      }

      return {
        ...c,
        computedScores,
        overallScore: Number(overallScore.toFixed(1))
      };
    });
  }, [rawCandidates, visibleMetrics, includeHiddenInScore, activeSources]);

  const stats = useMemo(() => {
    const sorted = [...candidates].sort((a, b) => b.overallScore - a.overallScore);
    return { topCand: sorted[0] || candidates[0] };
  }, [candidates]);

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

  const toggleColumn = (key: string) => {
    setVisibleColKeys(prev => 
      prev.includes(key) 
        ? prev.filter(k => k !== key) 
        : [...prev, key]
    );
  };

  const handleSort = (key: string) => {
    setSortConfig(prev => {
      if (prev.key === key) {
        return { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' };
      }
      return { key, direction: 'desc' };
    });
  };

  // For Insights: Top Card + first 5 visible metrics (calculate averages)
  const insightMetrics = visibleMetrics.slice(0, 5).map(m => {
    const validScores = candidates.filter(c => c.computedScores[m.key] > 0);
    const avg = validScores.length > 0 
       ? Number((validScores.reduce((acc, c) => acc + c.computedScores[m.key], 0) / validScores.length).toFixed(1))
       : 0;
    return { ...m, avg };
  });

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 px-4 py-8 md:py-12">
      <div className="max-w-[1400px] mx-auto space-y-8">
        
        {/* Navigation Breadcrumb */}
        <button onClick={() => router.push('/past-results')} className="flex items-center text-sm font-medium text-zinc-500 hover:text-indigo-600 dark:text-zinc-400 dark:hover:text-indigo-400 transition-colors group">
          <svg className="w-4 h-4 mr-1 group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Past Results
        </button>

        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-zinc-200 dark:border-zinc-800 pb-5 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 tracking-tight">Match Report Review</h1>
            <p className="mt-2 flex items-center gap-2 text-zinc-500 dark:text-zinc-400 font-mono text-xs">
              <span className="uppercase tracking-widest font-bold text-[10px] bg-zinc-200 dark:bg-zinc-800 px-1.5 py-0.5 rounded text-zinc-700 dark:text-zinc-300">Run ID</span> 
              {id}
            </p>
          </div>
          <div className="flex items-center gap-3">
             <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold bg-green-50 text-green-700 border border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800 shadow-sm">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-[pulse_2s_ease-in-out_infinite]" /> Computed & Stored
             </span>
             <button className="px-4 py-1.5 bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-zinc-50 dark:text-zinc-900 text-sm font-semibold rounded-md shadow-sm transition-colors flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Export CSV
             </button>
          </div>
        </div>

        {/* Insights Section */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Configuration Insights
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            {/* Top Match */}
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group col-span-1 sm:col-span-2 lg:col-span-1">
               <div className="absolute top-0 right-0 p-4 opacity-10 transform translate-x-1/4 -translate-y-1/4 group-hover:scale-110 transition-transform duration-500">
                  <svg className="w-24 h-24 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
               </div>
               <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-1">Top Score</p>
               <h3 className="text-xl font-bold text-zinc-900 dark:text-zinc-50 truncate">{stats.topCand.name}</h3>
               <p className="mt-2 text-sm text-indigo-600 dark:text-indigo-400 font-medium">Scored {stats.topCand.overallScore} / 100</p>
            </div>
            
            {/* Top 5 visible Metrics averages */}
            {insightMetrics.map(m => (
              <div key={m.key} className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                 <div className="absolute top-0 right-0 p-4 opacity-10 transform translate-x-1/4 -translate-y-1/4 group-hover:-translate-y-1/3 transition-transform duration-500">
                    <svg className={`w-24 h-24 ${m.color.split(' ')[0]}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                 </div>
                 <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-1 truncate">{m.label}</p>
                 <h3 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">{m.avg === 0 ? 'N/A' : m.avg} <span className="text-sm font-normal text-zinc-500">{m.avg !== 0 && 'avg'}</span></h3>
                 <div className="flex items-center gap-2 mt-2">
                   <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${m.color}`}>
                      W: {m.weight}
                   </span>
                 </div>
              </div>
            ))}
          </div>
        </div>

        {/* Breakdown Rankings Table */}
        <div className="space-y-4 pt-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
             <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
               <svg className="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
               </svg>
               Detailed Match Rankings
             </h2>
             <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
               <div className="hidden sm:flex items-center gap-3 bg-zinc-100 dark:bg-zinc-800/80 px-2.5 py-1 rounded border border-zinc-200 dark:border-zinc-700">
                 <span className="text-xs text-zinc-500 dark:text-zinc-400 font-mono tracking-wider">
                   Score = Σ (Metric * W)
                 </span>
                 <div className="w-px h-3.5 bg-zinc-300 dark:bg-zinc-600"></div>
                 <label className="flex items-center gap-2 cursor-pointer group">
                   <input 
                     type="checkbox" 
                     checked={includeHiddenInScore} 
                     onChange={(e) => setIncludeHiddenInScore(e.target.checked)}
                     className="rounded border-zinc-300 dark:border-zinc-600 text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5 cursor-pointer shadow-sm"
                   />
                   <span className="text-[10px] font-semibold text-zinc-600 dark:text-zinc-300 group-hover:text-zinc-900 dark:group-hover:text-zinc-100 transition-colors uppercase tracking-wide">
                     Include Hidden
                   </span>
                 </label>
               </div>

               {/* Sources Dropdown */}
               <div className="relative flex-1 sm:flex-none" ref={sourcesRef}>
                 <button 
                   onClick={() => setSourcesOpen(!sourcesOpen)}
                   className="w-full sm:w-auto px-3 py-1.5 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-md text-sm font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-700 transition flex items-center justify-between sm:justify-start gap-2 shadow-sm"
                 >
                   <div className="flex items-center gap-2 shrink-0">
                     <svg className="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                     Data Sources
                   </div>
                   <span className="bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300 py-0.5 px-1.5 rounded text-xs font-bold">{activeSources.length}/{availableSources.length}</span>
                 </button>
                 {sourcesOpen && (
                   <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg shadow-xl z-20 py-2">
                     <div className="px-4 pb-2 mb-2 border-b border-zinc-100 dark:border-zinc-800">
                       <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Active Evaluators</p>
                     </div>
                     <div className="max-h-80 overflow-y-auto px-2 space-y-1">
                       {availableSources.map(s => {
                         const isActive = activeSources.includes(s.id);
                         return (
                           <label key={s.id} className={`flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${isActive ? 'bg-emerald-50/50 dark:bg-emerald-900/10' : 'hover:bg-zinc-50 dark:hover:bg-zinc-800'}`}>
                             <div className="flex items-center gap-3">
                               <input 
                                 type="checkbox" 
                                 checked={isActive}
                                 onChange={() => {
                                   if (isActive && activeSources.length === 1) return; // Need at least one
                                   setActiveSources(prev => isActive ? prev.filter(x => x !== s.id) : [...prev, s.id]);
                                 }}
                                 className="rounded border-zinc-300 dark:border-zinc-700 text-emerald-600 focus:ring-emerald-500 cursor-pointer shadow-sm w-4 h-4"
                               />
                               <span className={`text-sm font-medium transition-colors ${isActive ? 'text-emerald-700 dark:text-emerald-400' : 'text-zinc-700 dark:text-zinc-300'}`}>{s.label}</span>
                             </div>
                           </label>
                         );
                       })}
                     </div>
                   </div>
                 )}
               </div>

               {/* Columns Dropdown */}
               <div className="relative flex-1 sm:flex-none" ref={dropdownRef}>
                 <button 
                   onClick={() => setDropdownOpen(!dropdownOpen)}
                   className="w-full sm:w-auto px-3 py-1.5 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-md text-sm font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-700 transition flex items-center justify-between sm:justify-start gap-2 shadow-sm"
                 >
                   <div className="flex items-center gap-2 shrink-0">
                     <svg className="w-4 h-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" /></svg>
                     Customize Columns
                   </div>
                   <span className="bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300 py-0.5 px-1.5 rounded text-xs font-bold">{visibleMetrics.length}/{allMetricsInfo.length}</span>
                 </button>
                 {dropdownOpen && (
                   <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg shadow-xl z-20 py-2">
                     <div className="px-4 pb-2 mb-2 border-b border-zinc-100 dark:border-zinc-800">
                       <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Toggle Display</p>
                     </div>
                     <div className="max-h-80 overflow-y-auto px-2 space-y-1">
                       {allMetricsInfo.map(m => {
                         const isVisible = visibleColKeys.includes(m.key);
                         return (
                           <label key={m.key} className={`flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${isVisible ? 'bg-indigo-50/50 dark:bg-indigo-900/10' : 'hover:bg-zinc-50 dark:hover:bg-zinc-800'}`}>
                             <div className="flex items-center gap-3">
                               <input 
                                 type="checkbox" 
                                 checked={isVisible}
                                 onChange={() => toggleColumn(m.key)}
                                 className="rounded border-zinc-300 dark:border-zinc-700 text-indigo-600 focus:ring-indigo-500 cursor-pointer shadow-sm w-4 h-4"
                               />
                               <div>
                                 <span className={`text-sm font-medium transition-colors ${isVisible ? 'text-indigo-700 dark:text-indigo-400' : 'text-zinc-700 dark:text-zinc-300'}`}>{m.label}</span>
                               </div>
                             </div>
                             <span className="text-[10px] text-zinc-400 font-mono">W:{m.weight}</span>
                           </label>
                         );
                       })}
                     </div>
                   </div>
                 )}
               </div>
             </div>
          </div>

          <div className="bg-white dark:bg-zinc-900 shadow-sm border border-zinc-200 dark:border-zinc-800 rounded-xl overflow-x-auto relative min-h-[440px]">
             <table className="w-full text-left text-sm whitespace-nowrap">
               <thead className="bg-zinc-50 dark:bg-zinc-900/50 border-b border-zinc-200 dark:border-zinc-800 text-zinc-700 dark:text-zinc-300 select-none">
                 <tr>
                   <th className="px-5 py-4 font-semibold w-16 text-center text-zinc-400 border-r border-zinc-200 dark:border-zinc-800">#</th>
                   <th className="px-5 py-4 font-semibold min-w-[220px] group cursor-pointer hover:bg-zinc-100 dark:hover:bg-zinc-800/80 transition-colors" onClick={() => handleSort('name')}>
                      <div className="flex items-center justify-between">
                        <span>Candidate Identity</span>
                        <div className="text-zinc-400">
                          {sortConfig.key === 'name' ? (
                            <span className="text-indigo-500">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                          ) : <span className="opacity-0 group-hover:opacity-40">↕</span>}
                        </div>
                      </div>
                   </th>
                   <th className="px-5 py-4 font-bold text-indigo-700 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/10 border-x border-zinc-200 dark:border-zinc-800 w-32 shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)] group cursor-pointer hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-colors sticky left-0 z-10" onClick={() => handleSort('overallScore')}>
                      <div className="flex items-center justify-between">
                        <span className="flex flex-col">
                           <span>Combined Score</span>
                        </span>
                        <div>
                          {sortConfig.key === 'overallScore' ? (
                            <span className="text-indigo-600 dark:text-indigo-400">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                          ) : <span className="opacity-0 group-hover:opacity-40">↕</span>}
                        </div>
                      </div>
                   </th>
                   {/* Dynamic Sortable Metric Columns */}
                   {visibleMetrics.map(m => (
                     <th key={m.key} className="px-4 py-4 font-semibold group cursor-pointer hover:bg-zinc-100 dark:hover:bg-zinc-800/80 transition-colors border-r border-zinc-100 dark:border-zinc-800/50 last:border-0 relative" onClick={() => handleSort(m.key)}>
                        <div className="flex items-center justify-between gap-4">
                          <div className="flex flex-col">
                            <div className="flex items-center gap-1.5">
                               <span className="text-zinc-900 dark:text-zinc-100">{m.label}</span>
                               <svg className="w-3.5 h-3.5 text-zinc-300 dark:text-zinc-600 group-hover:text-indigo-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                               </svg>
                            </div>
                            <span className={`text-[10px] font-mono mt-0.5 w-fit px-1.5 py-0.5 rounded border ${m.color}`}>W: {m.weight}</span>
                          </div>
                          <div className="shrink-0 font-mono text-zinc-400">
                            {sortConfig.key === m.key ? (
                              <span className="text-indigo-500">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                            ) : <span className="opacity-0 group-hover:opacity-40">↕</span>}
                          </div>
                        </div>
                        {/* Custom Tooltip */}
                        <div className="absolute top-full left-1/2 -translate-x-1/2 mt-1 w-max px-3 py-2 bg-zinc-800 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900 rounded-md shadow-[0_4px_12px_rgba(0,0,0,0.15)] opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-30 flex items-center gap-2">
                           <div className="absolute bottom-full left-1/2 -translate-x-1/2 border-4 border-transparent border-b-zinc-800 dark:border-b-zinc-100"></div>
                           <span className="text-[10px] font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wide">Sources:</span> 
                           <div className="flex items-center gap-1.5">
                             {m.sources.map(s => {
                               const sourceObj = availableSources.find(as => as.id === s);
                               if (!sourceObj) return null;
                               return (
                                 <div key={s} className="text-zinc-200 dark:text-zinc-800" title={sourceObj.label}>
                                   {sourceObj.icon({ className: "w-4 h-4" })}
                                 </div>
                               );
                             })}
                           </div>
                        </div>
                     </th>
                   ))}
                   {visibleMetrics.length === 0 && (
                     <th className="px-4 py-4 text-zinc-400 italic font-normal text-center">No metrics selected</th>
                   )}
                 </tr>
               </thead>
               <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/60">
                 {sortedCandidates.map((cand, idx) => (
                   <tr key={cand.id} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/30 transition-colors group">
                     <td className="px-5 py-4 text-center font-mono text-zinc-400 dark:text-zinc-500 text-xs border-r border-zinc-100 dark:border-zinc-800/60">
                       {idx + 1}
                     </td>
                     <td className="px-5 py-4">
                       <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-zinc-200 dark:bg-zinc-700 flex items-center justify-center text-zinc-500 dark:text-zinc-400 font-bold text-xs shrink-0 shadow-sm">
                            {cand.name.split(' ').map((n: string) => n[0]).join('')}
                          </div>
                          <span className="font-medium text-zinc-900 dark:text-zinc-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors cursor-pointer">
                            {cand.name}
                          </span>
                       </div>
                     </td>
                     <td className="px-5 py-4 bg-indigo-50/30 dark:bg-indigo-900/5 border-x border-zinc-100 dark:border-zinc-800/60 sticky left-0 z-0">
                       <div className="flex items-center gap-2">
                          <span className="text-base font-bold text-zinc-900 dark:text-zinc-100 w-10 text-right">
                             {cand.overallScore}
                          </span>
                          <div className="h-1.5 w-full bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden flex-1 max-w-[60px] shadow-inner">
                             <div 
                               className={`h-full rounded-full transition-all duration-500 ${cand.overallScore > 85 ? 'bg-indigo-500' : cand.overallScore > 75 ? 'bg-indigo-400' : 'bg-indigo-300'}`} 
                               style={{ width: `${cand.overallScore}%` }} 
                             />
                          </div>
                       </div>
                     </td>
                     {visibleMetrics.map(m => {
                        const score = cand.computedScores[m.key];
                        // Validate active
                        const isValid = score > 0; 
                        const isHigh = score >= 80;
                        const isLow = isValid && score < 50;
                        
                        return (
                          <td key={m.key} className="px-4 py-4 font-mono text-sm border-r border-zinc-100 dark:border-zinc-800/30 last:border-0">
                            {isValid ? (
                                <div className="flex items-center gap-2">
                                  <span className={`w-8 text-right font-medium ${isHigh ? 'text-green-600 dark:text-green-400' : isLow ? 'text-red-600 dark:text-red-400' : 'text-zinc-700 dark:text-zinc-300'}`}>
                                    {score}
                                  </span>
                                  <span className="text-[10px] text-zinc-400 dark:text-zinc-500 font-sans opacity-0 group-hover:opacity-100 transition-opacity">
                                    /100
                                  </span>
                                </div>
                            ) : (
                                <div className="flex items-center gap-2 text-zinc-300 dark:text-zinc-700">
                                  <span className="w-8 text-right text-[11px] italic font-sans font-medium">N/A</span>
                                </div>
                            )}
                          </td>
                        );
                     })}
                     {visibleMetrics.length === 0 && <td className="bg-zinc-50/50 dark:bg-zinc-900/20"></td>}
                   </tr>
                 ))}
                 {sortedCandidates.length === 0 && (
                   <tr>
                     <td colSpan={visibleMetrics.length + 3} className="text-center py-10 text-zinc-500">No data generated.</td>
                   </tr>
                 )}
               </tbody>
             </table>
          </div>
        </div>

      </div>
    </main>
  );
}
