'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BsCalculator, BsChevronDown, BsInfoCircle, BsLayers } from 'react-icons/bs';
import { MetricAudit, AuditItem, CandidateDetail } from '@/types/audit';
import GitHubEvolutionChart from './GitHubEvolutionChart';
import ScoringAudit from './ScoringAudit';
import TemporalDecayAudit from './audit/TemporalDecayAudit';
import BayesianFusionAudit from './audit/BayesianFusionAudit';
import WeightedAverageAudit from './audit/WeightedAverageAudit';
import AuditSourceCard from './audit/AuditSourceCard';

interface DetailedReportModalProps {
  candidate: any; // PDF candidate object (unstructured)
  candidateDetail: CandidateDetail | null;
  onClose: () => void;
  hoveredItem: string | null;
  setHoveredItem: (item: string | null) => void;
  isBlindMode: boolean;
  setIsBlindMode: (val: boolean) => void;
}

export default function DetailedReportModal({ 
  candidate, 
  candidateDetail, 
  onClose, 
  hoveredItem, 
  setHoveredItem,
  isBlindMode,
  setIsBlindMode
}: DetailedReportModalProps) {
  const [activeTab, setActiveTab] = useState<'cv' | 'github' | 'linkedin' | 'formula'>('cv');
  const [cvViewMode, setCvViewMode] = useState<'original' | 'intelligence'>('original');
  const [expandedAudit, setExpandedAudit] = useState<string | null>(null);

  const renderRedactedText = (text: string) => {
    if (!isBlindMode) return text;
    return (
      <span className="relative inline-block px-2 group/redact cursor-help align-middle">
        <span className="bg-zinc-900 dark:bg-black text-transparent select-none rounded-[2px]">
          {text}
        </span>
        <span className="absolute inset-0 bg-zinc-900 dark:bg-black rounded-[2px]" />
      </span>
    );
  };
  
  const formatDate = (date: any) => {
    if (!date) return '';
    if (typeof date === 'string') return date;
    if (typeof date === 'object' && date.text) return date.text;
    return JSON.stringify(date);
  };

  const handleMetricClick = (key: string) => {
    setActiveTab('formula');
    setTimeout(() => {
      const element = document.getElementById(`formula-${key}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        element.classList.add('ring-2', 'ring-indigo-500', 'transition-all');
        setTimeout(() => element.classList.remove('ring-2', 'ring-indigo-500'), 2000);
      }
    }, 100);
  };

  const handleSidebarScroll = (key: string) => {
    const element = document.getElementById(`sidebar-${key}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      element.classList.add('bg-indigo-100', 'dark:bg-indigo-900/30', 'transition-all', 'duration-500');
      setTimeout(() => element.classList.remove('bg-indigo-100', 'dark:bg-indigo-900/30'), 1500);
    }
  };

  if (!candidate) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-zinc-950/70 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-white dark:bg-zinc-900 w-full max-w-[95%] h-[90vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col border border-zinc-200 dark:border-zinc-800">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-900/50">
          <div className="flex items-center gap-4">
            <div>
              <h2 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
                {isBlindMode ? "Candidate Profile" : candidate.name}
              </h2>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">Deep-Dive Match Intelligence</p>
            </div>
            <div className="hidden sm:flex items-center gap-2 bg-indigo-50 dark:bg-indigo-900/20 px-3 py-1 rounded-full border border-indigo-100 dark:border-indigo-800">
              <span className="text-sm font-black text-indigo-600 dark:text-indigo-400">{candidate.overallScore}%</span>
              <span className="text-[10px] text-indigo-500 font-bold uppercase tracking-tighter">Match</span>
            </div>
            <div className="ml-4 flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700">
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
          </div>
          <button onClick={onClose} className="p-2 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-full transition-colors">
            <svg className="w-5 h-5 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 flex overflow-hidden">
          {/* Left Sidebar: Intelligence Breakdown */}
          <div className="w-full md:w-[40%] border-r border-zinc-200 dark:border-zinc-800 overflow-y-auto p-6 space-y-8 bg-zinc-50/30 dark:bg-black/20">
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 uppercase tracking-wide flex items-center gap-2">
              <svg className="w-4 h-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Intelligence Report
            </h3>

            {/* Global Source Influence (Shapley Values) */}
            {candidate.shapley_values && (
              <div className="p-5 rounded-2xl bg-indigo-600 shadow-xl shadow-indigo-600/20 border border-indigo-500/50 text-white relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 blur-3xl group-hover:bg-white/20 transition-all duration-700" />
                
                <div className="relative z-10 space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-[10px] font-black uppercase tracking-[0.25em] text-indigo-100">Source Influence Breakdown</h4>
                    <span className="text-[9px] font-bold bg-white/20 px-2 py-0.5 rounded-full backdrop-blur-sm">XAI Audit</span>
                  </div>

                  <div className="space-y-3">
                    {(Object.entries(candidate.shapley_values || {}) as [string, number][])
                      .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
                      .map(([source, value], idx) => {
                        const pct = (value * 100).toFixed(1);
                        const isPositive = value >= 0;
                        return (
                          <div key={source} className="space-y-1.5">
                            <div className="flex justify-between items-center text-[11px] font-bold">
                              <span className="flex items-center gap-2">
                                <span className={`w-1.5 h-1.5 rounded-full ${idx === 0 ? 'bg-white' : 'bg-white/50'}`} />
                                {source}
                              </span>
                              <span className={isPositive ? 'text-white' : 'text-rose-200'}>
                                {isPositive ? '+' : ''}{pct}%
                              </span>
                            </div>
                            <div className="h-1.5 w-full bg-black/20 rounded-full overflow-hidden border border-white/5">
                              <motion.div 
                                initial={{ width: 0 }}
                                animate={{ width: `${Math.max(0, Math.min(100, Math.abs(value * 100)))}%` }}
                                transition={{ duration: 1, delay: 0.2 + idx * 0.1 }}
                                className={`h-full ${isPositive ? 'bg-white' : 'bg-rose-300'}`} 
                              />
                            </div>
                          </div>
                        );
                      })}
                  </div>

                  <p className="text-[9px] text-indigo-100/60 leading-relaxed font-medium">
                    * Contributions calculated via <b>Shapley Values</b> across 8 source permutations.
                  </p>
                </div>
              </div>
            )}

            <div className="space-y-6">
              {(Object.entries(candidate.fullMetrics || {}) as [string, MetricAudit][])
                .sort(([, a], [, b]) => {
                  if (a.score === 0 && (b.score || 0) !== 0) return 1;
                  if ((a.score || 0) !== 0 && b.score === 0) return -1;
                  return 0;
                })
                .map(([key, m]) => {
                const priority = Math.round((1.2 - (m.weight || 1.0)) / 0.2);
                const isSectionHovered = hoveredItem === key;
                return (
                  <div key={key} id={`sidebar-${key}`} className="space-y-3 rounded-xl transition-all duration-300">
                    <div 
                      className={`flex items-start justify-between cursor-pointer p-2 -mx-2 rounded-xl transition-all ${isSectionHovered ? 'bg-indigo-50/50 dark:bg-indigo-900/10' : ''}`}
                      onMouseEnter={() => setHoveredItem(key)}
                      onMouseLeave={() => setHoveredItem(null)}
                      onClick={() => handleMetricClick(key)}
                    >
                      <h4 className={`font-bold transition-colors flex items-center gap-2 ${m.integrity_penalty_applied ? 'text-rose-500' : (isSectionHovered ? 'text-indigo-600 dark:text-indigo-400' : 'text-zinc-900 dark:text-zinc-50')}`}>
                        {m.name}
                        {m.integrity_penalty_applied ? (
                          <span className="text-[10px] px-1.5 py-0.5 rounded border border-rose-200 dark:border-rose-800 text-rose-600 bg-rose-50 dark:bg-rose-900/20">W:{priority}</span>
                        ) : (
                          <span className="text-[10px] px-1.5 py-0.5 rounded border border-indigo-200 dark:border-indigo-800 text-indigo-600 bg-indigo-50 dark:bg-indigo-900/20">W:{priority}</span>
                        )}
                      </h4>
                      <div className={`text-lg font-black transition-colors ${m.integrity_penalty_applied ? 'text-rose-600 dark:text-rose-500' : (isSectionHovered ? 'text-indigo-600 dark:text-indigo-400' : 'text-zinc-900 dark:text-zinc-100')}`}>{Math.round(m.score * 100)}%</div>
                    </div>
                    
                    {/* Ecosystem Parent Audit Trail */}
                    {m.weighted_average_breakdown && (
                      <div className="mb-4 p-4 rounded-xl border border-indigo-500/30 bg-slate-900/50 relative overflow-hidden group">
                        <div className="flex items-center justify-between cursor-pointer" onClick={() => setExpandedAudit(expandedAudit === `${m.name}-parent` ? null : `${m.name}-parent`)}>
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-indigo-500/20">
                              <BsCalculator className="w-4 h-4 text-indigo-400" />
                            </div>
                            <div>
                              <p className="text-[10px] uppercase tracking-widest text-indigo-400 font-bold mb-0.5">{m.name} Audit</p>
                              <p className="text-sm font-mono text-slate-300">Result: {Math.round(m.score * 100)}%</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-tighter">View Math Trail</span>
                            <BsChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${expandedAudit === `${m.name}-parent` ? 'rotate-180' : ''}`} />
                          </div>
                        </div>

                        <WeightedAverageAudit m={m} expandedAudit={expandedAudit} />
                      </div>
                    )}

                    <div className="grid grid-cols-1 gap-3">
                      {(m.breakdown || []).map((item: AuditItem, i: number) => {
                        return (
                          <div 
                            key={i} 
                            className="p-4 rounded-xl border bg-white dark:bg-zinc-800/40 border-zinc-200 dark:border-zinc-800 transition-all cursor-default"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <div className="flex flex-col">
                                  <span className="text-sm font-bold text-zinc-900 dark:text-zinc-100">{item.item || item.component}</span>
                                  {item.score !== undefined && (
                                    <span className="text-[10px] font-black text-indigo-500/70 uppercase tracking-tighter">
                                      Component Score: {Math.round(item.score * 100)}%
                                    </span>
                                  )}
                                </div>
                                {item.confidence_label && (
                                  <div className="flex items-center gap-1.5">
                                    <span className={`text-[9px] font-black px-1.5 py-0.5 rounded-md uppercase tracking-widest ${
                                      item.confidence_label === 'High Confidence' 
                                        ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                                        : item.confidence_label === 'Medium Confidence'
                                          ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
                                          : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'
                                    }`}>
                                      {item.confidence_label}
                                    </span>
                                    
                                    {/* Unverified Tag - Shown if no GitHub source is present in the signals */}
                                    {!((item.source_details || []).some((sd: any) => sd.source === 'GitHub') || (item.sources || []).includes('GitHub')) && (
                                      <span className="text-[9px] font-black px-1.5 py-0.5 rounded-md uppercase tracking-widest bg-zinc-500/10 text-zinc-500 border border-zinc-500/20 flex items-center gap-1">
                                        <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                        </svg>
                                        Unverified
                                      </span>
                                    )}
                                  </div>
                                )}
                              </div>
                            </div>
                            <div className="text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-3 leading-relaxed">
                              {item.notes}
                              {item.notes?.includes('Beta') && (
                                <span className="ml-1.5 inline-flex items-center group relative cursor-help align-middle">
                                  <svg className="w-3.5 h-3.5 text-indigo-500/70 hover:text-indigo-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                  </svg>
                                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 w-64 p-4 bg-zinc-900/95 dark:bg-zinc-800 backdrop-blur-md text-white text-[10px] rounded-2xl opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none shadow-[0_20px_50px_rgba(0,0,0,0.5)] border border-white/10 z-50 leading-relaxed translate-y-2 group-hover:translate-y-0">
                                    <p className="font-black mb-1.5 text-indigo-400 uppercase tracking-widest text-[9px]">The Math Behind the Match</p>
                                    <p className="mb-2">MERIT uses a <b>Beta Distribution</b> to mathematically fuse evidence from multiple sources:</p>
                                    <ul className="space-y-1 opacity-90">
                                      <li>• <b>Alpha (α)</b>: Strength of supporting evidence (CV mentions, GitHub code density).</li>
                                      <li>• <b>Beta (β)</b>: Level of uncertainty or contradictory signals (skill decay, lack of verified code).</li>
                                    </ul>
                                    <p className="mt-2 pt-2 border-t border-white/5 font-medium italic text-zinc-400">Score = α / (α + β)</p>
                                  </div>
                                </span>
                              )}
                            </div>
                            {(item.source_details || []).length > 0 && (
                              <div className="grid grid-cols-1 gap-2">
                                {(item.source_details || []).map((sd: any, j: number) => (
                                  <AuditSourceCard key={j} sd={sd} j={j} />
                                ))}
                              </div>
                            )}

                            {/* Signal Processing Audit - Generic Container */}
                            {(item.alpha !== undefined || (item.source_details?.length || 0) > 0) && (
                              <div className="mt-4 p-4 rounded-xl border border-indigo-500/30 bg-slate-900/50 relative overflow-hidden group">
                                <div className="flex items-center justify-between cursor-pointer" onClick={() => setExpandedAudit(expandedAudit === `${m.name}-${i}` ? null : `${m.name}-${i}`)}>
                                  <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-lg bg-indigo-500/20">
                                      <BsCalculator className="w-4 h-4 text-indigo-400" />
                                    </div>
                                    <div>
                                      <p className="text-[10px] uppercase tracking-widest text-indigo-400 font-bold mb-0.5">{(item.item || item.component)} Verification Audit</p>
                                      <p className="text-sm font-mono text-slate-300">
                                        Result: {(item.score * 100).toFixed(0)}% 
                                        {item.influence !== undefined && (
                                          <span className="text-[10px] text-indigo-400 ml-2 font-black bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">
                                            Influence: {item.influence.toFixed(1)}
                                          </span>
                                        )}
                                        {item.alpha !== undefined && <span className="text-[10px] text-zinc-500 ml-2">(Bayesian α={item.alpha?.toFixed(2)})</span>}
                                      </p>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-tighter">View Math Trail</span>
                                    <BsChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${expandedAudit === `${m.name}-${i}` ? 'rotate-180' : ''}`} />
                                  </div>
                                </div>

                                {/* Expandable Step-by-Step Audit */}
                                <AnimatePresence>
                                  {expandedAudit === `${m.name}-${i}` && (
                                    <motion.div 
                                      initial={{ height: 0, opacity: 0 }}
                                      animate={{ height: 'auto', opacity: 1 }}
                                      exit={{ height: 0, opacity: 0 }}
                                      className="mt-4 pt-4 border-t border-slate-800 space-y-4"
                                    >
                                      <TemporalDecayAudit item={item} />

                                      {/* Phase 1: Source Normalisation */}
                                      <div className="space-y-3">
                                        <div className="flex justify-between items-center text-xs font-black text-indigo-300 uppercase tracking-[0.15em] border-b border-indigo-500/20 pb-2 mb-1">
                                          <span>Phase 1: Heuristic Normalisation</span>
                                        </div>
                                        {(item.source_details || []).map((sd: any, idx: number) => (
                                          <div key={`p1-${idx}`} className="flex flex-col gap-1.5 border-b border-white/5 pb-3">
                                            <div className="flex justify-between items-center text-[12px]">
                                              <span className="text-zinc-300 font-bold tracking-tight">{sd.source} Signal</span>
                                              <span className="text-indigo-400 font-mono font-black bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                                                Strength: {sd.score?.toFixed(2)}
                                              </span>
                                            </div>
                                            <div className="text-[11px] font-mono text-zinc-400/90 pl-3 border-l-2 border-indigo-500/30 leading-relaxed italic">
                                              {sd.derivation}
                                            </div>
                                            {(sd.source === 'CV' || sd.source === 'LinkedIn') && (
                                              <div className="mt-1 pl-3 text-[9px] font-bold text-amber-500/70 uppercase tracking-tight flex items-center gap-1.5">
                                                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                                </svg>
                                                Source Trust Anchor: Self-reported data capped at 0.8
                                              </div>
                                            )}
                                          </div>
                                        ))}
                                      </div>

                                      <BayesianFusionAudit item={item} />
                                    </motion.div>
                                  )}
                                </AnimatePresence>
                              </div>
                            )}
                          </div>
                        );
                      })}

                      {/* Final Metric Aggregator (for hybrid metrics) */}
                      {((m.breakdown?.length || 0) > 1) && (
                        <div className="mt-2 p-4 rounded-xl border-2 border-dashed border-indigo-500/20 bg-indigo-500/5">
                          <div className="flex items-center gap-2 mb-3">
                            <div className="p-1.5 rounded-lg bg-indigo-500/20">
                              <BsLayers className="w-3.5 h-3.5 text-indigo-400" />
                            </div>
                            <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">Final Metric Aggregation</span>
                          </div>
                          <div className="space-y-2">
                            {(m.breakdown || []).map((item: AuditItem, idx: number) => (
                              <div key={idx} className="flex justify-between items-center text-[11px] font-mono">
                                <span className="text-zinc-500">{item.item || item.component}:</span>
                                <span className="text-zinc-300">
                                  {Math.round((item.score || 0) * 100)}% × {item.weight?.toFixed(2) || (1 / (m.breakdown?.length || 1)).toFixed(2)}
                                </span>
                              </div>
                            ))}
                            <div className="pt-2 border-t border-indigo-500/20 flex justify-between items-center">
                              <span className="text-xs font-bold text-white">Aggregated Result:</span>
                              <span className="text-sm font-black text-indigo-400">
                                {Math.round(m.score * 100)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Content: Tabs & Visualization */}
          <div className="hidden md:flex flex-col w-[60%] bg-zinc-100 dark:bg-zinc-950 overflow-hidden">
            <div className="flex border-b border-zinc-200 dark:border-zinc-800">
              <button onClick={() => setActiveTab('cv')} className={`px-6 py-3 text-sm font-bold transition-colors ${activeTab === 'cv' ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white dark:bg-zinc-900' : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'}`}>Candidate CV</button>
              <button onClick={() => setActiveTab('github')} className={`px-6 py-3 text-sm font-bold transition-colors ${activeTab === 'github' ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white dark:bg-zinc-900' : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'}`}>GitHub Evidence</button>
              <button onClick={() => setActiveTab('linkedin')} className={`px-6 py-3 text-sm font-bold transition-colors ${activeTab === 'linkedin' ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white dark:bg-zinc-900' : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'}`}>LinkedIn Experience</button>
              <button onClick={() => setActiveTab('formula')} className={`px-6 py-3 text-sm font-bold transition-colors ${activeTab === 'formula' ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white dark:bg-zinc-900' : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'}`}>Score Formula</button>
            </div>

            <div className={`flex-1 overflow-hidden ${activeTab === 'cv' ? '' : 'overflow-y-auto p-8'}`}>
              {!candidateDetail ? (
                <div className="h-full flex items-center justify-center text-zinc-400 animate-pulse font-medium">Extracting source profiles...</div>
              ) : (
                <>
                  {activeTab === 'cv' && (
                    <div className="h-full relative flex flex-col group/cv">
                      <div className="absolute top-6 right-6 z-10 flex bg-white dark:bg-zinc-800 p-1 rounded-xl shadow-2xl border border-zinc-200 dark:border-zinc-700 opacity-0 group-hover/cv:opacity-100 transition-opacity duration-300">
                        <button onClick={() => setCvViewMode('original')} className={`px-4 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${cvViewMode === 'original' ? 'bg-indigo-600 text-white shadow-lg' : 'text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200'}`}>Original Doc</button>
                        <button onClick={() => setCvViewMode('intelligence')} className={`px-4 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${cvViewMode === 'intelligence' ? 'bg-indigo-600 text-white shadow-lg' : 'text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200'}`}>AI Evidence</button>
                      </div>
                      {cvViewMode === 'original' ? (
                        <div className="relative w-full h-full overflow-hidden">
                          <iframe 
                            src={`${candidateDetail.cv_url}#view=FitH`} 
                            className={`w-full h-full border-none bg-zinc-900 transition-all duration-700 ${isBlindMode ? 'blur-xl grayscale scale-105' : ''}`} 
                            title="Candidate CV" 
                          />
                          {isBlindMode && (
                            <div className="absolute inset-0 z-20 flex items-center justify-center bg-zinc-950/20 backdrop-blur-[2px] animate-in fade-in zoom-in duration-500">
                              <div className="bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl p-10 rounded-[2.5rem] shadow-[0_32px_64px_-16px_rgba(0,0,0,0.3)] border border-white/20 dark:border-zinc-800/50 text-center max-sm mx-4 transform transition-all hover:scale-[1.02]">
                                <div className="w-20 h-20 bg-indigo-500/10 rounded-full flex items-center justify-center mx-auto mb-6 ring-8 ring-indigo-500/5">
                                  <svg className="w-10 h-10 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 00-2 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                  </svg>
                                </div>
                                <h3 className="text-xl font-black text-zinc-900 dark:text-zinc-100 mb-3 tracking-tight">Identity Mask Active</h3>
                                <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed font-medium">
                                  To ensure an <b>unbiased evaluation</b>, the original document is visually restricted. Please use the <span className="text-indigo-600 dark:text-indigo-400 font-bold">AI Evidence</span> engine to audit skills.
                                </p>
                                <button 
                                  onClick={() => setCvViewMode('intelligence')}
                                  className="mt-8 w-full px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl text-xs font-black uppercase tracking-[0.2em] transition-all shadow-xl shadow-indigo-500/20 active:scale-95"
                                >
                                  Switch to AI Evidence
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="flex-1 bg-zinc-100 dark:bg-black/40 overflow-y-auto p-8 md:p-12">
                          <div className="max-w-[850px] mx-auto bg-white dark:bg-zinc-900 shadow-2xl rounded-sm border border-zinc-200 dark:border-zinc-800 min-h-[1100px] p-12 md:p-20 relative overflow-hidden font-serif">
                            <div className="absolute top-0 left-0 w-full h-1.5 bg-indigo-600" />
                            
                            {/* CV Header */}
                            <div className="border-b-2 border-zinc-900 dark:border-white pb-8 mb-10 text-center">
                              <h2 className="text-4xl font-black uppercase tracking-tighter mb-4 text-zinc-900 dark:text-white">
                                {renderRedactedText(candidateDetail.name || "Candidate Identity")}
                              </h2>
                              <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500">
                                <span className="flex items-center gap-2">
                                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2-2v10a2 2 0 002 2z" /></svg>
                                  {renderRedactedText(candidateDetail.email || "email@redacted.com")}
                                </span>
                                <span className="flex items-center gap-2">
                                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                                  {renderRedactedText(candidateDetail.phone || "+44 000 000 000")}
                                </span>
                              </div>
                            </div>

                            {/* Professional Experience Section */}
                            {(candidateDetail.cv_experience?.length || 0) > 0 && (
                              <section className="mb-12">
                                <h3 className="text-xs font-black uppercase tracking-[0.35em] text-indigo-600 dark:text-indigo-400 mb-8 border-b border-zinc-100 dark:border-zinc-800 pb-2">Professional Experience</h3>
                                <div className="space-y-10">
                                  {(candidateDetail.cv_experience || []).map((exp: any, i: number) => (
                                    <div key={i} className="relative group/exp">
                                      <div className="flex justify-between items-baseline mb-2">
                                        <h4 className="text-lg font-black text-zinc-900 dark:text-zinc-50 tracking-tight group-hover/exp:text-indigo-600 transition-colors">{exp.name}</h4>
                                        <span className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">{exp.start_date} — {exp.end_date}</span>
                                      </div>
                                      <p className="text-sm font-bold text-zinc-500 mb-4 italic leading-relaxed">{exp.subtitle}</p>
                                      <p className="text-[14px] leading-[1.7] text-zinc-600 dark:text-zinc-400 antialiased">{exp.summary}</p>
                                    </div>
                                  ))}
                                </div>
                              </section>
                            )}

                            {/* Education Section */}
                            {(candidateDetail.cv_education?.length || 0) > 0 && (
                              <section className="mb-12">
                                <h3 className="text-xs font-black uppercase tracking-[0.35em] text-indigo-600 dark:text-indigo-400 mb-8 border-b border-zinc-100 dark:border-zinc-800 pb-2">Education</h3>
                                <div className="grid grid-cols-1 gap-8">
                                 {(candidateDetail.cv_education || []).map((edu: any, i: number) => (
                                    <div key={i} className="flex justify-between items-start group/edu">
                                      <div className="space-y-1">
                                        <h4 className="text-[16px] font-black text-zinc-900 dark:text-zinc-50 tracking-tight">
                                          {isBlindMode ? (
                                            <span className="bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-[10px] text-zinc-400 font-bold uppercase tracking-widest">Institution Redacted for Bias Mitigation</span>
                                          ) : edu.school_name}
                                        </h4>
                                        <p className="text-sm font-bold text-zinc-500">{edu.degree}</p>
                                      </div>
                                      <div className="text-right shrink-0">
                                        <div className="text-[10px] font-black text-zinc-400 uppercase tracking-widest mb-2">{edu.start_date} — {edu.end_date}</div>
                                        {edu.grade && (
                                          <span className="inline-block px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 text-[10px] font-black uppercase tracking-wider ring-1 ring-indigo-100 dark:ring-indigo-900/30">
                                            {edu.grade}
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </section>
                            )}

                            {/* Projects Section */}
                            {(candidateDetail.projects_history?.length || 0) > 0 && (
                              <section>
                                <h3 className="text-xs font-black uppercase tracking-[0.35em] text-indigo-600 dark:text-indigo-400 mb-8 border-b border-zinc-100 dark:border-zinc-800 pb-2">Technical Projects & Research</h3>
                                <div className="space-y-8">
                                  {(candidateDetail.projects_history || []).filter((p: any) => (p.title || p.name) && (p.title !== 'None' && p.name !== 'None')).map((proj: any, i: number) => {
                                    const projTitle = proj.title || proj.name || "Untitled Project";
                                    const projDesc = proj.description || proj.summary || "";
                                    
                                    const ghMatch = candidateDetail.github_projects?.find((gh: any) => {
                                      if (!projTitle || !gh.name) return false;
                                      const title = projTitle.toLowerCase();
                                      const ghName = gh.name.toLowerCase();
                                      const desc = projDesc.toLowerCase();
                                      return title.includes(ghName) || ghName.includes(title) || desc.includes(ghName);
                                    });

                                    return (
                                      <div key={i} className="group/proj relative">
                                        <div className="flex justify-between items-start mb-2">
                                          <h4 className="text-[16px] font-black text-zinc-900 dark:text-zinc-50 tracking-tight">{projTitle}</h4>
                                          {ghMatch ? (
                                            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-black dark:bg-white text-white dark:text-black text-[9px] font-black uppercase tracking-widest shadow-lg animate-in fade-in slide-in-from-right-4 duration-500">
                                              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
                                              Verified GitHub Signal
                                            </div>
                                          ) : (
                                            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-zinc-500 text-[9px] font-black uppercase tracking-widest animate-in fade-in slide-in-from-right-2 duration-700">
                                              {/(university|college|course|laboratory|lab|assignment|dissertation|thesis|module|student|coursework|academic)/i.test(`${projTitle} ${projDesc}`) 
                                                ? "Academic / University Research" 
                                                : "Proprietary / Private Project"}
                                            </div>
                                          )}
                                        </div>
                                        <p className="text-[14px] leading-[1.7] text-zinc-600 dark:text-zinc-400 antialiased mb-4">{projDesc}</p>
                                        
                                        {ghMatch && (
                                          <div className="bg-zinc-50 dark:bg-zinc-950/50 rounded-xl border border-zinc-100 dark:border-zinc-800 p-5 mt-2 transition-all group-hover/proj:border-indigo-500/30">
                                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
                                              <div className="space-y-1">
                                                <div className="text-[9px] font-black uppercase tracking-widest text-zinc-400">Complexity</div>
                                                <div className="text-sm font-black text-zinc-900 dark:text-zinc-100">{ghMatch.lines?.toLocaleString() || '---'} LoC</div>
                                              </div>
                                              <div className="space-y-1">
                                                <div className="text-[9px] font-black uppercase tracking-widest text-zinc-400">Activity</div>
                                                <div className="text-sm font-black text-zinc-900 dark:text-zinc-100">{ghMatch.commits || '---'} Commits</div>
                                              </div>
                                              <div className="space-y-1">
                                                <div className="text-[9px] font-black uppercase tracking-widest text-zinc-400">Traction</div>
                                                <div className="text-sm font-black text-zinc-900 dark:text-zinc-100">★ {ghMatch.stars || 0} / {ghMatch.forks || 0}</div>
                                              </div>
                                              <div className="space-y-1">
                                                <div className="text-[9px] font-black uppercase tracking-widest text-zinc-400">Stack</div>
                                                <div className="text-xs font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-tight">{ghMatch.language || 'Mixed'}</div>
                                              </div>
                                            </div>
                                            
                                            {ghMatch.languages_distribution && Object.keys(ghMatch.languages_distribution).length > 0 && (
                                              <div className="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800">
                                                <div className="flex h-1.5 w-full rounded-full overflow-hidden bg-zinc-200 dark:bg-zinc-800">
                                                  {(Object.entries(ghMatch.languages_distribution || {}) as [string, number][]).map(([lang, pct], idx) => (
                                                    <div 
                                                      key={lang} 
                                                      style={{ width: `${pct}%`, backgroundColor: `hsl(${idx * 40}, 70%, 60%)` }}
                                                      className="h-full transition-all"
                                                      title={`${lang}: ${pct}%`}
                                                    />
                                                  ))}
                                                </div>
                                                <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2">
                                                  {(Object.entries(ghMatch.languages_distribution || {}) as [string, number][]).slice(0, 4).map(([lang, pct]) => (
                                                    <div key={lang} className="flex items-center gap-1.5">
                                                      <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: `hsl(${Object.keys(ghMatch.languages_distribution).indexOf(lang) * 40}, 70%, 60%)` }} />
                                                      <span className="text-[9px] font-bold text-zinc-500">{lang} {pct}%</span>
                                                    </div>
                                                  ))}
                                                </div>
                                              </div>
                                            )}
                                          </div>
                                        )}
                                      </div>
                                    );
                                  })}
                                </div>
                              </section>
                            )}

                            {/* Blind Mode Watermark */}
                            {isBlindMode && (
                              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rotate-[-35deg] pointer-events-none opacity-[0.03] select-none">
                                <span className="text-[120px] font-black uppercase tracking-[0.5em] text-zinc-900 dark:text-white whitespace-nowrap">Anonymised Evidence</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'github' && (
                    <div className="space-y-6">
                      <div className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm flex items-center gap-6">
                        <div className={`w-16 h-16 rounded-full ring-2 ring-indigo-500/20 overflow-hidden bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center`}>
                          {isBlindMode ? (
                            <svg className="w-8 h-8 text-zinc-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" /></svg>
                          ) : (
                            <img src={candidateDetail.github_profile?.avatar_url} className="w-full h-full object-cover" alt="GH" />
                          )}
                        </div>
                        <div>
                          <h4 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
                            {isBlindMode ? "Engineering Contributor" : (candidateDetail.github_profile?.name || candidateDetail.github_profile?.username)}
                          </h4>
                          <div className="flex items-center gap-4 mt-1 text-xs font-bold text-zinc-500">
                            <span>★ {candidateDetail.github_profile?.total_stars} stars</span>
                            <span>⚡ {candidateDetail.github_profile?.total_commits} commits</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                        <h4 className="text-[10px] font-black uppercase tracking-widest text-zinc-400 mb-4">Technical Breadth (LoC %)</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                          {candidateDetail.github_profile?.languages?.map((l: any) => (
                            <div key={l.label} className="space-y-1">
                              <div className="flex justify-between text-[11px] font-bold">
                                <span className="text-zinc-600">{l.label}</span>
                                <span className="text-zinc-400">{l.pct}%</span>
                              </div>
                              <div className="h-1.5 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
                                <div className="h-full bg-indigo-600" style={{ width: `${l.pct}%` }} />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <GitHubEvolutionChart history={candidateDetail.github_profile?.language_history || []} />

                      <div className="grid grid-cols-1 gap-4">
                        {[...(candidateDetail.github_projects || [])].sort((a, b) => (b.stars || 0) - (a.stars || 0)).map((repo: any) => (
                          <div key={repo.id} className="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800">
                            <div className="flex justify-between items-start mb-2">
                              <h5 className="font-bold text-sm text-zinc-900 dark:text-zinc-100">{repo.name}</h5>
                              <span className="text-[10px] font-black text-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 px-2 py-0.5 rounded-full">{repo.language}</span>
                            </div>
                            <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2">{repo.description}</p>
                          </div>
                        ))}
                      </div>

                      {!candidateDetail.github_profile && (
                        <div className="p-12 text-center bg-zinc-50 dark:bg-zinc-950/20 rounded-3xl border border-zinc-100 dark:border-zinc-800 border-dashed">
                          <svg className="w-12 h-12 text-zinc-300 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                          </svg>
                          <h3 className="text-sm font-black text-zinc-900 dark:text-zinc-50 uppercase tracking-widest">No GitHub Profile Linked</h3>
                          <p className="text-xs text-zinc-500 mt-2">Open source contributions and technical evolution data are unavailable for this profile.</p>
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'linkedin' && (
                    <div className="space-y-6">
                      <div className="p-8 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                        <div className="flex items-center gap-6 mb-6">
                          <div className="w-20 h-20 rounded-2xl bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center ring-4 ring-indigo-500/10 shadow-xl overflow-hidden">
                            {isBlindMode ? (
                              <svg className="w-10 h-10 text-zinc-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" /></svg>
                            ) : (
                              <img src={candidateDetail.linkedin_profile?.profile_photo} className="w-full h-full object-cover" alt="LI" />
                            )}
                          </div>
                          <div className="space-y-1">
                            <h4 className="text-2xl font-black text-zinc-900 dark:text-zinc-50">
                              {isBlindMode ? "Professional Identity" : candidateDetail.linkedin_profile?.full_name}
                            </h4>
                            <p className="text-sm font-bold text-indigo-600 dark:text-indigo-400">{candidateDetail.linkedin_profile?.headline}</p>
                            <div className="flex items-center gap-3 text-[10px] font-black text-zinc-400 uppercase tracking-widest pt-1">
                              <span>{candidateDetail.linkedin_profile?.connections || 0} Connections</span>
                              <span className="w-1 h-1 rounded-full bg-zinc-300 dark:bg-zinc-700" />
                              <span>{candidateDetail.linkedin_profile?.followers || 0} Followers</span>
                            </div>
                          </div>
                        </div>
                        {candidateDetail.linkedin_profile?.about && (
                          <p className="text-sm text-zinc-600 dark:text-zinc-400 italic border-l-2 border-indigo-500/20 pl-4 py-1 leading-relaxed">
                            "{candidateDetail.linkedin_profile?.about}"
                          </p>
                        )}
                      </div>

                      {/* Skills Grid */}
                      {((candidateDetail.linkedin_profile?.skills?.length || 0) > 0) && (
                        <div className="p-8 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                          <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 mb-6 flex items-center gap-2">
                             Professional Endorsements
                             <span className="text-indigo-500">•</span>
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {candidateDetail.linkedin_profile?.skills?.map((skill: string, i: number) => (
                              <span key={i} className="px-3 py-1.5 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg text-[10px] font-black text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-800 uppercase tracking-tight">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="space-y-4">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 px-2">Professional Experience</h4>
                        {(candidateDetail.linkedin_experience || []).map((exp: any) => (
                          <div key={exp.id} className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800">
                            <div className="flex justify-between items-start mb-4">
                              <div>
                                <h4 className="font-bold text-zinc-900 dark:text-zinc-50">{exp.position}</h4>
                                <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">{exp.company_name}</span>
                              </div>
                              <span className="text-[10px] font-mono text-zinc-400">{formatDate(exp.start_date)} — {formatDate(exp.end_date) || 'Present'}</span>
                            </div>
                            <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">{exp.description}</p>
                          </div>
                        ))}
                      </div>
                      
                      <div className="space-y-4">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 px-2">Featured Projects</h4>
                        <div className="grid grid-cols-1 gap-4">
                          {(candidateDetail.linkedin_projects || []).map((proj: any, i: number) => (
                            <div key={i} className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                              <div className="flex justify-between items-start mb-2">
                                <h5 className="font-bold text-sm text-zinc-900 dark:text-zinc-50">{proj.title}</h5>
                                <span className="text-[10px] font-mono text-zinc-400">{formatDate(proj.start_date)} — {formatDate(proj.end_date)}</span>
                              </div>
                              <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">{proj.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 px-2">Certifications & Credentials</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          {(candidateDetail.linkedin_certifications || []).map((cert: any, i: number) => (
                            <div key={i} className="p-4 bg-zinc-50 dark:bg-zinc-800/30 rounded-xl border border-zinc-200 dark:border-zinc-800 flex items-center gap-4">
                              <div className="w-10 h-10 rounded-lg bg-white dark:bg-zinc-900 flex items-center justify-center border border-zinc-200 dark:border-zinc-700 shrink-0">
                                <svg className="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04kM12 20.944a11.955 11.955 0 01-8.618-3.04m17.236 0a11.955 11.955 0 01-8.618 3.04" />
                                </svg>
                              </div>
                              <div>
                                <h5 className="text-xs font-bold text-zinc-900 dark:text-zinc-50 leading-tight">{cert.title}</h5>
                                <p className="text-[10px] text-zinc-500 mt-1">{cert.issuer || 'Verified Credential'}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 px-2">Volunteering & Community</h4>
                        <div className="grid grid-cols-1 gap-4">
                          {(candidateDetail.linkedin_volunteering || []).map((vol: any, i: number) => (
                            <div key={i} className="p-4 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm flex justify-between items-center">
                              <div>
                                <h5 className="text-xs font-bold text-zinc-900 dark:text-zinc-50">{vol.position}</h5>
                                <p className="text-[10px] text-zinc-500 mt-0.5">{vol.organization || 'Community Program'}</p>
                              </div>
                              <span className="text-[10px] font-mono text-zinc-400">{formatDate(vol.start_date)} — {formatDate(vol.end_date) || 'Present'}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 px-2">Academic Credentials</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          {(candidateDetail.cv_education || []).map((edu: any, i: number) => (
                            <div key={i} className="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm group/edu hover:border-indigo-500/50 transition-all">
                              <h5 className="font-bold text-sm text-zinc-900 dark:text-zinc-100 group-hover/edu:text-indigo-600 transition-colors">
                                {isBlindMode ? "Academic Institution" : edu.school_name}
                              </h5>
                              <p className="text-xs text-indigo-600 dark:text-indigo-400 mt-1 font-bold">{edu.degree}</p>
                              <div className="mt-3 pt-3 border-t border-zinc-100 dark:border-zinc-800 flex justify-between items-center">
                                <span className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">{formatDate(edu.start_date)} — {formatDate(edu.end_date)}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      {!candidateDetail.linkedin_profile && (
                        <div className="p-12 text-center bg-zinc-50 dark:bg-zinc-950/20 rounded-3xl border border-zinc-100 dark:border-zinc-800 border-dashed">
                          <svg className="w-12 h-12 text-zinc-300 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.826a4 4 0 015.656 0l4 4a4 4 0 01-5.656 5.656l-1.101-1.101" />
                          </svg>
                          <h3 className="text-sm font-black text-zinc-900 dark:text-zinc-50 uppercase tracking-widest">No LinkedIn Profile Found</h3>
                          <p className="text-xs text-zinc-500 mt-2">Professional experience was extracted exclusively from the CV for this candidate.</p>
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'formula' && (
                    <ScoringAudit 
                      candidate={candidate} 
                      onMetricClick={handleSidebarScroll}
                    />
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
