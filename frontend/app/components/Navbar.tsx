'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import ThemeToggle from './ThemeToggle';

export default function Navbar() {
  const pathname = usePathname();
  const isActive = (path: string) => pathname === path || pathname?.startsWith(`${path}/`);

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo */}
          <Link href="/" className="flex items-center hover:opacity-80 transition-opacity">
            <Image
              src="/MERIT-white-transparent-logo.png"
              alt="MERIT Logo"
              width={180}
              height={60}
              className="h-12 w-auto dark:hidden"
              priority
            />
            <Image
              src="/MERIT-black-transparent-logo.png"
              alt="MERIT Logo"
              width={180}
              height={60}
              className="h-12 w-auto hidden dark:block"
              priority
            />
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-2">
            
            {/* Extract Dropdown */}
            <div className="relative group">
              <Link
                href="/extract"
                className={`
                  flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors
                  ${
                    isActive('/extract')
                      ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50'
                      : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-50 hover:bg-zinc-50 dark:hover:bg-zinc-900'
                  }
                `}
              >
                Extract
                <svg className="ml-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </Link>
              
              <div className="absolute left-0 pt-2 w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="rounded-md shadow-lg bg-white dark:bg-zinc-900 ring-1 ring-black ring-opacity-5 border border-zinc-200 dark:border-zinc-700 py-1">
                  <Link
                    href="/extract/cvs"
                    className="block px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  >
                    Candidate Info
                  </Link>
                  <Link
                    href="/extract/job-description"
                    className="block px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  >
                    Job Description
                  </Link>
                </div>
              </div>
            </div>

            {/* Update Dropdown */}
            <div className="relative group">
              <Link
                href="/update"
                className={`
                  flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors
                  ${
                    isActive('/update')
                      ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50'
                      : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-50 hover:bg-zinc-50 dark:hover:bg-zinc-900'
                  }
                `}
              >
                Update
                <svg className="ml-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </Link>
              
              <div className="absolute left-0 pt-2 w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="rounded-md shadow-lg bg-white dark:bg-zinc-900 ring-1 ring-black ring-opacity-5 border border-zinc-200 dark:border-zinc-700 py-1">
                  <Link
                    href="/update/cvs"
                    className="block px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  >
                    Candidate Info
                  </Link>
                  <Link
                    href="/update/job-description"
                    className="block px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  >
                    Job Description
                  </Link>
                  <Link
                    href="/config/update"
                    className="block px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  >
                    Matching Protocol
                  </Link>
                </div>
              </div>
            </div>

            {/* View Candidates */}
            <Link
              href="/view/candidates"
              className={`
                px-4 py-2 rounded-md text-sm font-medium transition-colors
                ${
                  isActive('/view/candidates')
                    ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50'
                    : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-50 hover:bg-zinc-50 dark:hover:bg-zinc-900'
                }
              `}
            >
              View Candidates
            </Link>

            {/* Config Dropdown */}
            <div className="relative group">
              <Link
                href="/config"
                className={`
                  flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors
                  ${
                    isActive('/config')
                      ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50'
                      : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-50 hover:bg-zinc-50 dark:hover:bg-zinc-900'
                  }
                `}
              >
                Config
                <svg className="ml-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </Link>
              
              <div className="absolute left-0 pt-2 w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="rounded-md shadow-lg bg-white dark:bg-zinc-900 ring-1 ring-black ring-opacity-5 border border-zinc-200 dark:border-zinc-700 py-1">
                  <Link
                    href="/config/create"
                    className="block px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  >
                    Create Config
                  </Link>
                  <Link
                    href="/config/update"
                    className="block px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  >
                    Update Config
                  </Link>
                  <Link
                    href="/config/execute"
                    className="block px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  >
                    Execute Config
                  </Link>
                </div>
              </div>
            </div>

            {/* Past Results */}
            <Link
              href="/past-results"
              className={`
                px-4 py-2 rounded-md text-sm font-medium transition-colors
                ${
                  pathname === '/past-results'
                    ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50'
                    : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-50 hover:bg-zinc-50 dark:hover:bg-zinc-900'
                }
              `}
            >
              Past Results
            </Link>

            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  );
}
