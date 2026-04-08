import Link from 'next/link';
import { FaCogs, FaPlay, FaArrowRight, FaClipboardList, FaRocket } from 'react-icons/fa';

export default function ConfigOverviewPage() {
  return (
    <main className="min-h-screen bg-white dark:bg-zinc-950 py-20 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-extrabold text-zinc-900 dark:text-zinc-50 mb-6">
            Configuration Dashboard
          </h1>
          <p className="text-xl text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto">
            Design your evaluation rules or run them against live candidate data. MERIT puts you in control of the algorithm.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Option 1: Create Config */}
          <Link 
            href="/config/create"
            className="group relative p-8 border border-zinc-200 dark:border-zinc-800 rounded-3xl bg-zinc-50/50 dark:bg-zinc-900/30 hover:border-blue-500/50 hover:bg-white dark:hover:bg-zinc-900 transition-all duration-300 overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <FaClipboardList className="w-24 h-24 text-blue-600 dark:text-blue-400" />
            </div>
            
            <div className="relative z-10">
              <div className="w-14 h-14 bg-blue-100 dark:bg-blue-900/40 rounded-2xl flex items-center justify-center mb-6 border border-blue-200 dark:border-blue-800 group-hover:scale-110 transition-transform">
                <FaClipboardList className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              
              <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-3">
                Create Protocol
              </h2>
              
              <p className="text-zinc-600 dark:text-zinc-400 mb-6 leading-relaxed text-sm">
                Build a reusable ranking template. Define which metrics matter most and set up your evaluation logic.
              </p>
              
              <div className="flex items-center text-blue-600 dark:text-blue-400 text-sm font-bold group-hover:gap-2 transition-all">
                <span>Start Builder</span>
                <FaArrowRight className="ml-2 w-3 h-3" />
              </div>
            </div>
          </Link>

          {/* Option 2: Update Config */}
          <Link 
            href="/config/update"
            className="group relative p-8 border border-zinc-200 dark:border-zinc-800 rounded-3xl bg-zinc-50/50 dark:bg-zinc-900/30 hover:border-indigo-500/50 hover:bg-white dark:hover:bg-zinc-900 transition-all duration-300 overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <FaCogs className="w-24 h-24 text-indigo-600 dark:text-indigo-400" />
            </div>
            
            <div className="relative z-10">
              <div className="w-14 h-14 bg-indigo-100 dark:bg-indigo-900/40 rounded-2xl flex items-center justify-center mb-6 border border-indigo-200 dark:border-indigo-800 group-hover:scale-110 transition-transform">
                <FaCogs className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              </div>
              
              <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-3">
                Update Protocol
              </h2>
              
              <p className="text-zinc-600 dark:text-zinc-400 mb-6 leading-relaxed text-sm">
                Refine existing configurations. Adjust weights, swap datasets, or toggle active matching criteria.
              </p>
              
              <div className="flex items-center text-indigo-600 dark:text-indigo-400 text-sm font-bold group-hover:gap-2 transition-all">
                <span>Refine Strategy</span>
                <FaArrowRight className="ml-2 w-3 h-3" />
              </div>
            </div>
          </Link>

          {/* Option 3: Execute Config */}
          <Link 
            href="/config/execute"
            className="group relative p-8 border border-zinc-200 dark:border-zinc-800 rounded-3xl bg-zinc-50/50 dark:bg-zinc-900/30 hover:border-amber-500/50 hover:bg-white dark:hover:bg-zinc-900 transition-all duration-300 overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <FaRocket className="w-24 h-24 text-amber-600 dark:text-amber-500" />
            </div>
            
            <div className="relative z-10">
              <div className="w-14 h-14 bg-amber-100 dark:bg-amber-900/40 rounded-2xl flex items-center justify-center mb-6 border border-amber-200 dark:border-amber-800 group-hover:scale-110 transition-transform">
                <FaPlay className="w-6 h-6 text-amber-600 dark:text-amber-500" />
              </div>
              
              <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-3">
                Execute Match
              </h2>
              
              <p className="text-zinc-600 dark:text-zinc-400 mb-6 leading-relaxed text-sm">
                Run an existing configuration against a chosen candidate batch to generate real-time rankings and insights.
              </p>
              
              <div className="flex items-center text-amber-600 dark:text-amber-500 text-sm font-bold group-hover:gap-2 transition-all">
                <span>Run Matcher</span>
                <FaArrowRight className="ml-2 w-3 h-3" />
              </div>
            </div>
          </Link>
        </div>

        {/* Informational Footer */}
        <div className="mt-20 p-8 border border-dashed border-zinc-300 dark:border-zinc-800 rounded-2xl text-center">
          <p className="text-zinc-500 dark:text-zinc-400 italic">
            Config templates can be reused across different candidate batches. You can also edit weights and metrics after an initial run to refine your results.
          </p>
        </div>
      </div>
    </main>
  );
}
