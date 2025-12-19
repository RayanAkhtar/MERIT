import React from 'react';

interface LinkSelectionProps {
  metrics: {
    uploaded_files: number;
    link_counts: Record<string, number>;
  };
  selectedLinks: Record<string, boolean>;
  setSelectedLinks: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
}

const LinkSelection: React.FC<LinkSelectionProps> = ({ metrics, selectedLinks, setSelectedLinks }) => {
  return (
    <div>
      <h4 className="text-md font-medium text-zinc-800 dark:text-zinc-200 mb-4">
        Which datasources would you like to use?
      </h4>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        
        {/* Box for CV count */}
        <div
          className={`
            p-4 rounded-lg border text-center transition-all duration-200 transform cursor-pointer
            ${selectedLinks['cv'] 
              ? 'bg-blue-600 text-white scale-105 shadow-lg' 
              : 'bg-white text-zinc-900 dark:bg-zinc-900 dark:text-zinc-50 hover:bg-blue-100 dark:hover:bg-blue-900 hover:text-blue-600'}
          `}
          onClick={() =>
            setSelectedLinks((prev) => ({
              ...prev,
              cv: !prev.cv,
            }))
          }
        >
          <p className="text-sm font-medium capitalize">cv</p>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
            {metrics.uploaded_files} {metrics.uploaded_files === 1 ? 'file' : 'files'}
          </p>
        </div>

        {Object.entries(metrics.link_counts).map(([link, count]) => (
          <div
            key={link}
            className={`
              p-4 rounded-lg border text-center transition-all duration-200 transform cursor-pointer
              ${link === 'other' 
                ? 'bg-zinc-200 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-500 cursor-not-allowed' 
                : selectedLinks[link] 
                ? 'bg-blue-600 text-white scale-105 shadow-lg' 
                : 'bg-white text-zinc-900 dark:bg-zinc-900 dark:text-zinc-50 hover:bg-blue-100 dark:hover:bg-blue-900 hover:text-blue-600'}
            `}
            onClick={() =>
              setSelectedLinks((prev) => ({
                ...prev,
                [link]: !prev[link],
              }))
            }
          >
            <p className="text-sm font-medium capitalize">{link}</p>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
              {count} {count === 1 ? 'file' : 'files'}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LinkSelection;