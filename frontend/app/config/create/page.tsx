'use client';

import { useState } from 'react';
import ConfigEditor from '../../components/ConfigEditor';

export default function ConfigPage() {
  const [isProcessing, setIsProcessing] = useState(false);
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

  const handleSave = async (data: any) => {
    setIsProcessing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/create-config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        alert(`Configuration '${data.name}' saved successfully!`);
      } else {
        const error = await response.json();
        alert(`Failed to save configuration: ${error.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("Error saving config:", error);
      alert("Error connecting to server.");
    } finally {
      setIsProcessing(false);
    }
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

        <ConfigEditor 
          mode="create" 
          onSave={handleSave} 
          isProcessing={isProcessing} 
        />
      </div>
    </main>
  );
}
