import Link from 'next/link';
import Image from 'next/image';

import { FaSearch, FaRegQuestionCircle, FaCogs } from 'react-icons/fa';

export default function Home() {
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
            href="/config"
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

      {/* Features Section */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="p-6 border border-zinc-200 dark:border-zinc-800 rounded-lg">
            <div className="w-10 h-10 bg-zinc-100 dark:bg-zinc-800 rounded-md flex items-center justify-center mb-4">
              <FaSearch className="w-5 h-5 text-zinc-700 dark:text-zinc-300" />
            </div>
            <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-2">
              Multiple sources
            </h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              Why base screenings around only CVs when there is so much more to consider?
            </p>
          </div>

          <div className="p-6 border border-zinc-200 dark:border-zinc-800 rounded-lg">
            <div className="w-10 h-10 bg-zinc-100 dark:bg-zinc-800 rounded-md flex items-center justify-center mb-4">
              <FaRegQuestionCircle className="w-5 h-5 text-zinc-700 dark:text-zinc-300" />
            </div>
            <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-2">
              Explainable systems
            </h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              Don't blindly trust the results, understand how they were generated.
            </p>
          </div>
  
          <div className="p-6 border border-zinc-200 dark:border-zinc-800 rounded-lg">
            <div className="w-10 h-10 bg-zinc-100 dark:bg-zinc-800 rounded-md flex items-center justify-center mb-4">
              <FaCogs className="w-5 h-5 text-zinc-700 dark:text-zinc-300" />
            </div>
            <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-2">
              Flexibility
            </h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              Don't like the algorithm, tweak both the metrics to consider as well as the weightings.
            </p>
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
            href="/config"
            className="inline-flex items-center px-6 py-3 rounded-md bg-zinc-900 dark:bg-zinc-50 text-white dark:text-zinc-900 font-medium hover:bg-zinc-800 dark:hover:bg-zinc-200 transition-colors"
          >
            Upload Documents
          </Link>
        </div>
      </section>
    </main>
  );
}
