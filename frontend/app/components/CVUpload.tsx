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
  cv_experience: any[];
  experience: string | null;
  education: StructuredItem[];
  cached?: boolean;
  file_id?: string;
  cv_url?: string;
  cv_hash?: string;
  reused_from_db?: boolean;
  github_enriched?: any;
  linkedin_enriched?: any;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

export default function CVUpload() {
  const [mode, setMode] = useState<'extract' | 'import'>('extract');
  const [step, setStep] = useState<'upload' | 'processing' | 'result'>('upload');
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [cacheData, setCacheData] = useState(true);
  const [activeDragZone, setActiveDragZone] = useState<'cv' | 'cv_doc' | 'github' | 'linkedin' | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [batchName, setBatchName] = useState('');
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [processedCount, setProcessedCount] = useState(0);
  const [extractedCVs, setExtractedCVs] = useState<ExtractedCV[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Triple-Source Import States
  const [importFiles, setImportFiles] = useState<{
    cv: FileWithPreview[],
    cv_doc: FileWithPreview[],
    github: FileWithPreview[],
    linkedin: FileWithPreview[]
  }>({ cv: [], cv_doc: [], github: [], linkedin: [] });

  const nextCandidate = () => {
    if (currentIndex < extractedCVs.length - 1) {
        setCurrentIndex(currentIndex + 1);
    }
  };

  const prevCandidate = () => {
    if (currentIndex > 0) {
        setCurrentIndex(currentIndex - 1);
    }
  };
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
  const cvDocInputRef = useRef<HTMLInputElement>(null);
  const githubInputRef = useRef<HTMLInputElement>(null);
  const linkedinInputRef = useRef<HTMLInputElement>(null);

  const allowedTypes = mode === 'extract' 
    ? ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown']
    : ['application/json'];
  const allowedExtensions = mode === 'extract' 
    ? ['.pdf', '.docx', '.txt', '.md']
    : ['.json'];

  const validateFile = (file: File, type: string = 'cv'): boolean => {
    if (mode === 'extract') {
        const extractTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown'];
        return extractTypes.includes(file.type) || ['.pdf', '.docx', '.txt', '.md'].some(ext => file.name.toLowerCase().endsWith(ext));
    }
    
    // Import Mode
    if (type === 'cv_doc') {
        const docTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown'];
        return docTypes.includes(file.type) || ['.pdf', '.docx', '.txt', '.md'].some(ext => file.name.toLowerCase().endsWith(ext));
    }
    
    return file.type === 'application/json' || file.name.toLowerCase().endsWith('.json');
  };

  const handleFiles = (fileList: FileList | null, type: 'cv' | 'cv_doc' | 'github' | 'linkedin' = 'cv') => {
    if (!fileList) return;

    const newFiles: FileWithPreview[] = [];
    for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];
        if (validateFile(file, type)) {
            newFiles.push(file);
        }
    }

    if (newFiles.length !== fileList.length) {
        setUploadStatus(`Rejected some files. ${type === 'cv_doc' ? 'CV Documents must be PDF, DOCX, TXT or MD.' : 'JSON sources must be .json files.'}`);
    }

    if (mode === 'extract') {
        setFiles(prev => [...prev, ...newFiles]);
    } else {
        setImportFiles(prev => ({
            ...prev,
            [type]: [...prev[type], ...newFiles]
        }));
    }
  };

  const handleDragOver = (e: React.DragEvent, type: 'cv' | 'cv_doc' | 'github' | 'linkedin' = 'cv') => {
    e.preventDefault();
    setActiveDragZone(type);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setActiveDragZone(null);
  };

  const handleDrop = (e: React.DragEvent, type: 'cv' | 'cv_doc' | 'github' | 'linkedin' = 'cv') => {
    e.preventDefault();
    setActiveDragZone(null);
    handleFiles(e.dataTransfer.files, type);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>, type: 'cv' | 'cv_doc' | 'github' | 'linkedin' = 'cv') => {
    handleFiles(e.target.files, type);
    if (e.target) {
        e.target.value = '';
    }
  };

  const removeFile = (index: number, type: 'cv' | 'cv_doc' | 'github' | 'linkedin' = 'cv') => {
    if (mode === 'extract') {
        setFiles(prev => prev.filter((_, i) => i !== index));
    } else {
        setImportFiles(prev => ({
            ...prev,
            [type]: prev[type].filter((_, i) => i !== index)
        }));
    }
  };

  const handleExtractBatch = async () => {
    const isImport = mode === 'import';
    const totalFiles = isImport 
        ? importFiles.cv.length + importFiles.github.length + importFiles.linkedin.length 
        : files.length;

    if (totalFiles === 0) {
      setUploadStatus('Please select at least one file.');
      return;
    }

    setIsUploading(true);
    setStep('processing');

    const results: ExtractedCV[] = [];
    const counts: Record<string, number> = {};
    const exampleLinks: Record<string, string> = {};

    if (isImport) {
        setUploadStatus('Processing multi-source import...');
        
        // Helper to load and parse all files in a category
        const loadBatch = async (fileList: FileWithPreview[]) => {
            const items: any[] = [];
            for (const f of fileList) {
                try {
                    const text = await f.text();
                    const data = JSON.parse(text);
                    if (Array.isArray(data)) items.push(...data);
                    else items.push(data);
                } catch (e) { console.error("Parse error:", e); }
            }
            return items;
        };

        const cvData = await loadBatch(importFiles.cv);
        const ghData = await loadBatch(importFiles.github);
        const liData = await loadBatch(importFiles.linkedin);
        const rawDocs = importFiles.cv_doc;

        setUploadStatus('Unifying candidate identities...');
        
        // Merge strategy: CV is the anchor. Match GH/LI by URL if possible.
        cvData.forEach((cand: any) => {
            const unified: ExtractedCV = { ...cand };
            
            // Robust Matching Helpers
            const normalizeUrl = (url: string) => url?.toLowerCase().replace(/\/$/, '').trim();
            const extractUsername = (url: string) => {
                const parts = normalizeUrl(url)?.split('/');
                return parts ? parts[parts.length - 1] : null;
            };
            const normalizeName = (name: string) => name?.toLowerCase().replace(/[^a-z]/g, '').trim();

            const cvName = normalizeName(cand.name || '');

            // --- CV Doc Match ---
            const docMatch = rawDocs.find(d => {
                const fileName = normalizeName(d.name.split('.')[0]);
                return fileName && cvName && (fileName.includes(cvName) || cvName.includes(fileName));
            });
            if (docMatch) (unified as any).raw_cv = docMatch;

            // --- GitHub Match ---
            const cvGhUrl = normalizeUrl(cand.links?.github?.[0]);
            const cvGhUser = cvGhUrl ? extractUsername(cvGhUrl) : null;
            
            let ghMatch = ghData.find(g => {
                const gUrl = normalizeUrl(g.url || g.github_url || g.profile_url);
                const gUser = g.username || g.login || (gUrl ? extractUsername(gUrl) : null);
                const gName = normalizeName(g.name || g.full_name || '');
                
                // Priority 1: Username
                if (cvGhUser && gUser && cvGhUser === gUser) return true;
                // Priority 2: URL
                if (cvGhUrl && gUrl && cvGhUrl === gUrl) return true;
                // Priority 3: Name Fallback (Fuzzy/Contains)
                if (cvName && gName && (cvName === gName || cvName.includes(gName) || gName.includes(cvName))) return true;
                return false;
            });
            if (ghMatch) unified.github_enriched = ghMatch;

            // --- LinkedIn Match ---
            const cvLiUrl = normalizeUrl(cand.links?.linkedin?.[0]);
            const cvLiUser = cvLiUrl ? extractUsername(cvLiUrl) : null;

            let liMatch = liData.find(l => {
                const lUrl = normalizeUrl(l.url || l.linkedin_url || l.profile_url || l.linkedin_profile_url);
                const lUser = l.username || l.profile_id || (lUrl ? extractUsername(lUrl) : null);
                const lName = normalizeName(l.name || l.full_name || '');

                // Priority 1: Username
                if (cvLiUser && lUser && cvLiUser === lUser) return true;
                // Priority 2: URL
                if (cvLiUrl && lUrl && cvLiUrl === lUrl) return true;
                // Priority 3: Name Fallback (Fuzzy/Contains)
                if (cvName && lName && (cvName === lName || cvName.includes(lName) || lName.includes(cvName))) return true;
                return false;
            });
            if (liMatch) unified.linkedin_enriched = liMatch;

            results.push(unified);

            // Metrics
            Object.keys(unified.links || {}).forEach(src => {
                if (unified.links[src]?.length > 0) {
                    counts[src] = (counts[src] || 0) + 1;
                    if (!exampleLinks[src]) exampleLinks[src] = unified.links[src][0];
                }
            });
        });

        // we assume cv is the primary record.
        setProcessedCount(totalFiles);
    } else {
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
                    
                    Object.keys(data.links || {}).forEach(sourceIdx => {
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
    }

    setExtractedCVs(results);
    setLinkMetrics({
      uploaded_files: mode === 'import' ? results.length : files.length,
      link_counts: counts,
      example_links: exampleLinks
    });

    if (mode === 'extract') {
        const sourcesToScan = ['github', 'linkedin'];
        const scannedSources = new Set<string>();

        for (const src of sourcesToScan) {
            const candidateWithLink = results.find(c => c.links[src]?.[0]);
            const link = candidateWithLink?.links[src]?.[0];

            if (link && !scannedSources.has(src)) {
                const reclaimedData = candidateWithLink[`${src}_enriched` as keyof ExtractedCV];
                if (reclaimedData) {
                    setSourceData(prev => ({ ...prev, [src]: reclaimedData }));
                    scannedSources.add(src);
                    continue;
                }

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
    setProcessedCount(0);
    setUploadStatus('Committing batch results...');
    
    const enrichedCandidates = [];
    
    for (let i = 0; i < extractedCVs.length; i++) {
        const candidate = extractedCVs[i];
        
        if (mode === 'import') {
            const importCandidate = { ...candidate };
            
            // Check if we need to upload a raw CV doc
            if ((candidate as any).raw_cv) {
                setUploadStatus(`Uploading CV for ${candidate.name || `Candidate ${i+1}`}...`);
                const formData = new FormData();
                formData.append('file', (candidate as any).raw_cv);
                
                try {
                    const uploadRes = await fetch(`${API_BASE_URL}/api/upload-cv`, {
                        method: 'POST',
                        body: formData
                    });
                    if (uploadRes.ok) {
                        const uploadData = await uploadRes.json();
                        importCandidate.cv_url = uploadData.cv_url;
                        importCandidate.cv_hash = uploadData.cv_hash;
                    }
                } catch (e) {
                    console.error("CV upload failed:", e);
                }
            }

            enrichedCandidates.push(importCandidate);
            setProcessedCount(i + 1);
            continue;
        }

        setUploadStatus(`Enriching ${candidate.name || `Candidate ${i+1}`}...`);
        
        const scanResults: Record<string, any> = {};
        const sourcesToEnrich = Object.keys(selectedLinks).filter(s => 
          selectedLinks[s] && ['github', 'linkedin'].includes(s)
        );

        for (const src of sourcesToEnrich) {
            const link = candidate.links[src]?.[0];
            if (!link) continue;

            if (candidate[`${src}_enriched` as keyof ExtractedCV]) {
                scanResults[`${src}_enriched`] = candidate[`${src}_enriched` as keyof ExtractedCV];
                continue;
            }

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
            cv_url: candidate.cv_url
        });
        
        setProcessedCount(i + 1);
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
                setCurrentIndex(0);
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
    const candidate = extractedCVs[currentIndex];
    if (!candidate) return null;

    return (
      <div className="p-8 rounded-[2.5rem] bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-xl space-y-10 relative overflow-hidden group">
        {/* Header: Identity & Contact */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-zinc-100 dark:border-zinc-800/50 pb-8">
            <div className="space-y-2">
                <h3 className="text-4xl font-black text-zinc-900 dark:text-zinc-50 tracking-tighter uppercase leading-none italic">
                    {candidate.name || 'Anonymous Candidate'}
                </h3>
                <div className="flex flex-wrap gap-4 text-[10px] font-black uppercase tracking-widest text-zinc-400">
                    <span className="flex items-center gap-2">
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                        {candidate.email || 'No Email'}
                    </span>
                    <span className="flex items-center gap-2">
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                        {candidate.phone || 'No Phone'}
                    </span>
                </div>
            </div>
            {((candidate as any).raw_cv || candidate.cv_url) && (
                <a 
                    href={(candidate as any).raw_cv ? URL.createObjectURL((candidate as any).raw_cv) : candidate.cv_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="px-6 py-3 rounded-2xl bg-zinc-100 dark:bg-zinc-900 text-zinc-900 dark:text-zinc-50 text-[10px] font-black uppercase tracking-widest border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-800 transition-all flex items-center gap-3"
                >
                    {(candidate as any).raw_cv ? 'Preview Local CV' : 'View Original Document'}
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                </a>
            )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Left: Skills & Experience */}
            <div className="space-y-10 text-left">
                <section className="space-y-4 text-left">
                    <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-500 flex items-center gap-3">
                        Technical Skill Palette
                        <div className="h-px flex-1 bg-gradient-to-r from-indigo-500/20 to-transparent" />
                    </h4>
                    <div className="flex flex-wrap gap-2">
                        {candidate.skills?.length > 0 ? (
                            candidate.skills.map((skill, i) => (
                                <span key={i} className="px-3 py-1 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-100 dark:border-zinc-800 text-[10px] font-bold text-zinc-600 dark:text-zinc-400">
                                    {skill}
                                </span>
                            ))
                        ) : (
                            <p className="text-xs text-zinc-500 italic">No skills extracted.</p>
                        )}
                    </div>
                </section>

                <section className="space-y-4 text-left">
                    <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-500 flex items-center gap-3">
                        Extracted Experience
                        <div className="h-px flex-1 bg-gradient-to-r from-indigo-500/20 to-transparent" />
                    </h4>
                    <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium whitespace-pre-wrap">
                        {candidate.experience || 'No detailed experience summary found.'}
                    </p>
                </section>
            </div>

            {/* Right: Featured Projects/History */}
            <div className="space-y-10 text-left">
                <section className="space-y-6 text-left">
                    <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-500 flex items-center gap-3">
                        Project Evidence
                        <div className="h-px flex-1 bg-gradient-to-r from-indigo-500/20 to-transparent" />
                    </h4>
                    <div className="space-y-4">
                        {candidate.projects?.length > 0 ? (
                            candidate.projects.slice(0, 3).map((proj, i) => (
                                <div key={i} className="p-4 rounded-2xl bg-zinc-50/50 dark:bg-zinc-900/30 border border-zinc-100 dark:border-zinc-800/50 space-y-1">
                                    <p className="text-xs font-black text-zinc-900 dark:text-zinc-50 uppercase tracking-tight">{proj.name}</p>
                                    <p className="text-[10px] text-zinc-500 font-medium line-clamp-2">{proj.summary}</p>
                                </div>
                            ))
                        ) : (
                            <p className="text-xs text-zinc-500 italic">No specific projects identified.</p>
                        )}
                    </div>
                </section>
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
                                Cache Utilised
                            </span>
                        )}
                    </h2>
                    {mode === 'import' ? (
                        <p className="text-zinc-500 font-medium">
                            Showing candidate {currentIndex + 1} of {extractedCVs.length}.
                        </p>
                    ) : (
                        <p className="text-zinc-500 font-medium">
                            Displaying representative batch preview ({extractedCVs.length} profiles).
                        </p>
                    )}
                </div>
                <div className="flex items-center gap-4">
                    {extractedCVs.length > 1 && mode === 'import' && (
                        <div className="flex items-center gap-2 mr-4">
                            <button 
                                onClick={prevCandidate}
                                disabled={currentIndex === 0}
                                className="p-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400 disabled:opacity-30 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-all"
                            >
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                                </svg>
                            </button>
                            <button 
                                onClick={nextCandidate}
                                disabled={currentIndex === extractedCVs.length - 1}
                                className="p-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400 disabled:opacity-30 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-all"
                            >
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                            </button>
                        </div>
                    )}
                    <button 
                        onClick={() => {
                            setStep('upload');
                            setFiles([]);
                            setExtractedCVs([]);
                            setCurrentIndex(0);
                        }}
                        className="text-xs font-black uppercase text-zinc-400 hover:text-indigo-500 transition-colors"
                    >
                    Restart Batch
                    </button>
                </div>
            </div>
            <div className="grid gap-10">
                {/* Candidate Snapshot Preview (CV Data) */}
                <div className="space-y-6">
                    <div className="flex items-center gap-4">
                        <span className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em] px-3 py-1 border border-indigo-500/30 rounded-full bg-indigo-500/5">Candidate Snapshot Preview</span>
                    </div>
                    {renderTemplatePreview()}
                </div>

                {/* External Validation Streams (GitHub & LinkedIn) */}
                <div className="space-y-6">
                    <div className="flex items-center gap-4">
                        <span className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em] px-3 py-1 border border-indigo-500/30 rounded-full bg-indigo-500/5">Datasource Validation Streams</span>
                    </div>
                    <LinkSelection 
                        mode={mode}
                        metrics={linkMetrics}
                        selectedLinks={selectedLinks}
                        setSelectedLinks={setSelectedLinks}
                        githubData={extractedCVs[currentIndex]?.github_enriched || sourceData['github']}
                        linkedinData={extractedCVs[currentIndex]?.linkedin_enriched || sourceData['linkedin']}
                    />
                </div>

                {/* Batch Configuration & Commit */}
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
                            className="relative w-full py-4 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-black uppercase tracking-[0.1em] text-sm shadow-xl shadow-indigo-600/20 transition-all hover:scale-[1.01] active:scale-[0.98] flex items-center justify-center gap-3 group disabled:opacity-80 disabled:hover:scale-100 disabled:active:scale-100 overflow-hidden"
                        >
                            {isSaving ? (
                                <>
                                    <div 
                                        className="absolute left-0 top-0 bottom-0 bg-indigo-800 transition-all duration-300 ease-out z-0"
                                        style={{ width: `${(processedCount / Math.max(1, extractedCVs.length)) * 100}%` }}
                                    />
                                    <div className="relative z-10 flex items-center gap-3">
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        <span>Synchronising ({processedCount}/{extractedCVs.length})...</span>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <span className="relative z-10">Commit Extracted Batch</span>
                                    <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
      {/* Mode Selector */}
      <div className="flex p-1 bg-zinc-100 dark:bg-zinc-900 rounded-2xl w-fit mx-auto mb-8 border border-zinc-200 dark:border-zinc-800">
        <button
          onClick={() => { setMode('extract'); setFiles([]); setUploadStatus(''); }}
          className={`px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${
            mode === 'extract' 
              ? 'bg-white dark:bg-zinc-800 text-indigo-600 shadow-md' 
              : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'
          }`}
        >
          Intelligence Extraction
        </button>
        <button
          onClick={() => { setMode('import'); setFiles([]); setUploadStatus(''); }}
          className={`px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${
            mode === 'import' 
              ? 'bg-white dark:bg-zinc-800 text-amber-600 shadow-md' 
              : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'
          }`}
        >
          Static Data Import
        </button>
      </div>

      {/* Drop Zone(s) */}
      {mode === 'extract' ? (
        <div
          onDragOver={(e) => handleDragOver(e, 'cv')}
          onDragLeave={handleDragLeave}
          onDrop={(e) => handleDrop(e, 'cv')}
          className={`
            relative border-2 border-dashed rounded-3xl p-16 text-center transition-all duration-300 group
            ${activeDragZone === 'cv' ? 'border-indigo-400 bg-indigo-50' : 'border-zinc-300 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-700 bg-white dark:bg-zinc-950 overflow-hidden'}
          `}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.md"
            onChange={(e) => handleFileInput(e, 'cv')}
            className="hidden"
            id="cv-upload"
          />
          <label htmlFor="cv-upload" className="cursor-pointer flex flex-col items-center gap-6 relative">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center shadow-inner group-hover:scale-110 transition-transform duration-300 bg-indigo-100 dark:bg-indigo-900/30">
                <svg className="w-8 h-8 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
            </div>
            <div className="space-y-2">
              <p className="text-base font-bold text-zinc-900 dark:text-zinc-50 tracking-tight text-center">
                <span className="text-indigo-600 dark:text-indigo-400">Initialise Batch Upload</span> or drag and drop
              </p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 font-medium text-center">
                 Securely processes PDF, DOCX, TXT and MD profiles
              </p>
            </div>
          </label>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          {/* CV JSON Import Zone */}
          <div
            onDragOver={(e) => handleDragOver(e, 'cv')}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, 'cv')}
            className={`relative border-2 border-dashed rounded-3xl p-8 text-center transition-all duration-300 group ${activeDragZone === 'cv' ? 'border-amber-400 bg-amber-50' : 'border-zinc-300 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-700 bg-white dark:bg-zinc-950 overflow-hidden'}`}
          >
            <input ref={fileInputRef} type="file" multiple accept=".json" onChange={(e) => handleFileInput(e, 'cv')} className="hidden" id="import-cv" />
            <label htmlFor="import-cv" className="cursor-pointer flex flex-col items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center text-amber-600 dark:text-amber-400 group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-bold text-zinc-900 dark:text-zinc-50 leading-tight">CV JSONs</p>
                <p className="text-[10px] text-zinc-500 uppercase font-black tracking-tighter">{importFiles.cv.length} Selected</p>
              </div>
            </label>
          </div>

          {/* Raw CV Documents Zone */}
          <div
            onDragOver={(e) => handleDragOver(e, 'cv_doc')}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, 'cv_doc')}
            className={`relative border-2 border-dashed rounded-3xl p-8 text-center transition-all duration-300 group ${activeDragZone === 'cv_doc' ? 'border-amber-400 bg-amber-50' : 'border-zinc-300 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-700 bg-white dark:bg-zinc-950 overflow-hidden'}`}
          >
            <input ref={cvDocInputRef} type="file" multiple accept=".pdf,.docx,.txt,.md" onChange={(e) => handleFileInput(e, 'cv_doc')} className="hidden" id="import-cv-doc" />
            <label htmlFor="import-cv-doc" className="cursor-pointer flex flex-col items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center text-amber-600 dark:text-amber-400 group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-bold text-zinc-900 dark:text-zinc-50 leading-tight">Raw CV Docs</p>
                <p className="text-[10px] text-zinc-500 uppercase font-black tracking-tighter">{importFiles.cv_doc.length} Selected</p>
              </div>
            </label>
          </div>

          {/* GitHub Import Zone */}
          <div
            onDragOver={(e) => handleDragOver(e, 'github')}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, 'github')}
            className={`relative border-2 border-dashed rounded-3xl p-8 text-center transition-all duration-300 group ${activeDragZone === 'github' ? 'border-amber-400 bg-amber-50' : 'border-zinc-300 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-700 bg-white dark:bg-zinc-950 overflow-hidden'}`}
          >
            <input ref={githubInputRef} type="file" multiple accept=".json" onChange={(e) => handleFileInput(e, 'github')} className="hidden" id="import-github" />
            <label htmlFor="import-github" className="cursor-pointer flex flex-col items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center text-amber-600 dark:text-amber-400 group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.43.372.823 1.102.823 2.222 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" /></svg>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-bold text-zinc-900 dark:text-zinc-50 leading-tight">GitHub JSONs</p>
                <p className="text-[10px] text-zinc-500 uppercase font-black tracking-tighter">{importFiles.github.length} Selected</p>
              </div>
            </label>
          </div>

          {/* LinkedIn Import Zone */}
          <div
            onDragOver={(e) => handleDragOver(e, 'linkedin')}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, 'linkedin')}
            className={`relative border-2 border-dashed rounded-3xl p-8 text-center transition-all duration-300 group ${activeDragZone === 'linkedin' ? 'border-amber-400 bg-amber-50' : 'border-zinc-300 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-700 bg-white dark:bg-zinc-950 overflow-hidden'}`}
          >
            <input ref={linkedinInputRef} type="file" multiple accept=".json" onChange={(e) => handleFileInput(e, 'linkedin')} className="hidden" id="import-linkedin" />
            <label htmlFor="import-linkedin" className="cursor-pointer flex flex-col items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center text-amber-600 dark:text-amber-400 group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" /></svg>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-bold text-zinc-900 dark:text-zinc-50 leading-tight">LinkedIn JSONs</p>
                <p className="text-[10px] text-zinc-500 uppercase font-black tracking-tighter">{importFiles.linkedin.length} Selected</p>
              </div>
            </label>
          </div>
        </div>
      )}

      {/* File Lists */}
      {mode === 'extract' ? (
        files.length > 0 && (
            <div className="space-y-4 pt-4 text-left">
              <div className="flex items-center justify-between border-b border-zinc-100 dark:border-zinc-800 pb-4 px-2">
                <h3 className="text-sm font-black uppercase tracking-[0.1em] text-zinc-400 flex items-center gap-3">
                  Selected Profiles
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                </h3>
                <span className="px-3 py-1 rounded-full text-[10px] font-black bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 uppercase tracking-widest border border-zinc-200 dark:border-zinc-700">
                  {files.length} {files.length === 1 ? 'file' : 'files'}
                </span>
              </div>
              <div className="grid gap-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar pb-2">
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-2xl bg-white dark:bg-zinc-950/50 group transition-all border-zinc-200 dark:border-zinc-800/50 hover:border-indigo-500/50"
                  >
                    <div className="flex items-center gap-4 flex-1 min-w-0">
                      <div className="w-10 h-10 rounded-xl bg-zinc-50 dark:bg-zinc-900 flex items-center justify-center font-black dark:text-zinc-400 text-xs text-left">
                        {index + 1}
                      </div>
                      <div className="flex-1 min-w-0 text-left">
                        <p className="text-sm font-bold text-zinc-900 dark:text-zinc-50 truncate">
                          {file.name}
                        </p>
                        <p className="text-[10px] font-black text-zinc-400 uppercase mt-0.5 tracking-widest">
                          {(file.size / 1024).toFixed(1)} KB • {file.name.split('.').pop()?.toUpperCase()}
                        </p>
                      </div>
                    </div>
                    <button onClick={() => removeFile(index, 'cv')} className="ml-4 p-2 text-zinc-300 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100">
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )
      ) : (
        (importFiles.cv.length > 0 || importFiles.cv_doc.length > 0 || importFiles.github.length > 0 || importFiles.linkedin.length > 0) && (
            <div className="space-y-6 pt-4">
                {['cv', 'cv_doc', 'github', 'linkedin'].map((type) => (
                    importFiles[type as keyof typeof importFiles].length > 0 && (
                        <div key={type} className="space-y-3">
                            <div className="flex items-center justify-between border-b border-zinc-100 dark:border-zinc-800 pb-2 px-2">
                                <h3 className="text-[10px] font-black uppercase tracking-widest text-zinc-400">{type.replace('_', ' ')} Batch</h3>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                {importFiles[type as keyof typeof importFiles].map((f, i) => (
                                    <div key={i} className="flex items-center justify-between p-3 border border-zinc-100 dark:border-zinc-800/50 rounded-xl bg-white dark:bg-zinc-950/50 group">
                                        <p className="text-[10px] font-bold text-zinc-600 dark:text-zinc-400 truncate max-w-[200px]">{f.name}</p>
                                        <button onClick={() => removeFile(i, type as any)} className="text-zinc-300 hover:text-red-500 transition-colors">
                                            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )
                ))}
            </div>
        )
      )}

      {/* Cache Data Option (Only for Standard Extraction) */}
      {mode === 'extract' && files.length > 0 && (
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
      {(files.length > 0 || Object.values(importFiles).some(f => f.length > 0)) && (
        <div className="pt-6">
            <button
            onClick={handleExtractBatch}
            disabled={isUploading}
            className={`w-full px-8 py-5 rounded-2xl font-black text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-xl uppercase tracking-[0.2em] text-sm flex items-center justify-center gap-4 hover:scale-[1.01] active:scale-[0.99] ${
                mode === 'extract' ? 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-600/20' : 'bg-amber-600 hover:bg-amber-500 shadow-amber-600/20'
            }`}
            >
            {isUploading ? (
                <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Initialising Engines...
                </>
            ) : (
                <>
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    {mode === 'extract' ? 'Extract Candidate Batch' : 'Ingest Unified Batch'}
                </>
            )}
            </button>
        </div>
      )}

      {/* Status Message */}
      {uploadStatus && (
        <div
          className={`px-6 py-4 rounded-xl border text-xs font-bold uppercase tracking-widest flex items-center gap-3 ${
            uploadStatus.includes('failed') || uploadStatus.includes('Rejected')
              ? 'bg-red-50 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800'
              : mode === 'extract' 
                ? 'bg-zinc-50 text-zinc-500 border-zinc-200 dark:bg-zinc-900/30 dark:text-zinc-500 dark:border-zinc-800'
                : 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800'
          }`}
        >
          <div className={`w-2 h-2 rounded-full ${uploadStatus.includes('failed') || uploadStatus.includes('Rejected') ? 'bg-red-500' : mode === 'extract' ? 'bg-emerald-500' : 'bg-amber-500'} animate-pulse`} />
          {uploadStatus}
        </div>
      )}
    </div>
  );
}
