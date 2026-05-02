'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { useMemo, useState, useRef, useEffect, Suspense } from 'react';
import DetailedReportModal from './components/DetailedReportModal';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

const LoadingScreen = () => (
  <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 flex flex-col items-center justify-center p-4">
    <div className="relative flex flex-col items-center gap-8">
      <div className="relative flex items-center justify-center">
        <div className="absolute inset-0 bg-indigo-500/20 dark:bg-indigo-500/10 blur-xl rounded-full animate-pulse" />
        <div className="w-16 h-16 rounded-full border-4 border-indigo-100 dark:border-indigo-500/10 border-t-indigo-600 dark:border-t-indigo-500 animate-spin relative z-10" />
      </div>
      <div className="space-y-3 text-center animate-pulse">
        <h3 className="text-xl font-black text-zinc-900 dark:text-white tracking-tighter">Synchronising with Ranking Engine</h3>
        <p className="text-xs font-bold text-zinc-500 uppercase tracking-[0.25em]">Executing matching heuristics...</p>
      </div>
    </div>
  </div>
);

function RankingReport() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const configId = searchParams.get('config_id');
  const snapshotId = searchParams.get('snapshot_id');

  const [rawResults, setRawResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [selectedCandidateDetail, setSelectedCandidateDetail] = useState<any>(null);
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  
  const [visibleColKeys, setVisibleColKeys] = useState<string[]>([]);
  const [sortConfig, setSortConfig] = useState<{ key: string, direction: 'asc' | 'desc' }>({ key: 'overallScore', direction: 'desc' });
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const [activeSources, setActiveSources] = useState<string[]>(['CV', 'GitHub', 'LinkedIn']);
  const [isBlindMode, setIsBlindMode] = useState<boolean>(true);
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const sourcesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (selectedCandidate && !selectedCandidateDetail) {
      fetchCandidateDetail(selectedCandidate.id);
    }
  }, [selectedCandidate]);

  const fetchCandidateDetail = async (id: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-candidate-detail/${id}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedCandidateDetail(data);
      }
    } catch (err) {
      console.error("Failed to fetch candidate details", err);
    }
  };

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
    if (snapshotId) {
      fetchSnapshot();
    } else if (configId) {
      fetchResults();
    } else {
      setLoading(false);
      setError("No identifier provided.");
    }
  }, [configId, snapshotId]);

  const fetchSnapshot = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-past-result/${snapshotId}`);
      if (response.ok) {
        const data = await response.json();
        setRawResults(data);
        
        const firstCand = data.results[0];
        if (firstCand) {
           const keys = Object.keys(firstCand.metrics);
           setVisibleColKeys(keys);
        }
      } else {
        const err = await response.json();
        setError(err.error || 'Failed to fetch snapshot details');
      }
    } catch (err) {
      setError('Connection to server failed.');
    } finally {
      setLoading(false);
    }
  };

  const fetchResults = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/rank-candidates/${configId}`);
      if (response.ok) {
        const data = await response.json();
        setRawResults(data);
        
        const firstCand = data.results[0];
        if (firstCand) {
           const keys = Object.keys(firstCand.metrics);
           setVisibleColKeys(keys);
        }
      } else {
        const err = await response.json();
        setError(err.error || 'Failed to fetch ranking results');
      }
    } catch (err) {
      setError('Connection to ranking server failed.');
    } finally {
      setLoading(false);
    }
  };

  const allMetricsInfo = useMemo(() => {
    if (!rawResults || !rawResults.results[0]) return [];
    
    return Object.entries(rawResults.results[0].metrics).map(([key, m]: [string, any]) => ({
      key,
      label: m.name,
      weight: m.weight || 0.6,
    })).sort((a, b) => b.weight - a.weight);
  }, [rawResults]);

  const candidates = useMemo(() => {
    if (!rawResults) return [];

    return rawResults.results.map((c: any) => {
      let dynamicWeightedSum = 0;
      let dynamicTotalWeight = 0;
      const dynamicMetrics: Record<string, any> = {};

      Object.entries(c.metrics).forEach(([key, m]: [string, any]) => {
        // Only include visible metrics in the dynamic recalculation
        if (!visibleColKeys.includes(key)) return;

        const newMetric = JSON.parse(JSON.stringify(m));
        let metricTotalPoints = 0;
        const validBreakdown = (newMetric.breakdown || []).filter(item => item.item !== "Authenticity & Integrity Audit").map((item: any) => {
          const activeSourceDetails = (item.source_details || []).filter((sd: any) => {
             if (['Temporal Analysis', 'University Anchor', 'Degree Match', 'Performance', 'Academic Audit', 'Grade Audit'].includes(sd.source) || sd.source.includes('Signal') || sd.source.includes('Detail')) return true;
             if (sd.source === 'Verification Bonus') return activeSources.includes('GitHub') && activeSources.includes('CV');
             return activeSources.includes(sd.source);
          });

          const ghSignal = activeSourceDetails.find((sd: any) => sd.source === 'GitHub')?.score || 0;
          const cvSignal = activeSourceDetails.find((sd: any) => sd.source === 'CV')?.score || 0;
          const liSignal = activeSourceDetails.find((sd: any) => sd.source === 'LinkedIn')?.score || 0;
          const recency = activeSourceDetails.find((sd: any) => sd.source === 'Temporal Analysis')?.score || 1.0;
          const activeRealSources = activeSourceDetails.filter((sd: any) => ['GitHub', 'CV', 'LinkedIn'].includes(sd.source));
          const consensusMult = activeRealSources.length > 1 ? 1.15 : 1.0;

          const allSignalScores = activeSourceDetails
            .filter((sd: any) => {
              const isSystem = ['Temporal Analysis', 'University Anchor', 'Degree Match', 'Performance', 'Academic Audit', 'Grade Audit'].some(sys => sd.source.includes(sys));
              return !isSystem && !sd.source.includes('Detail');
            })
            .map((sd: any) => sd.score || 0);

          let newItemScore = 0;
          if (item.recalculation_strategy === 'sum') {
            newItemScore = allSignalScores.reduce((acc: number, score: number) => acc + score, 0);
          } else {
            const baseSignal = allSignalScores.length > 0 ? Math.max(...allSignalScores) : 0;
            newItemScore = baseSignal * consensusMult * recency;
          }
          newItemScore = Math.min(1.0, newItemScore);
          
          metricTotalPoints += newItemScore;
          return { ...item, score: newItemScore, source_details: activeSourceDetails };
        }).filter((item: any) => item.source_details && item.source_details.length > 0);

        // Keep the original breakdown for rendering, but use validBreakdown for math
        newMetric.breakdown = newMetric.breakdown || [];

        const originalMetric = c.metrics[key] || {};
        
        // DYNAMIC RECALCULATION:
        // We calculate the metric score based on the filtered breakdown items.
        // If all 3 sources are active, we can trust the backend's aggregate if available,
        // but for toggling to work, we must derive it from the active source details.
        const isAllSourcesActive = activeSources.length === 3;
        
        // If the metric has items, we average their dynamically calculated scores
        let newMetricScore = validBreakdown.length > 0 
          ? Math.min(1.0, metricTotalPoints / validBreakdown.length) 
          : (isAllSourcesActive ? (originalMetric.score || 0) : 0);

        // APPLY INTEGRITY PENALTY (if applicable)
        // This ensures that even if sources are toggled, the keyword stuffing penalty
        // persists as long as the CV source is active (since stuffing is CV-based).
        if (originalMetric.integrity_penalty_applied && activeSources.includes('CV')) {
            const pVal = originalMetric.integrity_penalty_value || 0;
            newMetricScore = Math.max(0, newMetricScore - pVal);
            newMetric.integrity_penalty_applied = true;
            newMetric.integrity_penalty_value = pVal;
        }

        newMetric.score = newMetricScore;
        newMetric.breakdown = validBreakdown;
        
        // Use the backend's provided formula if available, otherwise reconstruct it
        if (originalMetric.technical_formula && isAllSourcesActive) {
            newMetric.technical_formula = originalMetric.technical_formula;
        } else if (validBreakdown.length === 1) {
            const item = validBreakdown[0];
            const li_s = activeSources.includes('LinkedIn') ? (item.source_details.find((sd: any) => sd.source.includes('LinkedIn'))?.score || 0) : 0;
            const cv_s = activeSources.includes('CV') ? (item.source_details.find((sd: any) => sd.source.includes('CV'))?.score || 0) : 0;
            const gh_s = activeSources.includes('GitHub') ? (item.source_details.find((sd: any) => sd.source.includes('GitHub'))?.score || 0) : 0;
            
            const recency = item.source_details.find((sd: any) => sd.source.includes('Temporal'))?.score || 1.0;
            const mult = item.source_details.filter((sd: any) => ['GitHub', 'CV', 'LinkedIn'].some(s => sd.source.includes(s))).length > 1 ? 1.15 : 1.0;
            
            if (newMetric.formula && newMetric.formula.includes('max(GH_Score, CV_Score)')) {
                newMetric.technical_formula = `max(${gh_s.toFixed(2)}, ${cv_s.toFixed(2)})${mult > 1 ? ' * 1.15' : ''}${recency !== 1.0 ? ' * ' + recency.toFixed(2) : ''} = ${item.score.toFixed(2)}`;
            } else if (newMetric.formula && newMetric.formula.includes('max(LinkedInSignal, CVSignal)')) {
                newMetric.technical_formula = `max(${li_s.toFixed(2)}, ${cv_s.toFixed(2)})${mult > 1 ? ' * 1.15' : ''} = ${item.score.toFixed(2)}`;
            }
        }

        dynamicMetrics[key] = newMetric;
        dynamicWeightedSum += newMetricScore * newMetric.weight;
        dynamicTotalWeight += newMetric.weight;
      });

      const finalDynamicScore = dynamicTotalWeight > 0 ? (dynamicWeightedSum / dynamicTotalWeight) : 0;
      const dynamicComputedScores: Record<string, number> = {};
      Object.entries(dynamicMetrics).forEach(([key, m]: [string, any]) => {
         dynamicComputedScores[key] = Math.round(m.score * 100);
      });

      return {
        id: c.candidate_id,
        name: c.name,
        email: c.email,
        computedScores: dynamicComputedScores,
        fullMetrics: dynamicMetrics,
        calculation_summary: {
           ...c.calculation_summary,
           weighted_sum: dynamicWeightedSum,
           total_weight: dynamicTotalWeight
        },
        total_score: finalDynamicScore,
        overallScore: Math.round(finalDynamicScore * 100)
      };
    });
  }, [rawResults, activeSources, visibleColKeys]);

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

  const closeReport = () => {
    setSelectedCandidate(null);
    setSelectedCandidateDetail(null);
    setHoveredItem(null);
  };

  const currentCandidate = useMemo(() => {
    if (!selectedCandidate || !candidates) return null;
    return candidates.find((c: any) => c.id === selectedCandidate.id);
  }, [selectedCandidate, candidates]);

  if (loading) return <LoadingScreen />;
  if (error) return <div className="p-20 text-center text-red-500 font-medium">{error}</div>;
  if (!rawResults) return null;

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 px-4 py-8 md:py-12">
      <DetailedReportModal 
        candidate={currentCandidate}
        candidateDetail={selectedCandidateDetail}
        onClose={closeReport}
        hoveredItem={hoveredItem}
        setHoveredItem={setHoveredItem}
        isBlindMode={isBlindMode}
        setIsBlindMode={setIsBlindMode}
      />

      <div className="max-w-[1400px] mx-auto space-y-8">
        <button onClick={() => router.push('/config/execute')} className="flex items-center text-sm font-medium text-zinc-500 hover:text-indigo-600 dark:text-zinc-400 dark:hover:text-indigo-400 transition-colors group">
          <svg className="w-4 h-4 mr-1 group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Ranking Engine
        </button>

        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 bg-white dark:bg-zinc-900 p-8 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest ${rawResults.is_snapshot ? 'bg-amber-600' : 'bg-indigo-600'} text-white shadow-sm`}>
                {rawResults.is_snapshot ? 'Historical Snapshot' : 'Live Analysis'}
              </span>
              <span className="text-zinc-400 text-xs font-medium">
                {rawResults.is_snapshot ? `Snapshot ID: ${rawResults.id.split('-')[0]}` : `Ranking Execution ID: ${configId}`}
              </span>
            </div>
            <h1 className="text-4xl font-black text-zinc-900 dark:text-zinc-50 tracking-tight">Intelligence Report</h1>
          </div>
          <div className="flex items-center gap-3">
             <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold ${rawResults.is_snapshot ? 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800' : 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800'} shadow-sm`}>
                <span className={`w-2 h-2 rounded-full ${rawResults.is_snapshot ? 'bg-amber-500' : 'bg-green-500 animate-pulse'}`} /> 
                {rawResults.is_snapshot ? `Static: ${new Date(rawResults.created_at).toLocaleString()}` : 'Computed & Live'}
             </span>
          </div>
        </div>

        <div className="space-y-4 pt-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
             <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
                <svg className="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Candidate Rankings
             </h2>
             
             <div className="flex items-center gap-2">
                <div className="relative" ref={sourcesRef}>
                  <button 
                    onClick={() => setSourcesOpen(!sourcesOpen)}
                    className="px-3 py-1.5 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-md text-sm font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-700 transition flex items-center gap-2 shadow-sm"
                  >
                    <svg className="w-4 h-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                    Sources: {activeSources.length}
                  </button>
                  {sourcesOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg shadow-xl z-20 py-2">
                      {['CV', 'GitHub', 'LinkedIn'].map(source => (
                        <label key={source} className="flex items-center px-4 py-2 hover:bg-zinc-50 dark:hover:bg-zinc-800 cursor-pointer transition-colors">
                          <input 
                            type="checkbox" 
                            checked={activeSources.includes(source)}
                            onChange={() => setActiveSources(prev => prev.includes(source) ? prev.filter(s => s !== source) : [...prev, source])}
                            className="rounded border-zinc-300 dark:border-zinc-700 text-indigo-600 focus:ring-indigo-500 w-4 h-4 shadow-sm"
                          />
                          <span className="ml-3 text-sm font-medium text-zinc-700 dark:text-zinc-300">{source}</span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 shadow-sm">
                  <label className="text-[10px] font-black uppercase tracking-widest text-zinc-500 cursor-pointer" htmlFor="blind-toggle">
                    Blind Mode
                  </label>
                  <button 
                    id="blind-toggle"
                    onClick={() => setIsBlindMode(!isBlindMode)}
                    className={`w-8 h-4 rounded-full transition-colors relative ${isBlindMode ? 'bg-indigo-600' : 'bg-zinc-300 dark:bg-zinc-600'}`}
                  >
                    <div className={`absolute top-0.5 w-3 h-3 bg-white rounded-full transition-all ${isBlindMode ? 'left-4.5' : 'left-0.5'}`} />
                  </button>
                </div>

                <div className="relative" ref={dropdownRef}>
                  <button 
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    className="w-full sm:w-auto px-3 py-1.5 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-md text-sm font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-700 transition flex items-center justify-between sm:justify-start gap-2 shadow-sm"
                  >
                    <div className="flex items-center gap-2 shrink-0">
                      <svg className="w-4 h-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" /></svg>
                      Config Metrics
                    </div>
                    <span className="bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300 py-0.5 px-1.5 rounded text-xs font-bold">{visibleMetrics.length}/{allMetricsInfo.length}</span>
                  </button>
                  {dropdownOpen && (
                    <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg shadow-xl z-20 py-2">
                      <div className="px-4 pb-2 mb-2 border-b border-zinc-100 dark:border-zinc-800">
                        <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Include in Table</p>
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
                                  onChange={() => setVisibleColKeys(prev => isVisible ? prev.filter(k => k !== m.key) : [...prev, m.key])}
                                  className="rounded border-zinc-300 dark:border-zinc-700 text-indigo-600 focus:ring-indigo-500 cursor-pointer shadow-sm w-4 h-4"
                                />
                                <span className={`text-sm font-medium transition-colors ${isVisible ? 'text-indigo-700 dark:text-indigo-400' : 'text-zinc-700 dark:text-zinc-300'}`}>{m.label}</span>
                              </div>
                              <span className="text-[10px] text-zinc-400 font-mono">P:{Math.round((1.2 - m.weight) / 0.2)}</span>
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
                    <th className="px-5 py-4 font-semibold min-w-[220px] group cursor-pointer hover:bg-zinc-100 dark:hover:bg-zinc-800/80 transition-colors" onClick={() => setSortConfig({key: 'name', direction: sortConfig.key === 'name' && sortConfig.direction === 'desc' ? 'asc' : 'desc'})}>
                       <div className="flex items-center gap-2">
                          Identity
                          {sortConfig.key === 'name' && (
                             <span className="text-indigo-500">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                          )}
                       </div>
                    </th>
                    <th className="px-5 py-4 font-bold text-indigo-700 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/10 border-x border-zinc-200 dark:border-zinc-800 w-32 group cursor-pointer hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-colors" onClick={() => setSortConfig({key: 'overallScore', direction: sortConfig.key === 'overallScore' && sortConfig.direction === 'desc' ? 'asc' : 'desc'})}>
                       <div className="flex items-center gap-2">
                          Combined
                          {sortConfig.key === 'overallScore' && (
                             <span className="text-indigo-500">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                          )}
                       </div>
                    </th>
                    {visibleMetrics.map(m => (
                      <th key={m.key} className="px-4 py-4 font-semibold group cursor-pointer hover:bg-zinc-100 dark:hover:bg-zinc-800/80 transition-colors border-r border-zinc-100 dark:border-zinc-800/50 relative max-w-[220px] whitespace-normal" onClick={() => setSortConfig({key: m.key, direction: sortConfig.key === m.key && sortConfig.direction === 'desc' ? 'asc' : 'desc'})}>
                         <div className="flex flex-col">
                            <div className="flex items-center gap-2">
                               <span className="leading-tight">{m.label}</span>
                               {sortConfig.key === m.key && (
                                  <span className="text-indigo-500 shrink-0">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                               )}
                            </div>
                            <span className="text-[10px] text-zinc-400 font-normal mt-1">Priority: {Math.round((1.2 - m.weight) / 0.2)}</span>
                         </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/60">
                  {sortedCandidates.map((cand, idx) => (
                    <tr key={cand.id} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/30 transition-colors">
                      <td className="px-5 py-4 text-center font-mono text-zinc-400 dark:text-zinc-500 text-xs border-r border-zinc-100 dark:border-zinc-800/60">{idx + 1}</td>
                      <td className="px-5 py-4">
                         <div className="flex items-center gap-3">
                            <div className="flex flex-col">
                               <span className="font-bold text-zinc-900 dark:text-zinc-100 uppercase tracking-tight">
                                 {isBlindMode ? `Candidate #${idx + 1}` : cand.name}
                               </span>
                               <span className="text-[10px] text-zinc-500">
                                 {isBlindMode ? "Email Redacted" : cand.email}
                               </span>
                            </div>
                            <button 
                              onClick={() => setSelectedCandidate(cand)}
                              className="ml-auto px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-800 text-[10px] font-bold uppercase tracking-wider hover:bg-indigo-600 hover:text-white transition-all shadow-sm"
                            >
                               Report
                            </button>
                         </div>
                      </td>
                      <td className="px-5 py-4 bg-indigo-50/30 dark:bg-indigo-900/5 border-x border-zinc-100 dark:border-zinc-800/60">
                         <div className="flex items-center gap-2">
                            <span className={`text-base font-black ${cand.calculation_summary?.integrity_penalty > 0 ? 'text-amber-600 dark:text-amber-500' : 'text-indigo-600 dark:text-indigo-400'}`}>
                              {cand.overallScore}%
                            </span>
                            {cand.calculation_summary?.integrity_penalty > 0 && (
                               <svg className="w-3.5 h-3.5 text-amber-500 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                               </svg>
                            )}
                         </div>
                      </td>
                      {visibleMetrics.map(m => {
                         const metricData = cand.fullMetrics[m.key];
                         const hasPenalty = metricData?.integrity_penalty_applied;
                         const score = cand.computedScores[m.key];
                         
                         return (
                          <td key={m.key} className="px-4 py-4 font-mono text-sm border-r border-zinc-100 dark:border-zinc-800/30 last:border-0">
                             <div className="flex items-center gap-2">
                                <span className={hasPenalty ? "text-rose-500 font-bold" : (score > 70 ? "text-green-500" : "text-zinc-600 dark:text-zinc-400")}>
                                   {score}%
                                </span>
                                {hasPenalty && (
                                   <svg className="w-3 h-3 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                   </svg>
                                )}
                             </div>
                          </td>
                         );
                      })}
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

export default function ConfigPage() {
  return (
    <Suspense fallback={<LoadingScreen />}>
      <RankingReport />
    </Suspense>
  );
}
