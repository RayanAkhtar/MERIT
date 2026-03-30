import Link from 'next/link';
import { FaSyncAlt, FaEdit, FaUserFriends, FaArrowRight, FaFileAlt } from 'react-icons/fa';

export default function UpdateOverviewPage() {
  return (
    <main className="min-h-screen bg-white dark:bg-zinc-950 py-20 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-extrabold text-zinc-900 dark:text-zinc-50 mb-6">
            Data Update Center
          </h1>
          <p className="text-xl text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto">
            Keep your evaluations fresh. Instantly update existing job descriptions or add new candidates to an already extracted batch.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-10">
          {/* Option 1: Job Description Update */}
          <Link 
            href="/update/job-description"
            className="group relative p-10 border border-zinc-200 dark:border-zinc-800 rounded-3xl bg-zinc-50/50 dark:bg-zinc-900/30 hover:border-violet-500/50 hover:bg-white dark:hover:bg-zinc-900 transition-all duration-300 overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
              <FaFileAlt className="w-32 h-32 text-violet-600 dark:text-violet-400" />
            </div>
            
            <div className="relative z-10">
              <div className="w-16 h-16 bg-violet-100 dark:bg-violet-900/40 rounded-2xl flex items-center justify-center mb-8 border border-violet-200 dark:border-violet-800 group-hover:scale-110 transition-transform">
                <FaEdit className="w-8 h-8 text-violet-600 dark:text-violet-400" />
              </div>
              
              <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-4">
                Update Job Descriptions
              </h2>
              
              <p className="text-lg text-zinc-600 dark:text-zinc-400 mb-8 leading-relaxed">
                Modify existing requirements if the role has evolved. MERIT will re-parse the data while maintaining your historical context.
              </p>
              
              <div className="flex items-center text-violet-600 dark:text-violet-400 font-bold group-hover:gap-2 transition-all">
                <span>Go to Updates</span>
                <FaArrowRight className="ml-2 w-4 h-4" />
              </div>
            </div>
          </Link>

          {/* Option 2: Candidate Batch Update */}
          <Link 
            href="/update/cvs"
            className="group relative p-10 border border-zinc-200 dark:border-zinc-800 rounded-3xl bg-zinc-50/50 dark:bg-zinc-900/30 hover:border-rose-500/50 hover:bg-white dark:hover:bg-zinc-900 transition-all duration-300 overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
              <FaUserFriends className="w-32 h-32 text-rose-600 dark:text-rose-400" />
            </div>
            
            <div className="relative z-10">
              <div className="w-16 h-16 bg-rose-100 dark:bg-rose-900/40 rounded-2xl flex items-center justify-center mb-8 border border-rose-200 dark:border-rose-800 group-hover:scale-110 transition-transform">
                <FaUserFriends className="w-8 h-8 text-rose-600 dark:text-rose-400" />
              </div>
              
              <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-4">
                Update Candidate Batch
              </h2>
              
              <p className="text-lg text-zinc-600 dark:text-zinc-400 mb-8 leading-relaxed">
                Add more CVs to an existing batch or replace outdated profiles. Ensure your candidate pool is always current.
              </p>
              
              <div className="flex items-center text-rose-600 dark:text-rose-400 font-bold group-hover:gap-2 transition-all">
                <span>Go to Updates</span>
                <FaArrowRight className="ml-2 w-4 h-4" />
              </div>
            </div>
          </Link>
        </div>

        {/* Informational Footer */}
        <div className="mt-20 p-8 border border-dashed border-zinc-300 dark:border-zinc-800 rounded-2xl text-center">
          <p className="text-zinc-500 dark:text-zinc-400 italic">
            Updating the data will notify active configurations if the underlying data has changed since their last execution.
          </p>
        </div>
      </div>
    </main>
  );
}
