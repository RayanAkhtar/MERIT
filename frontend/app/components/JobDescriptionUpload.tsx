'use client';

import { useState, useRef } from 'react';
import JobDescriptionReview, { ExtractedData } from './JobDescriptionReview';

interface FileWithPreview extends File {
  preview?: string;
}

const JobDescriptionUpload = () => {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [step, setStep] = useState<'upload' | 'review'>('upload');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [extractedDataList, setExtractedDataList] = useState<ExtractedData[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown'];
  const allowedExtensions = ['.pdf', '.docx', '.txt', '.md'];

  const validateFile = (file: File) => {
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    return allowedTypes.includes(file.type) || allowedExtensions.includes(extension);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      const validFiles = selectedFiles.filter(validateFile);
      
      if (validFiles.length > 0) {
        setFiles(validFiles);
        setUploadStatus('');
      } else if (selectedFiles.length > 0) {
        setUploadStatus('Invalid file type(s). Please upload PDF, DOCX, TXT, or MD files.');
      }
    }
  };

  const [uploadProgress, setUploadProgress] = useState(0);

  const handleUpload = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    setUploadProgress(0);
    const allResults: ExtractedData[] = [];
    
    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const currentProgress = Math.round(((i) / files.length) * 100);
        setUploadProgress(currentProgress);
        setUploadStatus(`Processing (${i + 1}/${files.length}): ${file.name}...`);

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'}/api/extract-job-description`, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          const results = Array.isArray(data) ? data : [data];
          allResults.push(...results);
        } else {
          const errorData = await response.json();
          setUploadStatus(`Extraction failed for ${file.name}: ${errorData.error || 'Unknown error'}`);
          setIsUploading(false);
          return;
        }
      }

      setUploadProgress(100);
      setExtractedDataList(allResults);
      setCurrentIndex(0);
      setStep('review');
      setUploadStatus('');
    } catch (error) {
      setUploadStatus('Network error. Please ensure the backend is running.');
    } finally {
      setIsUploading(false);
    }
  };

  const updateCurrentData = (newData: ExtractedData) => {
    setExtractedDataList(prev => {
        const next = [...prev];
        next[currentIndex] = newData;
        return next;
    });
  };

  const handleFinalSave = async () => {
    if (extractedDataList.length === 0) return;
    setIsUploading(true);
    setUploadStatus(`Synchronising ${extractedDataList.length} description(s)...`);

    try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'}/api/save-job-description`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(extractedDataList),
        });

        if (response.ok) {
            setUploadStatus('Batch Job Descriptions successfully synchronised to repository.');
        } else {
            const err = await response.json();
            setUploadStatus(`Save failed: ${err.error}`);
        }
    } catch (error) {
        setUploadStatus('Sync failed. Please check your connection.');
    } finally {
        setIsUploading(false);
    }
  };

  const nextItem = () => {
    if (currentIndex < extractedDataList.length - 1) {
        setCurrentIndex(currentIndex + 1);
    }
  };

  const prevItem = () => {
    if (currentIndex > 0) {
        setCurrentIndex(currentIndex - 1);
    }
  };

  if (step === 'review' && extractedDataList.length > 0) {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-8 mt-6">
          <div className="flex items-center justify-between">
              <div className="space-y-2">
                  <h2 className="text-2xl font-bold dark:text-white">Review Descriptions</h2>
                  <p className="text-zinc-500">
                    Showing item {currentIndex + 1} of {extractedDataList.length}. 
                    Verify and edit before batch saving.
                  </p>
              </div>

              {extractedDataList.length > 1 && (
                  <div className="flex items-center gap-3">
                      <button 
                        onClick={prevItem}
                        disabled={currentIndex === 0}
                        className="p-3 rounded-xl border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400 disabled:opacity-30 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-all"
                      >
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                          </svg>
                      </button>
                      <button 
                        onClick={nextItem}
                        disabled={currentIndex === extractedDataList.length - 1}
                        className="p-3 rounded-xl border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400 disabled:opacity-30 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-all"
                      >
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                      </button>
                  </div>
              )}
          </div>
          
          <JobDescriptionReview 
            data={extractedDataList[currentIndex]}
            setData={updateCurrentData}
            onSave={handleFinalSave}
            isSaving={isUploading}
            statusMessage={uploadStatus}
            saveButtonText={extractedDataList.length > 1 ? `Commit Batch (${extractedDataList.length})` : "Commit Description"}
          />

          <div className="flex justify-center pb-20">
            <button
                onClick={() => setStep('upload')}
                className="px-5 py-2.5 rounded-xl font-bold text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200 transition-all text-xs"
            >
                Back to Upload
            </button>
          </div>
      </div>
    );
  }

  return (
    <>
      <div className="w-full max-w-2xl mx-auto mt-12 bg-zinc-50/50 dark:bg-zinc-950/50 border border-zinc-200 dark:border-zinc-800 rounded-[2.5rem] p-10 shadow-2xl shadow-indigo-500/5 relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 blur-3xl rounded-full -mr-16 -mt-16 group-hover:bg-indigo-500/10 transition-colors" />
        
        <div className="flex flex-col items-center text-center space-y-8 relative">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept=".pdf,.docx,.txt,.md"
            multiple
          />

          <div className="w-20 h-20 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-500 rounded-2xl flex items-center justify-center shadow-xl">
             <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
             </svg>
          </div>

          <div className="space-y-2">
            <h3 className="text-xl font-black dark:text-zinc-50 uppercase tracking-tighter">
              {files.length > 0 
                ? files.length === 1 ? files[0].name : `${files.length} files selected`
                : 'Job Description Upload'}
            </h3>
            <p className="text-zinc-500 text-xs font-medium max-w-[240px] leading-relaxed mx-auto">
              Extract refined metadata from multiple PDF, DOCX, TXT or Markdown files in batch.
            </p>
          </div>

          <div className="flex items-center gap-6 pt-4">
            <button
              onClick={() => files.length > 0 ? handleUpload() : fileInputRef.current?.click()}
              disabled={isUploading}
              className={`px-10 py-3.5 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all active:scale-95 flex items-center gap-3 ${
                files.length > 0 
                  ? 'bg-indigo-600 text-white hover:bg-indigo-500 shadow-xl shadow-indigo-600/20' 
                  : 'bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 hover:opacity-90'
              }`}
            >
              {isUploading ? (
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
              ) : null}
              {files.length > 0 ? 'Initialise batch extraction' : 'Select target files'}
            </button>
            
            {files.length > 0 && !isUploading && (
              <button
                onClick={() => setFiles([])}
                className="text-[10px] font-black uppercase text-zinc-400 hover:text-red-500 transition-colors tracking-widest"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </div>

      {isUploading && files.length > 1 && (
        <div className="max-w-2xl mx-auto mt-8 px-4">
          <div className="h-1.5 w-full bg-zinc-100 dark:bg-zinc-900 rounded-full overflow-hidden">
            <div 
              className="h-full bg-indigo-600 transition-all duration-500 ease-out rounded-full shadow-[0_0_12px_rgba(79,70,229,0.4)]"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <div className="flex justify-between mt-2">
            <span className="text-[10px] font-black uppercase text-zinc-400 tracking-widest">Extraction Progress</span>
            <span className="text-[10px] font-black uppercase text-indigo-600 tracking-widest">{uploadProgress}%</span>
          </div>
        </div>
      )}

      {uploadStatus && (
        <div className="max-w-2xl mx-auto">
          <div className={`mt-6 p-4 rounded-xl border text-sm text-center font-medium animate-in slide-in-from-top-2 duration-300
            ${uploadStatus.includes('failed') || uploadStatus.includes('Invalid') 
              ? 'bg-red-50 text-red-800 border-red-100 dark:bg-red-950/20 dark:text-red-400 dark:border-red-900/50' 
              : 'bg-indigo-50 text-indigo-700 border-indigo-100 dark:bg-indigo-950/20 dark:text-indigo-400 dark:border-indigo-900/50'}
          `}>
            {uploadStatus}
          </div>
        </div>
      )}
    </>
  );
};

export default JobDescriptionUpload;
