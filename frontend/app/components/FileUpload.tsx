'use client';

import { useState, useRef } from 'react';
import LinkSelection from './LinkSelection';

interface FileWithPreview extends File {
  preview?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

export default function FileUpload() {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [metrics, setMetrics] = useState<{ uploaded_files: number; link_counts: Record<string, number> } | null>(null);
  const [selectedLinks, setSelectedLinks] = useState<Record<string, boolean>>({});
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

  const fetchMetrics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/supporting-links-metrics`);
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
        const initialSelections = Object.keys(data.link_counts).reduce((acc, link) => {
          acc[link] = false;
          return acc;
        }, {} as Record<string, boolean>);
        setSelectedLinks(initialSelections);
      } else {
        console.error("Failed to fetch metrics");
      }
    } catch (error) {
      console.error("Error fetching metrics:", error);
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setUploadStatus('Please select at least one file to upload.');
      return;
    }

    setIsUploading(true);
    setUploadStatus('Uploading files...');

    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch(`${API_BASE_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadStatus(`Successfully uploaded ${result.uploaded} file(s)!`);
        setFiles([]);
        await fetchMetrics();
      } else {
        const error = await response.json();
        setUploadStatus(`Upload failed: ${error.error || 'Unknown error'}`);
      }
    } catch (error) {
      setUploadStatus(`Upload failed: ${error instanceof Error ? error.message : 'Network error'}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center transition-colors
          ${isDragging 
            ? 'border-zinc-400 dark:border-zinc-600 bg-zinc-50 dark:bg-zinc-900' 
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
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer flex flex-col items-center gap-4"
        >
          <div className="w-12 h-12 bg-zinc-100 dark:bg-zinc-800 rounded-md flex items-center justify-center">
            <svg
              className="w-6 h-6 text-zinc-600 dark:text-zinc-400"
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
          <div className="space-y-1">
            <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
              <span className="text-zinc-600 dark:text-zinc-400">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-zinc-500 dark:text-zinc-500">
              PDF, DOCX files only
            </p>
          </div>
        </label>
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
                  <div className="w-10 h-10 bg-zinc-100 dark:bg-zinc-800 rounded-md flex items-center justify-center flex-shrink-0">
                    <svg
                      className="w-5 h-5 text-zinc-600 dark:text-zinc-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                  </div>
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
                  className="ml-4 p-2 text-zinc-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                  aria-label="Remove file"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Button */}
      {files.length > 0 && (
        <div className="flex flex-col gap-4">
          <button
            onClick={handleUpload}
            disabled={isUploading}
            className={`
              px-6 py-3 rounded-md font-medium transition-colors
              ${isUploading
                ? 'bg-zinc-300 dark:bg-zinc-700 text-zinc-500 dark:text-zinc-400 cursor-not-allowed'
                : 'bg-zinc-900 dark:bg-zinc-50 text-white dark:text-zinc-900 hover:bg-zinc-800 dark:hover:bg-zinc-200'
              }
            `}
          >
            {isUploading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading...
              </span>
            ) : (
              `Upload ${files.length} ${files.length === 1 ? 'file' : 'files'}`
            )}
          </button>
        </div>
      )}

      {/* Status Message */}
      {uploadStatus && (
        <div
          className={`
            p-4 rounded-lg border text-sm
            ${uploadStatus.includes('Success') || uploadStatus.includes('uploaded')
              ? 'bg-green-50 dark:bg-green-950/30 text-green-800 dark:text-green-400 border-green-200 dark:border-green-800'
              : uploadStatus.includes('failed') || uploadStatus.includes('rejected')
              ? 'bg-red-50 dark:bg-red-950/30 text-red-800 dark:text-red-400 border-red-200 dark:border-red-800'
              : 'bg-zinc-50 dark:bg-zinc-900 text-zinc-800 dark:text-zinc-300 border-zinc-200 dark:border-zinc-800'
            }
          `}
        >
          <div className="flex items-center gap-2">
            {uploadStatus.includes('Success') || uploadStatus.includes('uploaded') ? (
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : uploadStatus.includes('failed') || uploadStatus.includes('rejected') ? (
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="w-4 h-4 flex-shrink-0 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            )}
            <span>{uploadStatus}</span>
          </div>
        </div>
      )}

      {/* Metrics Section */}
      {metrics && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
            Metrics
          </h3>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Uploaded Files: {metrics.uploaded_files}
          </p>
          <LinkSelection
            metrics={metrics}
            selectedLinks={selectedLinks}
            setSelectedLinks={setSelectedLinks}
          />
        </div>
      )}
    </div>
  );
}

