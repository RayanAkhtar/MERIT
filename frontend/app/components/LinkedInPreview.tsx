import React from 'react';

export interface LinkedinData {
  full_name: string;
  headline: string;
  about: string | null;
  location: string | { linkedinText: string } | null;
  followers: string | null;
  connections: string | null;
  profile_photo: string | null;
  experience: {
    company_name: string;
    position: string;
    start_date: string | { text: string };
    end_date: string | { text: string };
    description?: string;
    skills?: string[];
  }[];
  education: {
    school_name: string;
    degree: string;
    start_date: string | { text: string };
    end_date: string | { text: string };
    field_of_study?: string | null;
  }[];
  volunteering?: {
    position: string;
    organization: string | null;
    start_date: string | { text: string } | null;
    end_date: string | { text: string } | null;
  }[];
  projects?: {
    title: string;
    link: string | null;
    duration: string;
    description?: string;
  }[];
  languages?: {
    name: string;
    proficiency: string | null;
  }[];
  recommendations?: {
    author: string;
    headline: string | null;
    text: string | null;
    date: string | null;
  }[];
  skills: string[] | { name: string; endorsements?: number }[];
  certifications?: {
    title: string;
    issuer: string | null;
    issue_date: string | null;
  }[];
  cached?: boolean;
}

interface LinkedInPreviewProps {
  linkedinData: LinkedinData;
  linkedinProjects: any[]; // Already filtered against GitHub
}

