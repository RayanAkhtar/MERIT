'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  IoChevronBack, IoCodeSlashOutline, IoDocumentTextOutline 
} from 'react-icons/io5';
import JobDescriptionReview, { ExtractedData } from '../../components/JobDescriptionReview';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

interface JobDescriptionProfile {
  id: string;
  title: string;
  description: string;
  metrics: any; // Grouped structure from DB
  created_at: string;
}

export default function UpdateJobDescriptionPage() {
  const [jobProfiles, setJobProfiles] = useState<JobDescriptionProfile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<JobDescriptionProfile | null>(null);
  const [editData, setEditData] = useState<ExtractedData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error' | null, message: string }>({ type: null, message: '' });

  useEffect(() => {
    fetchJobProfiles();
  }, []);

  const fetchJobProfiles = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-job-descriptions`);
      if (response.ok) {
        const data = await response.json();
        setJobProfiles(data);
      }
    } catch (error) {
      console.error('Error fetching job descriptions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const flattenMetrics = (groupedMetrics: any) => {
    const flat: any[] = [];
    if (!groupedMetrics) return flat;

    Object.entries(groupedMetrics).forEach(([category, data]: [string, any]) => {
      if (data.type === 'list') {
        data.value.forEach((val: string) => {
          flat.push({
            id: Math.random().toString(36).substr(2, 9),
            label: category.endsWith('s') ? category.slice(0, -1) : category,
            value: val,
            category: category
          });
        });
      } else if (data.type === 'key-value') {
        data.value.forEach((item: any) => {
          flat.push({
            id: Math.random().toString(36).substr(2, 9),
            label: item.label || 'Requirement',
            value: item.value || '',
            category: category
          });
        });
      }
    });

    return flat;
  };

  const handleSelect = (req: JobDescriptionProfile) => {
    if (showDeleteConfirm) setShowDeleteConfirm(false);
    setSelectedProfile(req);
    const flattened = flattenMetrics(req.metrics);
    setEditData({
      title: req.title,
      description: req.description,
      metrics: flattened
    });
    setStatus({ type: null, message: '' });
  };

  const handleUpdate = async () => {
    if (!selectedProfile || !editData) return;

    setIsSaving(true);
    setStatus({ type: null, message: '' });

    try {
      const response = await fetch(`${API_BASE_URL}/api/update-job-description/${selectedProfile.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: editData.title,
          description: editData.description,
          metrics: editData.metrics
        }),
      });

      if (response.ok) {
        setStatus({ type: 'success', message: 'Job Description updated successfully!' });
        fetchJobProfiles();
      } else {
        const err = await response.json();
        setStatus({ type: 'error', message: err.error || 'Failed to update.' });
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Network error occurred.' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedProfile) return;

    setIsDeleting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/delete-job-description/${selectedProfile.id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setEditData(null);
        setSelectedProfile(null);
        setShowDeleteConfirm(false);
        fetchJobProfiles();
      } else {
        const err = await response.json();
        alert(err.error || 'Deletion failed.');
      }
    } catch (error) {
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
          <span className="text-zinc-900 dark:text-zinc-50 font-medium">Job Profile Editor</span>
        </nav>

        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
          <div>
            <h1 className="text-4xl font-black text-zinc-900 dark:text-zinc-50 tracking-tight">Profile Refinement</h1>
            <p className="text-zinc-600 dark:text-zinc-400 mt-2 text-lg font-medium opacity-80">
              Synchronise and modify existing job description datasets.
            </p>
          </div>
          {editData && (
            <div className="flex items-center gap-3 animate-in fade-in slide-in-from-right-4 duration-500">
               <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="px-6 py-3 bg-red-50 dark:bg-red-900/10 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-900/30 rounded-2xl font-bold hover:bg-red-100 dark:hover:bg-red-900/20 transition-all active:scale-95"
               >
                  Permanently Delete
               </button>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          {/* Sidebar: Selection Panel */}
          <div className="lg:col-span-3 space-y-6">
            <div className="bg-white dark:bg-zinc-900 rounded-3xl border border-zinc-200 dark:border-zinc-800 overflow-hidden shadow-2xl shadow-indigo-500/5">
              <div className="p-6 border-b border-zinc-100 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50 flex items-center justify-between">
                <h3 className="font-black text-zinc-400 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em]">
                  Stored Profiles
                </h3>
                <span className="px-2 py-0.5 rounded-full bg-zinc-200 dark:bg-zinc-800 text-[10px] font-black text-zinc-500">
                  {jobProfiles.length}
                </span>
              </div>
              <div className="max-h-[700px] overflow-y-auto p-4 space-y-2">
                {isLoading ? (
                  <div className="p-12 text-center space-y-3">
                    <div className="w-8 h-8 border-2 border-zinc-200 border-t-indigo-600 rounded-full animate-spin mx-auto"></div>
                    <p className="text-[10px] text-zinc-400 font-black uppercase tracking-widest leading-loose">Synchronising data</p>
                  </div>
                ) : jobProfiles.length === 0 ? (
                  <div className="p-12 text-center outline-dashed outline-zinc-100 dark:outline-zinc-800 outline-offset-[-20px] rounded-3xl">
                    <p className="text-xs text-zinc-400 font-bold italic">No active profiles.</p>
                  </div>
                ) : (
                  jobProfiles.map((req) => (
                    <button
                      key={req.id}
                      onClick={() => handleSelect(req)}
                      className={`w-full text-left p-5 rounded-2xl transition-all group relative border-2 ${
                        selectedProfile?.id === req.id
                          ? 'bg-indigo-50 dark:bg-indigo-900/10 border-indigo-500/20 ring-4 ring-indigo-500/5'
                          : 'hover:bg-zinc-50 dark:hover:bg-zinc-800/50 border-transparent'
                      }`}
                    >
                      <h4 className={`font-bold truncate text-sm mb-1 ${selectedProfile?.id === req.id ? 'text-indigo-700 dark:text-indigo-400' : 'text-zinc-900 dark:text-zinc-100'}`}>
                        {req.title}
                      </h4>
                      <p className="text-[10px] text-zinc-400 font-bold uppercase tracking-tighter">
                        Active since {new Date(req.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                      </p>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Main Area: Structured Editor using shared Component */}
          <div className="lg:col-span-9">
            {editData ? (
                <JobDescriptionReview 
                    data={editData}
                    setData={setEditData}
                    onSave={handleUpdate}
                    isSaving={isSaving}
                    saveButtonText="Update Profile"
                    statusMessage={status.message}
                />
            ) : (
              <div className="flex flex-col items-center justify-center min-h-[650px] border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-[4rem] text-center bg-white/40 dark:bg-zinc-900/10 backdrop-blur-3xl p-12 group transition-all duration-700 hover:border-indigo-500/20">
                <div className="w-24 h-24 bg-indigo-50 dark:bg-indigo-950/50 rounded-[2rem] flex items-center justify-center mb-10 text-indigo-600 dark:text-indigo-400 ring-8 ring-indigo-50/50 dark:ring-indigo-950/20 group-hover:scale-110 transition-transform duration-700">
                  <IoCodeSlashOutline className="w-10 h-10" />
                </div>
                <h3 className="text-3xl font-black text-zinc-900 dark:text-zinc-50 mb-4 tracking-tighter">Profile Selection</h3>
                <p className="max-w-md text-zinc-500 dark:text-zinc-400 text-lg leading-relaxed font-medium">
                  Select a configured job description from the repository to initiate detailed benchmark refinement.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-zinc-950/80 backdrop-blur-2xl animate-in fade-in duration-500">
            <div className="w-full max-w-md p-12 bg-white dark:bg-zinc-900 rounded-[3rem] border border-zinc-200 dark:border-zinc-800 shadow-2xl space-y-10 animate-in zoom-in-95 duration-500 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/5 blur-3xl rounded-full -mr-16 -mt-16" />
              
              <div className="text-center space-y-6 relative">
                <div className="w-24 h-24 bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-500 rounded-[2.5rem] flex items-center justify-center mx-auto ring-12 ring-red-50/50 dark:ring-red-950/10 shadow-xl shadow-red-500/10">
                   <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                   </svg>
                </div>
                <div className="space-y-2">
                    <h3 className="text-3xl font-black text-zinc-900 dark:text-zinc-50 tracking-tighter">Terminal Deletion</h3>
                    <p className="text-zinc-500 dark:text-zinc-400 text-base leading-relaxed font-medium">
                      You are about to purge <span className="font-extrabold text-zinc-900 dark:text-zinc-100 italic">"{selectedProfile?.title}"</span>. 
                      This dataset will be permanently cleared from the repository.
                    </p>
                </div>
              </div>

              <div className="flex flex-col gap-4 relative">
                <button
                  disabled={isDeleting}
                  onClick={handleDelete}
                  className="w-full py-5 bg-red-600 hover:bg-red-500 text-white rounded-3xl font-black shadow-2xl shadow-red-600/30 active:scale-[0.98] transition-all flex items-center justify-center gap-3 uppercase tracking-widest text-xs"
                >
                  {isDeleting ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : "Purge Profile"}
                </button>
                <button
                  disabled={isDeleting}
                  onClick={() => setShowDeleteConfirm(false)}
                  className="w-full py-5 bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 rounded-3xl font-black hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-all active:scale-[0.98] uppercase tracking-widest text-xs"
                >
                  Abort Action
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
