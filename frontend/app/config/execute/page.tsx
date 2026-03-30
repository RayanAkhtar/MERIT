'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function ExecuteConfigPage() {
  const [selectedConfig, setSelectedConfig] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('NEWEST');

  // Mock saved configurations with execution status and timestamps
  const dummyConfigs = [
    { 
      id: 'cfg_1', 
      name: 'Senior ML Engineer Sourcing', 
      reqDoc: 'Senior Machine Learning Engineer', 
      batch: 'Batch B - LinkedIn Sourcing', 
      createdOn: 'Mar 22, 2026',
      timestamp: 1774137600000,
      candidatesCount: 12,
      skills: ['Python', 'PyTorch', 'Transformers', 'CUDA'],
      topWeights: [
        { label: 'Technical Skills', val: 0.95 },
        { label: 'System Design', val: 0.90 },
        { label: 'Experience (5+)', val: 0.85 },
        { label: 'Job Level', val: 0.70 },
        { label: 'Company Prestige', val: 0.65 }
      ],
      status: 'COMPUTED',
      lastRunDate: 'Today, 10:45 AM'
    },
    { 
      id: 'cfg_2', 
      name: 'Summer DS Interns - Fair', 
      reqDoc: 'Data Scientist Intern', 
      batch: 'Batch A - Graduate Fair 2026', 
      createdOn: 'Mar 25, 2026',
      timestamp: 1774396800000,
      candidatesCount: 45,
      skills: ['Python', 'Pandas', 'Scikit-Learn', 'SQL'],
      topWeights: [
        { label: 'Academic Excellence', val: 0.98 },
        { label: 'Technical Skills', val: 0.88 },
        { label: 'Extracurriculars', val: 0.60 },
        { label: 'Job Level', val: 0.50 },
        { label: 'Experience', val: 0.30 }
      ],
      status: 'NEEDS_UPDATE',
      lastRunDate: 'Yesterday'
    },
    { 
      id: 'cfg_3', 
      name: 'React Urgent Hire Filter', 
      reqDoc: 'Frontend Developer (React)', 
      batch: 'Batch C - Direct Apps', 
      createdOn: 'Today',
      timestamp: 1774483200000,
      candidatesCount: 104,
      skills: ['TypeScript', 'React', 'Next.js', 'Tailwind CSS'],
      topWeights: [
        { label: 'Experience (3+)', val: 1.00 },
        { label: 'Technical Skills', val: 0.95 },
        { label: 'UI/UX Sensitivity', val: 0.95 },
        { label: 'Open Source', val: 0.80 },
        { label: 'Job Level', val: 0.75 }
      ],
      status: 'PENDING',
      lastRunDate: null
    }
  ];

  let processedConfigs = dummyConfigs.filter(cfg => {
    if (statusFilter !== 'ALL' && cfg.status !== statusFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      if (!cfg.name.toLowerCase().includes(q) && !cfg.reqDoc.toLowerCase().includes(q)) {
        return false;
      }
    }
    return true;
  });

  processedConfigs.sort((a, b) => {
    if (sortBy === 'NEWEST') return b.timestamp - a.timestamp;
    if (sortBy === 'OLDEST') return a.timestamp - b.timestamp;
    if (sortBy === 'NAME_ASC') return a.name.localeCompare(b.name);
    if (sortBy === 'CANDIDATES_DESC') return b.candidatesCount - a.candidatesCount;
    return 0;
  });

  const handleExecute = () => {
    if (!selectedConfig) return;
    setIsExecuting(true);
    setTimeout(() => {
      setIsExecuting(false);
      alert('Match Results generated successfully! Check Past Results to view them.');
    }, 2000);
  };

  const selectedData = dummyConfigs.find(c => c.id === selectedConfig);

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 px-4 py-8 md:py-12">
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 tracking-tight">Execute Configuration</h1>
          <p className="mt-2 text-zinc-600 dark:text-zinc-400">
            Select a highly-optimized matching preset to evaluate your latest candidate batches.
          </p>
        </div>

        <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden flex flex-col">
          <div className="p-4 md:p-6 flex-1">
            
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
                <svg className="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Saved Presets
              </h2>
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Showing {processedConfigs.length} setups</span>
            </div>

            {/* Filter and Sort Control Bar */}
            <div className="flex flex-col sm:flex-row gap-4 mb-6 pb-4 border-b border-zinc-200 dark:border-zinc-800">
              <div className="flex-1">
                <input 
                  type="text" 
                  placeholder="Search setups or requirements..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full text-sm bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-md px-3 py-2 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-shadow"
                />
              </div>
              <div className="flex flex-wrap sm:flex-nowrap gap-4">
                <select 
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="flex-1 sm:flex-none text-sm bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-md px-3 py-2 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                >
                  <option value="ALL">All Statuses</option>
                  <option value="COMPUTED">Computed</option>
                  <option value="NEEDS_UPDATE">Needs Update</option>
                  <option value="PENDING">Pending</option>
                </select>
                <select 
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="flex-1 sm:flex-none text-sm bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-md px-3 py-2 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                >
                  <option value="NEWEST">Newest First</option>
                  <option value="OLDEST">Oldest First</option>
                  <option value="NAME_ASC">Name (A-Z)</option>
                  <option value="CANDIDATES_DESC">Most Candidates</option>
                </select>
              </div>
            </div>

            <div className="space-y-3">
              {processedConfigs.length === 0 ? (
                <div className="text-center py-12 border border-zinc-200 border-dashed rounded-lg dark:border-zinc-800">
                  <p className="text-sm text-zinc-500 dark:text-zinc-400">No configurations match your filters.</p>
                  <button onClick={() => { setSearchQuery(''); setStatusFilter('ALL'); }} className="mt-2 text-indigo-600 hover:text-indigo-800 hover:underline dark:text-indigo-400 dark:hover:text-indigo-300 text-sm font-medium">Clear filters</button>
                </div>
              ) : processedConfigs.map(config => (
                <div 
                  key={config.id}
                  onClick={() => setSelectedConfig(config.id)}
                  className={`
                    cursor-pointer transition-colors border
                    ${selectedConfig === config.id 
                        ? 'border-indigo-600 bg-indigo-50/20 dark:border-indigo-500 dark:bg-indigo-900/10 shadow-sm' 
                        : 'border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700 bg-white dark:bg-zinc-900'}
                  `}
                >
                  <div className="p-5 flex flex-col xl:flex-row gap-8">
                    
                    {/* Left Body: Formal Metadata */}
                    <div className="flex-[2] space-y-5">
                      
                      {/* Headers & Minimal Statuses */}
                      <div>
                        <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 text-base leading-tight">
                          {config.name}
                        </h3>
                        <div className="text-xs text-zinc-500 dark:text-zinc-400 mt-1.5 flex flex-wrap items-center gap-3">
                           <span>Created {config.createdOn}</span>
                           <span className="text-zinc-300 dark:text-zinc-700">|</span>
                           
                           {/* Status Tag Map */}
                           <span className="flex items-center gap-1.5">
                             {config.status === 'COMPUTED' && <><span className="w-1.5 h-1.5 rounded-full bg-green-500" />Computed</>}
                             {config.status === 'NEEDS_UPDATE' && <><span className="w-1.5 h-1.5 rounded-full bg-amber-500" />Needs Update</>}
                             {config.status === 'PENDING' && <><span className="w-1.5 h-1.5 rounded-full bg-zinc-300 dark:bg-zinc-600" />Pending</>}
                           </span>

                           {/* Results Text Link */}
                           {(config.status === 'COMPUTED' || config.status === 'NEEDS_UPDATE') && (
                             <>
                               <span className="text-zinc-300 dark:text-zinc-700">|</span>
                               <Link 
                                 href="/past-results"
                                 onClick={(e) => e.stopPropagation()}
                                 className="text-indigo-600 hover:text-indigo-800 hover:underline dark:text-indigo-400 transition-colors"
                                 title="View past results dashboard"
                               >
                                 View past history ↗
                               </Link>
                             </>
                           )}
                        </div>
                      </div>
                      
                      {/* Clean Grid Target Details */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm mt-4 lg:mt-6">
                        <div className="space-y-1">
                          <span className="text-zinc-500 dark:text-zinc-400 block text-[11px] uppercase tracking-wide font-medium">Job Requirement</span>
                          <span className="text-zinc-900 dark:text-zinc-100">{config.reqDoc}</span>
                        </div>
                        <div className="space-y-1">
                          <span className="text-zinc-500 dark:text-zinc-400 block text-[11px] uppercase tracking-wide font-medium">Candidate Array Goal</span>
                          <span className="text-zinc-900 dark:text-zinc-100 block truncate" title={config.batch}>
                            {config.batch} <span className="text-zinc-500 ml-1">({config.candidatesCount} entities)</span>
                          </span>
                        </div>
                      </div>

                      {/* Explicit Required Skills String */}
                      <div>
                        <span className="text-zinc-500 dark:text-zinc-400 block text-[11px] uppercase tracking-wide font-medium mb-1.5">Parsed Core Requirements</span>
                        <div className="text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed">
                          {config.skills.join(', ')}
                        </div>
                      </div>
                      
                    </div>
                    
                    {/* Divider Desktop */}
                    <div className="hidden xl:block w-px bg-zinc-200 dark:bg-zinc-800 my-1"></div>

                    {/* Top Right Box: Formal Weighting Table Form */}
                    <div className="xl:w-[280px] shrink-0">
                      <div>
                        <h4 className="text-[11px] uppercase font-medium text-zinc-500 dark:text-zinc-400 tracking-wide mb-3">
                          Priority Parameters Table
                        </h4>
                        
                        <div className="border border-zinc-200 dark:border-zinc-800 rounded bg-zinc-50/50 dark:bg-zinc-900/50">
                           <ul className="flex flex-col divide-y divide-zinc-200 dark:divide-zinc-800">
                             {config.topWeights.map((weight, idx) => (
                               <li key={idx} className="flex items-center justify-between py-2 px-3">
                                 <span className="text-[13px] text-zinc-700 dark:text-zinc-300 truncate pr-3">
                                   {weight.label}
                                 </span>
                                 <span className={`
                                    flex shrink-0 items-center justify-center px-1.5 h-5 text-[11px] border rounded-sm font-mono font-medium tracking-tight
                                    ${weight.val >= 0.80 
                                      ? 'border-indigo-200 text-indigo-700 bg-indigo-50 dark:border-indigo-800 dark:text-indigo-300 dark:bg-indigo-900/40' 
                                      : 'border-zinc-200 text-zinc-600 bg-zinc-50 dark:border-zinc-700 dark:text-zinc-400 dark:bg-zinc-800/50'}
                                 `}>
                                   {weight.val.toFixed(2)}
                                 </span>
                               </li>
                             ))}
                           </ul>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              ))}
            </div>

          </div>

          {/* Action Footer */}
          <div className="px-4 md:px-6 py-4 bg-zinc-50 dark:bg-zinc-800/50 border-t border-zinc-200 dark:border-zinc-800 flex flex-col md:flex-row items-center justify-between gap-4">
            
            <div className="flex items-center gap-4 text-sm font-medium">
              {selectedData && (selectedData.status === 'COMPUTED' || selectedData.status === 'NEEDS_UPDATE') ? (
                <div className="flex items-center gap-3">
                  <span className="text-zinc-500 dark:text-zinc-400 text-xs">
                    Last Run: {selectedData.lastRunDate}
                  </span>
                  <Link 
                    href="/past-results"
                    className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 flex items-center gap-1 hover:underline decoration-indigo-300 transition-colors"
                  >
                    View Past Result
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </Link>
                </div>
              ) : (
                <span className="text-zinc-400 dark:text-zinc-500 text-xs italic">
                  Select a configuration to execute matching processes.
                </span>
              )}
            </div>

            <button
              onClick={handleExecute}
              disabled={!selectedConfig || isExecuting}
              className={`
                px-8 py-2.5 rounded-md font-semibold text-white transition-all shadow-sm
                flex items-center gap-2 w-full md:w-auto justify-center
                ${(!selectedConfig || isExecuting)
                  ? 'bg-zinc-300 dark:bg-zinc-700 text-zinc-500 dark:text-zinc-400 cursor-not-allowed hidden-shadow'
                  : 'bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-400 shadow-md hover:shadow-lg active:scale-95'
                }
              `}
            >
              {isExecuting ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Running Matching AI...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                  </svg>
                  {selectedData?.status === 'NEEDS_UPDATE' ? 'Re-Execute Match' : 'Execute Match'}
                </>
              )}
            </button>
          </div>
        </div>

      </div>
    </main>
  );
}
