'use client';

import { useState, useRef } from 'react';
import LinkSelection from './LinkSelection';

interface FileWithPreview extends File {
  preview?: string;
}

interface StructuredItem {
  name: string;
  subtitle: string;
  summary: string;
}

interface ExtractedCV {
  name: string | null;
  email: string | null;
  phone: string | null;
  links: Record<string, string[]>;
  skills: string[];
  projects: StructuredItem[];
  extracurricular: StructuredItem[];
  experience: string | null;
  education: StructuredItem[];
  cached?: boolean;
  file_id?: string;
  cv_url?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

export default function CVUpload() {
  const [step, setStep] = useState<'upload' | 'processing' | 'result'>('upload');
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [cacheData, setCacheData] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [batchName, setBatchName] = useState('');
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [processedCount, setProcessedCount] = useState(0);
  const [extractedCVs, setExtractedCVs] = useState<ExtractedCV[]>([]);
  const [linkMetrics, setLinkMetrics] = useState<{ 
    uploaded_files: number, 
    link_counts: Record<string, number>,
    example_links: Record<string, string>
  }>({
    uploaded_files: 0,
    link_counts: {},
    example_links: {}
  });
  const [selectedLinks, setSelectedLinks] = useState<Record<string, boolean>>({});
  const [sourceData, setSourceData] = useState<Record<string, any>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/markdown'
  ];
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

