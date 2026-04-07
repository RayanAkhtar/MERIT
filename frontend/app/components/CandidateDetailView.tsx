'use client';

import { useState } from 'react';
import GitHubPreview from './GitHubPreview';
import LinkedInPreview from './LinkedInPreview';

interface CandidateDetailViewProps {
  candidate: any;
}

export default function CandidateDetailView({ candidate }: CandidateDetailViewProps) {
  const [activeTab, setActiveTab] = useState<'cv' | 'linkedin' | 'github'>('cv');

  if (!candidate) return null;

  const renderCVView = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Left Column: Personal Info & Expertise */}
      <div className="lg:col-span-1 space-y-6">
        <div className="p-8 rounded-[2rem] bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-xl shadow-zinc-200/40 dark:shadow-none relative overflow-hidden group min-h-[200px] flex flex-col justify-center">
          <div className="absolute -right-2 -top-2 p-6 opacity-[0.03] dark:opacity-[0.08] transition-transform duration-700 pointer-events-none">
            <svg className="w-24 h-24 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 14c3.31 0 6-2.69 6-6s-2.69-6-6-6-6 2.69-6 6 2.69 6 6 6zm0 2c-4.42 0-8 3.58-8 8h16c0-4.42-3.58-8-8-8z" />
            </svg>
          </div>
          
          <div className="relative space-y-4">
            <div>
              <p className="text-[10px] font-black text-indigo-500 uppercase tracking-widest mb-1">Full Name</p>
              <h3 className="text-xl font-black dark:text-white leading-none truncate">
                {candidate.name || 'Not Detected'}
              </h3>
            </div>
            
            <div className="pt-4 space-y-3">
              <div className="flex items-center gap-3 text-zinc-500 dark:text-zinc-400">
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                <span className="text-xs font-bold truncate">{candidate.email || 'Email missing'}</span>
              </div>
              <div className="flex items-center gap-3 text-zinc-500 dark:text-zinc-400">
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                <span className="text-xs font-bold truncate">{candidate.phone || 'Phone missing'}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="p-8 rounded-[2rem] bg-indigo-600 text-white shadow-xl shadow-indigo-600/20 relative overflow-hidden group">
          <p className="text-[10px] font-black uppercase tracking-widest mb-4 opacity-70">Detected Expertise</p>
          <div className="flex flex-wrap gap-2">
            {candidate.skills?.map((skill: string, i: number) => (
              <span key={i} className="px-3 py-1 bg-white/20 rounded-full text-[10px] font-black uppercase tracking-tight backdrop-blur-md border border-white/10">
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div className="p-8 rounded-[2.5rem] bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800">
          <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 mb-6">Academic Credentials</h4>
          <div className="space-y-6">
            {candidate.cv_education?.map((edu: any, i: number) => (
              <div key={i} className="space-y-1.5 border-l-2 border-emerald-500/30 pl-4 py-1.5">
                <h5 className="text-[11px] font-black text-zinc-800 dark:text-zinc-200 leading-tight uppercase tracking-tight">{edu.school_name}</h5>
                <p className="text-[10px] font-bold text-indigo-500/80 dark:text-indigo-400/80 italic">{edu.degree}</p>
                {edu.grade && <p className="text-[9px] text-zinc-500 font-mono">Grade: {edu.grade}</p>}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Column: Experience and Projects */}
      <div className="lg:col-span-2 space-y-8">
        <div className="p-8 rounded-[2.5rem] bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-xl min-h-[400px]">
          <h4 className="text-sm font-black uppercase tracking-[0.2em] text-zinc-400 mb-8">Professional Summary</h4>
          <div className="text-sm font-medium leading-relaxed text-zinc-600 dark:text-zinc-300/80 whitespace-pre-wrap">
            {candidate.experience_summary || 'No experience summary found.'}
          </div>
        </div>

        <div className="p-8 rounded-[2rem] bg-zinc-900 border border-zinc-800 shadow-xl">
          <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-6">Key Projects Extractions</h4>
          <div className="space-y-6">
            {candidate.projects_history?.map((proj: any, i: number) => (
              <div key={i} className="space-y-1.5 pb-4 border-b border-zinc-800 last:border-0">
                <h5 className="text-xs font-black text-white uppercase tracking-tight">{proj.name}</h5>
                <p className="text-[10px] font-bold text-indigo-400 italic leading-tight">{proj.subtitle}</p>
                <p className="text-[10px] text-zinc-400 leading-relaxed">{proj.summary}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderLinkedInView = () => {
    const li = candidate.linkedin_profile;
    if (!li || !li.raw_data) return (
      <div className="py-20 text-center opacity-40">
        <p className="text-xs font-black uppercase tracking-widest">No LinkedIn profile connected</p>
      </div>
    );

    // Calculate unique LinkedIn projects (filtering out those that likely match GitHub repos)
    const ghRepos = (candidate.github_projects || []).map((p: any) => p.name.toLowerCase());
    const uniqueLiProjects = (li.raw_data.projects || []).filter((p: any) => {
      const title = p.title.toLowerCase();
      return !ghRepos.some((ghName: string) => title.includes(ghName) || ghName.includes(title));
    });

    return (
      <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
         <LinkedInPreview linkedinData={li.raw_data} linkedinProjects={uniqueLiProjects} />
      </div>
    );
  };

  const renderGitHubView = () => {
    const gh = candidate.github_profile;
    if (!gh || !gh.raw_data) return (
      <div className="py-20 text-center opacity-40">
        <p className="text-xs font-black uppercase tracking-widest">No GitHub intelligence observed</p>
      </div>
    );

    return (
      <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
         <GitHubPreview githubData={gh.raw_data} />
      </div>
    );
  };

  return (
    <div className="space-y-10">
      {/* Tab Selection */}
      <div className="flex items-center justify-center space-x-1 p-1 bg-zinc-100 dark:bg-zinc-900 rounded-2xl w-fit mx-auto shadow-inner border border-zinc-200 dark:border-zinc-800">
        {[
          { id: 'cv', label: 'CV Snapshot', icon: <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /> },
          { id: 'linkedin', label: 'LinkedIn Profile', icon: <path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6zM2 9h4v12H2z" /> },
          { id: 'github', label: 'GitHub Intelligence', icon: <path d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /> }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`
              flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all
              ${activeTab === tab.id 
                ? 'bg-white dark:bg-zinc-800 text-indigo-600 dark:text-indigo-400 shadow-md transform scale-[1.02]' 
                : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'
              }
            `}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={activeTab === tab.id ? 2.5 : 2}>
              {tab.icon}
            </svg>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Main Content Area */}
      <div className="min-h-[600px] transition-all duration-500">
        {activeTab === 'cv' && renderCVView()}
        {activeTab === 'linkedin' && renderLinkedInView()}
        {activeTab === 'github' && renderGitHubView()}
      </div>
    </div>
  );
}
