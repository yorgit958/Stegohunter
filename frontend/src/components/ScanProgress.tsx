import React, { useEffect, useState } from 'react';
import { Loader2, Fingerprint, Database, Cpu, Activity, Search } from 'lucide-react';

interface ScanProgressProps {
  fileName: string;
}

const ScanProgress: React.FC<ScanProgressProps> = ({ fileName }) => {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    { name: "Initializing models", icon: Database },
    { name: "Extracting LSB features", icon: Fingerprint },
    { name: "Running DCT analysis", icon: Activity },
    { name: "Executing CNN inference", icon: Cpu },
    { name: "Aggregating ensemble score", icon: Search },
  ];

  // Simulated progress animation since the backend API is synchronous
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 2500); // Progress every 2.5s

    return () => clearInterval(timer);
  }, [steps.length]);

  return (
    <div className="w-full max-w-xl mx-auto border border-white/10 bg-black/40 backdrop-blur-md rounded-xl p-8 shadow-2xl">
      <div className="text-center mb-10">
        <div className="relative inline-block">
          <div className="absolute inset-0 border-[3px] border-primary/20 rounded-full animate-ping opacity-20" style={{ animationDuration: '3s' }}></div>
          <div className="bg-primary/10 p-4 rounded-full border border-primary/30 relative">
            <Loader2 className="w-12 h-12 text-primary animate-spin" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-white mt-6 mb-2">Analyzing Image</h2>
        <p className="text-white/50 truncate max-w-xs mx-auto">{fileName}</p>
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isActive = index === activeStep;
          const isPast = index < activeStep;
          const isPending = index > activeStep;

          return (
            <div 
              key={step.name} 
              className={`flex items-center gap-4 p-3 rounded-lg transition-all duration-300 ${
                isActive ? 'bg-primary/10 border border-primary/30' : 
                isPast ? 'opacity-60' : 'opacity-30'
              }`}
            >
              <div className={`p-2 rounded-full ${
                isActive ? 'bg-primary/20 text-primary animate-pulse' : 
                isPast ? 'bg-green-500/20 text-green-400' : 'bg-white/5 text-white'
              }`}>
                <Icon className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <span className={`font-medium ${
                  isActive ? 'text-primary' : 
                  isPast ? 'text-green-400' : 'text-white'
                }`}>
                  {step.name}
                </span>
                {isActive && (
                  <div className="w-full bg-black/50 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div className="bg-primary h-full animate-[progress_2.5s_ease-in-out_infinite] w-1/2 rounded-full"></div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      
      <p className="text-center mt-8 text-sm text-primary/80 animate-pulse">
        Running distributed ensemble... This may take up to 30 seconds.
      </p>
    </div>
  );
};

export default ScanProgress;
