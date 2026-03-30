import Link from 'next/link';
import { FaFileInvoice, FaUsers, FaArrowRight } from 'react-icons/fa';

export default function ExtractOverviewPage() {
  return (
    <main className="min-h-screen bg-white dark:bg-zinc-950 py-20 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-extrabold text-zinc-900 dark:text-zinc-50 mb-6">
            Data Extraction Pipeline
          </h1>
          <p className="text-xl text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto">
            Choose a starting point to begin structuring your data. MERIT extracts deep technical insights from both job requirements and candidate documents.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-10">
          {/* Option 1: Job Description */}
          <Link 
            href="/extract/job-requirements"
            className="group relative p-10 border border-zinc-200 dark:border-zinc-800 rounded-3xl bg-zinc-50/50 dark:bg-zinc-900/30 hover:border-indigo-500/50 hover:bg-white dark:hover:bg-zinc-900 transition-all duration-300 overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
              <FaFileInvoice className="w-32 h-32 text-indigo-600 dark:text-indigo-400" />
            </div>
            
            <div className="relative z-10">
              <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900/40 rounded-2xl flex items-center justify-center mb-8 border border-indigo-200 dark:border-indigo-800 group-hover:scale-110 transition-transform">
                <FaFileInvoice className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
              </div>
              
              <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-4">
                Job Requirements
              </h2>
              
              <p className="text-lg text-zinc-600 dark:text-zinc-400 mb-8 leading-relaxed">
                Extract core competencies, required tech stacks, and soft skills from job descriptions to build an evaluation baseline.
              </p>
              
              <div className="flex items-center text-indigo-600 dark:text-indigo-400 font-bold group-hover:gap-2 transition-all">
                <span>Start Extraction</span>
                <FaArrowRight className="ml-2 w-4 h-4" />
              </div>
            </div>
          </Link>

          {/* Option 2: Candidate Batch */}
          <Link 
            href="/extract/cvs"
            className="group relative p-10 border border-zinc-200 dark:border-zinc-800 rounded-3xl bg-zinc-50/50 dark:bg-zinc-900/30 hover:border-emerald-500/50 hover:bg-white dark:hover:bg-zinc-900 transition-all duration-300 overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
              <FaUsers className="w-32 h-32 text-emerald-600 dark:text-emerald-400" />
            </div>
            
            <div className="relative z-10">
              <div className="w-16 h-16 bg-emerald-100 dark:bg-emerald-900/40 rounded-2xl flex items-center justify-center mb-8 border border-emerald-200 dark:border-emerald-800 group-hover:scale-110 transition-transform">
                <FaUsers className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
              </div>
              
              <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-4">
                Candidate Batch
              </h2>
              
              <p className="text-lg text-zinc-600 dark:text-zinc-400 mb-8 leading-relaxed">
                Process thousands of CVs or portfolios simultaneously. MERIT identifies key signals across multiple data sources to structure applicant data.
              </p>
              
              <div className="flex items-center text-emerald-600 dark:text-emerald-400 font-bold group-hover:gap-2 transition-all">
                <span>Start Batching</span>
                <FaArrowRight className="ml-2 w-4 h-4" />
              </div>
            </div>
          </Link>
        </div>

        {/* Informational Footer */}
        <div className="mt-20 p-8 border border-dashed border-zinc-300 dark:border-zinc-800 rounded-2xl text-center">
          <p className="text-zinc-500 dark:text-zinc-400 italic">
            Tip: You can start with either. The evaluation system will later allow you to match specific batches against requirements.
          </p>
        </div>
      </div>
    </main>
  );
}
