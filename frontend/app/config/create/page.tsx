'use client';

import { useState, useEffect } from 'react';

export default function ConfigPage() {
  const [selectedReq, setSelectedReq] = useState('');
  const [selectedBatch, setSelectedBatch] = useState('');
  const [configName, setConfigName] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showReqModal, setShowReqModal] = useState(false);

  // 0 = Least Important, 1 = Most Important
  const [importance, setImportance] = useState<Record<string, number>>({});
  const [activeMetrics, setActiveMetrics] = useState<Record<string, boolean>>({});

  // temporary data to replace
  const availableRequirements = [
    { 
      id: "req_1", 
      title: "Senior Machine Learning Engineer", 
      date: "2026-03-20",
      preview: "Seeking an experienced ML Engineer to lead our NLP initiatives. Expected to build and scale LLM pipelines.",
      jobLevel: "Senior",
      experience: "5+ Years",
      techStack: [
        { language: "Python", skills: ["PyTorch", "FastAPI", "Transformers", "LangChain"] },
        { language: "C++", skills: ["CUDA", "TensorRT", "Performance Tuning"] }
      ],
      fullDescription: `Role Overview:
As a Senior Machine Learning Engineer, you will lead the design, development, and deployment of Natural Language Processing (NLP) models. You will be responsible for scaling our AI infrastructure and ensuring high-performance model execution in production environments.

Key Responsibilities:
• Design and train large language models and transformer-based architectures.
• Implement efficient MLOps pipelines (Docker, Kubernetes) for continuous model deployment.
• Mentor junior engineers and collaborate with data scientists to optimize algorithms.
• Ensure model security, fairness, and strict data privacy compliance.

Required Qualifications:
• 5+ years of hands-on experience in machine learning software engineering.
• Deep expertise in Python, PyTorch, and standard ML libraries.
• Experience with distributed computing frameworks (Ray, Spark).`,
      additionalMeasures: [
        { name: "System Design", sources: ["CV", "GitHub"] },
        { name: "Mentorship Experience", sources: ["CV", "LinkedIn"] }
      ]
    },
    { 
      id: "req_2", 
      title: "Frontend Developer (React/NextJS)", 
      date: "2026-03-24",
      preview: "We process thousands of events per second. Need a React expert to build our real-time dashboard.",
      jobLevel: "Mid-Level",
      experience: "3+ Years",
      techStack: [
        { language: "TypeScript", skills: ["React", "Next.js", "Redux", "Zustand"] },
        { language: "CSS/HTML", skills: ["Tailwind CSS", "Accessibility"] }
      ],
      fullDescription: `Role Overview:
We are looking for a dedicated Frontend Developer to join our core product team. You will be building high-performance, real-time dashboards used by thousands of clients simultaneously.

Key Responsibilities:
• Build scalable frontend architectures using React and Next.js.
• State management optimization and minimizing unnecessary re-renders.
• Translating UI/UX wireframes into responsive, high-fidelity Tailwind CSS components.
• Connecting to real-time WebSockets securely.

Required Qualifications:
• 3+ years of professional frontend development using React.
• Exceptional TypeScript proficiency.
• Deep understanding of browser APIs, CSS architecture, and accessibility standards.`,
      additionalMeasures: [
        { name: "UI/UX Sensitivity", sources: ["CV", "GitHub"] },
        { name: "Open Source Contributions", sources: ["GitHub", "LinkedIn"] }
      ]
    },
    { 
      id: "req_3", 
      title: "Data Scientist Intern", 
      date: "2026-03-25",
      preview: "Summer internship position for quantitative analysis and predictive modeling. Basic ML knowledge needed.",
      jobLevel: "Internship",
      experience: "Currently Enrolled",
      techStack: [
        { language: "Python", skills: ["Pandas", "Scikit-Learn"] },
        { language: "SQL", "skills": ["PostgreSQL"] }
      ],
      fullDescription: `Role Overview:
Join our data science team for a 12-week summer internship where you will work on real-world predictive modeling and exploratory data analysis.

Key Responsibilities:
• Clean and transform large datasets using pandas and SQL.
• Assist senior data scientists in A/B testing setup and statistical analysis.
• Present data findings to non-technical stakeholders using clear visualizations.

Required Qualifications:
• Currently enrolled in a BSc/MSc in Computer Science, Statistics, Mathematics, or related field.
• Ability to code proficiently in Python and SQL.
• Knowledge of fundamental statistical concepts (p-values, distributions, regression).`,
      additionalMeasures: [
        { name: "Academic Excellence", sources: ["CV"] },
        { name: "Extracurricular Projects", sources: ["CV", "GitHub"] }
      ]
    }
  ];

  const availableBatches = [
    { 
      id: "batch_1", 
      name: "Batch A - Graduate Fair 2026", 
      count: 45,
      preview: "A collection of CVs sourced from the university Spring career fair. Predominantly fresh graduates looking for entry-level and internship roles.",
      sampleCandidates: ["Alice Johnson", "Bob Smith", "Charlie Lee"],
      additionalMeasures: [
        { name: "University Ranking", sources: ["CV", "LinkedIn"] },
        { name: "Degree Classification", sources: ["CV"] },
        { name: "Side Projects", sources: ["CV", "GitHub"] }
      ]
    },
    { 
      id: "batch_2", 
      name: "Batch B - LinkedIn Sourcing", 
      count: 12,
      preview: "Highly targeted Senior profiles directly engaged through LinkedIn Recruiter. Focus is heavily on experienced hires.",
      sampleCandidates: ["Diana Prince", "Eve Adams", "Frank Castle"],
      additionalMeasures: [
        { name: "Company Prestige", sources: ["CV", "LinkedIn"] },
        { name: "Management History", sources: ["LinkedIn"] },
        { name: "Technical Endorsements", sources: ["LinkedIn", "GitHub"] },
        { name: "Open Source Contributions", sources: ["GitHub", "LinkedIn"] }
      ]
    },
    { 
      id: "batch_3", 
      name: "Batch C - Direct Applications", 
      count: 104,
      preview: "Inbound applications across multiple departments collected over the past 30 days via our careers page.",
      sampleCandidates: ["George Hill", "Hannah Abbott", "Ivan Drago"],
      additionalMeasures: [
        { name: "Cover Letter Quality", sources: ["CV"] },
        { name: "Domain Experience", sources: ["CV", "LinkedIn"] },
        { name: "Full Developer Profile", sources: ["CV", "LinkedIn", "GitHub"] }
      ]
    }
  ];

  const reqPreviewData = availableRequirements.find(r => r.id === selectedReq);
  const batchPreviewData = availableBatches.find(b => b.id === selectedBatch);

  // Hard-Coded criteria, often common in almost all ATS systems
  const baseCriteria: { key: string; label: string; source?: string; subSources?: string[] }[] = [
    { key: 'techSkills', label: 'Technical Skills & Environments' },
    { key: 'experience', label: 'Total Years of Experience' },
    { key: 'jobLevel', label: 'Job Level / Seniority Trajectory' },
    { key: 'spokenLanguages', label: 'Spoken / Human Languages' },
  ];

  // Additional measures that are unique to the Job Description
  const reqAdditional: { key: string; label: string; source: string; subSources?: string[] }[] = (reqPreviewData?.additionalMeasures || []).map(measure => ({
    key: `req_${measure.name.replace(/[^a-zA-Z0-9]/g, '_')}`,
    label: measure.name,
    source: 'Job Description'
  }));

  // Additional measures that are unique to the Candidate Batch
  const batchAdditional = (batchPreviewData?.additionalMeasures || []).map(measure => ({
    key: `batch_${measure.name.replace(/[^a-zA-Z0-9]/g, '_')}`,
    label: measure.name,
    source: 'Candidate Data',
    subSources: measure.sources,
  }));
  
  const allCriteria = [...baseCriteria, ...reqAdditional, ...batchAdditional];

  // Initialize or cleanup importance state when dynamic criteria change
  useEffect(() => {
    setImportance(prev => {
      const newState = { ...prev };
      // Assign 0.5 to any new keys by default
      allCriteria.forEach(c => {
        if (newState[c.key] === undefined) {
          newState[c.key] = 0.5;
        }
      });
      return newState;
    });
    setActiveMetrics(prev => {
      const newState = { ...prev };
      allCriteria.forEach(c => {
        if (newState[c.key] === undefined) {
          newState[c.key] = true;
        }
      });
      return newState;
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedReq, selectedBatch]);

  // Helper check for fully populated importance ratings
  const allRatingsSet = allCriteria.every(item => 
    !activeMetrics[item.key] || importance[item.key] !== undefined
  );

  const handleRunMatch = () => {
    if (!selectedReq || !selectedBatch || !allRatingsSet || !configName.trim()) return;
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      alert(`Configuration '${configName}' saved successfully!`);
    }, 1500);
  };

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 px-4 py-12 md:py-16 relative">
      <div className="max-w-4xl mx-auto space-y-8">
        
        <div>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 tracking-tight">Create Configuration</h1>
          <p className="mt-2 text-zinc-600 dark:text-zinc-400">
            Design a new matching configuration.
          </p>
        </div>

        <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden flex flex-col">
          <div className="p-6 md:p-8 space-y-8 flex-1">
            
            {/* Job Description Selection */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 text-xs font-bold ring-1 ring-indigo-200 dark:ring-indigo-800">1</span>
                Select Job Description
              </h2>
              
              <div className="grid md:grid-cols-2 gap-4 items-start">
                <div className="bg-zinc-50 dark:bg-zinc-950/50 p-4 border border-zinc-200 dark:border-zinc-800 rounded-lg">
                  <select
                    value={selectedReq}
                    onChange={(e) => setSelectedReq(e.target.value)}
                    className="w-full bg-white dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 rounded-md py-2.5 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 mb-2"
                  >
                    <option value="" disabled>-- Choose a Job Description --</option>
                    {availableRequirements.map((req) => (
                      <option key={req.id} value={req.id}>
                        {req.title}
                      </option>
                    ))}
                  </select>
                </div>

                {reqPreviewData && (
                  <div className="bg-indigo-50 dark:bg-indigo-950/20 p-5 border border-indigo-100 dark:border-indigo-900/50 rounded-lg text-sm transition-all animate-in fade-in slide-in-from-top-2 relative">
                    <h3 className="font-semibold text-indigo-900 dark:text-indigo-300 mb-3">Requirement Details</h3>
                    
                    <div className="grid grid-cols-2 gap-y-2 gap-x-4 mb-4 text-xs border-b border-indigo-100 dark:border-indigo-900/50 pb-3">
                      <div>
                        <span className="block text-indigo-600/70 dark:text-indigo-400/70 font-medium">Job Level</span>
                        <span className="font-semibold text-zinc-900 dark:text-zinc-100">{reqPreviewData.jobLevel}</span>
                      </div>
                      <div>
                        <span className="block text-indigo-600/70 dark:text-indigo-400/70 font-medium">Experience</span>
                        <span className="font-semibold text-zinc-900 dark:text-zinc-100">{reqPreviewData.experience}</span>
                      </div>
                    </div>

                    <div className="mb-4">
                      <span className="block text-indigo-600/70 dark:text-indigo-400/70 font-medium text-xs mb-1.5">Primary Languages</span>
                      <div className="flex flex-wrap gap-1.5">
                        {reqPreviewData.techStack.map(stack => (
                          <span key={stack.language} className="px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-800 dark:text-indigo-300 rounded font-semibold text-xs border border-indigo-200 dark:border-indigo-800">
                            {stack.language}
                          </span>
                        ))}
                      </div>
                    </div>

                    <p className="text-zinc-700 dark:text-zinc-300 mb-4 leading-relaxed line-clamp-2">
                      {reqPreviewData.preview}
                    </p>
                    
                    <button 
                      onClick={() => setShowReqModal(true)}
                      className="text-indigo-600 dark:text-indigo-400 text-xs font-semibold hover:underline flex items-center gap-1"
                    >
                      View Full Requirements
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </button>
                  </div>
                )}
              </div>
            </div>

            <hr className="border-zinc-200 dark:border-zinc-800" />

            {/* Candidate Batch Selection */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 text-xs font-bold ring-1 ring-blue-200 dark:ring-blue-800">2</span>
                Select Candidate Batch
              </h2>
              
              <div className="grid md:grid-cols-2 gap-4 items-start">
                <div className="bg-zinc-50 dark:bg-zinc-950/50 p-4 border border-zinc-200 dark:border-zinc-800 rounded-lg">
                  <select
                    value={selectedBatch}
                    onChange={(e) => setSelectedBatch(e.target.value)}
                    className="w-full bg-white dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 rounded-md py-2.5 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 mb-2"
                  >
                    <option value="" disabled>-- Choose a Candidate Batch --</option>
                    {availableBatches.map((batch) => (
                      <option key={batch.id} value={batch.id}>
                        {batch.name} ({batch.count} CVs)
                      </option>
                    ))}
                  </select>
                </div>

                {batchPreviewData && (
                  <div className="bg-blue-50 dark:bg-blue-950/20 p-4 border border-blue-100 dark:border-blue-900/50 rounded-lg text-sm transition-all animate-in fade-in slide-in-from-top-2">
                    <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">Batch Details</h3>
                    <p className="text-zinc-700 dark:text-zinc-300 mb-3 leading-relaxed">
                      {batchPreviewData.preview}
                    </p>
                    <div className="text-xs text-zinc-500 dark:text-zinc-400">
                      <p className="font-semibold mb-1 text-zinc-900 dark:text-zinc-200">Sample Candidates:</p>
                      <ul className="list-disc list-inside space-y-0.5">
                        {batchPreviewData.sampleCandidates.map(c => <li key={c}>{c}</li>)}
                        {batchPreviewData.count > 3 && <li>...and {batchPreviewData.count - 3} more</li>}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Criteria Prioritization once a job description and candidate batch are selected */}
            {selectedReq && selectedBatch && (
              <>
                <hr className="border-zinc-200 dark:border-zinc-800" />
                <div className="space-y-4 animate-in fade-in slide-in-from-top-4 duration-500">
                  <div>
                    <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-400 text-xs font-bold ring-1 ring-green-200 dark:ring-green-800">3</span>
                      Prioritize Matching Criteria
                    </h2>
                    <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400 ml-8">
                      Weight these criteria from <strong className="text-zinc-900 dark:text-zinc-200">0.0 (Ignore)</strong> to <strong className="text-zinc-900 dark:text-zinc-200">1.0 (Highest Priority)</strong>. Includes custom measures pulled from your selected Job Description and Candidate batch.
                    </p>
                  </div>

                  <div className="ml-8 bg-zinc-50 dark:bg-zinc-950/50 p-6 border border-zinc-200 dark:border-zinc-800 rounded-lg">
                    <div className="space-y-6">
                      {allCriteria.map((item) => {
                        const isDynamic = !!item.source;
                        const isActive = activeMetrics[item.key] ?? true;
                        return (
                          <div key={item.key} className={`flex flex-col md:flex-row md:items-center justify-between gap-4 py-3 border-b border-zinc-200 dark:border-zinc-800 last:border-0 last:pb-0 ${!isActive ? 'opacity-40 grayscale' : ''} ${isDynamic ? 'bg-indigo-50/50 dark:bg-indigo-900/10 -mx-4 px-4 rounded-md' : ''}`}>
                            <div className="flex flex-col gap-1.5">
                              <label className="flex items-center gap-3 cursor-pointer group">
                                <input 
                                  type="checkbox" 
                                  checked={isActive} 
                                  onChange={(e) => setActiveMetrics({ ...activeMetrics, [item.key]: e.target.checked })}
                                  className="w-4 h-4 rounded border-zinc-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                                />
                                <span className="text-sm font-medium text-zinc-900 dark:text-zinc-200 flex flex-wrap items-center gap-2 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                                  <span className={!isActive ? 'line-through' : ''}>{item.label}</span>
                                  {!item.source && <span className="px-2 py-0.5 text-[10px] uppercase font-bold bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 rounded-md">Base Standard</span>}
                                  {item.source && item.source !== 'Candidate Data' && <span className="px-2 py-0.5 text-[10px] uppercase font-bold bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300 rounded-md">{item.source}</span>}
                                  {item.subSources && <span className="px-2 py-0.5 text-[10px] uppercase font-bold bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded-md">Candidate: {item.subSources.join(', ')}</span>}
                                </span>
                              </label>
                            </div>
                            
                            {isActive && (
                              <div className="flex flex-col gap-2 w-full md:w-64 self-start md:self-auto bg-white dark:bg-zinc-900 p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-sm animate-in fade-in slide-in-from-right-2">
                                <div className="flex items-center justify-between text-xs font-semibold">
                                  <span className="text-zinc-500 dark:text-zinc-400 font-mono">0.0</span>
                                  <span className="text-indigo-700 dark:text-indigo-400 font-mono bg-indigo-50 dark:bg-indigo-900/30 px-2.5 py-0.5 rounded border border-indigo-100 dark:border-indigo-800/50">
                                     W: {importance[item.key] !== undefined ? importance[item.key].toFixed(2) : '0.50'}
                                  </span>
                                  <span className="text-zinc-700 dark:text-zinc-300 font-mono">1.0</span>
                                </div>
                                <input 
                                   type="range"
                                   min="0"
                                   max="1"
                                   step="0.01"
                                   value={importance[item.key] !== undefined ? importance[item.key] : 0.5}
                                   onChange={(e) => setImportance({ ...importance, [item.key]: parseFloat(e.target.value) })}
                                   className="w-full h-1.5 bg-zinc-200 dark:bg-zinc-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                                />
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </>
            )}

          </div>

          {/* Action Footer with Config Naming */}
          <div className="px-6 py-4 bg-zinc-50 dark:bg-zinc-800/50 border-t border-zinc-200 dark:border-zinc-800 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="w-full md:w-auto flex-1 max-w-sm flex items-center gap-3">
              <label htmlFor="configName" className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 whitespace-nowrap">
                Config Name
              </label>
              <input 
                id="configName"
                type="text" 
                placeholder="e.g. Senior ML Grad Protocol" 
                value={configName}
                onChange={(e) => setConfigName(e.target.value)}
                className="w-full bg-white dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            
            <button
              onClick={handleRunMatch}
              disabled={!selectedReq || !selectedBatch || !allRatingsSet || !configName.trim() || isProcessing}
              className={`
                w-full md:w-auto px-6 py-2.5 rounded-md font-medium text-white transition-all shadow-sm
                flex items-center justify-center gap-2
                ${(!selectedReq || !selectedBatch || !allRatingsSet || !configName.trim() || isProcessing)
                  ? 'bg-zinc-300 dark:bg-zinc-700 text-zinc-500 dark:text-zinc-400 cursor-not-allowed hidden-shadow'
                  : 'bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-white active:scale-95'
                }
              `}
            >
              {isProcessing ? (
                <>
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Saving Config...
                </>
              ) : (
                'Save Configuration'
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Full Requirement Details Modal */}
      {showReqModal && reqPreviewData && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 dark:bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div 
            className="bg-white dark:bg-zinc-900 rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden border border-zinc-200 dark:border-zinc-800 transform animate-in slide-in-from-bottom-10"
            role="dialog"
          >
            <div className="flex justify-between items-center p-6 border-b border-zinc-100 dark:border-zinc-800">
              <h2 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
                {reqPreviewData.title}
              </h2>
              <button 
                onClick={() => setShowReqModal(false)}
                className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition-colors p-1"
                aria-label="Close dialog"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="flex flex-wrap gap-2 mb-6">
                <span className="px-3 py-1 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 rounded-full text-xs font-semibold border border-indigo-100 dark:border-indigo-800/50">
                  {reqPreviewData.jobLevel}
                </span>
                <span className="px-3 py-1 bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 rounded-full text-xs font-medium border border-zinc-200 dark:border-zinc-700">
                  Experience: {reqPreviewData.experience}
                </span>
              </div>

              <div className="mb-6">
                <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 mb-4 border-b border-zinc-100 dark:border-zinc-800 pb-2">Technical Skills & Environments</h3>
                <div className="space-y-4">
                  {reqPreviewData.techStack.map((stack) => (
                    <div key={stack.language} className="flex flex-col sm:flex-row sm:items-baseline gap-2 sm:gap-4">
                      <span className="w-24 flex-shrink-0 font-semibold text-indigo-700 dark:text-indigo-400 text-sm">
                        {stack.language}
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {stack.skills.map((skill) => (
                          <span key={skill} className="px-2 py-1 bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-800 dark:text-zinc-200 rounded text-xs font-medium">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 mb-3 border-b border-zinc-100 dark:border-zinc-800 pb-2">Full Description</h3>
                <div className="text-sm text-zinc-600 dark:text-zinc-400 whitespace-pre-wrap leading-relaxed">
                  {reqPreviewData.fullDescription}
                </div>
              </div>
            </div>

            <div className="p-4 bg-zinc-50 dark:bg-zinc-800/50 border-t border-zinc-100 dark:border-zinc-800 text-right flex justify-end">
              <button 
                onClick={() => setShowReqModal(false)}
                className="px-5 py-2 bg-white dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-md font-medium text-sm hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
