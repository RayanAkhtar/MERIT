'use client';

import { useState } from 'react';

export interface JobDescriptionMetric {
    id: string;
    label: string;
    value: string;
    subValue?: string;
    category: string;
}

export interface ExtractedData {
    title: string;
    description: string;
    metrics: JobDescriptionMetric[];
}

interface JobDescriptionReviewProps {
    data: ExtractedData;
    setData: (data: ExtractedData) => void;
    onSave: () => void;
    isSaving: boolean;
    saveButtonText?: string;
    statusMessage?: string;
}

const JobDescriptionReview: React.FC<JobDescriptionReviewProps> = ({ 
    data, 
    setData, 
    onSave, 
    isSaving, 
    saveButtonText = "Commit Description",
    statusMessage 
}) => {
    const [isAddingMetric, setIsAddingMetric] = useState(false);
    const [newMetric, setNewMetric] = useState<JobDescriptionMetric>({ 
        id: '',
        label: '', 
        value: '', 
        subValue: '', 
        category: 'Technologies' 
    });

    const categoryTypes: Record<string, 'row' | 'tag'> = {
        'General': 'row',
        'Education': 'row',
        'Languages': 'tag',
        'Technologies': 'tag',
        'Experience': 'row',
        'Soft Skills': 'tag',
        'Responsibilities': 'row',
        'Requirements': 'row'
    };

    const updateMetric = (id: string, field: 'value' | 'subValue' | 'label', newValue: string) => {
        setData({
            ...data,
            metrics: data.metrics.map(m => m.id === id ? { ...m, [field]: newValue } : m)
        });
    };

    const deleteMetric = (id: string) => {
        setData({
            ...data,
            metrics: data.metrics.filter(m => m.id !== id)
        });
    };

    const addMetric = () => {
        if (!newMetric.label && categoryTypes[newMetric.category] !== 'tag') return;
        
        const metric: JobDescriptionMetric = {
            ...newMetric,
            id: Math.random().toString(36).substr(2, 9),
            label: (categoryTypes[newMetric.category] === 'tag') ? newMetric.category.slice(0, -1) : newMetric.label,
        };

        setData({
            ...data,
            metrics: [...data.metrics, metric]
        });
        setNewMetric({ id: '', label: '', value: '', subValue: '', category: 'Technologies' });
        setIsAddingMetric(false);
    };

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Header Data - Minimalist Redesign */}
            <div className="p-8 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/50 dark:bg-zinc-950/50 space-y-6">
                <div className="flex items-center gap-3 border-b border-zinc-100 dark:border-zinc-800 pb-4">
                    <div className="w-8 h-8 rounded-lg bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 flex items-center justify-center shrink-0">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
                        </svg>
                    </div>
                    <h2 className="text-sm font-black text-zinc-900 dark:text-zinc-100 uppercase tracking-widest italic">Description Context</h2>
                </div>
                
                <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase text-zinc-400 tracking-widest block">Extracted Intelligence</label>
                    <textarea 
                        value={data.description || ''}
                        onChange={(e) => setData({...data, description: e.target.value})}
                        className="w-full h-64 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl px-5 py-4 focus:ring-4 focus:ring-indigo-500/5 focus:border-indigo-500/20 transition-all resize-none text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium"
                        placeholder="Raw job description context..."
                    />
                </div>
            </div>

            {/* Metrics List - Grouped by Category */}
            <div className="grid gap-12">
                {(['General', 'Education', 'Languages', 'Technologies', 'Experience', 'Soft Skills', 'Responsibilities', 'Requirements'] as const).map((cat) => {
                    const catMetrics = data.metrics.filter(m => m.category === cat);
                    const isTagType = categoryTypes[cat] === 'tag';
                    
                    if (catMetrics.length === 0 && !['Languages', 'Technologies', 'Soft Skills', 'Responsibilities', 'Requirements'].includes(cat)) return null;

                    return (
                        <div key={cat} className="space-y-6">
                            <div className="flex items-center justify-between border-b border-zinc-200/50 dark:border-zinc-800/50 pb-6 mb-6">
                                <div className="flex items-center gap-4">
                                    <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-400">{cat}</h3>
                                    <span className="text-[9px] bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 px-3 py-1 rounded-full font-black">
                                        {catMetrics.length}
                                    </span>
                                </div>
                                <button 
                                    onClick={() => {
                                        setNewMetric({ id: '', label: cat === 'Languages' ? 'Language' : cat === 'Technologies' ? 'Technology' : cat === 'Soft Skills' ? 'Soft Skill' : 'Requirement', value: '', subValue: '', category: cat });
                                        setIsAddingMetric(true);
                                    }}
                                    className="text-[9px] font-black uppercase text-indigo-500 hover:text-indigo-400 transition-all bg-indigo-50 dark:bg-indigo-900/20 px-4 py-2 rounded-lg border border-indigo-500/10 active:scale-95 flex items-center gap-2"
                                >
                                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 4v16m8-8H4" />
                                    </svg>
                                    Add Key Metric
                                </button>
                            </div>
                            
                            <div className={isTagType ? "flex flex-wrap gap-3" : "grid gap-4"}>
                                {catMetrics.length === 0 ? (
                                    <p className="text-xs italic text-zinc-400 py-2">No {cat.toLowerCase()} context extracted.</p>
                                ) : (
                                    catMetrics.map((metric) => (
                                        isTagType ? (
                                            <div key={metric.id} className="flex items-center gap-3 px-4 py-2.5 bg-white dark:bg-zinc-950/50 border border-zinc-200 dark:border-zinc-800 rounded-2xl group hover:border-indigo-500/40 transition-all shadow-sm">
                                                <input 
                                                    type="text" 
                                                    value={metric.value || ''} 
                                                    onChange={(e) => updateMetric(metric.id, 'value', e.target.value)}
                                                    className="bg-transparent border-none p-0 text-sm font-black text-zinc-900 dark:text-zinc-100 focus:ring-0 min-w-[40px] w-auto uppercase tracking-tighter"
                                                    style={{ width: `${Math.max((metric.value?.length || 0) * 8 + 8, 40)}px` }}
                                                />
                                                <button 
                                                    onClick={() => deleteMetric(metric.id)}
                                                    className="p-1 text-zinc-300 hover:text-red-500 transition-colors"
                                                >
                                                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                                                    </svg>
                                                </button>
                                            </div>
                                        ) : (
                                            <div key={metric.id} className="flex items-center gap-4 p-6 border border-zinc-200 dark:border-zinc-800/80 rounded-3xl bg-zinc-50/30 dark:bg-zinc-950/50 group hover:border-indigo-500/30 transition-all shadow-sm">
                                                <div className="flex-1 flex flex-col sm:flex-row sm:items-center gap-4">
                                                    {cat === 'General' && (
                                                        <div className="w-full sm:w-1/3">
                                                            <span className="text-zinc-400 dark:text-zinc-500 font-bold text-[10px] uppercase tracking-widest">{metric.label}</span>
                                                        </div>
                                                    )}
                                                    
                                                    <div className="flex-1">
                                                        <input 
                                                            type="text" 
                                                            value={metric.value || ''} 
                                                            onChange={(e) => updateMetric(metric.id, 'value', e.target.value)}
                                                            className="w-full bg-zinc-50/50 dark:bg-zinc-900/30 border border-transparent rounded-xl px-4 py-2.5 text-zinc-700 dark:text-zinc-200 focus:border-indigo-500/20 focus:ring-0 text-sm font-medium transition-all"
                                                            placeholder="Metric refinement..."
                                                        />
                                                    </div>
                                                </div>
                                                
                                                <button 
                                                    onClick={() => deleteMetric(metric.id)}
                                                    className="p-2 text-zinc-200 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                                                >
                                                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                    </svg>
                                                </button>
                                            </div>
                                        )
                                    ))
                                )}
                            </div>
                        </div>
                    );
                })}

                {/* Inline Form Add Modal-style */}
                {isAddingMetric && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-zinc-950/40 backdrop-blur-sm animate-in fade-in duration-300">
                        <div className="w-full max-w-lg p-10 border border-zinc-100 dark:border-zinc-800 rounded-[3rem] bg-white dark:bg-zinc-950 shadow-2xl space-y-8 animate-in zoom-in-95 duration-300">
                           <div className="space-y-2 text-center">
                               <h4 className="text-2xl font-black dark:text-white tracking-tight">Manual Appending</h4>
                               <p className="text-zinc-500 text-sm">Expanding the {newMetric.category} dataset.</p>
                           </div>
                           
                           <div className="space-y-6">
                                <div>
                                    <label className="text-[10px] font-black uppercase text-indigo-500 tracking-widest mb-2 block">Value Refinement</label>
                                    {(categoryTypes[newMetric.category] === 'tag' || newMetric.category !== 'General') ? (
                                        <input 
                                            type="text"
                                            autoFocus
                                            placeholder="..."
                                            value={newMetric.value}
                                            onChange={(e) => setNewMetric({...newMetric, value: e.target.value})}
                                            className="w-full bg-zinc-50 dark:bg-zinc-900 border border-zinc-100 dark:border-zinc-800 rounded-2xl px-6 py-4 dark:text-zinc-200 focus:ring-2 focus:ring-indigo-500/20 font-bold"
                                        />
                                    ) : (
                                        <div className="grid grid-cols-2 gap-4">
                                            <input 
                                                type="text"
                                                value={newMetric.label}
                                                readOnly
                                                className="w-full bg-zinc-50 dark:bg-zinc-900 border border-transparent rounded-2xl px-6 py-4 text-zinc-400 cursor-default font-bold"
                                            />
                                            <input 
                                                type="text"
                                                autoFocus
                                                value={newMetric.value}
                                                onChange={(e) => setNewMetric({...newMetric, value: e.target.value})}
                                                className="w-full bg-zinc-50 dark:bg-zinc-900 border border-zinc-100 dark:border-zinc-800 rounded-2xl px-6 py-4 dark:text-zinc-200 focus:ring-2 focus:ring-indigo-500/20 font-bold"
                                            />
                                        </div>
                                    )}
                                </div>
                           </div>
                           <div className="flex gap-4">
                             <button 
                                onClick={addMetric}
                                disabled={!newMetric.value && !newMetric.label}
                                className="flex-[1.5] bg-indigo-600 text-white rounded-2xl py-4 font-black disabled:opacity-40 transition-all shadow-xl shadow-indigo-600/25 active:scale-95"
                             >
                                 Confirm Entry
                             </button>
                             <button 
                                onClick={() => setIsAddingMetric(false)}
                                className="flex-1 border border-zinc-200 dark:border-zinc-800 rounded-2xl text-zinc-500 font-bold hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-all"
                             >
                                 Dismiss
                             </button>
                           </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Final Title Selection & Save Step - Minimalist Redesign */}
            <div className="pt-6">
                <div className="p-8 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/50 dark:bg-zinc-950/50 space-y-8">
                    <div className="space-y-6">
                        <div className="flex flex-col sm:flex-row sm:items-center gap-6">
                            <div className="w-10 h-10 rounded-lg bg-indigo-600 text-white flex items-center justify-center shrink-0">
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <div className="flex-1 space-y-2">
                                <label className="text-[10px] font-black uppercase text-zinc-400 tracking-widest block">Benchmark Job Title</label>
                                <div className="relative">
                                    <input 
                                        type="text" 
                                        value={data.title || ''}
                                        onChange={(e) => setData({...data, title: e.target.value})}
                                        placeholder="Enter definitive job title..."
                                        className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl px-5 py-3 text-lg font-black text-zinc-900 dark:text-zinc-100 focus:ring-4 focus:ring-indigo-500/5 focus:border-indigo-500/20 transition-all outline-none"
                                    />
                                    <div className="absolute top-0 right-4 translate-y-[0.8rem]">
                                        <span className="text-[9px] text-indigo-500/30 font-black uppercase tracking-widest">Editable</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div className="flex flex-col sm:flex-row items-center justify-end gap-6 pt-6 border-t border-zinc-100 dark:border-zinc-800">
                            <button
                                onClick={onSave}
                                disabled={isSaving || !data.title}
                                className="w-full sm:w-auto px-8 py-3 rounded-xl font-black text-xs text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 transition-all active:scale-[0.97] flex items-center justify-center gap-2"
                            >
                                {isSaving ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Creating
                                    </>
                                ) : (
                                    'Create Benchmark'
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Status Message */}
            {statusMessage && (
                <div className={`p-6 rounded-3xl border text-sm font-bold animate-in bounce-in duration-500 ${
                  statusMessage.toLowerCase().includes('success') 
                    ? "bg-emerald-50 text-emerald-700 border-emerald-100 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-800/30"
                    : "bg-red-50 text-red-700 border-red-100 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800/30"
                }`}>
                    {statusMessage}
                </div>
            )}
        </div>
    );
};

export default JobDescriptionReview;