const LinkedInPreview: React.FC<LinkedInPreviewProps> = ({ linkedinData, linkedinProjects }) => {
  const renderDate = (date: any) => {
    if (!date) return 'N/A';
    if (typeof date === 'string') return date;
    if (typeof date === 'object' && date.text) return date.text;
    if (typeof date === 'object' && date.year) return `${date.month ? date.month + ' ' : ''}${date.year}`;
    return 'N/A';
  };

  const renderLocation = (loc: any) => {
    if (!loc) return 'Global';
    if (typeof loc === 'string') return loc;
    if (typeof loc === 'object') {
        return loc.linkedinText || loc.text || loc.city || 'Global';
    }
    return 'Global';
  };

  return (
    <div className="p-10 rounded-[2.5rem] bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-2xl relative overflow-hidden group min-h-[500px]">
        <div className="absolute -right-32 -top-32 w-96 h-96 bg-blue-600/5 rounded-full blur-[100px] pointer-events-none opacity-50 dark:opacity-100" />
        
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-8 mb-16 relative z-10">
            <div className="flex items-center gap-6">
                <div className="p-4 rounded-2xl bg-blue-600 shadow-[0_0_30px_rgba(37,99,235,0.2)] dark:shadow-[0_0_30px_rgba(37,99,235,0.3)] hover:scale-110 transition-transform">
                    <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                    </svg>
                </div>
                <div>
                    <h5 className="font-black text-2xl tracking-tighter text-zinc-900 dark:text-white font-sans italic uppercase">Professional Identity</h5>
                    <p className="text-[10px] font-black text-zinc-500 uppercase tracking-[0.4em]">Reputation and Professional Data</p>
                </div>
            </div>

            <div className="flex items-center gap-3 px-5 py-2.5 rounded-xl bg-zinc-200 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-800">
                <div className="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.3)] dark:shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-600 dark:text-blue-500">
                    Reputation Validated
                </span>
            </div>
        </div>

        <div className="space-y-12 relative z-10">
            {/* Profile Identity Card */}
            <div className="p-8 rounded-3xl bg-white dark:bg-[#08080a] border border-zinc-200 dark:border-zinc-800/50 shadow-2xl relative overflow-hidden group/li-card">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-600/[0.05] dark:from-blue-600/[0.03] to-transparent opacity-0 group-hover/li-card:opacity-100 transition-opacity duration-1000" />
                
                <div className="flex flex-col lg:flex-row gap-10">
                    <div className="flex items-start gap-8 lg:w-2/3">
                        <div className="relative shrink-0">
                            {linkedinData.profile_photo ? (
                                <img 
                                    src={linkedinData.profile_photo} 
                                    alt={linkedinData.full_name} 
                                    className="w-24 h-24 rounded-2xl object-cover border border-zinc-200 dark:border-zinc-800 group-hover/li-card:border-blue-500/30 transition-all duration-700" 
                                />
                            ) : (
                                <div className="w-24 h-24 rounded-2xl bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex items-center justify-center">
                                    <svg className="w-10 h-10 text-zinc-400 dark:text-zinc-700" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                                    </svg>
                                </div>
                            )}
                            <div className="absolute -bottom-2 -right-2 p-2 rounded bg-blue-600 text-white shadow-lg">
                                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                                </svg>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="space-y-1">
                                <h3 className="text-3xl font-black text-zinc-900 dark:text-white tracking-tighter leading-none italic">{linkedinData.full_name}</h3>
                                <p className="text-blue-600 dark:text-blue-500 font-bold tracking-tight text-sm">{linkedinData.headline}</p>
                            </div>
                            <div className="flex flex-wrap items-center gap-4 text-xs font-black uppercase tracking-widest text-zinc-400 dark:text-zinc-500">
                                <span className="flex items-center gap-2">
                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M15 11a3 3 0 11-6-0 3 3 0 016 0z" />
                                    </svg>
                                    {renderLocation(linkedinData.location)}
                                </span>
                                <span className="w-1 h-1 rounded-full bg-zinc-200 dark:bg-zinc-800" />
                                <span className="text-zinc-500 dark:text-zinc-400">{linkedinData.followers || '0'} Followers</span>
                                <span className="w-1 h-1 rounded-full bg-zinc-200 dark:bg-zinc-800" />
                                <span className="text-zinc-500 dark:text-zinc-400">{linkedinData.connections || '0'} Connections</span>
                            </div>
                            {linkedinData.about && (
                                <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400 leading-relaxed italic border-l border-zinc-200 dark:border-zinc-800 pl-4">
                                    "{linkedinData.about.length > 200 ? linkedinData.about.substring(0, 200) + '...' : linkedinData.about}"
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Experience Timeline Grid */}
            <div className="space-y-8">
                <div className="flex items-center gap-5">
                    <div className="w-1.5 h-10 bg-blue-600 rounded-full shadow-[0_0_15px_rgba(37,99,235,0.5)]" />
                    <h6 className="text-[11px] font-black uppercase tracking-[0.35em] text-zinc-400">Employment History</h6>
                </div>

                <div className="space-y-6">
                    {Object.entries(linkedinData.experience.reduce((acc: any, exp: any) => {
                        const company = exp.company_name;
                        if (!acc[company]) acc[company] = { name: company, roles: [] };
                        acc[company].roles.push(exp);
                        return acc;
                    }, {} as Record<string, any>)).map(([companyName, data]: any, i) => (
                        <div key={i} className="p-5 rounded-3xl bg-white dark:bg-[#08080a]/50 border border-zinc-200 dark:border-zinc-800/80 hover:border-blue-500/20 transition-all group/co shadow-xl dark:shadow-none">
                            <div className="flex items-start gap-5">
                                <div className="shrink-0 w-10 h-10 rounded-xl bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex items-center justify-center text-zinc-400 dark:text-zinc-700 group-hover/co:text-blue-600 dark:group-hover/co:text-blue-500 transition-colors">
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1" />
                                    </svg>
                                </div>
                                <div className="flex-1 min-w-0 space-y-4">
                                    <div className="flex items-center justify-between">
                                        <h4 className="text-sm font-black text-zinc-900 dark:text-white uppercase tracking-widest">{companyName}</h4>
                                        <span className="px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-900 text-[9px] font-black text-zinc-400 dark:text-zinc-600 uppercase tracking-tighter border border-zinc-200 dark:border-zinc-800">
                                            {data.roles.length} {data.roles.length === 1 ? 'Role' : 'Roles'}
                                        </span>
                                    </div>
                                    
                                    <div className="relative ml-4 space-y-6">
                                        {data.roles.map((role: any, ri: number) => (
                                            <div key={ri} className="relative pl-8 group/role">
                                                {ri < data.roles.length - 1 && (
                                                    <div className="absolute left-[-3px] top-[15px] bottom-[-25px] w-[1px] bg-gradient-to-b from-blue-500/30 dark:from-blue-500/40 to-transparent z-0" />
                                                )}
                                                <div className="absolute left-[-6px] top-[7px] w-2 h-2 rounded-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 group-hover/role:bg-blue-600 group-hover/role:border-blue-500/50 transition-all z-10 shadow-lg dark:shadow-[0_0_8px_rgba(0,0,0,0.5)]" />
                                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 mb-1">
                                                    <h5 className="text-[11px] font-black text-zinc-600 dark:text-zinc-300 group-hover/role:text-blue-600 dark:group-hover/role:text-blue-400 transition-colors uppercase tracking-tight">{role.position}</h5>
                                                    <span className="text-[9px] font-black text-zinc-400 dark:text-zinc-500 uppercase tracking-tighter tabular-nums shrink-0 opacity-80 group-hover/role:text-zinc-700 dark:group-hover/role:text-zinc-300">
                                                        {renderDate(role.start_date)} — {renderDate(role.end_date)}
                                                    </span>
                                                </div>
                                                {role.skills && role.skills.length > 0 && (
                                                    <div className="flex flex-wrap gap-2 mt-2">
                                                        {role.skills.slice(0, 5).map((sk: string, idx: number) => (
                                                            <span key={idx} className="text-[8px] font-black text-zinc-400 dark:text-zinc-500 group-hover/role:text-blue-600/80 dark:group-hover/role:text-blue-400/80 uppercase tracking-widest transition-colors py-0.5 px-0 opacity-60 group-hover/role:opacity-100">
                                                                {sk}
                                                                {idx < Math.min(role.skills.length, 5) - 1 && <span className="ml-2 text-zinc-200 dark:text-zinc-800">|</span>}
                                                            </span>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Academic Foundation section */}
            <div className="space-y-8">
                <div className="flex items-center gap-5">
                    <div className="w-1.5 h-10 bg-indigo-500 rounded-full shadow-[0_0_15px_rgba(99,102,241,0.5)]" />
                    <h6 className="text-[11px] font-black uppercase tracking-[0.35em] text-zinc-400">Academic Background</h6>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
                    {linkedinData.education.map((edu, i) => (
                        <div key={i} className="p-6 rounded-3xl bg-white dark:bg-[#08080a] border border-zinc-200 dark:border-zinc-800/80 hover:border-indigo-500/30 transition-all group/edu cursor-default shadow-xl dark:shadow-none">
                            <div className="space-y-4">
                                <div className="flex items-start justify-between">
                                    <div className="w-10 h-10 rounded-xl bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex items-center justify-center text-zinc-400 dark:text-zinc-600 group-hover/edu:text-indigo-600 dark:group-hover/edu:text-indigo-500 group-hover/edu:bg-indigo-600/5 transition-all">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                                        </svg>
                                    </div>
                                    <span className="text-[9px] font-black text-zinc-400 dark:text-zinc-700 bg-zinc-100 dark:bg-zinc-950 px-2 py-1 rounded border border-zinc-200 dark:border-zinc-800 uppercase tracking-tighter tabular-nums">
                                        {renderDate(edu.start_date)} - {renderDate(edu.end_date)}
                                    </span>
                                </div>
                                <div className="space-y-1">
                                    <h4 className="text-sm font-black text-zinc-900 dark:text-white group-hover/edu:text-indigo-600 dark:group-hover/edu:text-indigo-400 transition-colors truncate">{edu.school_name}</h4>
                                    <p className="text-[10px] font-black text-zinc-400 dark:text-zinc-500 uppercase tracking-widest truncate">{edu.degree}</p>
                                    {edu.field_of_study && (
                                        <p className="text-[9px] font-black text-indigo-600 dark:text-indigo-500/70 uppercase tracking-[0.2em]">{edu.field_of_study}</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Recommendations Section (Full Width after language removal) */}
            {linkedinData.recommendations && linkedinData.recommendations.length > 0 && (
                <div className="space-y-8">
                    <div className="flex items-center gap-4">
                        <div className="w-1 h-8 bg-pink-500 rounded-full shadow-[0_0_10px_rgba(236,72,153,0.3)]" />
                        <h6 className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-500">Peer Sentiment: Professional Backing</h6>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-h-[400px] overflow-y-auto pr-4 scrollbar-thin scrollbar-thumb-zinc-300 dark:scrollbar-thumb-zinc-800 scrollbar-track-transparent">
                        {linkedinData.recommendations.map((rec, i) => (
                            <div key={i} className="p-6 rounded-3xl bg-white dark:bg-[#08080a] border border-zinc-200 dark:border-zinc-800 hover:border-pink-500/20 transition-all shadow-xl text-left">
                                <p className="text-[10px] font-medium text-zinc-500 dark:text-zinc-400 italic mb-6 leading-relaxed opacity-80">
                                    "{rec.text?.length && rec.text.length > 250 ? rec.text.substring(0, 250) + '...' : rec.text}"
                                </p>
                                <div className="flex items-center gap-4 border-t border-zinc-100 dark:border-zinc-900 pt-5">
                                    <div className="w-10 h-10 rounded-xl bg-zinc-50 dark:bg-zinc-900 flex items-center justify-center font-black text-pink-600 dark:text-pink-500/80 text-[10px] tracking-widest">
                                        {rec.author.split(' ').map(n => n?.[0]).join('')}
                                    </div>
                                    <div className="min-w-0">
                                        <h5 className="text-[11px] font-black text-zinc-900 dark:text-white uppercase tracking-tight truncate">{rec.author}</h5>
                                        <p className="text-[8px] font-bold text-zinc-500 dark:text-zinc-600 uppercase truncate tracking-widest">{rec.headline}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Volunteers & Projects Integration */}
            {(linkedinData.volunteering?.length || linkedinProjects.length > 0) && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                    {linkedinData.volunteering && linkedinData.volunteering.length > 0 && (
                        <div className="space-y-8 text-left">
                            <div className="flex items-center gap-4">
                                <div className="w-1 h-8 bg-emerald-500 rounded-full" />
                                <h6 className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-500">Extracurricular Activity</h6>
                            </div>
                            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-4 scrollbar-thin scrollbar-thumb-zinc-300 dark:scrollbar-thumb-zinc-800 scrollbar-track-transparent">
                                {[...(linkedinData.volunteering || [])].reverse().map((vol, i) => (
                                    <div key={i} className="p-5 rounded-2xl bg-white dark:bg-zinc-900/40 border border-zinc-200 dark:border-zinc-800/50 hover:border-emerald-500/20 transition-all group/vol shadow-lg dark:shadow-none">
                                        <div className="flex justify-between items-start mb-2">
                                            <h5 className="text-xs font-black text-zinc-900 dark:text-white group-hover/vol:text-emerald-600 dark:group-hover/vol:text-emerald-400 transition-colors uppercase tracking-tight">{vol.position}</h5>
                                            <span className="text-[8px] font-black text-zinc-400 dark:text-zinc-700 uppercase tracking-tighter">{renderDate(vol.start_date)}</span>
                                        </div>
                                        <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">{vol.organization}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {linkedinProjects.length > 0 && (
                        <div className="space-y-8 text-left">
                            <div className="flex items-center justify-between group/tip cursor-help">
                                <div className="flex items-center gap-4">
                                    <div className="w-1 h-8 bg-amber-500 rounded-full" />
                                    <h6 className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-500">Projects</h6>
                                </div>
                                <div className="flex items-center gap-2 transition-all">
                                    <div className="p-1.5 rounded-md bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-600">
                                        <svg className="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                    </div>
                                    <div className="absolute right-12 opacity-0 group-hover/tip:opacity-100 pointer-events-none transition-all duration-300 w-64 p-3 rounded-xl bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-2xl z-[100] text-left">
                                        <p className="text-[9px] font-bold text-zinc-500 dark:text-zinc-400 uppercase leading-relaxed tracking-widest">
                                            These projects are unique to the candidate's LinkedIn profile and are not already captured in their public GitHub data. These often include private repositories, corporate assignments, or university GitLab projects.
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-4 scrollbar-thin scrollbar-thumb-zinc-300 dark:scrollbar-thumb-zinc-800 scrollbar-track-transparent">
                                {linkedinProjects.map((proj, i) => (
                                    <div key={i} className="p-5 rounded-2xl bg-white dark:bg-zinc-900/40 border border-zinc-200 dark:border-zinc-800/50 hover:border-amber-500/20 transition-all group/proj shadow-lg dark:shadow-none">
                                        <div className="flex justify-between items-start mb-3">
                                            <h5 className="text-xs font-black text-zinc-900 dark:text-white group-hover/proj:text-amber-600 dark:group-hover/proj:text-amber-400 transition-colors uppercase tracking-tight italic">{proj.title}</h5>
                                            <span className="text-[8px] font-black text-zinc-400 dark:text-zinc-700 uppercase tracking-tighter tabular-nums">{proj.duration}</span>
                                        </div>
                                        {proj.description && (
                                            <p className="text-[10px] font-bold text-zinc-500 leading-relaxed uppercase tracking-wider line-clamp-3">
                                                {proj.description}
                                            </p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    </div>
  );
};

export default LinkedInPreview;
