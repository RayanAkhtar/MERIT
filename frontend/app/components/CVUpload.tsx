'use client';

import { useState, useRef } from 'react';

interface FileWithPreview extends File {
  preview?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

export default function CVUpload() {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
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

  const handleUpload = async () => {
    if (files.length === 0) {
        setUploadStatus('Please select at least one CV file.');
        return;
    }

    setIsUploading(true);
    setUploadStatus('Attempting to save CVs...');

    const formData = new FormData();
    files.forEach((file) => {
        formData.append('files', file);
    });

    try {
        const response = await fetch(`${API_BASE_URL}/api/save-cvs`, {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            setUploadStatus('Saved CVs successfuly!');
        } else {
            const errorData = await response.json();
            setUploadStatus(`Save failed: ${errorData.error || 'Unknown error'}`);
        }
    } catch (error) {
        setUploadStatus(`Save failed: ${error instanceof Error ? error.message : 'Network error'}`);
    } finally {
        setIsUploading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 mt-6">
      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center transition-colors
          ${isDragging 
            ? 'border-blue-400 dark:border-blue-600 bg-blue-50 dark:bg-zinc-900/50' 
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
          id="cv-upload"
        />
        <label
          htmlFor="cv-upload"
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
              <span className="text-blue-600 dark:text-blue-400">Click to upload CVs</span> or drag and drop
            </p>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
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
              Selected CVs
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

      {/* Submit Button */}
      {files.length > 0 && (
        <button
          onClick={handleUpload}
          disabled={isUploading}
          className="w-full px-6 py-3 rounded-md font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isUploading ? 'Saving...' : 'Save CVs'}
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
