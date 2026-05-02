"use client";

import Link from 'next/link';
import Image from 'next/image';
import { useState } from 'react';
import { FaSearch, FaCogs, FaChartBar, FaNetworkWired, FaSlidersH, FaLightbulb, FaBrain, FaCode, FaShieldAlt, FaFlag, FaTrashAlt, FaBroom, FaExclamationTriangle } from 'react-icons/fa';

export default function Home() {
  const [isPurgingDb, setIsPurgingDb] = useState(false);
  const [isPurgingCache, setIsPurgingCache] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error', message: string } | null>(null);

  const purgeDatabase = async () => {
    if (!confirm("Are you ABSOLUTELY sure? This will delete all job descriptions, candidates, and storage files. This cannot be undone.")) return;
    
    setIsPurgingDb(true);
    setStatus(null);
    try {
      const res = await fetch('http://localhost:5000/api/purge-database', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setStatus({ type: 'success', message: 'Database and storage purged successfully.' });
      } else {
        setStatus({ type: 'error', message: data.error || 'Failed to purge database.' });
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Server connection failed.' });
    } finally {
      setIsPurgingDb(false);
    }
  };

  const purgeCache = async () => {
    if (!confirm("Delete all cached extraction results? Folder structure will be preserved.")) return;

    setIsPurgingCache(true);
    setStatus(null);
    try {
      const res = await fetch('http://localhost:5000/api/purge-cache', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setStatus({ type: 'success', message: 'Cache files cleared.' });
      } else {
        setStatus({ type: 'error', message: data.error || 'Failed to clear cache.' });
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Server connection failed.' });
    } finally {
      setIsPurgingCache(false);
    }
  };

  return (
    <main className="min-h-screen bg-white dark:bg-zinc-950">
      {/* Hero Section */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
        <div className="text-center">
          <div className="flex justify-center mb-8">
            <Image
              src="/MERIT-white-transparent.png"
              alt="MERIT Logo"
              width={240}
              height={80}
              className="h-64 w-auto dark:hidden"
              priority
            />
            <Image
              src="/MERIT-black-transparent.png"
              alt="MERIT Logo"
              width={240}
              height={80}
              className="h-64 w-auto hidden dark:block"
              priority
            />
          </div>
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold mb-6 text-zinc-900 dark:text-zinc-50">
            Multi-source Employment
            Ranking & Insight Tool
          </h1>
          <p className="text-lg md:text-xl text-zinc-600 dark:text-zinc-400 mb-10 max-w-2xl mx-auto">
            A screening tool that supports more than just CVs, scan GitHub, LinkedIn, and more.
          </p>
          <Link
            href="/extract"
            className="inline-flex items-center px-6 py-3 rounded-md bg-zinc-900 dark:bg-zinc-50 text-white dark:text-zinc-900 font-medium hover:bg-zinc-800 dark:hover:bg-zinc-200 transition-colors"
          >
            Get Started
            <svg
              className="ml-2 w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
          </Link>
        </div>
      </section>

      {/* Core Innovations Section */}
      <section className="bg-zinc-50 dark:bg-zinc-900/30 border-y border-zinc-200 dark:border-zinc-800">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
              Core Innovations
            </h2>
            <p className="text-lg text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto">
              MERIT is a prototype designed to explore multi-source validation in candidate screening, moving beyond standard CV-only systems.
            </p>
          </div>
          
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
              <div className="p-8 border border-zinc-200/60 dark:border-zinc-800/60 rounded-3xl bg-white dark:bg-zinc-950/50 hover:shadow-xl hover:shadow-indigo-500/5 dark:hover:shadow-indigo-500/10 hover:border-indigo-500/30 transition-all duration-300 group">
                <div className="w-14 h-14 bg-indigo-50 dark:bg-indigo-900/20 rounded-2xl flex items-center justify-center mb-6 group-hover:rotate-3 transition-transform">
                  <FaNetworkWired className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
                </div>
                <h3 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-3">
                  Multi-Source Intelligence
                </h3>
                <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed text-lg">
                  Integrates candidate data across GitHub repositories and LinkedIn profiles to provide a more holistic view than a standalone CV.
                </p>
              </div>

              <div className="p-8 border border-zinc-200/60 dark:border-zinc-800/60 rounded-3xl bg-white dark:bg-zinc-950/50 hover:shadow-xl hover:shadow-emerald-500/5 dark:hover:shadow-emerald-500/10 hover:border-emerald-500/30 transition-all duration-300 group">
                <div className="w-14 h-14 bg-emerald-50 dark:bg-emerald-900/20 rounded-2xl flex items-center justify-center mb-6 group-hover:-rotate-3 transition-transform">
                  <FaSlidersH className="w-7 h-7 text-emerald-600 dark:text-emerald-400" />
                </div>
                <h3 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-3">
                  Highly Customisable
                </h3>
                <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed text-lg">
                  Define custom evaluation templates and weights for specific metrics, allowing for targeted matching based on job requirements.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="p-8 border border-zinc-200/60 dark:border-zinc-800/60 rounded-3xl bg-white dark:bg-zinc-950/50 hover:shadow-xl hover:shadow-amber-500/5 dark:hover:shadow-amber-500/10 hover:border-amber-500/30 transition-all duration-300 group">
                <div className="w-12 h-12 bg-amber-50 dark:bg-amber-900/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <FaLightbulb className="w-6 h-6 text-amber-500 dark:text-amber-400" />
                </div>
                <h3 className="text-xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
                  Explainable Insights
                </h3>
                <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
                  Provides transparency in scoring by showing which data points from the CV or social profiles contributed to the final result.
                </p>
              </div>

              <div className="p-8 border border-zinc-200/60 dark:border-zinc-800/60 rounded-3xl bg-white dark:bg-zinc-950/50 hover:shadow-xl hover:shadow-rose-500/5 dark:hover:shadow-rose-500/10 hover:border-rose-500/30 transition-all duration-300 group">
                <div className="w-12 h-12 bg-rose-50 dark:bg-rose-900/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <FaBrain className="w-6 h-6 text-rose-500 dark:text-rose-400" />
                </div>
                <h3 className="text-xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
                  Derived Metrics
                </h3>
                <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
                  Automatically extracts relevant matching criteria by comparing job requirements against the available candidate pool data.
                </p>
              </div>

              <div className="p-8 border border-zinc-200/60 dark:border-zinc-800/60 rounded-3xl bg-white dark:bg-zinc-950/50 hover:shadow-xl hover:shadow-sky-500/5 dark:hover:shadow-sky-500/10 hover:border-sky-500/30 transition-all duration-300 group">
                <div className="w-12 h-12 bg-sky-50 dark:bg-sky-900/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <FaCode className="w-6 h-6 text-sky-500 dark:text-sky-400" />
                </div>
                <h3 className="text-xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
                  Open Extensibility
                </h3>
                <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
                  Designed with a flexible architecture. Developers can easily extend the source code to add support for any new custom data sources.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow Steps Section */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-2xl md:text-3xl font-semibold text-center text-zinc-900 dark:text-zinc-50 mb-12">
          How MERIT Works
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="p-8 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-950 hover:border-zinc-300 dark:hover:border-zinc-700 transition-colors">
            <div className="w-12 h-12 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex items-center justify-center mb-6">
              <FaSearch className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 mb-3">
              Extract
            </h3>
            <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
              Upload CVs and Job Requirements. MERIT securely extracts and structures complex data from multiple sources like GitHub, LinkedIn, and PDF documents. 
            </p>
          </div>

          <div className="p-8 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-950 hover:border-zinc-300 dark:hover:border-zinc-700 transition-colors">
            <div className="w-12 h-12 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg flex items-center justify-center mb-6">
              <FaCogs className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
            </div>
            <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 mb-3">
              Config
            </h3>
            <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
              Create dynamic evaluation criteria and assign specific weightings. Execute these tailored configurations against candidate batches to generate precise rankings.
            </p>
          </div>
  
          <div className="p-8 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-950 hover:border-zinc-300 dark:hover:border-zinc-700 transition-colors">
            <div className="w-12 h-12 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg flex items-center justify-center mb-6">
              <FaChartBar className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            </div>
            <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 mb-3">
              Past Results
            </h3>
            <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
              Access explainable matching insights. Understand exactly how and why candidates were ranked based on your historical execution data.
            </p>
          </div>
        </div>
      </section>

      {/* System Maintenance Section */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-zinc-200 dark:border-zinc-800">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8 p-8 bg-rose-500/5 dark:bg-rose-500/10 rounded-3xl border border-rose-500/20">
          <div>
            <h3 className="text-xl font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-2 mb-2">
              <FaShieldAlt className="text-rose-500" />
              System Maintenance
            </h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 max-w-md">
              Use these tools to reset the prototype state. Purging the database will delete all records and cloud storage files. Purging the cache will clear local extraction data.
            </p>
            {status && (
              <div className={`mt-4 p-3 rounded-lg text-sm font-medium ${status.type === 'success' ? 'bg-emerald-500/10 text-emerald-600' : 'bg-rose-500/10 text-rose-600'}`}>
                {status.message}
              </div>
            )}
          </div>
          
          <div className="flex flex-wrap gap-4">
            <button
              onClick={purgeCache}
              disabled={isPurgingCache}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-zinc-900 dark:bg-zinc-800 text-white font-medium hover:bg-zinc-800 dark:hover:bg-zinc-700 transition-all active:scale-95 disabled:opacity-50"
            >
              <FaBroom className={isPurgingCache ? 'animate-spin' : ''} />
              {isPurgingCache ? 'Clearing Cache...' : 'Purge Cache'}
            </button>
            
            <button
              onClick={purgeDatabase}
              disabled={isPurgingDb}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-rose-600 text-white font-medium hover:bg-rose-700 transition-all active:scale-95 shadow-lg shadow-rose-500/20 disabled:opacity-50"
            >
              <FaTrashAlt className={isPurgingDb ? 'animate-pulse' : ''} />
              {isPurgingDb ? 'Purging Everything...' : 'Purge Database'}
            </button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="border border-zinc-200 dark:border-zinc-800 rounded-lg p-8 md:p-12 text-center bg-zinc-50 dark:bg-zinc-900/50">
          <h2 className="text-2xl md:text-3xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
            Ready to get started?
          </h2>
          <p className="text-zinc-600 dark:text-zinc-400 mb-6 max-w-xl mx-auto">
            Upload your documents and start processing them right away.
          </p>
          <Link
            href="/extract"
            className="inline-flex items-center px-6 py-3 rounded-md bg-zinc-900 dark:bg-zinc-50 text-white dark:text-zinc-900 font-medium hover:bg-zinc-800 dark:hover:bg-zinc-200 transition-colors"
          >
            Start Extracting
          </Link>
        </div>
      </section>
    </main>
  );
}
