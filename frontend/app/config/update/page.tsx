'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { IoChevronBack, IoSettingsOutline, IoTrashOutline } from 'react-icons/io5';
import ConfigEditor from '../../components/ConfigEditor';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

interface MatchingConfig {
  id: string;
  name: string;
  job_id: string;
  batch_id: string;
  weights: Record<string, number>;
  active_metrics: Record<string, boolean>;
  created_at: string;
}

export default function UpdateConfigPage() {
  const [configs, setConfigs] = useState<MatchingConfig[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<MatchingConfig | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error' | null, message: string }>({ type: null, message: '' });

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-configs`);
      if (response.ok) {
        const data = await response.json();
        setConfigs(data);
      }
    } catch (error) {
      console.error('Error fetching configs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (config: MatchingConfig) => {
    setSelectedConfig(config);
    setStatus({ type: null, message: '' });
  };

  const handleUpdate = async (updatedData: any) => {
    if (!selectedConfig) return;

    setIsSaving(true);
    setStatus({ type: null, message: '' });

    try {
      const response = await fetch(`${API_BASE_URL}/api/update-config/${selectedConfig.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData),
      });

      if (response.ok) {
        setStatus({ type: 'success', message: 'Configuration updated successfully!' });
        fetchConfigs();
        // Update selected config in place to reflect changes in UI
        setSelectedConfig({ ...selectedConfig, ...updatedData });
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
    if (!selectedConfig) return;

    setIsDeleting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/delete-config/${selectedConfig.id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setSelectedConfig(null);
        setShowDeleteConfirm(false);
        fetchConfigs();
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
          <Link href="/config" className="hover:text-zinc-900 dark:hover:text-zinc-50 transition-colors flex items-center gap-1">
            <IoChevronBack className="w-4 h-4" />
            Config
          </Link>
          <span className="mx-2">/</span>
          <span className="text-zinc-900 dark:text-zinc-50 font-medium">Update Configuration</span>
        </nav>

        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
          <div>
            <h1 className="text-4xl font-black text-zinc-900 dark:text-zinc-50 tracking-tight">Config Refinement</h1>
            <p className="text-zinc-600 dark:text-zinc-400 mt-2 text-lg font-medium opacity-80">
              Modify weights and datasets for existing configurations.
            </p>
          </div>
          {selectedConfig && (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="px-6 py-3 bg-red-50 dark:bg-red-900/10 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-900/30 rounded-2xl font-bold hover:bg-red-100 dark:hover:bg-red-900/20 transition-all active:scale-95 flex items-center gap-2"
            >
              <IoTrashOutline />
              Delete Config
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          {/* Sidebar */}
          <div className="lg:col-span-3 space-y-6">
            <div className="bg-white dark:bg-zinc-900 rounded-3xl border border-zinc-200 dark:border-zinc-800 overflow-hidden shadow-sm">
              <div className="p-6 border-b border-zinc-100 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50 flex items-center justify-between">
                <h3 className="font-black text-zinc-400 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em]">Stored Configs</h3>
                <span className="px-2 py-0.5 rounded-full bg-zinc-200 dark:bg-zinc-800 text-[10px] font-black text-zinc-500">{configs.length}</span>
              </div>
              <div className="max-h-[600px] overflow-y-auto p-4 space-y-2">
                {isLoading ? (
                  <div className="p-12 text-center text-[10px] text-zinc-400 font-black uppercase tracking-widest leading-loose">Synchronising...</div>
                ) : configs.length === 0 ? (
                  <div className="p-12 text-center text-xs text-zinc-400 font-bold italic">No configs found.</div>
                ) : (
                  configs.map((cfg) => (
                    <button
                      key={cfg.id}
                      onClick={() => handleSelect(cfg)}
                      className={`w-full text-left p-5 rounded-2xl transition-all border-2 ${
                        selectedConfig?.id === cfg.id
                          ? 'bg-indigo-50 dark:bg-indigo-900/10 border-indigo-500/20'
                          : 'hover:bg-zinc-50 dark:hover:bg-zinc-800/50 border-transparent'
                      }`}
                    >
                      <h4 className={`font-bold truncate text-sm mb-1 ${selectedConfig?.id === cfg.id ? 'text-indigo-700 dark:text-indigo-400' : 'text-zinc-900 dark:text-zinc-100'}`}>{cfg.name}</h4>
                      <p className="text-[10px] text-zinc-400 font-bold uppercase tracking-tighter">Created {new Date(cfg.created_at).toLocaleDateString()}</p>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Editor */}
          <div className="lg:col-span-9">
            {selectedConfig ? (
              <div className="space-y-4">
                {status.type && (
                    <div className={`p-4 rounded-xl text-sm font-medium ${status.type === 'success' ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400 border border-green-200 dark:border-green-800' : 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400 border border-red-200 dark:border-red-800'}`}>
                        {status.message}
                    </div>
                )}
                <ConfigEditor 
                    mode="update" 
                    initialData={selectedConfig} 
                    onSave={handleUpdate} 
                    isProcessing={isSaving} 
                />
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center min-h-[500px] border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-[3rem] text-center bg-white/40 dark:bg-zinc-900/10 backdrop-blur-3xl p-12">
                <div className="w-20 h-20 bg-indigo-50 dark:bg-indigo-950/50 rounded-[1.5rem] flex items-center justify-center mb-8 text-indigo-600 dark:text-indigo-400">
                  <IoSettingsOutline className="w-10 h-10 animate-spin-slow" />
                </div>
                <h3 className="text-2xl font-black text-zinc-900 dark:text-zinc-50 mb-3 tracking-tighter">Select a Protocol</h3>
                <p className="max-w-xs text-zinc-500 dark:text-zinc-400 text-base leading-relaxed font-medium">Select a configuration to adjust weights, datasets, and matching rules.</p>
              </div>
            )}
          </div>
        </div>

        {/* Delete Modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-zinc-950/80 backdrop-blur-md">
            <div className="w-full max-w-md p-10 bg-white dark:bg-zinc-900 rounded-[2.5rem] border border-zinc-200 dark:border-zinc-800 shadow-2xl space-y-8 animate-in zoom-in-95">
              <div className="text-center space-y-4">
                <div className="w-20 h-20 bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-500 rounded-[2rem] flex items-center justify-center mx-auto">
                   <IoTrashOutline className="w-10 h-10" />
                </div>
                <h3 className="text-2xl font-black text-zinc-900 dark:text-zinc-50 tracking-tighter">Delete Configuration?</h3>
                <p className="text-zinc-500 dark:text-zinc-400 text-sm font-medium">Are you sure you want to delete <span className="font-bold text-zinc-900 dark:text-zinc-100">"{selectedConfig?.name}"</span>? This cannot be undone.</p>
              </div>
              <div className="flex flex-col gap-3">
                <button disabled={isDeleting} onClick={handleDelete} className="w-full py-4 bg-red-600' hover:bg-red-500 text-white rounded-2xl font-bold transition-all active:scale-[0.98]">{isDeleting ? 'Deleting...' : 'Delete Permanently'}</button>
                <button onClick={() => setShowDeleteConfirm(false)} className="w-full py-4 bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 rounded-2xl font-bold transition-all active:scale-[0.98]">Cancel</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
