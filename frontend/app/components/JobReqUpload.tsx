'use client';

import { useState, useRef } from 'react';

interface FileWithPreview extends File {
  preview?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

interface ExtractedMetric {
  id: string;
  label: string;
  value: string;
  subValue?: string; // Specifically for years of exp in Languages
  category: string;
}

interface ExtractedData {
  title: string;
  description: string;
  metrics: ExtractedMetric[];
}

export default function JobReqUpload() {
  const [step, setStep] = useState<'upload' | 'extracting' | 'review'>('upload');
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [text, setText] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null);
  const [isAddingMetric, setIsAddingMetric] = useState(false);
  const [newMetric, setNewMetric] = useState<{ label: string, value: string, subValue: string, category: ExtractedMetric['category'] }>({ 
    label: '', 
    value: '', 
    subValue: '', 
    category: 'Technologies' 
  });
  const fileInputRef = useRef<HTMLInputElement>(null);
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

  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown'];
  const allowedExtensions = ['.pdf', '.docx', '.txt', '.md'];

  const validateFile = (file: File): boolean => {
    const isValidType = allowedTypes.includes(file.type);
    const isValidExtension = allowedExtensions.some(ext => 
      file.name.toLowerCase().endsWith(ext)
    );
    return isValidType || isValidExtension;
  };

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList) return;

    const newFiles: FileWithPreview[] = [];
    for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];
        if (validateFile(file)) {
            newFiles.push(file);
        }
    }

    const rejectedFiles = fileList.length !== newFiles.length;
    
    if (newFiles.length > 0) {
        // Always take the latest valid file to overwrite
        setFiles([newFiles[newFiles.length - 1]]);
        
        if (newFiles.length > 1) {
            setUploadStatus('Only one file can be uploaded at a time. Overwriting with the latest valid file.');
        } else if (rejectedFiles) {
            setUploadStatus('Some files were rejected. Only PDF, DOCX, TXT and MD files are allowed.');
        } else {
            setUploadStatus('');
        }
    } else if (rejectedFiles) {
        setUploadStatus('Invalid file type. Only PDF, DOCX, TXT and MD files are allowed.');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
    if (fileInputRef.current) {
        fileInputRef.current.value = '';
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleExtract = async () => {
    if (files.length === 0 && !text.trim()) {
        setUploadStatus('Please upload files or paste text descriptions.');
        return;
    }

    setStep('extracting');
    setUploadStatus('Extracting key requirements...');

    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    formData.append('text', text);

    try {
        const response = await fetch(`${API_BASE_URL}/api/extract-job-requirements`, {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            setExtractedData(data);
            setStep('review');
            setUploadStatus('');
        } else {
            const error = await response.json();
            setUploadStatus(`Extraction failed: ${error.error || 'Server error'}`);
            setStep('upload');
        }
    } catch (error) {
        setUploadStatus(`Extraction failed: Network error`);
        setStep('upload');
    }
  };

  const updateMetric = (id: string, field: 'value' | 'subValue' | 'label', newValue: string) => {
    if (!extractedData) return;
    setExtractedData({
        ...extractedData,
        metrics: extractedData.metrics.map(m => m.id === id ? { ...m, [field]: newValue } : m)
    });
  };

  const deleteMetric = (id: string) => {
    if (!extractedData) return;
    setExtractedData({
        ...extractedData,
        metrics: extractedData.metrics.filter(m => m.id !== id)
    });
  };

  const addMetric = () => {
    if (!extractedData || !newMetric.label) return;
    
    const metric: ExtractedMetric = {
        id: Math.random().toString(36).substr(2, 9),
        label: (categoryTypes[newMetric.category] === 'tag') ? newMetric.category.slice(0, -1) : newMetric.label,
        value: newMetric.value,
        subValue: newMetric.subValue,
        category: newMetric.category
    };

    setExtractedData({
        ...extractedData,
        metrics: [...extractedData.metrics, metric]
    });
    setNewMetric({ label: '', value: '', subValue: '', category: 'Technologies' });
    setIsAddingMetric(false);
  };

  const handleFinalSave = async () => {
    setIsUploading(true);
    setUploadStatus('Saving finalized Job Requirements to Database...');

    try {
        const response = await fetch(`${API_BASE_URL}/api/save-job-requirements`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(extractedData),
        });

        if (response.ok) {
            setUploadStatus('Saved Job Requirements successfully!');
            // Optional: reset state or redirect
            setTimeout(() => {
                setStep('upload');
                setFiles([]);
                setText('');
                setExtractedData(null);
                setUploadStatus('');
            }, 1500);
        } else {
            const error = await response.json();
            setUploadStatus(`Save failed: ${error.error || 'Server error'}`);
        }
    } catch (error) {
        setUploadStatus(`Save failed: Network error`);
    } finally {
        setIsUploading(false);
    }
  };

  if (step === 'extracting') {
    return (
        <div className="w-full max-w-4xl mx-auto py-20 text-center space-y-6">
            <div className="flex justify-center">
                <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <h2 className="text-2xl font-bold dark:text-white">Analyzing Requirements...</h2>
            <p className="text-zinc-500">Our engines are extracting metrics and structuring the job data.</p>
        </div>
    );
  }

  if (step === 'review' && extractedData) {
    return (
        <div className="w-full max-w-4xl mx-auto space-y-8 mt-6 pb-20">
            <div className="space-y-2">
                <h2 className="text-2xl font-bold dark:text-white">Review Extraction</h2>
                <p className="text-zinc-500">Please verify the extracted metrics. You can edit or remove any entries before saving.</p>
            </div>

            {/* Header Data */}
            <div className="p-6 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-950 space-y-4">
                <div className="hidden">
                   <label className="text-xs font-bold uppercase text-zinc-400">Projected Job Title</label>
                   <input 
                    type="text" 
                    value={extractedData.title}
                    onChange={(e) => setExtractedData({...extractedData, title: e.target.value})}
                    className="w-full text-xl font-semibold bg-transparent border-none focus:ring-0 dark:text-white"
                   />
                </div>
                <hr className="border-zinc-100 dark:border-zinc-800" />
                <div>
                    <label className="text-xs font-bold uppercase text-zinc-400">Captured Description</label>
                    <textarea 
                        value={extractedData.description}
                        onChange={(e) => setExtractedData({...extractedData, description: e.target.value})}
                        className="w-full h-64 bg-zinc-50/30 dark:bg-zinc-950/30 border border-zinc-100 dark:border-zinc-900 rounded-xl px-4 py-3 focus:ring-0 resize-none text-xs text-zinc-600 dark:text-zinc-500 overflow-y-auto leading-relaxed"
                    />
                </div>
            </div>

            {/* Metrics List - Grouped by Category */}
            <div className="space-y-10">
                {(['General', 'Education', 'Languages', 'Technologies', 'Experience', 'Soft Skills', 'Responsibilities', 'Requirements'] as const).map((cat) => {
                    const catMetrics = extractedData.metrics.filter(m => m.category === cat);
                    const isTagType = categoryTypes[cat] === 'tag';
                    
                    if (catMetrics.length === 0 && !['Languages', 'Technologies', 'Soft Skills', 'Responsibilities', 'Requirements'].includes(cat)) return null;

                    return (
                        <div key={cat} className="space-y-4">
                            <div className="flex items-center justify-between border-b border-zinc-100 dark:border-zinc-800 pb-2">
                                <h3 className="text-sm font-black uppercase tracking-wider text-zinc-400">{cat}</h3>
                                {(['General', 'Education', 'Languages', 'Technologies', 'Experience', 'Soft Skills', 'Responsibilities', 'Requirements'].includes(cat)) && (
                                    <button 
                                        onClick={() => {
                                            setNewMetric({ label: cat === 'Languages' ? 'Language' : cat === 'Technologies' ? 'Technology' : 'Soft Skill', value: '', subValue: '', category: cat });
                                            setIsAddingMetric(true);
                                        }}
                                        className="text-xs font-bold text-indigo-600 hover:text-indigo-500 flex items-center gap-1 transition-colors"
                                    >
                                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 4v16m8-8H4" />
                                        </svg>
                                        Add {['Responsibilities', 'Requirements'].includes(cat) ? cat.slice(0, -1) : cat.endsWith('ies') ? cat.slice(0, -3) + 'y' : cat.endsWith('s') ? cat.slice(0, -1) : cat}
                                    </button>
                                )}
                            </div>
                            
                            <div className={isTagType ? "flex flex-wrap gap-2 px-1" : "grid gap-3"}>
                                {catMetrics.length === 0 ? (
                                    <p className="text-xs italic text-zinc-500 px-2">No {cat.toLowerCase()} extracted.</p>
                                ) : (
                                    catMetrics.map((metric) => (
                                        isTagType ? (
                                            <div key={metric.id} className="flex items-center gap-2 px-3 py-1.5 bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 rounded-full group hover:border-indigo-500 transition-all">
                                                <input 
                                                    type="text" 
                                                    value={metric.value} 
                                                    onChange={(e) => updateMetric(metric.id, 'value', e.target.value)}
                                                    className="bg-transparent border-none p-0 text-sm font-bold text-indigo-700 dark:text-indigo-300 focus:ring-0 min-w-[30px] w-auto"
                                                    style={{ width: `${Math.max(metric.value.length * 8, 30)}px` }}
                                                />
                                                <button 
                                                    onClick={() => deleteMetric(metric.id)}
                                                    className="p-0.5 text-indigo-300 hover:text-red-500 transition-colors"
                                                >
                                                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                    </svg>
                                                </button>
                                            </div>
                                        ) : (
                                            <div key={metric.id} className="flex items-center gap-4 p-3 pr-4 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-950 group hover:border-indigo-500/30 transition-all">
                                            <div className="flex-1 flex flex-col sm:flex-row sm:items-center gap-3">
                                                {/* Label Part (Only for General) */}
                                                {cat === 'General' && (
                                                    <div className="w-full sm:w-1/3">
                                                        <span className="text-zinc-600 dark:text-zinc-400 font-bold text-sm select-none pointer-events-none">{metric.label}</span>
                                                    </div>
                                                )}
                                                
                                                {/* Value Part */}
                                                <div className="flex-1 flex items-center gap-2">
                                                    {cat === 'General' && (
                                                        <span className="text-zinc-300 dark:text-zinc-700 font-light hidden sm:inline">:</span>
                                                    )}
                                                    <input 
                                                        type="text" 
                                                        value={metric.value} 
                                                        placeholder={cat === 'Languages' ? 'Python/Java' : 'Requirement'}
                                                        onChange={(e) => updateMetric(metric.id, 'value', e.target.value)}
                                                        className="flex-1 bg-zinc-50/50 dark:bg-zinc-900/50 border-none rounded px-2 py-1 text-zinc-700 dark:text-zinc-300 focus:ring-1 focus:ring-indigo-500 text-sm"
                                                    />
                                                </div>

                                                {/* SubValue (Years) for Languages - REMOVED */}
                                            </div>
                                            
                                            <button 
                                                onClick={() => deleteMetric(metric.id)}
                                                className="p-1.5 text-zinc-300 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                                            >
                                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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

                {/* Inline Form Add Modal-style (Used for all Add operations) */}
                {isAddingMetric && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-zinc-950/20 backdrop-blur-sm animate-in fade-in duration-200">
                        <div className="w-full max-w-lg p-8 border border-zinc-200 dark:border-zinc-800 rounded-3xl bg-white dark:bg-zinc-950 shadow-2xl space-y-6 animate-in zoom-in-95 duration-200">
                           <h4 className="text-xl font-bold dark:text-white">Add {newMetric.category} Metric</h4>
                           
                           <div className="space-y-4">
                                <div>
                                    <label className="text-[10px] font-black uppercase text-indigo-500">Category</label>
                                    <select 
                                        value={newMetric.category}
                                        onChange={(e) => setNewMetric({...newMetric, category: e.target.value as ExtractedMetric['category']})}
                                        className="w-full bg-zinc-50 dark:bg-zinc-900 border-none rounded-xl px-4 py-3 mt-1 dark:text-zinc-300"
                                    >
                                        <option>General</option>
                                        <option>Education</option>
                                        <option>Languages</option>
                                        <option>Technologies</option>
                                        <option>Experience</option>
                                        <option>Soft Skills</option>
                                        <option>Responsibilities</option>
                                        <option>Requirements</option>
                                        {Object.keys(categoryTypes).filter(c => !['General', 'Education', 'Languages', 'Technologies', 'Experience', 'Soft Skills', 'Responsibilities', 'Requirements'].includes(c)).map(custom => (
                                            <option key={custom}>{custom}</option>
                                        ))}
                                    </select>
                                </div>
                                {(categoryTypes[newMetric.category] === 'tag' || newMetric.category !== 'General') ? (
                                    <div>
                                        <label className="text-[10px] font-black uppercase text-indigo-500">Requirement Value</label>
                                        <input 
                                            type="text"
                                            placeholder={newMetric.category === 'Languages' ? 'e.g. Python' : 
                                                         newMetric.category === 'Technologies' ? 'e.g. Docker' : 
                                                         'e.g. 3 years experience with Python'}
                                            value={newMetric.value}
                                            onChange={(e) => setNewMetric({...newMetric, value: e.target.value})}
                                            className="w-full bg-zinc-50 dark:bg-zinc-900 border-none rounded-xl px-4 py-3 mt-1 dark:text-zinc-300 focus:ring-1 focus:ring-indigo-500"
                                        />
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="text-[10px] font-black uppercase text-indigo-500">Label (Fixed)</label>
                                            <input 
                                                type="text"
                                                value={newMetric.label}
                                                readOnly
                                                className="w-full bg-zinc-50 dark:bg-zinc-900 border-none rounded-xl px-4 py-3 mt-1 text-zinc-400 cursor-default"
                                            />
                                        </div>
                                        <div>
                                            <label className="text-[10px] font-black uppercase text-indigo-500">Value</label>
                                            <input 
                                                type="text"
                                                placeholder="Requirement..."
                                                value={newMetric.value}
                                                onChange={(e) => setNewMetric({...newMetric, value: e.target.value})}
                                                className="w-full bg-zinc-50 dark:bg-zinc-900 border-none rounded-xl px-4 py-3 mt-1 dark:text-zinc-300 focus:ring-1 focus:ring-indigo-500"
                                            />
                                        </div>
                                    </div>
                                )}
                                {/* Years of Experience for Languages - REMOVED */}
                           </div>
                           <div className="flex gap-3">
                             <button 
                                onClick={() => {
                                    addMetric();
                                    setIsAddingMetric(false);
                                }}
                                disabled={!newMetric.value && !newMetric.label}
                                className="flex-1 bg-indigo-600 text-white rounded-xl py-3 font-bold disabled:opacity-50 transition-colors shadow-lg shadow-indigo-500/20"
                             >
                                 Confirm Add
                             </button>
                             <button 
                                onClick={() => setIsAddingMetric(false)}
                                className="flex-1 px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl text-zinc-500 dark:text-zinc-400 font-bold"
                             >
                                 Cancel
                             </button>
                           </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Final Title Selection & Save Step */}
            <div className="relative mt-12 mb-6">
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/5 to-purple-500/5 dark:from-indigo-500/10 dark:to-purple-500/10 rounded-[2.5rem] blur-xl" />
                <div className="relative p-6 border border-zinc-200 dark:border-zinc-800/50 rounded-[1.5rem] bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md shadow-xl shadow-zinc-200/20 dark:shadow-none">
                    <div className="space-y-6">
                        <div className="flex items-center gap-4 p-4 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-white/50 dark:bg-zinc-950/50">
                            <div className="w-1/3">
                                <span className="text-sm font-black uppercase tracking-wider text-indigo-500">Configuration Name</span>
                            </div>
                            <div className="flex-1 flex items-center gap-2">
                                <span className="text-zinc-300 dark:text-zinc-700 font-light">:</span>
                                <input 
                                    type="text" 
                                    value={extractedData.title}
                                    onChange={(e) => setExtractedData({...extractedData, title: e.target.value})}
                                    placeholder="e.g. Senior Software Engineer Role"
                                    className="flex-1 bg-zinc-50/50 dark:bg-zinc-900/50 border-none rounded-lg px-3 py-2 text-zinc-900 dark:text-zinc-50 font-bold focus:ring-1 focus:ring-indigo-500 text-sm"
                                />
                            </div>
                        </div>
                        
                        <div className="flex flex-col sm:flex-row items-center justify-between gap-6 pt-2">
                            <p className="text-[10px] text-zinc-400 font-medium pl-2">
                                This name will be the primary identifier in your dashboard.
                            </p>
                            
                            <div className="flex items-center gap-3 w-full sm:w-auto">
                                <button
                                    onClick={() => setStep('upload')}
                                    className="px-5 py-2.5 rounded-xl font-bold text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200 transition-all text-xs"
                                >
                                    Back
                                </button>
                                <button
                                    onClick={handleFinalSave}
                                    disabled={isUploading || !extractedData.title}
                                    className="flex-1 sm:flex-none px-8 py-3 rounded-xl font-bold text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 transition-all shadow-lg shadow-indigo-600/25 active:scale-[0.97] text-xs flex items-center justify-center gap-2"
                                >
                                    {isUploading ? (
                                        <>
                                            <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            Saving...
                                        </>
                                    ) : (
                                        'Commit Requirements'
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Status Message */}
            {uploadStatus && (
                <div className={`p-4 rounded-lg border text-sm bg-green-50 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800`}>
                    {uploadStatus}
                </div>
            )}
        </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 mt-6">
      <div className="grid md:grid-cols-2 gap-6">
          {/* File Upload Zone */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center transition-colors h-64 flex flex-col justify-center items-center
              ${isDragging 
                ? 'border-indigo-400 dark:border-indigo-600 bg-indigo-50 dark:bg-zinc-900/50' 
                : 'border-zinc-300 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-600 bg-white dark:bg-zinc-950'
              }
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt,.md,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,text/markdown"
              onChange={handleFileInput}
              className="hidden"
              id="job-req-upload"
            />
            <label
              htmlFor="job-req-upload"
              className="cursor-pointer flex flex-col items-center gap-4"
            >
              <div className="w-12 h-12 bg-zinc-100 dark:bg-zinc-800 rounded-md flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-zinc-600 dark:text-zinc-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
                  <span className="text-indigo-600 dark:text-indigo-400">Upload a description</span> or drag & drop
                </p>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">PDF, DOCX, TXT, MD files only</p>
              </div>
            </label>
          </div>

          {/* Text Area Zone */}
          <div className="h-64 flex flex-col">
            <textarea 
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="flex-1 w-full bg-white dark:bg-zinc-950 border border-zinc-300 dark:border-zinc-700 rounded-lg p-4 resize-none focus:ring-2 focus:ring-indigo-500 dark:text-white"
              placeholder="Or paste the job description text here..."
            />
          </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
              Selected Files
            </h3>
            <span className="px-2 py-1 rounded text-xs font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300">
              1 file max
            </span>
          </div>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 border border-zinc-200 dark:border-zinc-800 rounded-lg bg-white dark:bg-zinc-950"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="ml-4 text-zinc-400 hover:text-red-500 transition-colors"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extraction Button */}
      {(files.length > 0 || text.trim()) && (
        <button
          onClick={handleExtract}
          disabled={isUploading}
          className="w-full px-6 py-3 rounded-md font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Extract Job Requirements
        </button>
      )}

      {/* Status Message */}
      {uploadStatus && (
        <div
          className={`p-4 rounded-lg border text-sm ${
            uploadStatus.includes('failed')
              ? 'bg-red-50 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800'
              : 'bg-green-50 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800'
          }`}
        >
          {uploadStatus}
        </div>
      )}
    </div>
  );
}
