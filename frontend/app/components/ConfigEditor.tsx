'use client';

import { useState, useEffect } from 'react';

interface ConfigEditorProps {
  initialData?: {
    id?: string;
    name: string;
    job_id: string;
    batch_id: string;
    weights: Record<string, number>;
    active_metrics: Record<string, boolean>;
  };
  mode: 'create' | 'update';
  onSave: (data: any) => Promise<void>;
  isProcessing: boolean;
}

export default function ConfigEditor({ initialData, mode, onSave, isProcessing }: ConfigEditorProps) {
  const [availableRequirements, setAvailableRequirements] = useState<any[]>([]);
  const [availableBatches, setAvailableBatches] = useState<any[]>([]);
  const [selectedReq, setSelectedReq] = useState(initialData?.job_id || '');
  const [selectedBatch, setSelectedBatch] = useState(initialData?.batch_id || '');
  const [configName, setConfigName] = useState(initialData?.name || '');
  const [isLoading, setIsLoading] = useState(true);
  const [showReqModal, setShowReqModal] = useState(false);

  // 0 = Least Important, 1 = Most Important
  const [importance, setImportance] = useState<Record<string, number>>(initialData?.weights || {});

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [reqsRes, batchesRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/get-job-descriptions`),
          fetch(`${API_BASE_URL}/api/get-candidate-batches`)
        ]);

        if (reqsRes.ok) {
          const data = await reqsRes.json();
          setAvailableRequirements(data);
        }

        if (batchesRes.ok) {
          const data = await batchesRes.json();
          setAvailableBatches(data);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [API_BASE_URL]);

  // Update internal state if initialData changes (for update mode)
  useEffect(() => {
    if (initialData) {
      setSelectedReq(initialData.job_id);
      setSelectedBatch(initialData.batch_id);
      setConfigName(initialData.name);
      setImportance(initialData.weights);
    }
  }, [initialData]);

  const reqPreviewData = availableRequirements.find(r => r.id === selectedReq);
  const batchPreviewData = availableBatches.find(b => b.id === selectedBatch);

  const baseCriteria: { key: string; label: string; sources: string[] }[] = [
    { key: 'education', label: 'Educational Qualifications', sources: ['CV'] },
    { key: 'experience', label: 'Professional Experience Over Time', sources: ['CV', 'LinkedIn'] },
    { key: 'projects', label: 'Technical Projects & Contributions', sources: ['CV', 'GitHub', 'LinkedIn'] },
    { key: 'techSkills', label: 'Technical Skills & Tooling Depth', sources: ['CV', 'GitHub'] },
  ];

  const reqAdditional: { key: string; label: string; source: string; subSources?: string[] }[] = [];
  
  if (reqPreviewData?.metrics) {
    let metricIdx = 0;
    const seenLabels = new Set<string>();
    
    Object.entries(reqPreviewData.metrics).forEach(([category, data]: [string, any]) => {
      if (data.type === 'key-value' && Array.isArray(data.value)) {
        data.value.forEach((item: any) => {
          if (item.name && !seenLabels.has(item.name)) {
            seenLabels.add(item.name);
            reqAdditional.push({
              key: `req_${category.toLowerCase().replace(/[^a-z0-9]/g, '')}_${item.name.replace(/[^a-zA-Z0-9]/g, '_')}_${metricIdx++}`,
              label: item.name,
              source: 'JD'
            });
          }
        });
      } else if (data.type === 'list' && Array.isArray(data.value)) {
        data.value.forEach((item: any) => {
          const label = typeof item === 'string' ? item : (item.name || item.value);
          if (label && !seenLabels.has(label)) {
            seenLabels.add(label);
            reqAdditional.push({
              key: `req_${category.toLowerCase().replace(/[^a-z0-9]/g, '')}_${label.replace(/[^a-zA-Z0-9]/g, '_')}_${metricIdx++}`,
              label: label,
              source: 'JD'
            });
          }
        });
      }
    });
  }

  // Additional measures that are unique to the Candidate Batch
  // For now, we use a default set since batch_data doesn't store metrics
  const batchAdditional = (batchPreviewData?.additionalMeasures || []).map((measure: any) => ({
    key: `batch_${measure.name.replace(/[^a-zA-Z0-9]/g, '_')}`,
    label: measure.name,
    source: 'Candidate Data',
    subSources: measure.sources,
  }));

  // GitHub Specific Intelligence
  const githubIntelligence = [
    { key: 'intel_github_complexity', label: 'GitHub: Project Complexity & Architecture', sources: ['GitHub'] },
    { key: 'intel_github_alignment', label: 'GitHub: Ecosystem & Language Alignment', sources: ['GitHub'] },
    { key: 'intel_github_impact', label: 'GitHub: Repository Stars & Community Impact', sources: ['GitHub'] },
  ];

  // LinkedIn Specific Intelligence
  const linkedinIntelligence = [
    { key: 'intel_linkedin_extracurricular', label: 'LinkedIn: Extracurricular Activity & Presence', sources: ['CV', 'LinkedIn'] },
    { key: 'intel_linkedin_network', label: 'LinkedIn: Professional Network Size', sources: ['LinkedIn'] },
  ];
  
  const allCriteria = [
    ...reqAdditional,        // 1. JD Tags First
    ...baseCriteria,         // 2. CV & Overlaps Second
    ...batchAdditional,      // 3. Batch Extras
    ...githubIntelligence,   // 4. GitHub Third
    ...linkedinIntelligence, // 5. LinkedIn Last
  ];

  useEffect(() => {
    setImportance(prev => {
      const newState = { ...prev };
      allCriteria.forEach(c => {
        if (newState[c.key] === undefined) {
          newState[c.key] = 0.0;
        }
      });
      return newState;
    });
  }, [selectedReq, selectedBatch, reqAdditional.length, batchAdditional.length]);

  const allRatingsSet = allCriteria.every(item => 
    importance[item.key] !== undefined
  );

  const handleSave = () => {
    onSave({
      name: configName,
      job_id: selectedReq,
      batch_id: selectedBatch,
      weights: importance
    });
  };

  if (isLoading && mode === 'update' && !initialData) {
      return <div className="p-20 text-center">Loading configuration settings...</div>;
  }

  return (
    <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden flex flex-col">
      <div className="p-6 md:p-8 space-y-8 flex-1">
        
        {/* Job Description Selection */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
            <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 text-xs font-bold ring-1 ring-indigo-200 dark:ring-indigo-800">1</span>
            Select Job Description
          </h2>
          
          <div className="grid md:grid-cols-2 gap-4 items-start">
            <div className="bg-zinc-50 dark:bg-zinc-950/50 p-4 border border-zinc-200 dark:border-zinc-800 rounded-lg">
              <select
                value={selectedReq}
                onChange={(e) => setSelectedReq(e.target.value)}
                className="w-full bg-white dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 rounded-md py-2.5 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 mb-2"
              >
                <option value="" disabled>-- Choose a Job Description --</option>
                {availableRequirements.map((req) => (
                  <option key={req.id} value={req.id}>
                    {req.title}
                  </option>
                ))}
              </select>
            </div>

            {reqPreviewData && (
                <div className="bg-indigo-50 dark:bg-indigo-950/20 p-5 border border-indigo-100 dark:border-indigo-900/50 rounded-lg text-sm transition-all animate-in fade-in slide-in-from-top-2 relative">
                <h3 className="font-semibold text-indigo-900 dark:text-indigo-300 mb-3">Requirement Details</h3>
                
                <div className="grid grid-cols-2 gap-y-2 gap-x-4 mb-4 text-xs border-b border-indigo-100 dark:border-indigo-900/50 pb-3">
                  <div>
                    <span className="block text-indigo-600/70 dark:text-indigo-400/70 font-medium">Job Title</span>
                    <span className="font-semibold text-zinc-900 dark:text-zinc-100">{reqPreviewData.title}</span>
                  </div>
                  <div>
                    <span className="block text-indigo-600/70 dark:text-indigo-400/70 font-medium">Saved At</span>
                    <span className="font-semibold text-zinc-900 dark:text-zinc-100">{new Date(reqPreviewData.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="mb-4">
                  <span className="block text-indigo-600/70 dark:text-indigo-400/70 font-medium text-xs mb-1.5">Required Languages</span>
                  <div className="flex flex-wrap gap-1.5">
                    {reqPreviewData.metrics?.['Languages']?.value?.map((lang: string) => (
                      <span key={lang} className="px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-800 dark:text-indigo-300 rounded font-semibold text-xs border border-indigo-200 dark:border-indigo-800">
                        {lang}
                      </span>
                    )) || <span className="text-zinc-500 italic">None specified</span>}
                  </div>
                </div>

                <p className="text-zinc-700 dark:text-zinc-300 mb-4 leading-relaxed line-clamp-2">
                  {reqPreviewData.description}
                </p>
                
                <button 
                  onClick={() => setShowReqModal(true)}
                  className="text-indigo-600 dark:text-indigo-400 text-xs font-semibold hover:underline flex items-center gap-1"
                >
                  View Full Requirements
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        </div>

        <hr className="border-zinc-200 dark:border-zinc-800" />

        {/* Candidate Batch Selection */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
            <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 text-xs font-bold ring-1 ring-blue-200 dark:ring-blue-800">2</span>
            Select Candidate Batch
          </h2>
          
          <div className="grid md:grid-cols-2 gap-4 items-start">
            <div className="bg-zinc-50 dark:bg-zinc-950/50 p-4 border border-zinc-200 dark:border-zinc-800 rounded-lg">
              <select
                value={selectedBatch}
                onChange={(e) => setSelectedBatch(e.target.value)}
                className="w-full bg-white dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 rounded-md py-2.5 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 mb-2"
              >
                <option value="" disabled>-- Choose a Candidate Batch --</option>
                {availableBatches.map((batch) => (
                  <option key={batch.id} value={batch.id}>
                    {batch.batch_name} ({batch.candidate_ids?.length || 0} CVs)
                  </option>
                ))}
              </select>
            </div>

            {batchPreviewData && (
              <div className="bg-blue-50 dark:bg-blue-950/20 p-4 border border-blue-100 dark:border-blue-900/50 rounded-lg text-sm transition-all animate-in fade-in slide-in-from-top-2">
                <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">Batch Details</h3>
                <p className="text-zinc-700 dark:text-zinc-300 mb-3 leading-relaxed">
                  Sourced on {new Date(batchPreviewData.created_at).toLocaleDateString()}. Contains {batchPreviewData.candidate_ids?.length || 0} candidates.
                </p>
                <div className="text-xs text-zinc-500 dark:text-zinc-400">
                  <p className="font-semibold mb-1 text-zinc-900 dark:text-zinc-200">Batch ID:</p>
                  <p className="font-mono">{batchPreviewData.id}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Criteria Prioritization */}
        {selectedReq && selectedBatch && (
          <>
            <hr className="border-zinc-200 dark:border-zinc-800" />
            <div className="space-y-4 animate-in fade-in slide-in-from-top-4 duration-500">
              <div>
                <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-400 text-xs font-bold ring-1 ring-green-200 dark:ring-green-800">3</span>
                  Prioritize Matching Criteria
                </h2>
                <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400 ml-8">
                  Weight these criteria from <strong className="text-zinc-900 dark:text-zinc-200">1 (Low Priority)</strong> to <strong className="text-zinc-900 dark:text-zinc-200">5 (High Priority) </strong>, or leave empty to ignore.
                </p>
              </div>

              <div className="ml-8 bg-zinc-50 dark:bg-zinc-950/50 p-6 border border-zinc-200 dark:border-zinc-800 rounded-lg">
                <div className="space-y-6">
                  {allCriteria.map((item) => {
                    return (
                      <div key={item.key} className={`flex flex-col md:flex-row md:items-center justify-between gap-4 py-3 border-b border-zinc-200 dark:border-zinc-800 last:border-0 last:pb-0 ${item.source ? 'bg-indigo-50/50 dark:bg-indigo-900/10 -mx-4 px-4 rounded-md' : ''}`}>
                        <div className="flex flex-col gap-1.5">
                          <div className="flex items-center gap-3">
                            <span className="text-sm font-medium text-zinc-900 dark:text-zinc-200 flex flex-wrap items-center gap-2 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                              <span>{item.label}</span>
                              
                              {/* Standardized Source Badges */}
                              {item.sources?.map((src: string) => (
                                <span key={src} className={`
                                  px-2 py-0.5 text-[10px] uppercase font-bold rounded-md
                                  ${src === 'CV' ? 'bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300' : ''}
                                  ${src === 'GitHub' ? 'bg-zinc-900 text-zinc-100 dark:bg-zinc-100 dark:text-zinc-900 border border-zinc-200 dark:border-zinc-700' : ''}
                                  ${src === 'LinkedIn' ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/20' : ''}
                                `}>
                                  {src}
                                </span>
                              ))}

                              {/* Specialized Source Tags */}
                              {item.source === 'JD' && <span className="px-2 py-0.5 text-[10px] uppercase font-bold bg-indigo-600 text-white rounded-md shadow-sm shadow-indigo-500/20">JD</span>}
                              {item.subSources && <span className="px-2 py-0.5 text-[10px] uppercase font-bold bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded-md">Candidate: {item.subSources.join(', ')}</span>}
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-1.5 bg-white dark:bg-zinc-900 p-1.5 rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-sm animate-in fade-in slide-in-from-right-2">
                          {[1, 2, 3, 4, 5].map((val) => {
                            const weightValue = val * 0.2;
                            const currentWeight = importance[item.key] ?? 0.0;
                            const isSelected = Math.abs(currentWeight - weightValue) < 0.01;
                            
                            return (
                              <button
                                key={val}
                                onClick={() => setImportance({ ...importance, [item.key]: weightValue })}
                                className={`
                                  w-10 h-10 rounded-md text-sm font-bold transition-all flex items-center justify-center
                                  ${isSelected 
                                    ? 'bg-indigo-600 text-white shadow-md scale-110 z-10' 
                                    : 'bg-zinc-50 text-zinc-400 hover:bg-zinc-100 hover:text-zinc-600 dark:bg-zinc-800 dark:text-zinc-500 dark:hover:bg-zinc-700 dark:hover:text-zinc-300'}
                                `}
                                title={`Weight: ${weightValue.toFixed(1)}`}
                              >
                                {val}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </>
        )}

      </div>

      {/* Action Footer */}
      <div className="px-6 py-4 bg-zinc-50 dark:bg-zinc-800/50 border-t border-zinc-200 dark:border-zinc-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="w-full md:w-auto flex-1 max-w-sm flex items-center gap-3">
          <label htmlFor="configName" className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 whitespace-nowrap">
            Config Name
          </label>
          <input 
            id="configName"
            type="text" 
            placeholder="e.g. Senior ML Grad Protocol" 
            value={configName}
            onChange={(e) => setConfigName(e.target.value)}
            className="w-full bg-white dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        
        <button
          onClick={handleSave}
          disabled={!selectedReq || !selectedBatch || !allRatingsSet || !configName.trim() || isProcessing}
          className={`
            w-full md:w-auto px-6 py-2.5 rounded-md font-medium text-white transition-all shadow-sm
            flex items-center justify-center gap-2
            ${(!selectedReq || !selectedBatch || !allRatingsSet || !configName.trim() || isProcessing)
              ? 'bg-zinc-300 dark:bg-zinc-700 text-zinc-500 dark:text-zinc-400 cursor-not-allowed hidden-shadow'
              : 'bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-white active:scale-95'
            }
          `}
        >
          {isProcessing ? (
            <>
              <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {mode === 'create' ? 'Saving Config...' : 'Updating Config...'}
            </>
          ) : (
            mode === 'create' ? 'Save Configuration' : 'Update Configuration'
          )}
        </button>
      </div>

      {/* Requirement Details Modal */}
      {showReqModal && reqPreviewData && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 dark:bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden border border-zinc-200 dark:border-zinc-800 transform animate-in slide-in-from-bottom-10" role="dialog">
            <div className="flex justify-between items-center p-6 border-b border-zinc-100 dark:border-zinc-800">
              <h2 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">{reqPreviewData.title}</h2>
              <button onClick={() => setShowReqModal(false)} className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 p-1">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="flex flex-wrap gap-2 mb-6">
                <span className="px-3 py-1 bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 rounded-full text-xs font-medium border border-zinc-200 dark:border-zinc-700">
                  Saved: {new Date(reqPreviewData.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 mb-4 border-b border-zinc-100 dark:border-zinc-800 pb-2">Extracted Metrics</h3>
                <div className="space-y-4">
                  {Object.entries(reqPreviewData.metrics || {}).map(([category, data]: [string, any]) => (
                    <div key={category} className="flex flex-col sm:flex-row sm:items-baseline gap-2 sm:gap-4">
                      <span className="w-32 flex-shrink-0 font-semibold text-indigo-700 dark:text-indigo-400 text-sm">{category}</span>
                      <div className="flex flex-wrap gap-2">
                        {data.type === 'list' ? (
                          data.value.map((val: string) => (
                            <span key={val} className="px-2 py-1 bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-800 dark:text-zinc-200 rounded text-xs font-medium">{val}</span>
                          ))
                        ) : (
                          data.value.map((val: any, idx: number) => (
                            <span key={idx} className="px-2 py-1 bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-800 dark:text-zinc-200 rounded text-xs font-medium">{val.name || val.value}</span>
                          ))
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="text-sm text-zinc-600 dark:text-zinc-400 whitespace-pre-wrap leading-relaxed">{reqPreviewData.description}</div>
            </div>
            <div className="p-4 bg-zinc-50 dark:bg-zinc-800/50 border-t border-zinc-100 dark:border-zinc-800 text-right flex justify-end">
              <button onClick={() => setShowReqModal(false)} className="px-5 py-2 bg-white dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-md font-medium text-sm hover:bg-zinc-50 dark:hover:bg-zinc-800">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