    if (newFiles.length !== fileList.length) {
        setUploadStatus('Some files were rejected. Only PDF, DOCX, TXT and MD files are allowed.');
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

  const handleExtractBatch = async () => {
    if (files.length === 0) {
      setUploadStatus('Please select at least one candidate file.');
      return;
    }

    const results: ExtractedCV[] = [];
    const counts: Record<string, number> = {};
    const exampleLinks: Record<string, string> = {};

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      setUploadStatus(`Processing ${file.name}...`);
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('cache_data', cacheData.toString());

      try {
        const response = await fetch(`${API_BASE_URL}/api/extract-cv`, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const data: ExtractedCV = await response.json();
          results.push(data);
          
          Object.keys(data.links).forEach(sourceIdx => {
            if (data.links[sourceIdx] && data.links[sourceIdx].length > 0) {
              counts[sourceIdx] = (counts[sourceIdx] || 0) + 1;
              if (!exampleLinks[sourceIdx]) {
                exampleLinks[sourceIdx] = data.links[sourceIdx][0];
              }
            }
          });
        }
      } catch (error) {
        console.error(`Failed to process ${file.name}:`, error);
      }
      setProcessedCount(i + 1);
    }

    setExtractedCVs(results);
    setLinkMetrics({
      uploaded_files: files.length,
      link_counts: counts,
      example_links: exampleLinks
    });

    // Search the entire batch for at least one candidate for each source preview
    setExtractedCVs(results);
    const sourcesToScan = ['github', 'linkedin'];
    const scannedSources = new Set<string>();

    for (const src of sourcesToScan) {
        // Find the first candidate in the batch that has a link for this source
        const candidateWithLink = results.find(c => c.links[src]?.[0]);
        const link = candidateWithLink?.links[src]?.[0];

        if (link && !scannedSources.has(src)) {
            setUploadStatus(`Performing ${src} intelligence scan for ${candidateWithLink.name || 'candidate'}...`);
            try {
                const res = await fetch(`${API_BASE_URL}/api/scan-datasource`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        source_type: src, 
                        url: link, 
                        cache_data: cacheData 
                    })
                });
                if (res.ok) {
                    const data = await res.json();
                    setSourceData(prev => ({ ...prev, [src]: data }));
                    scannedSources.add(src);
                }
            } catch (err) {
                console.error(`${src} scan failed:`, err);
            }
        }
    }
    
    // Default select all found links
    const initialSelected: Record<string, boolean> = {};
    Object.keys(counts).forEach(source => {
      initialSelected[source] = true;
    });
    setSelectedLinks(initialSelected);

    setStep('result');
    setIsUploading(false);
    setUploadStatus(`Batch processing complete.`);
  };

  const handleCommitBatch = async () => {
    setIsSaving(true);
    setUploadStatus('Committing batch results...');
    
    const enrichedCandidates = [];
    
    for (let i = 0; i < extractedCVs.length; i++) {
        const candidate = extractedCVs[i];
        setUploadStatus(`Enriching ${candidate.name || `Candidate ${i+1}`}...`);
        
        const scanResults: Record<string, any> = {};
        const sourcesToEnrich = Object.keys(selectedLinks).filter(s => 
          selectedLinks[s] && ['github', 'linkedin'].includes(s)
        );

        for (const src of sourcesToEnrich) {
            const link = candidate.links[src]?.[0];
            if (!link) continue;

            // Use first candidate's data if already scanned
            if (i === 0 && sourceData[src]) {
                scanResults[`${src}_enriched`] = sourceData[src];
                continue;
            }

            try {
                const res = await fetch(`${API_BASE_URL}/api/scan-datasource`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        source_type: src, 
                        url: link, 
                        cache_data: cacheData 
                    })
                });
                if (res.ok) {
                    scanResults[`${src}_enriched`] = await res.json();
                }
            } catch (e) {
                console.error(`Enrichment failed for ${src}:`, e);
            }
        }
        
        enrichedCandidates.push({
            ...candidate,
            ...scanResults,
            cv_url: candidate.cv_url // Explicitly preserve cv_url
        });
    }
    
    setUploadStatus('Pushing records and creating batch...');
    try {
        const response = await fetch(`${API_BASE_URL}/api/save-candidates`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                candidates: enrichedCandidates,
                batch_name: batchName || `Batch ${new Date().toLocaleDateString()}` 
            })
        });
        
        if (response.ok) {
            setUploadStatus(`Successfully committed ${enrichedCandidates.length} candidate profiles to batch "${batchName || 'Default'}"!`);
            setTimeout(() => {
                setStep('upload');
                setFiles([]);
                setExtractedCVs([]);
                setUploadStatus('');
                setBatchName('');
                setSourceData({});
            }, 2500);
        } else {
            const err = await response.json();
            setUploadStatus(`Failed to save: ${err.error || 'Server error'}`);
        }
    } catch (e) {
        setUploadStatus('Database synchronization failed. Please check network.');
    } finally {
        setIsSaving(false);
    }
  };

  const renderTemplatePreview = () => {
    if (extractedCVs.length === 0) return null;
    const template = extractedCVs[0];
    
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Left Column: Personal Info & Expertise */}
        <div className="lg:col-span-1 space-y-6">
            <div className="p-8 rounded-[2rem] bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-xl shadow-zinc-200/40 dark:shadow-none relative overflow-hidden group min-h-[200px] flex flex-col justify-center">
                {/* Decorative background icon to avoid text overlap */}
                <div className="absolute -right-2 -top-2 p-6 opacity-[0.03] dark:opacity-[0.08] transition-transform duration-700 pointer-events-none">
                    <svg className="w-24 h-24 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 24 24">
                       <path d="M12 14c3.31 0 6-2.69 6-6s-2.69-6-6-6-6 2.69-6 6 2.69 6 6 6zm0 2c-4.42 0-8 3.58-8 8h16c0-4.42-3.58-8-8-8z" />
                    </svg>
                </div>
                
                <div className="relative space-y-4">
                    <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0">
                            <p className="text-[10px] font-black text-indigo-500 uppercase tracking-widest mb-1">Full Name</p>
                            <h3 className="text-xl font-black dark:text-white leading-none truncate">
                                {template.name || 'Not Detected'}
                            </h3>
                        </div>
                        {template.cached !== undefined && (
                            <div className={`shrink-0 flex items-center gap-1.5 px-2 py-0.5 rounded border text-[8px] font-bold uppercase tracking-tighter ${
                                template.cached ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' : 'bg-amber-500/10 text-amber-500 border-amber-500/20'
                            }`}>
                                <div className={`w-1 h-1 rounded-full ${template.cached ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                                {template.cached ? 'CACHED' : 'SAVED'}
                            </div>
                        )}
                    </div>
                    
                    <div className="pt-4 space-y-3">
                        <div className="flex items-center gap-3 text-zinc-500 dark:text-zinc-400">
                           <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                           <span className="text-xs font-bold truncate">{template.email || 'Email missing'}</span>
                        </div>
                        <div className="flex items-center gap-3 text-zinc-500 dark:text-zinc-400">
                           <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                           <span className="text-xs font-bold truncate">{template.phone || 'Phone missing'}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="p-8 rounded-[2rem] bg-indigo-600 text-white shadow-xl shadow-indigo-600/20 relative overflow-hidden group">
                <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-white/10 rounded-full blur-2xl group-hover:scale-125 transition-transform" />
                <p className="text-[10px] font-black uppercase tracking-widest mb-4 opacity-70">Detected Expertise</p>
                <div className="max-h-[160px] overflow-y-auto pr-2 custom-scrollbar relative z-10">
                    <div className="flex flex-wrap gap-2">
                        {template.skills.slice(0, 20).map((skill, i) => (
                            <span key={i} className="px-3 py-1 bg-white/20 rounded-full text-[10px] font-black uppercase tracking-tight backdrop-blur-md border border-white/10">
                                {skill}
                            </span>
                        ))}
                        {template.skills.length === 0 && <span className="text-xs font-bold opacity-50 italic">No skills extracted</span>}
                    </div>
                </div>
            </div>

            {/* Academic Credentials (Structured - Moved here to balance) */}
            <div className="p-8 rounded-[2.5rem] bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 transition-colors">
                <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 mb-6">
                    Academic Credentials
                </h4>
                <div className="overflow-y-auto max-h-[220px] pr-4 custom-scrollbar space-y-6">
                    {template.education.map((edu, i) => (
                        <div key={i} className="space-y-1.5 border-l-2 border-emerald-500/30 pl-4 py-1.5 transition-colors">
                            <h5 className="text-[11px] font-black text-zinc-800 dark:text-zinc-200 leading-tight uppercase tracking-tight">{edu.name}</h5>
                            <p className="text-[10px] font-bold text-indigo-500/80 dark:text-indigo-400/80 italic">
                                {edu.subtitle}
                            </p>
                        </div>
                    ))}
                    {template.education.length === 0 && (
                        <p className="text-xs font-bold text-zinc-400 italic font-mono uppercase tracking-widest opacity-40">No academic detections</p>
                    )}
                </div>
            </div>

            {/* Extracurricular Activities (Moved here to balance height) */}
            <div className="p-8 rounded-[2rem] bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 group/extra">
                <div className="flex items-center justify-between mb-6">
                    <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400">
                        Extracurricular
                    </h4>
                    <span className="text-[10px] font-black px-2.5 py-0.5 bg-blue-500/10 text-blue-500 rounded-full border border-blue-500/20">
                        {template.extracurricular.length}
                    </span>
                </div>
                <div className="overflow-y-auto max-h-[260px] pr-4 custom-scrollbar space-y-4">
                    {template.extracurricular.map((act, i) => (
                        <div key={i} className="space-y-1 border-l-2 border-indigo-500/30 pl-4 py-1">
                            <h5 className="text-[11px] font-black text-zinc-800 dark:text-zinc-200 leading-none transition-colors">{act.name}</h5>
                            <p className="text-[9px] font-bold text-indigo-500/70 uppercase tracking-tighter">{act.subtitle}</p>
                            <p className="text-[10px] text-zinc-500 dark:text-zinc-400 line-clamp-2 leading-relaxed">{act.summary}</p>
                        </div>
                    ))}
                    {template.extracurricular.length === 0 && (
                        <p className="text-xs font-bold text-zinc-400 italic">No extracurricular records</p>
                    )}
                </div>
            </div>
        </div>

        {/* Right Column: Experience and Projects */}
        <div className="lg:col-span-2 space-y-10">
            {/* Experience Card (Expanded height) */}
            <div className="p-8 rounded-[2.5rem] bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-xl shadow-zinc-200/40 dark:shadow-none h-[480px] flex flex-col group overflow-hidden shrink-0">
                <div className="flex items-center justify-between mb-8">
                     <div className="flex items-center gap-3">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 group-hover:animate-ping" />
                        <h4 className="text-sm font-black uppercase tracking-[0.2em] text-zinc-400">
                            Extracted Experience
                        </h4>
                     </div>
                     <span className="px-3 py-1 bg-emerald-500/5 text-emerald-500 text-[9px] font-black rounded-lg border border-emerald-500/10 uppercase tracking-widest">
                        Validated Context
                     </span>
                </div>
                
                <div className="flex-1 overflow-y-auto pr-4 custom-scrollbar">
                    {template.experience ? (
                        <div className="text-sm font-medium leading-relaxed text-zinc-600 dark:text-zinc-300/80 whitespace-pre-wrap px-1">
                            {template.experience}
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-center space-y-4 py-12 opacity-20">
                            <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                            </svg>
                            <p className="text-xs font-black uppercase tracking-widest">No Professional History Extracted</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Structured Projects Section (Expanded height) */}
            <div className="p-8 rounded-[2rem] bg-zinc-900 border border-zinc-800 shadow-xl shadow-indigo-500/5 h-[400px] flex flex-col relative overflow-hidden group">
                <div className="flex items-center justify-between mb-6">
                    <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">Key Projects</p>
                    <span className="text-[10px] px-2 py-0.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded font-mono group-hover:bg-indigo-500/20 transition-colors">
                        {template.projects.length}
                    </span>
                </div>
                
                <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                    {template.projects.map((proj, i) => (
                        <div key={i} className="space-y-1.5 pb-4 border-b border-zinc-800 last:border-0 transition-colors rounded-lg">
                            <h5 className="text-xs font-black text-white uppercase tracking-tight">{proj.name}</h5>
                            <p className="text-[10px] font-bold text-indigo-400 italic leading-tight">{proj.subtitle}</p>
                            <p className="text-[10px] text-zinc-400 leading-relaxed line-clamp-2">{proj.summary}</p>
                        </div>
                    ))}
                    {template.projects.length === 0 && (
                        <p className="text-xs font-bold text-zinc-600 italic">No project data available</p>
                    )}
                </div>
            </div>
        </div>
      </div>
    );
  };

  if (step === 'processing') {
    return (
        <div className="w-full max-w-4xl mx-auto py-24 text-center space-y-10">
            <div className="relative mx-auto w-24 h-24">
                <div className="absolute inset-0 border-4 border-zinc-200 dark:border-zinc-800 rounded-full"></div>
                <div 
                    className="absolute inset-0 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"
                    style={{ animationDuration: '0.8s' }}
                ></div>
                <div className="absolute inset-0 flex items-center justify-center font-black dark:text-white">
                    {Math.round((processedCount / files.length) * 100)}%
                </div>
            </div>
            
            <div className="space-y-3">
                <h2 className="text-2xl font-black dark:text-white uppercase tracking-tighter">Processing Batch</h2>
                <p className="text-zinc-500 dark:text-zinc-400 font-medium">Extracting data from {files.length} candidate profiles.</p>
            </div>
            
            <div className="max-w-md mx-auto space-y-2 text-zinc-400 text-xs font-mono uppercase tracking-widest">
                <p className="animate-pulse">{uploadStatus}</p>
                <div className="w-full bg-zinc-100 dark:bg-zinc-900 h-1 rounded-full overflow-hidden">
                    <div 
                        className="bg-indigo-600 h-full transition-all duration-300 ease-out"
                        style={{ width: `${(processedCount / files.length) * 100}%` }}
                    />
                </div>
                <div className="flex justify-between">
                    <span>Initiated</span>
                    <span>{processedCount} / {files.length}</span>
                </div>
            </div>
        </div>
    );
  }

  if (step === 'result') {
    return (
        <div className="w-full max-w-4xl mx-auto space-y-10 mt-6 pb-20 fade-in animate-in">
            <div className="flex items-center justify-between px-2">
                <div className="space-y-1">
                    <h2 className="text-2xl font-black dark:text-white uppercase tracking-tighter flex items-center gap-3">
                        Batch Summary
                        {extractedCVs.some(cv => cv.cached) && (
                            <span className="flex items-center gap-1.5 px-2 py-0.5 rounded border border-emerald-500/20 bg-emerald-500/10 text-emerald-500 text-[9px] font-bold uppercase tracking-tight">
                                <span className="w-1 h-1 rounded-full bg-emerald-500" />
                                Cache Utilized
                            </span>
                        )}
                    </h2>
                    <p className="text-zinc-500 font-medium">{extractedCVs.length} successfuly extracted from {files.length} files.</p>
                </div>
                <button 
                  onClick={() => setStep('upload')}
                  className="text-xs font-black uppercase text-zinc-400 hover:text-indigo-500 transition-colors"
                >
                  Restart Batch
                </button>
            </div>
            <div className="grid gap-10">
                {/* 1. Candidate Snapshot Preview (CV Data) */}
                <div className="space-y-6">
                    <div className="flex items-center gap-4">
                        <span className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em] px-3 py-1 border border-indigo-500/30 rounded-full bg-indigo-500/5">Candidate Snapshot Preview</span>
                    </div>
                    {renderTemplatePreview()}
                </div>

                {/* 2. External Validation Streams (GitHub & LinkedIn) */}
                <div className="space-y-6">
                    <div className="flex items-center gap-4">
                        <span className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em] px-3 py-1 border border-indigo-500/30 rounded-full bg-indigo-500/5">Datasource Validation Streams</span>
                    </div>
                    <LinkSelection 
                        metrics={linkMetrics}
                        selectedLinks={selectedLinks}
                        setSelectedLinks={setSelectedLinks}
                        githubData={sourceData['github']}
                        linkedinData={sourceData['linkedin']}
                    />
                </div>

                {/* 3. Batch Configuration & Commit */}
                <div className="pt-6 relative space-y-6">
                    <div className="flex items-center gap-4 p-4 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-white/50 dark:bg-zinc-950/50 backdrop-blur-sm">
                        <div className="w-1/3">
                            <span className="text-[10px] font-black uppercase tracking-wider text-indigo-500">Assign Batch Name</span>
                        </div>
                        <div className="flex-1 flex items-center gap-2">
                            <span className="text-zinc-300 dark:text-zinc-700 font-light">:</span>
                            <input 
                                type="text" 
                                value={batchName}
                                onChange={(e) => setBatchName(e.target.value)}
                                placeholder="e.g. Summer 2024 Engineering Interns"
                                className="flex-1 bg-transparent border-none p-0 text-zinc-900 dark:text-zinc-50 font-bold focus:ring-0 text-xs"
                            />
                        </div>
                    </div>
                    
                    <div className="relative">
                        <div className="absolute inset-0 bg-blue-600/10 blur-3xl -z-10 rounded-full transform scale-50 translate-y-10" />
                        <button
                            onClick={handleCommitBatch}
                            disabled={isSaving || !batchName.trim()}
                            className="w-full py-4 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-black uppercase tracking-[0.1em] text-sm shadow-xl shadow-indigo-600/20 transition-all hover:scale-[1.01] active:scale-[0.98] flex items-center justify-center gap-3 group disabled:opacity-40"
                        >
                            {isSaving ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    Synchronising...
                                </>
                            ) : (
                                <>
                                    Commit Extracted Batch
                                    <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                    </svg>
                                </>
                            )}
                        </button>
                    </div>
                    <p className="text-center text-[10px] text-zinc-500 font-bold uppercase mt-4 tracking-widest opacity-50 italic">
                        Proceeding will finalise the extraction for {extractedCVs.length} candidates
                    </p>
                </div>
            </div>
        </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 mt-6 pb-12">
      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-3xl p-16 text-center transition-all duration-300 group
          ${isDragging 
            ? 'border-indigo-400 dark:border-indigo-600 bg-indigo-50 dark:bg-zinc-900/50 scale-[1.02] shadow-2xl' 
            : 'border-zinc-300 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-700 bg-white dark:bg-zinc-950 overflow-hidden'
          }
        `}
      >
        {!isDragging && (
            <div className="absolute -right-20 -bottom-20 w-64 h-64 bg-indigo-100/30 dark:bg-indigo-900/10 rounded-full blur-3xl pointer-events-none" />
        )}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.md,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,text/markdown"
          onChange={handleFileInput}
          className="hidden"
          id="cv-upload"
        />
        <label
          htmlFor="cv-upload"
          className="cursor-pointer flex flex-col items-center gap-6 relative"
        >
          <div className="w-16 h-16 bg-zinc-100 dark:bg-zinc-900 rounded-2xl flex items-center justify-center shadow-inner group-hover:scale-110 transition-transform duration-300">
            <svg
              className="w-8 h-8 text-indigo-600 dark:text-indigo-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>
          <div className="space-y-2">
            <p className="text-base font-bold text-zinc-900 dark:text-zinc-50 tracking-tight">
              <span className="text-indigo-600 dark:text-indigo-400">Initialize Batch Upload</span> or drag and drop
            </p>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 font-medium">
               Securely processes PDF, DOCX, TXT and MD profiles
            </p>
          </div>
        </label>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-4 pt-4">
          <div className="flex items-center justify-between border-b border-zinc-100 dark:border-zinc-800 pb-4 px-2">
            <h3 className="text-sm font-black uppercase tracking-[0.1em] text-zinc-400 flex items-center gap-3">
              Selected Profiles
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
            </h3>
            <span className="px-3 py-1 rounded-full text-[10px] font-black bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 uppercase tracking-widest border border-zinc-200 dark:border-zinc-700">
              {files.length} {files.length === 1 ? 'record' : 'records'}
            </span>
          </div>
          <div className="grid gap-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar pb-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 border border-zinc-200 dark:border-zinc-800/50 rounded-2xl bg-white dark:bg-zinc-950/50 group hover:border-indigo-500/50 transition-all hover:bg-zinc-50/50 dark:hover:bg-zinc-901/50"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="w-10 h-10 rounded-xl bg-zinc-50 dark:bg-zinc-900 flex items-center justify-center font-black dark:text-zinc-400 text-xs">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold text-zinc-900 dark:text-zinc-50 truncate">
                      {file.name}
                    </p>
                    <p className="text-[10px] font-black text-zinc-400 uppercase mt-0.5 tracking-widest">
                      {(file.size / 1024 / 1024).toFixed(2)} MB • {file.name.split('.').pop()?.toUpperCase()}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="ml-4 p-2 text-zinc-300 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cache Data Option */}
      {files.length > 0 && (
        <div className="flex flex-col gap-2 p-5 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/50 dark:bg-zinc-900/50 mt-4">
            <div className="flex items-center gap-3">
              <input 
                type="checkbox" 
                id="cache-data-cv" 
                checked={cacheData}
                onChange={(e) => setCacheData(e.target.checked)}
                className="w-4 h-4 rounded border-zinc-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label htmlFor="cache-data-cv" className="text-sm font-bold text-zinc-700 dark:text-zinc-300 cursor-pointer">
                Cache Extraction Data
              </label>
            </div>
            <p className="text-[10px] text-zinc-500 dark:text-zinc-400 leading-relaxed pl-7 text-left">
              <span className="font-bold text-amber-500 uppercase tracking-tighter mr-1">Note:</span> 
              Mainly for testing and debugging. Caches both CV parsing and external scans (GitHub/LinkedIn) to save API credits.
            </p>
        </div>
      )}

      {/* Submit Button */}
      {files.length > 0 && (
        <div className="pt-6">
            <button
            onClick={handleExtractBatch}
            disabled={isUploading}
            className="w-full px-8 py-5 rounded-2xl font-black text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-xl shadow-indigo-600/20 uppercase tracking-[0.2em] text-sm flex items-center justify-center gap-4 hover:scale-[1.01] active:scale-[0.99]"
            >
            {isUploading ? (
                <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Initializing Engines...
                </>
            ) : (
                <>
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Extract Candidate Batch
                </>
            )}
            </button>
        </div>
      )}

      {/* Status Message */}
      {uploadStatus && (
        <div
          className={`px-6 py-4 rounded-xl border text-xs font-bold uppercase tracking-widest flex items-center gap-3 ${
            uploadStatus.includes('failed')
              ? 'bg-red-50 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800'
              : 'bg-zinc-50 text-zinc-500 border-zinc-200 dark:bg-zinc-900/30 dark:text-zinc-500 dark:border-zinc-800'
          }`}
        >
          <div className={`w-2 h-2 rounded-full ${uploadStatus.includes('failed') ? 'bg-red-500' : 'bg-emerald-500'} animate-pulse`} />
          {uploadStatus}
        </div>
      )}
    </div>
  );
}
