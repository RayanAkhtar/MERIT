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
  category: 'General' | 'Education' | 'Languages' | 'Technologies' | 'Experience' | 'Soft Skills';
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

  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
  const allowedExtensions = ['.pdf', '.docx'];

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

    if (newFiles.length !== fileList.length) {
        setUploadStatus('Some files were rejected. Only PDF and DOCX files are allowed.');
    }

    setFiles(prev => [...prev, ...newFiles]);
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
        label: newMetric.label,
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
                <div>
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
                        className="w-full h-32 bg-transparent border-none focus:ring-0 resize-none text-zinc-600 dark:text-zinc-400"
                    />
                </div>
            </div>

            {/* Metrics List - Grouped by Category */}
            <div className="space-y-10">
                {(['General', 'Education', 'Languages', 'Technologies', 'Experience', 'Soft Skills'] as const).map((cat) => {
                    const catMetrics = extractedData.metrics.filter(m => m.category === cat);
                    if (catMetrics.length === 0 && !['Languages', 'Technologies', 'Soft Skills'].includes(cat)) return null;

                    return (
                        <div key={cat} className="space-y-4">
                            <div className="flex items-center justify-between border-b border-zinc-100 dark:border-zinc-800 pb-2">
                                <h3 className="text-sm font-black uppercase tracking-wider text-zinc-400">{cat}</h3>
                                {(['Languages', 'Technologies', 'Soft Skills'].includes(cat)) && (
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
                                        Add {cat.slice(0, -1)}
                                    </button>
                                )}
                            </div>
                            
                            <div className="grid gap-3">
                                {catMetrics.length === 0 ? (
                                    <p className="text-xs italic text-zinc-500 px-2">No {cat.toLowerCase()} extracted.</p>
                                ) : (
                                    catMetrics.map((metric) => (
                                        <div key={metric.id} className="flex items-center gap-4 p-3 pr-4 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-950 group hover:border-indigo-500/30 transition-all">
                                            <div className="flex-1 flex flex-col sm:flex-row sm:items-center gap-3">
                                                {/* Label Part */}
                                                <div className="w-full sm:w-1/3">
                                                    <input 
                                                        type="text" 
                                                        value={metric.label} 
                                                        placeholder="Label"
                                                        onChange={(e) => updateMetric(metric.id, 'label', e.target.value)}
                                                        className="w-full bg-transparent border-none rounded px-0 py-0 text-zinc-900 dark:text-zinc-50 font-bold focus:ring-0 text-sm"
                                                    />
                                                </div>
                                                
                                                {/* Value Part */}
                                                <div className="flex-1 flex items-center gap-2">
                                                    <span className="text-zinc-300 dark:text-zinc-700 font-light hidden sm:inline">:</span>
                                                    <input 
                                                        type="text" 
                                                        value={metric.value} 
                                                        placeholder={cat === 'Languages' ? 'Python/Java' : 'Requirement'}
                                                        onChange={(e) => updateMetric(metric.id, 'value', e.target.value)}
                                                        className="flex-1 bg-zinc-50/50 dark:bg-zinc-900/50 border-none rounded px-2 py-1 text-zinc-700 dark:text-zinc-300 focus:ring-1 focus:ring-indigo-500 text-sm"
                                                    />
                                                </div>

                                                {/* SubValue (Years) for Languages */}
                                                {cat === 'Languages' && (
                                                    <div className="w-full sm:w-32 flex items-center gap-2">
                                                        <span className="text-zinc-400 text-xs">Exp:</span>
                                                        <input 
                                                            type="text" 
                                                            placeholder="e.g. 3+ yrs"
                                                            value={metric.subValue || ''} 
                                                            onChange={(e) => updateMetric(metric.id, 'subValue', e.target.value)}
                                                            className="flex-1 bg-zinc-50/50 dark:bg-zinc-900/50 border-none rounded px-2 py-1 text-zinc-700 dark:text-zinc-300 focus:ring-1 focus:ring-indigo-500 text-sm"
                                                        />
                                                    </div>
                                                )}
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
                                    ))
                                )}
                            </div>
                        </div>
                    );
                })}

                {/* Legacy "Add Custom Metric" button for unusual cases */}
                {!isAddingMetric && (
                    <button 
                        onClick={() => setIsAddingMetric(true)}
                        className="flex items-center justify-center gap-2 w-full p-4 border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl text-zinc-500 hover:text-indigo-600 hover:border-indigo-600 transition-all group opacity-50 hover:opacity-100"
                    >
                        <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Add Global Metric
                    </button>
                )}

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
                                    </select>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-[10px] font-black uppercase text-indigo-500">Label</label>
                                        <input 
                                            type="text"
                                            placeholder="e.g. Python"
                                            value={newMetric.label}
                                            onChange={(e) => setNewMetric({...newMetric, label: e.target.value})}
                                            className="w-full bg-zinc-50 dark:bg-zinc-900 border-none rounded-xl px-4 py-3 mt-1 dark:text-zinc-300 focus:ring-1 focus:ring-indigo-500"
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
                                {newMetric.category === 'Languages' && (
                                    <div>
                                        <label className="text-[10px] font-black uppercase text-indigo-500">Years of Experience</label>
                                        <input 
                                            type="text"
                                            placeholder="e.g. 5+ yrs"
                                            value={newMetric.subValue}
                                            onChange={(e) => setNewMetric({...newMetric, subValue: e.target.value})}
                                            className="w-full bg-zinc-50 dark:bg-zinc-900 border-none rounded-xl px-4 py-3 mt-1 dark:text-zinc-300 focus:ring-1 focus:ring-indigo-500"
                                        />
                                    </div>
                                )}
                           </div>
                           <div className="flex gap-3">
                             <button 
                                onClick={addMetric}
                                disabled={!newMetric.label}
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

            {/* Actions */}
            <div className="flex gap-4">
                <button
                    onClick={() => setStep('upload')}
                    className="px-6 py-3 rounded-md font-medium text-zinc-700 dark:text-zinc-300 bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
                >
                    Back to Upload
                </button>
                <button
                    onClick={handleFinalSave}
                    disabled={isUploading}
                    className="flex-1 px-6 py-3 rounded-md font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                    {isUploading ? 'Finalizing...' : 'Save & Close Requirements'}
                </button>
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
              multiple
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
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
                  <span className="text-indigo-600 dark:text-indigo-400">Upload descriptions</span> or drag & drop
                </p>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">PDF, DOCX files only</p>
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
              {files.length} {files.length === 1 ? 'file' : 'files'}
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
