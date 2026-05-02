'use client';

import { useState } from 'react';
import GitHubEvolutionChart from './GitHubEvolutionChart';
import ScoringAudit from './ScoringAudit';

interface DetailedReportModalProps {
  candidate: any;
  candidateDetail: any;
  onClose: () => void;
  hoveredItem: string | null;
  setHoveredItem: (item: string | null) => void;
}

export default function DetailedReportModal({ 
  candidate, 
  candidateDetail, 
  onClose, 
  hoveredItem, 
  setHoveredItem 
}: DetailedReportModalProps) {
  const [activeTab, setActiveTab] = useState<'cv' | 'github' | 'linkedin' | 'formula'>('cv');
  const [cvViewMode, setCvViewMode] = useState<'original' | 'intelligence'>('original');
  
  const formatDate = (date: any) => {
    if (!date) return '';
    if (typeof date === 'string') return date;
    if (typeof date === 'object' && date.text) return date.text;
    return JSON.stringify(date);
  };

  const handleMetricClick = (key: string) => {
    setActiveTab('formula');
    setTimeout(() => {
      const element = document.getElementById(`formula-${key}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // Optional: briefly flash the element
        element.classList.add('ring-2', 'ring-indigo-500', 'transition-all');
        setTimeout(() => element.classList.remove('ring-2', 'ring-indigo-500'), 2000);
      }
    }, 100);
  };

  if (!candidate) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-zinc-950/70 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-white dark:bg-zinc-900 w-full max-w-[95%] h-[90vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col border border-zinc-200 dark:border-zinc-800">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-900/50">
          <div className="flex items-center gap-4">
            <div>
              <h2 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">{candidate.name}</h2>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">Deep-Dive Match Intelligence</p>
            </div>
            <div className="hidden sm:flex items-center gap-2 bg-indigo-50 dark:bg-indigo-900/20 px-3 py-1 rounded-full border border-indigo-100 dark:border-indigo-800">
              <span className="text-sm font-black text-indigo-600 dark:text-indigo-400">{candidate.overallScore}%</span>
              <span className="text-[10px] text-indigo-500 font-bold uppercase tracking-tighter">Match</span>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-full transition-colors">
            <svg className="w-5 h-5 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 flex overflow-hidden">
          {/* Left Sidebar: Intelligence Breakdown */}
          <div className="w-full md:w-[40%] border-r border-zinc-200 dark:border-zinc-800 overflow-y-auto p-6 space-y-8 bg-zinc-50/30 dark:bg-black/20">
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 uppercase tracking-wide flex items-center gap-2">
              <svg className="w-4 h-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Intelligence Report
            </h3>
            <div className="space-y-6">
              {Object.entries(candidate.fullMetrics)
                .sort(([, a]: [string, any], [, b]: [string, any]) => {
                  if (a.score === 0 && b.score !== 0) return 1;
                  if (a.score !== 0 && b.score === 0) return -1;
                  return 0;
                })
                .map(([key, m]: [string, any]) => {
                const priority = Math.round((1.2 - m.weight) / 0.2);
                const isSectionHovered = hoveredItem === key;
                return (
                  <div key={key} className="space-y-3">
                    <div 
                      className={`flex items-start justify-between cursor-pointer p-2 -mx-2 rounded-xl transition-all ${isSectionHovered ? 'bg-indigo-50/50 dark:bg-indigo-900/10' : ''}`}
                      onMouseEnter={() => setHoveredItem(key)}
                      onMouseLeave={() => setHoveredItem(null)}
                      onClick={() => handleMetricClick(key)}
                    >
                      <h4 className={`font-bold transition-colors flex items-center gap-2 ${isSectionHovered ? 'text-indigo-600 dark:text-indigo-400' : 'text-zinc-900 dark:text-zinc-50'}`}>
                        {m.name}
                        <span className="text-[10px] px-1.5 py-0.5 rounded border border-indigo-200 dark:border-indigo-800 text-indigo-600 bg-indigo-50 dark:bg-indigo-900/20">W:{priority}</span>
                      </h4>
                      <div className={`text-lg font-black transition-colors ${isSectionHovered ? 'text-indigo-600 dark:text-indigo-400' : 'text-zinc-900 dark:text-zinc-100'}`}>{Math.round(m.score * 100)}%</div>
                    </div>
                    <div className="grid grid-cols-1 gap-3">
                      {(m.breakdown || []).map((item: any, i: number) => {
                        return (
                          <div 
                            key={i} 
                            className="p-4 rounded-xl border bg-white dark:bg-zinc-800/40 border-zinc-200 dark:border-zinc-800 transition-all cursor-default"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-bold text-zinc-900 dark:text-zinc-100">{item.item || item.component}</span>
                              {/* Internal percentages removed for cleaner UI as requested */}
                            </div>
                            <div className="text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-3 leading-relaxed">{item.notes}</div>
                            {item.source_details && item.source_details.length > 0 && (
                              <div className="grid grid-cols-1 gap-2">
                                {item.source_details.map((sd: any, j: number) => (
                                  <div key={j} className="p-3 bg-zinc-50 dark:bg-zinc-900/50 rounded-lg border border-zinc-100 dark:border-zinc-800 flex flex-col gap-1">
                                    <span className="text-[10px] font-black uppercase text-indigo-500 dark:text-indigo-400">{sd.source} Signal</span>
                                    <p className="text-xs text-zinc-800 dark:text-zinc-200 leading-tight italic">"{sd.explanation}"</p>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Content: Tabs & Visualization */}
          <div className="hidden md:flex flex-col w-[60%] bg-zinc-100 dark:bg-zinc-950 overflow-hidden">
            <div className="flex border-b border-zinc-200 dark:border-zinc-800">
              <button onClick={() => setActiveTab('cv')} className={`px-6 py-3 text-sm font-bold transition-colors ${activeTab === 'cv' ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white dark:bg-zinc-900' : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'}`}>Candidate CV</button>
              <button onClick={() => setActiveTab('github')} className={`px-6 py-3 text-sm font-bold transition-colors ${activeTab === 'github' ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white dark:bg-zinc-900' : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'}`}>GitHub Evidence</button>
              <button onClick={() => setActiveTab('linkedin')} className={`px-6 py-3 text-sm font-bold transition-colors ${activeTab === 'linkedin' ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white dark:bg-zinc-900' : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'}`}>LinkedIn Experience</button>
              <button onClick={() => setActiveTab('formula')} className={`px-6 py-3 text-sm font-bold transition-colors ${activeTab === 'formula' ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white dark:bg-zinc-900' : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'}`}>Score Formula</button>
            </div>

            <div className={`flex-1 overflow-hidden ${activeTab === 'cv' ? '' : 'overflow-y-auto p-8'}`}>
              {!candidateDetail ? (
                <div className="h-full flex items-center justify-center text-zinc-400 animate-pulse font-medium">Extracting source profiles...</div>
              ) : (
                <>
                  {activeTab === 'cv' && (
                    <div className="h-full relative flex flex-col group/cv">
                      <div className="absolute top-6 right-6 z-10 flex bg-white dark:bg-zinc-800 p-1 rounded-xl shadow-2xl border border-zinc-200 dark:border-zinc-700 opacity-0 group-hover/cv:opacity-100 transition-opacity duration-300">
                        <button onClick={() => setCvViewMode('original')} className={`px-4 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${cvViewMode === 'original' ? 'bg-indigo-600 text-white shadow-lg' : 'text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200'}`}>Original Doc</button>
                        <button onClick={() => setCvViewMode('intelligence')} className={`px-4 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${cvViewMode === 'intelligence' ? 'bg-indigo-600 text-white shadow-lg' : 'text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200'}`}>AI Evidence</button>
                      </div>
                      {cvViewMode === 'original' ? (
                        <iframe src={`${candidateDetail.cv_url}#view=FitH`} className="w-full h-full border-none bg-zinc-900" title="Candidate CV" />
                      ) : (
                        <div className="flex-1 bg-zinc-100 dark:bg-black/40 overflow-y-auto p-12">
                          <div className="max-w-[850px] mx-auto bg-white dark:bg-zinc-900 shadow-2xl rounded-sm border border-zinc-200 dark:border-zinc-800 min-h-[1100px] p-16 md:p-20 relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-1 bg-indigo-600/50" />
                            <div className="prose prose-zinc dark:prose-invert max-w-none">
                              <p className="text-zinc-800 dark:text-zinc-100 leading-[1.8] whitespace-pre-wrap font-serif text-[15px] antialiased">
                                {candidateDetail.full_cv_text?.split(/(\s+)/).map((part: string, i: number) => {
                                  if (!part.trim()) return part;
                                  const cleanPart = part.toLowerCase().replace(/[^a-z0-9]/g, '');
                                  const cleanHover = hoveredItem?.toLowerCase().replace(/[^a-z0-9]/g, '') || '';
                                  const isHighlighted = cleanHover && (cleanPart.includes(cleanHover) || cleanHover.includes(cleanPart)) && cleanHover.length > 2 && cleanPart.length > 2;
                                  return <span key={i} className={isHighlighted ? "bg-indigo-500/30 text-indigo-700 dark:text-indigo-300 font-bold px-0.5 rounded-sm ring-1 ring-indigo-500/20 shadow-sm transition-all scale-110 inline-block" : "transition-all duration-300"}>{part}</span>;
                                })}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'github' && (
                    <div className="space-y-6">
                      <div className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm flex items-center gap-6">
                        <img src={candidateDetail.github_profile?.avatar_url} className="w-16 h-16 rounded-full ring-2 ring-indigo-500/20" alt="GH" />
                        <div>
                          <h4 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">{candidateDetail.github_profile?.name || candidateDetail.github_profile?.username}</h4>
                          <div className="flex items-center gap-4 mt-1 text-xs font-bold text-zinc-500">
                            <span>★ {candidateDetail.github_profile?.total_stars} stars</span>
                            <span>⚡ {candidateDetail.github_profile?.total_commits} commits</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                        <h4 className="text-[10px] font-black uppercase tracking-widest text-zinc-400 mb-4">Technical Breadth (LoC %)</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                          {candidateDetail.github_profile?.languages?.map((l: any) => (
                            <div key={l.label} className="space-y-1">
                              <div className="flex justify-between text-[11px] font-bold">
                                <span className="text-zinc-600">{l.label}</span>
                                <span className="text-zinc-400">{l.pct}%</span>
                              </div>
                              <div className="h-1.5 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
                                <div className="h-full bg-indigo-600" style={{ width: `${l.pct}%` }} />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <GitHubEvolutionChart history={candidateDetail.github_profile?.language_history || []} />

                      <div className="grid grid-cols-1 gap-4">
                        {[...(candidateDetail.github_projects || [])].sort((a, b) => (b.stars || 0) - (a.stars || 0)).map((repo: any) => (
                          <div key={repo.id} className="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800">
                            <div className="flex justify-between items-start mb-2">
                              <h5 className="font-bold text-sm text-zinc-900 dark:text-zinc-100">{repo.name}</h5>
                              <span className="text-[10px] font-black text-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 px-2 py-0.5 rounded-full">{repo.language}</span>
                            </div>
                            <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2">{repo.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeTab === 'linkedin' && (
                    <div className="space-y-6">
                      <div className="p-8 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                        <div className="flex items-center gap-6 mb-6">
                          <img src={candidateDetail.linkedin_profile?.profile_photo} className="w-20 h-20 rounded-2xl object-cover ring-4 ring-indigo-500/10 shadow-xl" alt="LI" />
                          <div className="space-y-1">
                            <h4 className="text-2xl font-black text-zinc-900 dark:text-zinc-50">{candidateDetail.linkedin_profile?.full_name}</h4>
                            <p className="text-sm font-bold text-indigo-600 dark:text-indigo-400">{candidateDetail.linkedin_profile?.headline}</p>
                            <div className="flex items-center gap-3 text-[10px] font-black text-zinc-400 uppercase tracking-widest pt-1">
                              <span>{candidateDetail.linkedin_profile?.connections || 0} Connections</span>
                              <span className="w-1 h-1 rounded-full bg-zinc-300 dark:bg-zinc-700" />
                              <span>{candidateDetail.linkedin_profile?.followers || 0} Followers</span>
                            </div>
                          </div>
                        </div>
                        {candidateDetail.linkedin_profile?.about && (
                          <p className="text-sm text-zinc-600 dark:text-zinc-400 italic border-l-2 border-indigo-500/20 pl-4 py-1 leading-relaxed">
                            "{candidateDetail.linkedin_profile?.about}"
                          </p>
                        )}
                      </div>

                      {/* Skills Grid */}
                      {candidateDetail.linkedin_profile?.skills && candidateDetail.linkedin_profile.skills.length > 0 && (
                        <div className="p-8 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                          <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 mb-6 flex items-center gap-2">
                             Professional Endorsements
                             <span className="text-indigo-500">•</span>
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {candidateDetail.linkedin_profile.skills.map((skill: string, i: number) => (
                              <span key={i} className="px-3 py-1.5 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg text-[10px] font-black text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-800 uppercase tracking-tight">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="space-y-4">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 px-2">Professional Experience</h4>
                        {candidateDetail.linkedin_experience?.map((exp: any) => (
                          <div key={exp.id} className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800">
                            <div className="flex justify-between items-start mb-4">
                              <div>
                                <h4 className="font-bold text-zinc-900 dark:text-zinc-50">{exp.position}</h4>
                                <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">{exp.company_name}</span>
                              </div>
                              <span className="text-[10px] font-mono text-zinc-400">{formatDate(exp.start_date)} — {formatDate(exp.end_date) || 'Present'}</span>
                            </div>
                            <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">{exp.description}</p>
                          </div>
                        ))}
                      </div>
                      
                      <div className="space-y-4">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 px-2">Featured Projects</h4>
                        <div className="grid grid-cols-1 gap-4">
                          {candidateDetail.linkedin_projects?.map((proj: any, i: number) => (
                            <div key={i} className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                              <div className="flex justify-between items-start mb-2">
                                <h5 className="font-bold text-sm text-zinc-900 dark:text-zinc-50">{proj.title}</h5>
                                <span className="text-[10px] font-mono text-zinc-400">{formatDate(proj.start_date)} — {formatDate(proj.end_date)}</span>
                              </div>
                              <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">{proj.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 px-2">Certifications & Credentials</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          {candidateDetail.linkedin_certifications?.map((cert: any, i: number) => (
                            <div key={i} className="p-4 bg-zinc-50 dark:bg-zinc-800/30 rounded-xl border border-zinc-200 dark:border-zinc-800 flex items-center gap-4">
                              <div className="w-10 h-10 rounded-lg bg-white dark:bg-zinc-900 flex items-center justify-center border border-zinc-200 dark:border-zinc-700 shrink-0">
                                <svg className="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04kM12 20.944a11.955 11.955 0 01-8.618-3.04m17.236 0a11.955 11.955 0 01-8.618 3.04" />
                                </svg>
                              </div>
                              <div>
                                <h5 className="text-xs font-bold text-zinc-900 dark:text-zinc-50 leading-tight">{cert.title}</h5>
                                <p className="text-[10px] text-zinc-500 mt-1">{cert.issuer || 'Verified Credential'}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 px-2">Volunteering & Community</h4>
                        <div className="grid grid-cols-1 gap-4">
                          {candidateDetail.linkedin_volunteering?.map((vol: any, i: number) => (
                            <div key={i} className="p-4 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm flex justify-between items-center">
                              <div>
                                <h5 className="text-xs font-bold text-zinc-900 dark:text-zinc-50">{vol.position}</h5>
                                <p className="text-[10px] text-zinc-500 mt-0.5">{vol.organization || 'Community Program'}</p>
                              </div>
                              <span className="text-[10px] font-mono text-zinc-400">{formatDate(vol.start_date)} — {formatDate(vol.end_date) || 'Present'}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 px-2">Academic Credentials</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          {candidateDetail.cv_education?.map((edu: any, i: number) => (
                            <div key={i} className="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm group/edu hover:border-indigo-500/50 transition-all">
                              <h5 className="font-bold text-sm text-zinc-900 dark:text-zinc-100 group-hover/edu:text-indigo-600 transition-colors">{edu.school_name}</h5>
                              <p className="text-xs text-indigo-600 dark:text-indigo-400 mt-1 font-bold">{edu.degree}</p>
                              <div className="mt-3 pt-3 border-t border-zinc-100 dark:border-zinc-800 flex justify-between items-center">
                                <span className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">{formatDate(edu.start_date)} — {formatDate(edu.end_date)}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === 'formula' && <ScoringAudit candidate={candidate} />}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
