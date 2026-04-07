'use client';

import { useState, useRef } from 'react';
import JobDescriptionReview, { ExtractedData } from './JobDescriptionReview';

interface FileWithPreview extends File {
  preview?: string;
}

const JobDescriptionUpload = () => {
  const [file, setFile] = useState<FileWithPreview | null>(null);
  const [step, setStep] = useState<'upload' | 'review'>('upload');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown'];
  const allowedExtensions = ['.pdf', '.docx', '.txt', '.md'];

  const validateFile = (file: File) => {
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    return allowedTypes.includes(file.type) || allowedExtensions.includes(extension);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
        setUploadStatus('');
      } else {
        setUploadStatus('Invalid file type. Please upload a PDF, DOCX, TXT, or MD file.');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setUploadStatus('Extracting intelligence...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'}/api/extract-job-description`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setExtractedData(data);
        setStep('review');
        setUploadStatus('');
      } else {
        const errorData = await response.json();
        setUploadStatus(`Extraction failed: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      setUploadStatus('Network error. Please ensure the backend is running.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleFinalSave = async () => {
    if (!extractedData) return;
    setIsUploading(true);
    setUploadStatus('Synchronising description...');

    try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'}/api/save-job-description`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(extractedData),
        });

        if (response.ok) {
            setUploadStatus('Job Description successfully synchronised to repository.');
            // Optionally redirect or reset
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

  if (step === 'review' && extractedData) {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-8 mt-6">
          <div className="space-y-2">
              <h2 className="text-2xl font-bold dark:text-white">Review Description</h2>
              <p className="text-zinc-500">Please verify the extracted metrics. You can edit or remove any entries before saving.</p>
          </div>
          
          <JobDescriptionReview 
            data={extractedData}
            setData={setExtractedData}
            onSave={handleFinalSave}
            isSaving={isUploading}
            statusMessage={uploadStatus}
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
          />

          <div className="w-20 h-20 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-500 rounded-2xl flex items-center justify-center shadow-xl">
             <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
             </svg>
          </div>

          <div className="space-y-2">
            <h3 className="text-xl font-black dark:text-zinc-50 uppercase tracking-tighter">
              {file ? file.name : 'Job Description Upload'}
            </h3>
            <p className="text-zinc-500 text-xs font-medium max-w-[240px] leading-relaxed mx-auto">
              Extract refined metadata from PDF, DOCX, TXT or Markdown files.
            </p>
          </div>

          <div className="flex items-center gap-6 pt-4">
            <button
              onClick={() => file ? handleUpload() : fileInputRef.current?.click()}
              disabled={isUploading}
              className={`px-10 py-3.5 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all active:scale-95 flex items-center gap-3 ${
                file 
                  ? 'bg-indigo-600 text-white hover:bg-indigo-500 shadow-xl shadow-indigo-600/20' 
                  : 'bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 hover:opacity-90'
              }`}
            >
              {isUploading ? (
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
              ) : null}
              {file ? 'Initialise extraction' : 'Select target file'}
            </button>
            
            {file && !isUploading && (
              <button
                onClick={() => setFile(null)}
                className="text-[10px] font-black uppercase text-zinc-400 hover:text-red-500 transition-colors tracking-widest"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </div>

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
