'use client';

import React, { useState, useMemo } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

// We will compute unnormalized PDF values inline and numerically normalize them
// to support real-numbered alpha and beta parameters.

export default function BetaDistributionPage() {
  const [cv, setCv] = useState(0);
  const [github, setGithub] = useState(0);
  const [linkedin, setLinkedin] = useState(0);

  const [useCv, setUseCv] = useState(true);
  const [useGithub, setUseGithub] = useState(true);
  const [useLinkedin, setUseLinkedin] = useState(true);

  const [cvUnlocked, setCvUnlocked] = useState(false);
  const [linkedinUnlocked, setLinkedinUnlocked] = useState(false);

  // SVG Icons for Lock/Unlock
  const LockIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
  );
  const UnlockIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 9.9-1"></path></svg>
  );

  const getSliderBg = (val: number, isUnlocked: boolean, color: string, isGithub: boolean = false) => {
    const percent = val * 100;
    if (isGithub || isUnlocked) {
      return `linear-gradient(to right, ${color} ${percent}%, rgba(150, 150, 150, 0.2) ${percent}%)`;
    }
    return `
      linear-gradient(to right, ${color} ${percent}%, transparent ${percent}%),
      linear-gradient(to right, rgba(150, 150, 150, 0.2) 80%, transparent 80%),
      repeating-linear-gradient(45deg, rgba(150, 150, 150, 0.4), rgba(150, 150, 150, 0.4) 4px, rgba(150, 150, 150, 0.1) 4px, rgba(150, 150, 150, 0.1) 8px)
    `;
  };

  // Trust values from constants.py
  const trustGh = 0.9;
  const trustCv = 0.5;
  const trustLi = 0.2;

  // Priors from constants.py
  const priorAlpha = 0.1;
  const priorBeta = 0.1;

  // Alpha and Beta calculations following bayesian.py exact logic
  let alpha = priorAlpha;
  let betaParam = priorBeta;

  const evidences: {strength: number, confidence: number}[] = [];
  if (useGithub) evidences.push({ strength: github / 1.0, confidence: trustGh });
  if (useCv) evidences.push({ strength: cv / 1.0, confidence: trustCv });
  if (useLinkedin) evidences.push({ strength: linkedin / 1.0, confidence: trustLi });

  evidences.forEach(ev => {
    // positive evidence updates
    alpha += ev.strength * ev.confidence;
    betaParam += (1.0 - ev.strength) * ev.confidence;
    
    // add residual noise for uncertainty
    alpha += (1.0 - ev.confidence) * 0.01;
    betaParam += (1.0 - ev.confidence) * 0.01;
  });

  const mean = alpha / (alpha + betaParam);
  const variance = (alpha * betaParam) / (Math.pow(alpha + betaParam, 2) * (alpha + betaParam + 1));
  const stdDev = Math.sqrt(variance);

  // To ensure the graph forms a bell curve (peak in the middle) for visualization, 
  // we scale the parameters so they are > 1. This keeps the mean identical but 
  // forces the math to draw a peak instead of asymptotes at the edges.
  const VISUAL_MULTIPLIER = 20;
  const plotAlpha = alpha * VISUAL_MULTIPLIER;
  const plotBeta = betaParam * VISUAL_MULTIPLIER;

  const HIGH_THRESHOLD = 0.275;
  const MEDIUM_THRESHOLD = 0.35;
  
  let confidenceLabel = "Low Confidence";
  let confidenceColor = "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-900/50";
  
  if (stdDev < HIGH_THRESHOLD) {
    confidenceLabel = "High Confidence";
    confidenceColor = "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-900/50";
  } else if (stdDev < MEDIUM_THRESHOLD) {
    confidenceLabel = "Medium Confidence";
    confidenceColor = "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900/50";
  }

  const data = useMemo(() => {
    const points = [];
    let sum = 0;
    const dx = 1 / 100;
    
    for (let i = 0; i <= 100; i++) {
      const x = i / 100;
      let y = 0;
      // Handle edge cases to avoid Infinity when alpha or beta < 1
      if (x === 0) {
        y = plotAlpha < 1 ? 1000 : (plotAlpha === 1 ? 1 : 0);
      } else if (x === 1) {
        y = plotBeta < 1 ? 1000 : (plotBeta === 1 ? 1 : 0);
      } else {
        y = Math.pow(x, plotAlpha - 1) * Math.pow(1 - x, plotBeta - 1);
      }
      points.push({ x, y });
      
      // Trapezoidal rule summation
      if (i === 0 || i === 100) sum += y / 2;
      else sum += y;
    }
    
    // Normalize so area = 1
    const area = sum * dx;
    for (let i = 0; i <= 100; i++) {
      points[i].y = Number((points[i].y / area).toFixed(4));
      if (points[i].y > 100) points[i].y = 100; // Cap for visualization
      points[i].x = Number(points[i].x.toFixed(2));
    }
    
    return points;
  }, [plotAlpha, plotBeta]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 p-3 rounded-lg shadow-lg">
          <p className="text-zinc-600 dark:text-zinc-300 text-sm mb-1">Score: <span className="font-semibold text-zinc-900 dark:text-zinc-100">{label}</span></p>
          <p className="text-zinc-600 dark:text-zinc-300 text-sm">Density: <span className="font-semibold text-zinc-900 dark:text-zinc-100">{payload[0].value}</span></p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-zinc-50 dark:bg-zinc-950 p-6 md:p-12">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header Section */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
            Bayesian Candidate Scoring
          </h1>
          <p className="text-zinc-500 dark:text-zinc-400 max-w-2xl text-lg">
            Interactive visualization of how evidence from CVs, GitHub, and LinkedIn updates our confidence in a candidate's true capability using a Beta distribution.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Panel: Controls & Stats */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Stats Card */}
            <div className="bg-white dark:bg-zinc-900 rounded-2xl p-6 border border-zinc-200 dark:border-zinc-800 shadow-sm">
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-4">Distribution Stats</h2>
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="bg-zinc-50 dark:bg-zinc-950 p-4 rounded-xl border border-zinc-100 dark:border-zinc-800">
                  <div className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Mean (μ)</div>
                  <div className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">{mean.toFixed(3)}</div>
                </div>
                <div className="bg-zinc-50 dark:bg-zinc-950 p-4 rounded-xl border border-zinc-100 dark:border-zinc-800">
                  <div className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Std Dev (σ)</div>
                  <div className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">{stdDev.toFixed(4)}</div>
                </div>
                <div className="bg-zinc-50 dark:bg-zinc-950 p-4 rounded-xl border border-zinc-100 dark:border-zinc-800">
                  <div className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Variance (σ²)</div>
                  <div className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">{variance.toFixed(4)}</div>
                </div>
                <div className="bg-zinc-50 dark:bg-zinc-950 p-4 rounded-xl border border-zinc-100 dark:border-zinc-800">
                  <div className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Alpha (α)</div>
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{alpha.toFixed(3)}</div>
                </div>
                <div className="bg-zinc-50 dark:bg-zinc-950 p-4 rounded-xl border border-zinc-100 dark:border-zinc-800">
                  <div className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Beta (β)</div>
                  <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">{betaParam.toFixed(3)}</div>
                </div>
                <div className="bg-zinc-50 dark:bg-zinc-950 p-4 rounded-xl border border-zinc-100 dark:border-zinc-800">
                  <div className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Total (α+β)</div>
                  <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{(alpha + betaParam).toFixed(3)}</div>
                </div>
              </div>
              
              <div className={`mt-4 p-4 rounded-xl border flex justify-center items-center ${confidenceColor} transition-colors`}>
                 <span className="font-bold text-lg">{confidenceLabel}</span>
              </div>
            </div>

            {/* Sliders Card */}
            <div className="bg-white dark:bg-zinc-900 rounded-2xl p-6 border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-6">
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2">Evidence Sliders</h2>
              
              {/* CV Slider */}
              <div className={`space-y-3 p-3 rounded-lg border transition-all ${useCv ? 'border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800/50' : 'border-transparent opacity-50 grayscale'}`}>
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <input 
                      type="checkbox" 
                      id="use-cv" 
                      checked={useCv} 
                      onChange={(e) => setUseCv(e.target.checked)} 
                      className="rounded border-zinc-300 dark:border-zinc-600 text-blue-600 focus:ring-blue-600 w-4 h-4 cursor-pointer" 
                    />
                    <label htmlFor="cv-slider" className="text-sm font-medium text-zinc-700 dark:text-zinc-300 cursor-pointer">CV Score (0-1.0)</label>
                  </div>
                  <span className="text-sm font-bold text-zinc-900 dark:text-zinc-100 w-8 text-right">{cv.toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between gap-3 pt-1">
                  <input 
                    id="cv-slider"
                    type="range" 
                    min="0" 
                    max="1.0" 
                    step="0.01"
                    value={cv} 
                    disabled={!useCv}
                    onChange={(e) => {
                      let val = parseFloat(e.target.value);
                      if (!cvUnlocked && val > 0.8) val = 0.8;
                      setCv(val);
                    }}
                    style={{ background: getSliderBg(cv, cvUnlocked, '#2563eb') }}
                    className="w-full h-2 rounded-lg appearance-none cursor-pointer accent-blue-600 disabled:cursor-not-allowed"
                  />
                  <button 
                    onClick={() => {
                      if (cvUnlocked && cv > 0.8) setCv(0.8);
                      setCvUnlocked(!cvUnlocked);
                    }} 
                    disabled={!useCv}
                    className="p-1.5 rounded bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title={cvUnlocked ? "Lock to 0.8 max" : "Unlock full range"}
                  >
                    {cvUnlocked ? <UnlockIcon /> : <LockIcon />}
                  </button>
                </div>
              </div>

              {/* GitHub Slider */}
              <div className={`space-y-3 p-3 rounded-lg border transition-all ${useGithub ? 'border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800/50' : 'border-transparent opacity-50 grayscale'}`}>
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <input 
                      type="checkbox" 
                      id="use-github" 
                      checked={useGithub} 
                      onChange={(e) => setUseGithub(e.target.checked)} 
                      className="rounded border-zinc-300 dark:border-zinc-600 text-indigo-600 focus:ring-indigo-600 w-4 h-4 cursor-pointer" 
                    />
                    <label htmlFor="github-slider" className="text-sm font-medium text-zinc-700 dark:text-zinc-300 cursor-pointer">GitHub Score (0-1.0)</label>
                  </div>
                  <span className="text-sm font-bold text-zinc-900 dark:text-zinc-100 w-8 text-right">{github.toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between gap-3 pt-1">
                  <input 
                    id="github-slider"
                    type="range" 
                    min="0" 
                    max="1.0" 
                    step="0.01"
                    value={github} 
                    disabled={!useGithub}
                    onChange={(e) => setGithub(parseFloat(e.target.value))}
                    style={{ background: getSliderBg(github, true, '#4f46e5', true) }}
                    className="w-full h-2 rounded-lg appearance-none cursor-pointer accent-indigo-600 disabled:cursor-not-allowed"
                  />
                  <div className="p-1.5 w-[26px] opacity-0" aria-hidden="true"></div>
                </div>
              </div>

              {/* LinkedIn Slider */}
              <div className={`space-y-3 p-3 rounded-lg border transition-all ${useLinkedin ? 'border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800/50' : 'border-transparent opacity-50 grayscale'}`}>
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <input 
                      type="checkbox" 
                      id="use-linkedin" 
                      checked={useLinkedin} 
                      onChange={(e) => setUseLinkedin(e.target.checked)} 
                      className="rounded border-zinc-300 dark:border-zinc-600 text-purple-600 focus:ring-purple-600 w-4 h-4 cursor-pointer" 
                    />
                    <label htmlFor="linkedin-slider" className="text-sm font-medium text-zinc-700 dark:text-zinc-300 cursor-pointer">LinkedIn Score (0-1.0)</label>
                  </div>
                  <span className="text-sm font-bold text-zinc-900 dark:text-zinc-100 w-8 text-right">{linkedin.toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between gap-3 pt-1">
                  <input 
                    id="linkedin-slider"
                    type="range" 
                    min="0" 
                    max="1.0" 
                    step="0.01"
                    value={linkedin} 
                    disabled={!useLinkedin}
                    onChange={(e) => {
                      let val = parseFloat(e.target.value);
                      if (!linkedinUnlocked && val > 0.8) val = 0.8;
                      setLinkedin(parseFloat(val.toFixed(2)));
                    }}
                    style={{ background: getSliderBg(linkedin, linkedinUnlocked, '#9333ea') }}
                    className="w-full h-2 rounded-lg appearance-none cursor-pointer accent-purple-600 disabled:cursor-not-allowed"
                  />
                  <button 
                    onClick={() => {
                      if (linkedinUnlocked && linkedin > 0.8) setLinkedin(0.8);
                      setLinkedinUnlocked(!linkedinUnlocked);
                    }} 
                    disabled={!useLinkedin}
                    className="p-1.5 rounded bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title={linkedinUnlocked ? "Lock to 0.8 max" : "Unlock full range"}
                  >
                    {linkedinUnlocked ? <UnlockIcon /> : <LockIcon />}
                  </button>
                </div>
              </div>
              
            </div>

            {/* Confidence Thresholds Info */}
            <div className="bg-white dark:bg-zinc-900 rounded-2xl p-6 border border-zinc-200 dark:border-zinc-800 shadow-sm">
              <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 mb-3">Confidence Mapping (Std Dev)</h2>
              <div className="space-y-2 text-sm text-zinc-600 dark:text-zinc-400">
                <div className="flex justify-between">
                  <span className="flex items-center"><span className="w-2 h-2 rounded-full bg-emerald-500 mr-2"></span>High</span>
                  <span className="font-mono">σ &lt; 0.275</span>
                </div>
                <div className="flex justify-between">
                  <span className="flex items-center"><span className="w-2 h-2 rounded-full bg-amber-500 mr-2"></span>Medium</span>
                  <span className="font-mono">0.275 ≤ σ &lt; 0.350</span>
                </div>
                <div className="flex justify-between">
                  <span className="flex items-center"><span className="w-2 h-2 rounded-full bg-red-500 mr-2"></span>Low</span>
                  <span className="font-mono">σ ≥ 0.350</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel: Chart */}
          <div className="lg:col-span-8">
            <div className="bg-white dark:bg-zinc-900 rounded-2xl p-6 border border-zinc-200 dark:border-zinc-800 shadow-sm h-full min-h-[500px] flex flex-col">
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-6">Probability Density Function</h2>
              <div className="flex-grow w-full h-full relative min-h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={data}
                    margin={{
                      top: 10,
                      right: 30,
                      left: 0,
                      bottom: 0,
                    }}
                  >
                    <defs>
                      <linearGradient id="colorPdf" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#52525b" strokeOpacity={0.2} />
                    <XAxis 
                      dataKey="x" 
                      type="number" 
                      domain={[0, 1]} 
                      ticks={[0, 0.2, 0.4, 0.6, 0.8, 1.0]} 
                      stroke="#71717a"
                      tick={{ fill: '#71717a' }}
                      tickMargin={10}
                    />
                    <YAxis 
                      stroke="#71717a"
                      tick={{ fill: '#71717a' }}
                      tickMargin={10}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <ReferenceLine x={mean} stroke="#ef4444" strokeDasharray="5 5" label={{ position: 'top', value: 'Mean', fill: '#ef4444', fontSize: 12 }} />
                    <Area 
                      type="monotone" 
                      dataKey="y" 
                      stroke="#3b82f6" 
                      strokeWidth={3}
                      fillOpacity={1} 
                      fill="url(#colorPdf)" 
                      animationDuration={300}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
}
