import React from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend
} from 'recharts';

export interface LanguageDistribution {
  label: string;
  pct: number;
}

export interface FeaturedProject {
  name: string;
  type: string;
  stars: number;
  description: string;
  url: string;
  top_languages: string[];
}

export interface LanguageHistoryEntry {
  year: string;
  [key: string]: string | number;
}

export interface GithubRepository {
  name: string;
  description: string | null;
  language: string | null;
  url: string;
  stars: number;
  forks: number;
}

export interface GithubData {
  username: string;
  name: string | null;
  bio: string | null;
  company: string | null;
  location: string | null;
  email: string | null;
  avatar_url: string;
  profile_url: string;
  created_at: string;
  followers: number;
  following: number;
  public_repos: number;
  total_prs: number;
  total_commits: number;
  oss_prs: number;
  repo_count: number;
  total_lines: number;
  total_stars: number;
  total_forks: number;
  languages: LanguageDistribution[];
  featured_projects: FeaturedProject[];
  repositories?: GithubRepository[];
  language_history: LanguageHistoryEntry[];
}

interface GitHubPreviewProps {
  githubData: GithubData;
}

const GitHubPreview: React.FC<GitHubPreviewProps> = ({ githubData }) => {
  const [hiddenLangs, setHiddenLangs] = React.useState<Set<string>>(new Set());

  // Years extraction and mapping
  const availableYears = React.useMemo(() => {
    if (!githubData?.language_history) return [];
    return githubData.language_history.map(entry => entry.year).sort((a,b) => parseInt(a) - parseInt(b));
  }, [githubData?.language_history]);

  const [minYearIdx, setMinYearIdx] = React.useState(0);
  const [maxYearIdx, setMaxYearIdx] = React.useState(0);
  const [lastActive, setLastActive] = React.useState<'min' | 'max'>('min');

  // Initialize indices when data loads
  React.useEffect(() => {
    if (availableYears.length > 0) {
      setMinYearIdx(0);
      setMaxYearIdx(availableYears.length - 1);
    }
  }, [availableYears]);

  const filteredHistory = React.useMemo(() => {
    if (!githubData?.language_history || availableYears.length === 0) return [];
    const minYear = availableYears[minYearIdx];
    const maxYear = availableYears[maxYearIdx];
    return githubData.language_history.filter(e => e.year >= minYear && e.year <= maxYear);
  }, [githubData?.language_history, availableYears, minYearIdx, maxYearIdx]);

  const handleLegendClick = (o: any) => {
    const { dataKey } = o;
    setHiddenLangs((prev) => {
        const next = new Set(prev);
        if (next.has(dataKey)) {
            next.delete(dataKey);
        } else {
            next.add(dataKey);
        }
        return next;
    });
  };

  const baseLanguageColors: Record<string, string> = {
    'TypeScript': '#6366f1',
    'JavaScript': '#10b981',
    'Python': '#f59e0b',
    'TeX': '#ec4899',
    'Rust': '#a855f7',
    'Go': '#64748b',
    'Shell': '#f97316',
    'HTML': '#3b82f6',
    'CSS': '#ef4444',
    'C++': '#06b6d4',
    'SQL': '#8b5cf6',
    'C#': '#f43f5e',
    'Ruby': '#e11d48',
    'Java': '#b91c1c',
    'PHP': '#4f46e5',
    'C': '#475569',
    'Jupyter Notebook': '#f59e0b'
  };

  const dynamicColorMap = React.useMemo(() => {
    const map: Record<string, string> = { ...baseLanguageColors };
    const allLangs = new Set<string>();
    githubData.languages.forEach(l => allLangs.add(l.label));
    githubData.featured_projects.forEach(p => p.top_languages.forEach(l => allLangs.add(l)));

    allLangs.forEach(lang => {
      if (!map[lang]) {
        // Generate a random vibrant color for new languages
        const hue = Math.floor(Math.random() * 360);
        map[lang] = `hsl(${hue}, 70%, 50%)`;
      }
    });

    return map;
  }, [githubData]);

  const getLangColor = (lang: string) => dynamicColorMap[lang] || '#3f3f46';

  const formatNumber = (num: number) => {
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num.toString();
  };

  const getConicGradient = () => {
    if (!githubData.languages || githubData.languages.length === 0) {
        return 'conic-gradient(#3f3f46 0% 100%)';
    }
    
    let currentPct = 0;
    const segments = githubData.languages.map((lang) => {
        const start = currentPct;
        currentPct += lang.pct;
        const color = getLangColor(lang.label);
        return `${color} ${start}% ${currentPct}%`;
    });
    
    return `conic-gradient(${segments.join(', ')})`;
  };

  return (
    <div className="p-10 rounded-[2.5rem] bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-xl space-y-12 relative overflow-hidden min-h-[500px]">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-8 relative z-10">
            <div className="flex items-center gap-6">
                <div className="p-4 rounded-xl bg-zinc-200 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-800 flex items-center justify-center transition-all">
                    <svg className="w-8 h-8 text-zinc-900 dark:text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.042-1.416-4.042-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                </div>
                <div className="space-y-1">
                    <h5 className="font-black text-2xl tracking-tighter text-zinc-900 dark:text-white font-sans italic uppercase">Technical Intelligence</h5>
                    <p className="text-[10px] font-black text-zinc-400 dark:text-zinc-500 uppercase tracking-[0.4em]">Language History and Contribution Statistics</p>
                </div>
            </div>
            
            <div className="flex items-center gap-3 px-5 py-2.5 rounded-xl bg-zinc-200 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-800">
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.3)]" />
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-emerald-600 dark:text-emerald-500">
                    Extraction Validated
                </span>
            </div>
        </div>

        <div className="space-y-16 relative z-10">
            {/* Row 0: GitHub Profile Summary Card */}
            <div className="p-8 rounded-3xl bg-white dark:bg-[#09090b] border border-zinc-200 dark:border-zinc-800/50 shadow-2xl relative overflow-hidden group/profile">
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/[0.05] dark:from-indigo-500/[0.02] to-transparent opacity-0 group-hover/profile:opacity-100 transition-opacity duration-1000" />
                
                {/* Global Notice Tooltip */}
                <div className="absolute top-6 right-6 z-30 group/global-tip">
                    <div className="w-6 h-6 rounded-full border border-purple-500/30 flex items-center justify-center text-[10px] font-black text-purple-600 dark:text-purple-400 bg-purple-500/5 cursor-help hover:bg-purple-500/10 hover:border-purple-500/60 transition-all shadow-[0_0_10px_rgba(168,85,247,0.1)]">?</div>
                    <div className="absolute top-0 right-8 w-64 p-4 rounded-xl bg-white dark:bg-zinc-950/90 border border-zinc-200 dark:border-zinc-800 text-[10px] font-medium leading-relaxed normal-case tracking-normal opacity-0 group-hover/global-tip:opacity-100 transition-all duration-300 pointer-events-none shadow-2xl text-zinc-600 dark:text-zinc-400 backdrop-blur-xl translate-x-2 group-hover/global-tip:translate-x-0">
                        <div className="text-purple-600 dark:text-purple-400 font-black uppercase mb-2 tracking-widest text-[9px]">Contribution Integrity Notice</div>
                        Metrics are aggregated exclusively from public repositories. GitHub's internal totals often include private corporate activity not visible to public scanners.
                    </div>
                </div>

                <div className="flex flex-col lg:flex-row gap-8 relative z-10">
                    {/* Left: Identity */}
                    <div className="flex items-start gap-6 lg:w-1/2">
                        <div className="relative shrink-0">
                            <img 
                                src={githubData.avatar_url} 
                                alt={githubData.name || 'Github User'} 
                                className="w-20 h-20 rounded-2xl object-cover grayscale-[0.2] dark:grayscale-[0.2] group-hover/profile:grayscale-0 transition-all duration-700"
                            />
                            <div className="absolute -bottom-2 -left-2 px-2 py-0.5 rounded bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-[7px] font-black tracking-[0.2em] text-indigo-600 dark:text-indigo-400">
                                {githubData.username.toUpperCase()}
                            </div>
                        </div>

                        <div className="space-y-3 min-w-0">
                            <div className="space-y-1">
                                <h3 className="text-3xl font-black text-zinc-900 dark:text-white tracking-tighter leading-none">
                                    {githubData.name || githubData.username}
                                </h3>
                                <div className="flex items-center gap-3">
                                    <span className="text-[9px] font-black uppercase tracking-[0.2em] text-zinc-400 dark:text-zinc-500">
                                       Joined {new Date(githubData.created_at).getFullYear()}
                                    </span>
                                    {githubData.location && (
                                        <>
                                            <span className="w-1 h-1 rounded-full bg-zinc-200 dark:bg-zinc-800" />
                                            <span className="text-[9px] font-black uppercase tracking-[0.2em] text-zinc-400 dark:text-zinc-500">
                                                {githubData.location}
                                            </span>
                                        </>
                                    )}
                                </div>
                            </div>
                            
                            <p className="text-[11px] font-medium text-zinc-500 dark:text-zinc-400 leading-relaxed italic opacity-80 line-clamp-2">
                                "{githubData.bio || "Quantitative technical contribution signature not provided."}"
                            </p>

                            <div className="flex gap-2 pt-1">
                                <button 
                                    onClick={() => window.open(githubData.profile_url, '_blank')}
                                    className="px-3 py-1 rounded bg-zinc-100 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 text-[8px] font-black tracking-[0.2em] text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:border-zinc-400 dark:hover:border-zinc-600 transition-all uppercase"
                                >
                                    View GitHub Profile
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Right: Activity & Reputation Overview */}
                    <div className="lg:w-1/2 lg:border-l border-zinc-100 dark:border-zinc-800/50 lg:pl-12 flex items-center justify-between">
                        {[
                            { label: 'TOTAL PRS', value: githubData.total_prs, color: 'text-indigo-600 dark:text-indigo-400' },
                            { label: 'TOTAL COMMITS', value: githubData.total_commits, color: 'text-emerald-600 dark:text-emerald-400' },
                            { label: 'TOTAL STARS', value: githubData.total_stars, color: 'text-amber-600 dark:text-amber-400' },
                            { label: 'TOTAL REPOS', value: githubData.public_repos, color: 'text-zinc-900 dark:text-white' }
                        ].map((stat, i) => (
                            <div key={i} className="space-y-1 relative group/stat">
                                <span className="text-[8px] font-black uppercase tracking-[0.2em] text-zinc-400 dark:text-zinc-600">
                                    {stat.label}
                                </span>
                                <span className={`block text-2xl font-black ${stat.color} tracking-tighter tabular-nums`}>
                                    {stat.value}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Row 1: Pulse Chart & Taxonomy Grid */}
            <div className="space-y-12">
                <div className="flex items-center gap-5">
                    <div className="w-1.5 h-10 bg-indigo-600 rounded-full shadow-[0_0_15px_rgba(79,70,229,0.3)] dark:shadow-[0_0_15px_rgba(79,70,229,0.5)]" />
                    <h6 className="text-[11px] font-black uppercase tracking-[0.35em] text-zinc-500 dark:text-zinc-400">Developer Ecosystem</h6>
                </div>
                
                <div className="p-10 rounded-3xl bg-white dark:bg-[#0b0b0d]/50 border border-zinc-100 dark:border-zinc-800/50 shadow-2xl backdrop-blur-md">
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
                        {/* Glassmorphic Pie Chart */}
                        <div className="lg:col-span-12 xl:col-span-5 flex justify-center">
                            <div className="relative w-64 h-64 flex-shrink-0">
                                <div 
                                    className="w-full h-full rounded-full shadow-lg transition-transform duration-1000"
                                    style={{ 
                                        background: getConicGradient(),
                                        maskImage: 'radial-gradient(circle, transparent 65%, black 66%)',
                                        WebkitMaskImage: 'radial-gradient(circle, transparent 65%, black 66%)'
                                    }}
                                />
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <div className="text-center">
                                        <span className="block text-4xl font-black text-zinc-900 dark:text-white tracking-tighter leading-none">{formatNumber(githubData.total_lines)}</span>
                                        <span className="block text-[8px] font-black text-zinc-500 dark:text-zinc-600 uppercase tracking-[0.2em] mt-2">Total Lines Scanned</span>
                                        <div className="h-4" />
                                        <span className="block text-2xl font-black text-zinc-400 dark:text-white/50 tracking-tighter leading-none">{githubData.repo_count}</span>
                                        <span className="block text-[7px] font-black text-zinc-400 dark:text-zinc-700 uppercase tracking-[0.2em]">Verified Repos</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Taxonomy Badges */}
                        <div className="lg:col-span-12 xl:col-span-7 flex flex-wrap gap-3">
                            {githubData.languages.map((lang, i) => (
                                <div key={i} className="flex items-center gap-3 px-4 py-2 rounded-full bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800/50 hover:border-zinc-400 dark:hover:border-zinc-600 transition-all group/lang cursor-default">
                                    <div className="w-1.5 h-1.5 rounded-full shadow-[0_0_8px_currentColor]" style={{ backgroundColor: getLangColor(lang.label), color: getLangColor(lang.label) }} />
                                    <span className="text-[10px] font-black text-zinc-500 dark:text-zinc-400 group-hover/lang:text-zinc-900 dark:group-hover/lang:text-white transition-colors uppercase tracking-widest leading-none">{lang.label}</span>
                                    <span className="text-[9px] font-black text-zinc-400 dark:text-zinc-700">{lang.pct}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Row 2: Language History Trend */}
            <div className="space-y-10 pt-4">
                <div className="flex items-center gap-5">
                    <div className="w-1.5 h-10 bg-purple-600 dark:bg-purple-500 rounded-full shadow-[0_0_15px_rgba(168,85,247,0.3)] dark:shadow-[0_0_15px_rgba(168,85,247,0.5)]" />
                    <h6 className="text-[11px] font-black uppercase tracking-[0.35em] text-zinc-500 dark:text-zinc-400">Language Trends</h6>
                </div>

                <div className="p-10 rounded-3xl bg-white dark:bg-[#09090b] border border-zinc-100 dark:border-zinc-800/50 shadow-2xl relative overflow-hidden">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 mb-12 p-8 rounded-2xl bg-zinc-50 dark:bg-zinc-900/30 border border-zinc-100 dark:border-zinc-800 shadow-inner">
                        <div className="space-y-2">
                            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-400 dark:text-zinc-600">Time Range</span>
                            <div className="flex items-center gap-4 text-zinc-900 dark:text-white font-black tracking-tighter text-2xl">
                                <span className="px-3 py-1.5 rounded-lg bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-purple-600 dark:text-purple-400">
                                    {availableYears[minYearIdx] || '...'}
                                </span>
                                <span className="text-zinc-300 dark:text-zinc-700 opacity-50">—</span>
                                <span className="px-3 py-1.5 rounded-lg bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-purple-600 dark:text-purple-400">
                                    {availableYears[maxYearIdx] || '...'}
                                </span>
                            </div>
                        </div>

                        <div className="flex-1 max-w-md">
                            <div className="space-y-4">
                                <div className="flex justify-between text-[9px] font-black text-zinc-400 dark:text-zinc-600 uppercase tracking-widest">
                                    <span>Early Commit History</span>
                                    <span>Present Day</span>
                                </div>
                                <div className="relative h-2 bg-zinc-200 dark:bg-zinc-950 rounded-full flex items-center">
                                    <div 
                                        className="absolute h-full bg-purple-500/20 dark:bg-purple-500/30 rounded-full"
                                        style={{ 
                                            left: availableYears.length > 1 ? `${(minYearIdx / (availableYears.length - 1)) * 100}%` : '0%',
                                            right: availableYears.length > 1 ? `${100 - (maxYearIdx / (availableYears.length - 1)) * 100}%` : '0%'
                                        }}
                                    />
                                    <input 
                                        type="range"
                                        min={0}
                                        max={Math.max(0, availableYears.length - 1)}
                                        value={minYearIdx}
                                        onMouseDown={() => setLastActive('min')}
                                        onChange={(e) => setMinYearIdx(Math.min(parseInt(e.target.value), maxYearIdx))}
                                        className={`absolute w-full appearance-none bg-transparent cursor-pointer pointer-events-auto h-1 accent-purple-600 dark:accent-purple-500 ${lastActive === 'min' ? 'z-30' : 'z-20'}`}
                                    />
                                    <input 
                                        type="range"
                                        min={0}
                                        max={Math.max(0, availableYears.length - 1)}
                                        value={maxYearIdx}
                                        onMouseDown={() => setLastActive('max')}
                                        onChange={(e) => setMaxYearIdx(Math.max(parseInt(e.target.value), minYearIdx))}
                                        className={`absolute w-full appearance-none bg-transparent cursor-pointer pointer-events-auto h-1 accent-purple-600 dark:accent-purple-500 ${lastActive === 'max' ? 'z-30' : 'z-20'}`}
                                    />
                                </div>
                                <p className="text-[8px] font-bold text-zinc-400 dark:text-zinc-500 italic text-center uppercase tracking-widest">
                                    Slide to adjust the analytical window
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="h-[480px] w-full relative z-10">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart
                                data={filteredHistory}
                                margin={{ top: 20, right: 30, left: 30, bottom: 20 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" dark-stroke="#27272a" vertical={false} />
                                <XAxis 
                                    dataKey="year" 
                                    stroke="#71717a" 
                                    fontSize={10} 
                                    tickLine={false} 
                                    axisLine={false}
                                    tick={{ fontWeight: 800, letterSpacing: '0.1em' }}
                                    dy={10}
                                />
                                <YAxis 
                                    stroke="#71717a" 
                                    fontSize={9} 
                                    tickLine={false} 
                                    axisLine={false}
                                    tickFormatter={(value) => formatNumber(value)}
                                    tick={{ fontWeight: 800 }}
                                    domain={['auto', 'auto']}
                                    label={{ 
                                        value: 'Validated Lines of Code', 
                                        angle: -90, 
                                        position: 'insideLeft',
                                        offset: 10,
                                        style: { fontSize: '9px', fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.1em', fill: '#71717a' }
                                    }}
                                />
                                <Tooltip 
                                    itemSorter={(item) => Number(item.value) * -1}
                                    contentStyle={{ 
                                        backgroundColor: 'var(--tw-backgroundColor-white)', 
                                        border: '1px solid #e4e4e7',
                                        borderRadius: '1rem',
                                        padding: '12px',
                                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
                                    }}
                                    dark-contentStyle={{
                                        backgroundColor: '#09090b',
                                        border: '1px solid #27272a',
                                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)'
                                    }}
                                    itemStyle={{ fontSize: '10px', fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.05em' }}
                                    labelStyle={{ color: '#71717a', fontSize: '9px', fontWeight: 900, marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.2em' }}
                                    formatter={(value: any, name: any) => [`${formatNumber(Number(value))} Lines`, name.toString().toUpperCase()]}
                                />
                                <Legend 
                                    verticalAlign="top" 
                                    align="right" 
                                    iconSize={0}
                                    onClick={handleLegendClick}
                                    formatter={(value, entry: any) => {
                                        const color = getLangColor(entry.dataKey);
                                        const isHidden = hiddenLangs.has(entry.dataKey);
                                        return (
                                            <span className={`
                                                inline-flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all duration-300 mx-1 mb-2
                                                ${isHidden 
                                                    ? 'bg-zinc-100 dark:bg-zinc-900/20 border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-600 opacity-40 grayscale line-through' 
                                                    : 'bg-white dark:bg-zinc-900/80 border-zinc-200 dark:border-zinc-800 text-zinc-900 dark:text-zinc-300 hover:border-zinc-400 dark:hover:border-zinc-500 hover:scale-105 active:scale-95 shadow-lg dark:shadow-xl'}
                                            `}>
                                                <span className="w-1.5 h-1.5 rounded-full shadow-[0_0_8px_currentColor]" style={{ backgroundColor: color, color: color }} />
                                                <span className="font-black tracking-widest uppercase text-[8px]">{value}</span>
                                            </span>
                                        );
                                    }}
                                    wrapperStyle={{ 
                                        paddingBottom: '40px',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        justifyContent: 'flex-end',
                                        flexWrap: 'wrap'
                                    }}
                                />
                                {Object.keys(filteredHistory[0] || {})
                                    .filter(k => k !== 'year')
                                    .map((lang, idx) => (
                                        <Line
                                            key={lang}
                                            type="monotone"
                                            dataKey={lang}
                                            stroke={getLangColor(lang)}
                                            strokeWidth={3}
                                            dot={{ r: 4, strokeWidth: 2, fill: 'var(--tw-backgroundColor-white)' }}
                                            activeDot={{ r: 6, strokeWidth: 0, fill: getLangColor(lang) }}
                                            animationDuration={800}
                                            animationBegin={idx * 50}
                                            hide={hiddenLangs.has(lang)}
                                        />
                                    ))
                                }
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Row 3: Technical Depth / Featured Projects */}
            <div className="space-y-12">
                <div className="flex items-center gap-5">
                    <div className="w-1.5 h-10 bg-emerald-600 dark:bg-emerald-500 rounded-full shadow-[0_0_15px_rgba(16,185,129,0.3)] dark:shadow-[0_0_15px_rgba(16,185,129,0.5)]" />
                    <h6 className="text-[11px] font-black uppercase tracking-[0.35em] text-zinc-500 dark:text-zinc-400">Public Projects</h6>
                </div>

                <div className="flex flex-col gap-6">
                    {githubData.featured_projects.map((proj, i) => (
                        <div 
                            key={i} 
                            onClick={() => window.open(proj.url, '_blank')}
                            className="group/card p-8 rounded-3xl bg-white dark:bg-[#0b0b0d]/50 border border-zinc-200 dark:border-zinc-800/50 hover:border-emerald-500/30 transition-all flex flex-col md:flex-row gap-12 relative overflow-hidden shadow-2xl backdrop-blur-md cursor-pointer"
                        >
                            <div className="flex-1 space-y-6">
                                <div className="flex items-center justify-between md:justify-start gap-5">
                                    <div className="w-12 h-12 rounded-2xl bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex items-center justify-center shadow-2xl group-hover/card:bg-indigo-600 transition-all duration-500">
                                        <svg className="w-5 h-5 text-emerald-600 dark:text-emerald-500 group-hover/card:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                    </div>
                                    <span className="px-3 py-1 rounded bg-emerald-500/5 text-emerald-600 dark:text-emerald-500 text-[10px] font-black border border-emerald-500/10 uppercase tracking-[0.2em] shadow-lg">
                                        {proj.type}
                                    </span>
                                </div>

                                <div className="space-y-4">
                                    <h4 className="text-3xl font-black text-zinc-900 dark:text-white group-hover/card:text-emerald-600 dark:group-hover/card:text-emerald-400 transition-colors tracking-tighter text-left">
                                        {proj.name}
                                    </h4>
                                    <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400 leading-relaxed italic opacity-80 border-l-2 border-zinc-200 dark:border-zinc-800 pl-5 py-1 line-clamp-3 text-left">
                                        "{proj.description}"
                                    </p>
                                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-50 dark:bg-zinc-900/50 border border-amber-500/20 w-fit">
                                        <span className="text-amber-500 text-[10px]">★</span>
                                        <span className="text-[9px] font-black text-amber-600 dark:text-amber-500 uppercase tracking-[0.2em]">{proj.stars} Stars</span>
                                    </div>
                                </div>
                            </div>

                            <div className="w-full md:w-64 space-y-6 md:border-l border-zinc-100 dark:border-zinc-800/50 md:pl-10 text-left">
                                <h3 className="text-[9px] font-black tracking-[0.3em] text-zinc-400 dark:text-zinc-600 uppercase">Stack Architecture</h3>
                                <div className="space-y-4">
                                    {proj.top_languages.map((lang, li) => (
                                        <div key={li} className="flex items-center gap-4 group/stk">
                                            <div className="w-1.5 h-1.5 rounded-full shadow-[0_0_8px_currentColor]" style={{ backgroundColor: getLangColor(lang), color: getLangColor(lang) }} />
                                            <span className="text-[10px] font-black text-zinc-600 dark:text-zinc-300 uppercase tracking-[0.2em] leading-none">
                                               {lang}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    </div>
  );
};

export default GitHubPreview;
