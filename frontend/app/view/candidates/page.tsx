'use client';

import { useState, useEffect } from 'react';
import CandidateDetailView from '../../components/CandidateDetailView';

interface Batch {
  id: string;
  batch_name: string;
  created_at: string;
  candidate_ids: string[];
}

interface Candidate {
  id: string;
  name: string;
  email: string;
  github_profile_id: string | null;
  linkedin_profile_id: string | null;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

export default function ViewCandidatesPage() {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [selectedBatchId, setSelectedBatchId] = useState<string>('');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>('');
  const [candidateDetail, setCandidateDetail] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-candidate-batches`);
      if (response.ok) {
        const data = await response.json();
        setBatches(data);
      }
    } catch (error) {
      console.error('Failed to fetch batches:', error);
    }
  };

  const handleBatchSelect = async (batchId: string) => {
    setSelectedBatchId(batchId);
    setSelectedCandidateId('');
    setCandidateDetail(null);
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-batch-candidates/${batchId}`);
      if (response.ok) {
        const data = await response.json();
        setCandidates(data);
      }
    } catch (error) {
      console.error('Failed to fetch candidates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCandidateSelect = async (candidateId: string) => {
    setSelectedCandidateId(candidateId);
    setDetailLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-candidate-detail/${candidateId}`);
      if (response.ok) {
        const data = await response.json();
        setCandidateDetail(data);
      }
    } catch (error) {
      console.error('Failed to fetch candidate details:', error);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-white dark:bg-zinc-950 px-6 py-12">
      <div className="max-w-[1600px] mx-auto space-y-12">
        <header className="space-y-2">
            <h1 className="text-4xl font-black dark:text-white uppercase tracking-tighter">Candidate Observer</h1>
            <p className="text-zinc-500 dark:text-zinc-400 font-medium">Deep-intelligence inspection for all extracted candidate records.</p>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-10 items-start">
            {/* Sidebar: Batch & Candidate Selection */}
            <div className="xl:col-span-1 space-y-8 sticky top-28">
                {/* Batch Selection */}
                <div className="p-8 rounded-[2rem] bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 space-y-6 shadow-sm">
                    <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-500">Selection Context</h2>
                    <div className="space-y-4">
                        <div className="space-y-1">
                            <label className="text-[9px] font-black uppercase tracking-wider text-zinc-400">Target Batch</label>
                            <select 
                                value={selectedBatchId}
                                onChange={(e) => handleBatchSelect(e.target.value)}
                                className="w-full bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-3 text-xs font-bold focus:ring-2 focus:ring-indigo-500/20 transition-all dark:text-white"
                            >
                                <option value="" disabled>Select a workspace batch...</option>
                                {batches.map(batch => (
                                    <option key={batch.id} value={batch.id}>{batch.batch_name}</option>
                                ))}
                            </select>
                        </div>

                        {selectedBatchId && (
                            <div className="space-y-2 pt-4">
                                <label className="text-[9px] font-black uppercase tracking-wider text-zinc-400 px-1 border-l-2 border-indigo-500 ml-1">Observing Candidates</label>
                                <div className="space-y-1.5 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                    {loading ? (
                                        <div className="py-8 text-center text-zinc-400 animate-pulse text-[10px] font-black uppercase">Initialising records...</div>
                                    ) : candidates.length === 0 ? (
                                        <div className="py-8 text-center text-zinc-400 text-[10px] font-black uppercase">No records found in batch</div>
                                    ) : (
                                        candidates.map(candidate => (
                                            <button
                                                key={candidate.id}
                                                onClick={() => handleCandidateSelect(candidate.id)}
                                                className={`
                                                    w-full text-left p-4 rounded-2xl border transition-all flex items-center justify-between group
                                                    ${selectedCandidateId === candidate.id 
                                                        ? 'bg-white dark:bg-zinc-800 border-indigo-500/50 shadow-lg shadow-indigo-500/5' 
                                                        : 'bg-transparent border-transparent hover:bg-white dark:hover:bg-zinc-900 hover:border-zinc-200 dark:hover:border-zinc-800'
                                                    }
                                                `}
                                            >
                                                <div className="min-w-0">
                                                    <p className={`text-xs font-black truncate ${selectedCandidateId === candidate.id ? 'text-indigo-600 dark:text-indigo-400' : 'text-zinc-700 dark:text-zinc-300'}`}>
                                                        {candidate.name}
                                                    </p>
                                                    <p className="text-[9px] font-bold text-zinc-400 truncate mt-0.5">{candidate.email}</p>
                                                </div>
                                                <div className="flex items-center gap-1 opacity-40 group-hover:opacity-100 transition-opacity">
                                                    {candidate.github_profile_id && <div className="w-1.5 h-1.5 rounded-full bg-zinc-900 dark:bg-zinc-100" />}
                                                    {candidate.linkedin_profile_id && <div className="w-1.5 h-1.5 rounded-full bg-[#0A66C2]" />}
                                                </div>
                                            </button>
                                        ))
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <div className="p-8 rounded-[2rem] bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 space-y-6 shadow-sm">
                    <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-500">Intelligence Key</h2>
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-1.5 h-1.5 rounded-full bg-zinc-900 dark:bg-zinc-100" />
                            <span className="text-[9px] font-black text-zinc-500 uppercase tracking-widest leading-none">GitHub Intelligence</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-1.5 h-1.5 rounded-full bg-[#0A66C2]" />
                            <span className="text-[9px] font-black text-zinc-500 uppercase tracking-widest leading-none">LinkedIn Profile</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content: Candidate Intelligence View */}
            <div className="xl:col-span-3 min-h-[800px] rounded-[3rem] bg-zinc-50 dark:bg-zinc-900/30 border border-zinc-200 dark:border-zinc-800 p-10 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-20 opacity-[0.02] pointer-events-none">
                    <svg className="w-96 h-96 text-indigo-500" fill="currentColor" viewBox="0 0 24 24"><path d="M15 12c0 1.657-1.343 3-3 3s-3-1.343-3-3 1.343-3 3-3 3 1.343 3 3z" /><path fillRule="evenodd" d="M12 5c-7 0-9 7-9 7s2 7 9 7 9-7 9-7-2-7-9-7zm0 12c-2.761 0-5-2.239-5-5s2.239-5 5-5 5 2.239 5 5-2.239 5-5 5z" clipRule="evenodd" /></svg>
                </div>

                {!selectedCandidateId ? (
                    <div className="h-full flex flex-col items-center justify-center text-center space-y-6 py-40">
                         <div className="w-20 h-20 bg-white dark:bg-zinc-950 rounded-[2rem] border border-zinc-200 dark:border-zinc-800 flex items-center justify-center shadow-xl">
                            <svg className="w-8 h-8 text-zinc-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                         </div>
                         <div className="space-y-1">
                             <h3 className="text-lg font-black dark:text-zinc-200 uppercase tracking-tighter">Observatory Standby</h3>
                             <p className="text-xs font-bold text-zinc-500 max-w-xs">Select a candidate from your workspace to initiate high-fidelity intelligence viewing.</p>
                         </div>
                    </div>
                ) : detailLoading ? (
                    <div className="h-full flex flex-col items-center justify-center space-y-6 py-40">
                         <div className="w-12 h-12 border-4 border-zinc-200 dark:border-zinc-800 border-t-indigo-600 rounded-full animate-spin" />
                         <p className="text-[10px] font-black uppercase tracking-widest text-zinc-400 animate-pulse">Synchronising source data...</p>
                    </div>
                ) : (
                    <div className="relative fade-in animate-in">
                         <CandidateDetailView candidate={candidateDetail} />
                    </div>
                )}
            </div>
        </div>
      </div>
    </main>
  );
}
