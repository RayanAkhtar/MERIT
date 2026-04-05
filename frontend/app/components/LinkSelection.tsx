import React from 'react';
import GitHubPreview, { GithubData } from './GitHubPreview';
import LinkedInPreview, { LinkedinData } from './LinkedInPreview';

interface LinkSelectionProps {
  metrics: {
    uploaded_files: number;
    link_counts: Record<string, number>;
    example_links: Record<string, string>;
  };
  selectedLinks: Record<string, boolean>;
  setSelectedLinks: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
  githubData?: GithubData | null;
  linkedinData?: LinkedinData | null;
}

const LinkSelection: React.FC<LinkSelectionProps> = ({ metrics, selectedLinks, setSelectedLinks, githubData, linkedinData }) => {

  const linkedinProjects = React.useMemo(() => {
    if (!linkedinData?.projects) return [];
    
    const normalize = (name: string) => (name || '').toLowerCase().replace(/[^a-z0-9]/g, '').trim();

    const githubNormalizedNames = [
        ...(githubData?.featured_projects || []).map(p => normalize(p.name)),
        ...(githubData?.repositories || []).map(r => normalize(r.name))
    ].filter(n => n.length > 2);
    
    return linkedinData.projects.filter(proj => {
        const lName = normalize(proj.title);
        if (lName.length <= 2) return true;
        
        return !githubNormalizedNames.some(gName => 
            lName.includes(gName) || gName.includes(lName)
        );
    });
  }, [linkedinData?.projects, githubData?.featured_projects, githubData?.repositories]);

  return (
    <div className="space-y-4 text-left font-sans">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400">
             Discovered Data Sources
          </h4>
          <p className="text-xs font-bold text-indigo-500/80 uppercase tracking-tight">
              Select a source for intelligence injection
          </p>
        </div>
        <span className="text-[10px] font-black text-zinc-500 dark:text-zinc-500 uppercase tracking-widest italic text-right px-4 py-1 rounded-full border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 shadow-sm dark:shadow-none">
            {metrics.uploaded_files} PROFILES ANALYZED
        </span>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(metrics.link_counts).length === 0 ? (
          <div className="col-span-full p-12 border-2 border-dashed border-zinc-800 rounded-[2.5rem] bg-zinc-900/30 text-center">
            <p className="text-sm font-bold text-zinc-500 uppercase tracking-widest">No injection sources detected in this batch.</p>
          </div>
        ) : (
          Object.entries(metrics.link_counts).map(([link, count]) => {
            const percentage = Math.round((count / metrics.uploaded_files) * 100);
            const isSelected = selectedLinks[link];
            const isUnavailable = link === 'other';

            return (
              <div
                key={link}
                className={`
                  p-6 rounded-[2rem] border text-left transition-all duration-500 transform relative overflow-hidden group
                  ${isUnavailable 
                    ? 'bg-zinc-100 dark:bg-zinc-900/20 border-zinc-200 dark:border-zinc-800/30 opacity-40 cursor-not-allowed grayscale' 
                    : 'cursor-pointer hover:border-indigo-500/30 hover:bg-zinc-50 dark:hover:bg-zinc-900/50 shadow-sm hover:shadow-xl' }
                  ${!isUnavailable && isSelected 
                    ? 'bg-gradient-to-br from-indigo-600 to-indigo-700 border-indigo-500 text-white shadow-2xl shadow-indigo-600/30 scale-[1.02]' 
                    : !isUnavailable ? 'bg-white dark:bg-zinc-950/80 border-zinc-200 dark:border-zinc-800 text-zinc-900 dark:text-zinc-100' : ''}
                `}
                onClick={() =>
                  !isUnavailable && setSelectedLinks((prev) => ({
                    ...prev,
                    [link]: !prev[link],
                  }))
                }
              >

                <div className={`absolute -right-2 -top-2 p-6 opacity-[0.03] transition-transform duration-700 group-hover:scale-110 ${isSelected ? 'text-white' : 'text-indigo-400'}`}>
                    <svg className="w-20 h-20" fill="currentColor" viewBox="0 0 24 24">
                       <path d="M12 14c3.31 0 6-2.69 6-6s-2.69-6-6-6-6 2.69-6 6 2.69 6 6 6zm0 2c-4.42 0-8 3.58-8 8h16c0-4.42-3.58-8-8-8z" />
                    </svg>
                </div>

                <div className="flex flex-col gap-5 relative">
                    <div className="flex items-center justify-between">
                        <div className={`p-3 rounded-2xl ${isSelected ? 'bg-white/20 backdrop-blur-md' : 'bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800'} transition-all`}>
                            {link === 'linkedin' ? (
                                <svg className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-blue-600 dark:text-white'}`} fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                                </svg>
                            ) : link === 'github' ? (
                                <svg className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-zinc-900 dark:text-white'}`} fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.042-1.416-4.042-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                                </svg>
                            ) : (
                                <svg className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-zinc-600'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                                </svg>
                            )}
                        </div>
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${isSelected ? 'bg-white border-white' : 'border-zinc-200 dark:border-zinc-800'}`}>
                            {isSelected && (
                                <svg className="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={4}>
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                                </svg>
                            )}
                        </div>
                    </div>

                    <div>
                        <div className="flex items-baseline gap-2">
                            <p className="text-2xl font-black uppercase tracking-tight leading-none italic">{link}</p>
                            <p className={`text-xs font-black px-2 py-0.5 rounded-md ${isSelected ? 'bg-white/20 text-white' : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'}`}>
                                {percentage}%
                            </p>
                        </div>
                        <p className={`text-[10px] mt-2 font-black uppercase tracking-widest ${isSelected ? 'text-indigo-100/70' : 'text-zinc-500'}`}>
                            {count} Signal{count !== 1 ? 's' : ''} Detected
                        </p>
                    </div>

                    <div className="w-full bg-black/20 h-1.5 rounded-full overflow-hidden">
                        <div 
                            className={`h-full transition-all duration-700 ${isSelected ? 'bg-white shadow-[0_0_10px_#fff]' : 'bg-indigo-500'}`}
                            style={{ width: `${percentage}%` }}
                        />
                    </div>
                </div>
              </div>
            );
          })
        )}
      </div>


      {(selectedLinks['linkedin'] || selectedLinks['github']) && (
        <div className="flex flex-col gap-10 pt-8 animate-in fade-in slide-in-from-bottom-8 duration-700">

            {selectedLinks['github'] && (
                !githubData ? (
                    <div className="p-10 rounded-[2.5rem] bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-xl space-y-12 relative overflow-hidden min-h-[500px]">
                        <div className="w-full flex flex-col items-center justify-center py-24 space-y-8">
                            <div className="relative w-16 h-16">
                                <div className="absolute inset-0 border-4 border-indigo-500/20 rounded-full" />
                                <div className="absolute inset-0 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                            </div>
                            <p className="text-[10px] font-black uppercase tracking-[0.4em] text-zinc-600 animate-pulse text-center">Infiltrating Technical Repositories...</p>
                        </div>
                    </div>
                ) : (
                    <GitHubPreview githubData={githubData} />
                )
            )}


            {selectedLinks['linkedin'] && (
                !linkedinData ? (
                    <div className="p-10 rounded-[2.5rem] bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-2xl relative overflow-hidden group min-h-[500px]">
                        <div className="w-full flex flex-col items-center justify-center py-24 space-y-8">
                            <div className="relative w-16 h-16">
                                <div className="absolute inset-0 border-4 border-blue-500/20 rounded-full" />
                                <div className="absolute inset-0 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                            </div>
                            <p className="text-[10px] font-black uppercase tracking-[0.4em] text-zinc-600 animate-pulse text-center">Parsing Professional Trajectories...</p>
                        </div>
                    </div>
                ) : (
                    <LinkedInPreview 
                        linkedinData={linkedinData} 
                        linkedinProjects={linkedinProjects} 
                    />
                )
            )}
        </div>
      )}
    </div>
  );
};

export default LinkSelection;