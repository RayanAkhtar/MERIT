'use client';
import Link from 'next/link';

export default function UpdateJobDescriptionPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-zinc-950 p-8">
      <div className="max-w-4xl mx-auto">
        <nav className="mb-8 flex items-center text-sm text-zinc-500 dark:text-zinc-400">
          <Link href="/update" className="hover:text-zinc-900 dark:hover:text-zinc-50 transition-colors">Update</Link>
          <span className="mx-2">/</span>
          <span className="text-zinc-900 dark:text-zinc-50 font-medium">Job Description</span>
        </nav>
        <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-4">Update Job Description</h1>
        <p className="text-zinc-600 dark:text-zinc-400 mb-8">
          Refine an existing job requirement set with new details or modified criteria.
        </p>
        <div className="p-12 border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-2xl text-center">
          <p className="text-zinc-500 dark:text-zinc-400">Job update workspace coming soon...</p>
        </div>
      </div>
    </div>
  );
}
