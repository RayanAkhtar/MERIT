'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  IoChevronBack, IoPeopleOutline, IoMailOutline, IoCallOutline, 
  IoLogoGithub, IoLogoLinkedin, IoTrashOutline, IoSaveOutline,
  IoCheckmarkCircleOutline, IoEyeOutline, IoCloudUploadOutline, IoCloseOutline
} from 'react-icons/io5';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

interface CandidateBatch {
  id: string;
  batch_name: string;
  candidate_ids: string[];
  created_at: string;
}

interface Candidate {
  id: string;
  name: string;
  email: string;
  phone: string;
  source_links: any;
  github_url?: string;
  linkedin_url?: string;
  cv_url?: string;
}

export default function UpdateCandidatesPage() {
  const [batches, setBatches] = useState<CandidateBatch[]>([]);
  const [selectedBatch, setSelectedBatch] = useState<CandidateBatch | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isCandidatesLoading, setIsCandidatesLoading] = useState<boolean>(false);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [deleteTarget, setDeleteTarget] = useState<{ 
    type: 'batch' | 'candidate', 
    id: string, 
    name: string,
    count?: number
  } | null>(null);
  const [status, setStatus] = useState<{ id: string, message: string, type: 'success' | 'error' } | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isUpdatingCV, setIsUpdatingCV] = useState<string | null>(null);
  const [isDeletingCandidate, setIsDeletingCandidate] = useState<string | null>(null);

  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-candidate-batches`);
      if (response.ok) {
        const data = await response.json();
        setBatches(data);
      }
    } catch (error) {
      console.error('Error fetching batches:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBatchSelect = async (batch: CandidateBatch) => {
    if (deleteTarget) setDeleteTarget(null);
    setSelectedBatch(batch);
    setIsCandidatesLoading(true);
    setCandidates([]);
    setStatus(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-batch-candidates/${batch.id}`);
      if (response.ok) {
        const data = await response.json();
        // Map source_links to individual fields for easier editing
        const mapped = data.map((c: any) => ({
          ...c,
          name: c.name || '',
          email: c.email || '',
          phone: c.phone || '',
          github_url: c.source_links?.github?.[0] || '',
          linkedin_url: c.source_links?.linkedin?.[0] || ''
        }));
        setCandidates(mapped);
      }
    } catch (error) {
      console.error('Error fetching candidates:', error);
    } finally {
      setIsCandidatesLoading(false);
    }
  };

  const handleFieldChange = (candidateId: string, field: string, value: string) => {
    setCandidates(prev => prev.map(c => 
      c.id === candidateId ? { ...c, [field]: value } : c
    ));
  };

  const handleUpdateCandidate = async (candidate: Candidate) => {
    setSavingId(candidate.id);
    setStatus(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/update-candidate/${candidate.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: candidate.name,
          email: candidate.email,
          phone: candidate.phone,
          github_url: candidate.github_url,
          linkedin_url: candidate.linkedin_url
        }),
      });

      if (response.ok) {
        setStatus({ id: candidate.id, message: 'Candidate info updated!', type: 'success' });
        setTimeout(() => setStatus(null), 3000);
      } else {
        setStatus({ id: candidate.id, message: 'Failed to update.', type: 'error' });
      }
    } catch (error) {
      setStatus({ id: candidate.id, message: 'Network error.', type: 'error' });
    } finally {
      setSavingId(null);
    }
  };

  const handleDeleteBatch = async () => {
    if (!deleteTarget || deleteTarget.type !== 'batch') return;

    setIsDeleting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/delete-candidate-batch/${deleteTarget.id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setCandidates([]);
        setSelectedBatch(null);
        setDeleteTarget(null);
        fetchBatches();
      } else {
        alert('Deletion failed.');
      }
    } catch (error) {
      alert('Network error occurred.');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleUpdateCV = async (candidateId: string, file: File) => {
    setIsUpdatingCV(candidateId);
    setStatus({ id: candidateId, message: 'Processing replacement...', type: 'success' });
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('cache_data', 'false');

    try {
      const extractRes = await fetch(`${API_BASE_URL}/api/extract-cv`, {
        method: 'POST',
        body: formData,
      });

      if (extractRes.ok) {
        const newData = await extractRes.json();
        
        // Push update to DB: only update cv_url to keep manually refined info intact
        const updateRes = await fetch(`${API_BASE_URL}/api/update-candidate/${candidateId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            cv_url: newData.cv_url
          }),
        });

        if (updateRes.ok) {
          // Update local state: keep current fields, only change cv_url
          setCandidates(prev => prev.map(c => 
            c.id === candidateId ? { 
              ...c, 
              cv_url: newData.cv_url
            } : c
          ));
          setStatus({ id: candidateId, message: 'CV updated successfully!', type: 'success' });
        } else {
          setStatus({ id: candidateId, message: 'Failed to persist update.', type: 'error' });
        }
      } else {
        setStatus({ id: candidateId, message: 'Extraction failed.', type: 'error' });
      }
    } catch (error) {
      setStatus({ id: candidateId, message: 'Network error.', type: 'error' });
    } finally {
      setIsUpdatingCV(null);
      setTimeout(() => setStatus(null), 3000);
    }
  };

  const handleDeleteCandidate = async () => {
    if (!deleteTarget || deleteTarget.type !== 'candidate') return;
    
    setIsDeleting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/delete-candidate/${deleteTarget.id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setCandidates(prev => prev.filter(c => c.id !== deleteTarget.id));
        setDeleteTarget(null);
      } else {
        alert('Deletion failed.');
      }
    } catch (error) {
      console.error('Error deleting candidate:', error);
      alert('Network error occurred.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <nav className="mb-8 flex items-center text-sm text-zinc-500 dark:text-zinc-400">
          <Link href="/update" className="hover:text-zinc-900 dark:hover:text-zinc-50 transition-colors flex items-center gap-1">
            <IoChevronBack className="w-4 h-4" />
            Update
          </Link>
          <span className="mx-2">/</span>
          <span className="text-zinc-900 dark:text-zinc-50 font-medium font-outfit uppercase tracking-widest text-[10px]">Candidate Editor</span>
        </nav>

        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
          <div>
            <h1 className="text-4xl font-black text-zinc-900 dark:text-zinc-50 tracking-tight">Candidate Refinement</h1>
            <p className="text-zinc-600 dark:text-zinc-400 mt-2 text-lg font-medium opacity-80">
              Synchronise and modify extracted applicant intelligence.
            </p>
          </div>
          {selectedBatch && (
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3"
            >
               <button
                  onClick={() => setDeleteTarget({
                    type: 'batch',
                    id: selectedBatch.id,
                    name: selectedBatch.batch_name,
                    count: selectedBatch.candidate_ids.length
                  })}
                  className="px-6 py-3 bg-red-50 dark:bg-red-900/10 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-900/30 rounded-2xl font-bold hover:bg-red-100 dark:hover:bg-red-900/20 transition-all active:scale-95 text-xs flex items-center gap-2"
               >
                  <IoTrashOutline className="w-4 h-4" />
                  Purge Batch
               </button>
            </motion.div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          {/* Sidebar: Batch Selection */}
          <div className="lg:col-span-3 space-y-6">
            <div className="bg-white dark:bg-zinc-900 rounded-[2.5rem] border border-zinc-200 dark:border-zinc-800 overflow-hidden shadow-2xl shadow-indigo-500/5">
              <div className="p-6 border-b border-zinc-100 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50 flex items-center justify-between">
                <h3 className="font-black text-zinc-400 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em]">
                  Active Batches
                </h3>
                <span className="px-2 py-0.5 rounded-full bg-zinc-200 dark:bg-zinc-800 text-[10px] font-black text-zinc-500">
                  {batches.length}
                </span>
              </div>
              <div className="max-h-[600px] overflow-y-auto p-4 space-y-2">
                {isLoading ? (
                  <div className="p-12 text-center space-y-3">
                    <div className="w-8 h-8 border-2 border-zinc-200 border-t-indigo-600 rounded-full animate-spin mx-auto"></div>
                    <p className="text-[10px] text-zinc-400 font-black uppercase tracking-widest leading-loose">Synchronising</p>
                  </div>
                ) : batches.length === 0 ? (
                  <div className="p-12 text-center outline-dashed outline-zinc-100 dark:outline-zinc-800 outline-offset-[-20px] rounded-3xl">
                    <p className="text-xs text-zinc-400 font-bold italic">No batches found.</p>
                  </div>
                ) : (
                  batches.map((batch) => (
                    <button
                      key={batch.id}
                      onClick={() => handleBatchSelect(batch)}
                      className={`w-full text-left p-5 rounded-2xl transition-all group relative border-2 ${
                        selectedBatch?.id === batch.id
                          ? 'bg-indigo-50 dark:bg-indigo-900/10 border-indigo-500/20 ring-4 ring-indigo-500/5'
                          : 'hover:bg-zinc-50 dark:hover:bg-zinc-800/50 border-transparent'
                      }`}
                    >
                      <h4 className={`font-bold truncate text-sm mb-1 ${selectedBatch?.id === batch.id ? 'text-indigo-700 dark:text-indigo-400' : 'text-zinc-900 dark:text-zinc-100'}`}>
                        {batch.batch_name}
                      </h4>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-zinc-400 font-black uppercase tracking-tighter">
                          {batch.candidate_ids.length} Candidates
                        </span>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Main Area: Candidate List & Editor */}
          <div className="lg:col-span-9">
            <AnimatePresence mode="wait">
              {isCandidatesLoading ? (
                <motion.div 
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col items-center justify-center min-h-[600px] space-y-6"
                >
                  <div className="relative w-20 h-20">
                    <div className="absolute inset-0 border-4 border-indigo-500/10 rounded-full"></div>
                    <div className="absolute inset-0 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                  </div>
                  <p className="text-zinc-400 font-black uppercase tracking-[0.3em] text-xs">Assembling Dataset</p>
                </motion.div>
              ) : selectedBatch && candidates.length > 0 ? (
                <motion.div 
                  key="list"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-6 pb-20"
                >
                  <div className="bg-white dark:bg-zinc-900 rounded-[3rem] border border-zinc-200 dark:border-zinc-800 p-8 shadow-2xl shadow-indigo-500/5">
                    <div className="flex items-center justify-between mb-8 px-2">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-900/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                          <IoPeopleOutline className="w-6 h-6" />
                        </div>
                        <div>
                          <h2 className="text-xl font-black text-zinc-900 dark:text-zinc-50">{selectedBatch.batch_name}</h2>
                          <p className="text-xs text-zinc-500 font-medium">Verify and update candidate metadata</p>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {candidates.map((candidate) => (
                        <div 
                          key={candidate.id}
                          className="bg-zinc-50/50 dark:bg-zinc-950/50 border border-zinc-100 dark:border-zinc-800/50 rounded-3xl p-6 transition-all hover:border-indigo-500/30 group relative overflow-hidden"
                        >
                          {/* Card Header: Identity Snapshot & Quick Actions */}
                          <div className="flex items-center justify-between mb-6 pb-6 border-b border-zinc-200/50 dark:border-zinc-800/50">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center text-xs font-black">
                                {candidate.name.charAt(0)}
                              </div>
                              <h3 className="font-black text-zinc-900 dark:text-zinc-50 uppercase tracking-tighter text-sm">{candidate.name || 'Anonymous Candidate'}</h3>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              {candidate.cv_url ? (
                                <>
                                  <button 
                                    onClick={() => setPreviewUrl(candidate.cv_url || null)}
                                    className="flex items-center gap-2 text-[9px] font-black uppercase text-indigo-500 hover:text-indigo-400 transition-colors bg-indigo-50 dark:bg-indigo-900/20 px-3 py-1.5 rounded-lg border border-indigo-500/10"
                                  >
                                    <IoEyeOutline className="w-3.5 h-3.5" />
                                    Preview
                                  </button>
                                  <button
                                    onClick={() => {
                                      const input = document.createElement('input');
                                      input.type = 'file';
                                      input.accept = '.pdf,.docx,.txt,.md';
                                      input.onchange = (e) => {
                                        const file = (e.target as HTMLInputElement).files?.[0];
                                        if (file) handleUpdateCV(candidate.id, file);
                                      };
                                      input.click();
                                    }}
                                    disabled={isUpdatingCV === candidate.id}
                                    className="flex items-center gap-2 text-[9px] font-black uppercase text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition-colors bg-zinc-100 dark:bg-zinc-800/50 px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700"
                                  >
                                    <IoCloudUploadOutline className="w-3.5 h-3.5" />
                                    {isUpdatingCV === candidate.id ? 'Synchronising...' : 'Update CV'}
                                  </button>
                                </>
                              ) : (
                                <button
                                  onClick={() => {
                                    const input = document.createElement('input');
                                    input.type = 'file';
                                    input.accept = '.pdf,.docx,.txt,.md';
                                    input.onchange = (e) => {
                                      const file = (e.target as HTMLInputElement).files?.[0];
                                      if (file) handleUpdateCV(candidate.id, file);
                                    };
                                    input.click();
                                  }}
                                  disabled={isUpdatingCV === candidate.id}
                                  className="flex items-center gap-2 text-[9px] font-black uppercase text-indigo-500 hover:text-indigo-400 transition-colors bg-indigo-50 dark:bg-indigo-900/20 px-4 py-2 rounded-lg border border-indigo-500/10"
                                >
                                  <IoCloudUploadOutline className="w-3.5 h-3.5" />
                                  {isUpdatingCV === candidate.id ? 'Synchronising...' : 'Upload CV'}
                                </button>
                              )}
                               <button
                                onClick={() => setDeleteTarget({
                                  type: 'candidate',
                                  id: candidate.id,
                                  name: candidate.name
                                })}
                                className="flex items-center justify-center w-9 h-9 rounded-lg bg-red-50 dark:bg-red-900/10 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/20 border border-red-200 dark:border-red-900/30 transition-all active:scale-90"
                                title="Remove Candidate"
                              >
                                <IoTrashOutline className="w-4 h-4" />
                              </button>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {/* Card Content remains same but without the CV buttons repeating */}
                            <div className="space-y-4">
                              <div>
                                <label className="text-[10px] font-black uppercase text-zinc-400 tracking-widest mb-2 block">Full Identity</label>
                                <input 
                                  type="text"
                                  value={candidate.name}
                                  onChange={(e) => handleFieldChange(candidate.id, 'name', e.target.value)}
                                  className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2.5 text-sm font-bold text-zinc-700 dark:text-zinc-200 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/30 outline-none transition-all"
                                />
                              </div>
                              <div className="relative">
                                <label className="text-[10px] font-black uppercase text-zinc-400 tracking-widest mb-2 block">Email Channel</label>
                                <div className="relative">
                                  <IoMailOutline className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400" />
                                  <input 
                                    type="email"
                                    value={candidate.email}
                                    onChange={(e) => handleFieldChange(candidate.id, 'email', e.target.value)}
                                    className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-11 pr-4 py-2.5 text-sm font-medium text-zinc-600 dark:text-zinc-400 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all"
                                  />
                                </div>
                              </div>
                            </div>

                            <div className="space-y-4">
                              <div>
                                <label className="text-[10px] font-black uppercase text-zinc-400 tracking-widest mb-2 block">Contact Primary</label>
                                <div className="relative">
                                  <IoCallOutline className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400" />
                                  <input 
                                    type="text"
                                    value={candidate.phone}
                                    onChange={(e) => handleFieldChange(candidate.id, 'phone', e.target.value)}
                                    className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-11 pr-4 py-2.5 text-sm font-medium text-zinc-600 dark:text-zinc-400 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all"
                                  />
                                </div>
                              </div>
                              <div>
                                <label className="text-[10px] font-black uppercase text-zinc-400 tracking-widest mb-2 block">GitHub Intelligence</label>
                                <div className="relative">
                                  <IoLogoGithub className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400" />
                                  <input 
                                    type="text"
                                    value={candidate.github_url}
                                    onChange={(e) => handleFieldChange(candidate.id, 'github_url', e.target.value)}
                                    placeholder="https://github.com/..."
                                    className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-11 pr-4 py-2.5 text-sm font-medium text-zinc-600 dark:text-zinc-400 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all"
                                  />
                                </div>
                              </div>
                            </div>

                            <div className="flex flex-col justify-between">
                              <div>
                                <label className="text-[10px] font-black uppercase text-zinc-400 tracking-widest mb-2 block">LinkedIn Profile</label>
                                <div className="relative">
                                  <IoLogoLinkedin className="absolute left-4 top-1/2 -translate-y-1/2 text-indigo-500/50" />
                                  <input 
                                    type="text"
                                    value={candidate.linkedin_url}
                                    onChange={(e) => handleFieldChange(candidate.id, 'linkedin_url', e.target.value)}
                                    placeholder="https://linkedin.com/in/..."
                                    className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-11 pr-4 py-2.5 text-sm font-medium text-zinc-600 dark:text-zinc-400 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all"
                                  />
                                </div>
                              </div>
                              
                              <div className="flex items-center justify-between mt-6">
                                <div className="flex items-center gap-2">
                                  {status?.id === candidate.id && (
                                    <motion.div 
                                      initial={{ opacity: 0, scale: 0.8 }}
                                      animate={{ opacity: 1, scale: 1 }}
                                      className={`flex items-center gap-1 text-[10px] font-black uppercase tracking-wider ${status.type === 'success' ? 'text-emerald-500' : 'text-red-500'}`}
                                    >
                                      {status.type === 'success' ? <IoCheckmarkCircleOutline className="w-3.5 h-3.5" /> : null}
                                      {status.message}
                                    </motion.div>
                                  )}
                                </div>
                                <button
                                  onClick={() => handleUpdateCandidate(candidate)}
                                  disabled={savingId === candidate.id}
                                  className="px-6 py-2.5 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-xl text-xs font-black uppercase tracking-widest hover:opacity-90 transition-all active:scale-95 disabled:opacity-40 flex items-center gap-2"
                                >
                                  {savingId === candidate.id ? (
                                    <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                                  ) : (
                                    <IoSaveOutline className="w-3.5 h-3.5" />
                                  )}
                                  Commit
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div 
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center justify-center min-h-[600px] border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-[4rem] text-center bg-white/40 dark:bg-zinc-900/10 backdrop-blur-3xl p-12 group transition-all duration-700 hover:border-indigo-500/20"
                >
                  <div className="w-24 h-24 bg-indigo-50 dark:bg-indigo-950/50 rounded-[2rem] flex items-center justify-center mb-10 text-indigo-600 dark:text-indigo-400 ring-8 ring-indigo-50/50 dark:ring-indigo-950/20 group-hover:scale-110 transition-transform duration-700">
                    <IoPeopleOutline className="w-10 h-10" />
                  </div>
                  <h3 className="text-3xl font-black text-zinc-900 dark:text-zinc-50 mb-4 tracking-tighter">Dataset Selection</h3>
                  <p className="max-w-md text-zinc-500 dark:text-zinc-400 text-lg leading-relaxed font-medium">
                    Select a candidate batch from the repository to initiate detailed metadata refinement.
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Simplified Delete Confirmation Modal */}
        <AnimatePresence>
          {deleteTarget && (
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-zinc-950/20 backdrop-blur-sm">
              <motion.div 
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="w-full max-w-sm bg-white dark:bg-zinc-900 rounded-3xl border border-zinc-200 dark:border-zinc-800 shadow-2xl overflow-hidden"
              >
                <div className="p-8 text-center space-y-6">
                  <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-2xl flex items-center justify-center mx-auto">
                    <IoTrashOutline className="w-6 h-6" />
                  </div>
                  
                  <div className="space-y-2">
                    <h3 className="text-xl font-bold text-zinc-900 dark:text-zinc-50 tracking-tight">
                      {deleteTarget.type === 'batch' ? 'Delete Batch' : 'Remove Candidate'}
                    </h3>
                    <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed">
                      {deleteTarget.type === 'batch' ? (
                        <>
                          This will permanently delete the batch <span className="font-semibold text-zinc-900 dark:text-zinc-200">"{deleteTarget.name}"</span> and all {deleteTarget.count} profiles within it.
                        </>
                      ) : (
                        <>
                          Are you sure you want to remove <span className="font-semibold text-zinc-900 dark:text-zinc-200">"{deleteTarget.name}"</span>? 
                          This action cannot be undone.
                        </>
                      )}
                    </p>
                  </div>

                  <div className="flex gap-3">
                    <button
                      disabled={isDeleting}
                      onClick={() => setDeleteTarget(null)}
                      className="flex-1 py-3 px-4 bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 rounded-xl font-semibold text-sm hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      disabled={isDeleting}
                      onClick={deleteTarget.type === 'batch' ? handleDeleteBatch : handleDeleteCandidate}
                      className="flex-1 py-3 px-4 bg-red-600 hover:bg-red-700 text-white rounded-xl font-semibold text-sm transition-colors flex items-center justify-center"
                    >
                      {isDeleting ? (
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      ) : (
                        'Delete'
                      )}
                    </button>
                  </div>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* Global Preview Modal */}
        <AnimatePresence>
          {previewUrl && (
            <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 md:p-10 bg-zinc-950/90 backdrop-blur-md">
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="w-full h-full max-w-6xl bg-white dark:bg-zinc-900 rounded-[3rem] border border-zinc-200 dark:border-zinc-800 shadow-2xl flex flex-col overflow-hidden"
              >
                <div className="flex items-center justify-between p-6 border-b border-zinc-100 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-2xl bg-indigo-50 dark:bg-indigo-900/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                      <IoEyeOutline className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-black text-zinc-900 dark:text-zinc-50 uppercase tracking-widest text-[10px]">Intelligence Preview</h3>
                      <p className="text-[9px] text-zinc-500 font-bold uppercase tracking-tight">Original Document Source</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => setPreviewUrl(null)}
                    className="w-12 h-12 rounded-2xl bg-zinc-100 dark:bg-zinc-800 text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-50 transition-all flex items-center justify-center active:scale-90"
                  >
                    <IoCloseOutline className="w-6 h-6" />
                  </button>
                </div>
                <div className="flex-1 bg-zinc-100 dark:bg-zinc-950 p-2">
                  <iframe 
                    src={previewUrl} 
                    className="w-full h-full rounded-2xl border-none shadow-inner"
                    title="CV Preview"
                  />
                </div>
                <div className="p-6 bg-white dark:bg-zinc-900 flex justify-end">
                   <a 
                    href={previewUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="px-6 py-3 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:opacity-90 transition-all flex items-center gap-2"
                  >
                    <IoChevronBack className="w-4 h-4 rotate-180" />
                    Open in External Tab
                  </a>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
