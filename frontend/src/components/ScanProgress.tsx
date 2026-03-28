import React, { useEffect, useState, useRef } from 'react';
import { Loader2, Fingerprint, Database, Cpu, Activity, Search, CheckCircle2, XCircle } from 'lucide-react';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8005';

interface ScanProgressProps {
  fileName: string;
  scanJobId?: string | null;
  onComplete?: (jobId: string) => void;
  onError?: (error: string) => void;
}

const ScanProgress: React.FC<ScanProgressProps> = ({ fileName, scanJobId, onComplete, onError }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [currentLabel, setCurrentLabel] = useState("Initializing models");
  const [status, setStatus] = useState<'connecting' | 'in_progress' | 'completed' | 'error'>('connecting');
  const wsRef = useRef<WebSocket | null>(null);
  const fallbackTimerRef = useRef<NodeJS.Timeout | null>(null);

  const steps = [
    { name: "Uploading to secure storage", icon: Database },
    { name: "Running AI analysis engines", icon: Fingerprint },
    { name: "Storing analysis results", icon: Activity },
    { name: "Finalizing report", icon: Cpu },
    { name: "Scan complete", icon: Search },
  ];

  useEffect(() => {
    if (!scanJobId) {
      // No job ID yet — use a gentle animation while waiting
      fallbackTimerRef.current = setInterval(() => {
        setActiveStep((prev) => (prev < 1 ? prev + 1 : prev));
      }, 3000);
      return () => {
        if (fallbackTimerRef.current) clearInterval(fallbackTimerRef.current);
      };
    }

    // Get user ID from auth storage for WebSocket routing
    let userId = 'anonymous';
    try {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const parsed = JSON.parse(authStorage);
        userId = parsed?.state?.user?.id || 'anonymous';
      }
    } catch { /* ignore */ }

    // Establish WebSocket connection
    const wsUrl = `${WS_BASE_URL}/ws/${userId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('in_progress');
      console.log('[WebSocket] Connected to Notification Service');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'scan_progress' && data.scan_job_id === scanJobId) {
          setActiveStep(data.step_index);
          setCurrentLabel(data.step);

          if (data.status === 'completed') {
            setStatus('completed');
            // Small delay to let the user see the "complete" state
            setTimeout(() => {
              onComplete?.(scanJobId);
            }, 1500);
          } else if (data.status === 'error') {
            setStatus('error');
            onError?.(data.step || 'Analysis failed');
          }
        }
      } catch (e) {
        console.error('[WebSocket] Parse error:', e);
      }
    };

    ws.onerror = () => {
      console.warn('[WebSocket] Connection error — falling back to polling.');
      setStatus('in_progress');
      // Fallback: poll the job status if WebSocket fails
      startPollingFallback(scanJobId, userId);
    };

    ws.onclose = () => {
      console.log('[WebSocket] Connection closed');
    };

    // Keep-alive ping every 30 seconds
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
      }
    }, 30000);

    return () => {
      clearInterval(pingInterval);
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    };
  }, [scanJobId]);

  const startPollingFallback = async (jobId: string, _userId: string) => {
    // If WebSocket fails, poll the Gateway for job status every 3 seconds
    const { scanApi } = await import('../lib/api');
    const poll = setInterval(async () => {
      try {
        const data = await scanApi.getJob(jobId);
        if (data.job?.status === 'completed') {
          clearInterval(poll);
          setStatus('completed');
          setActiveStep(4);
          setTimeout(() => onComplete?.(jobId), 1500);
        } else if (data.job?.status === 'failed') {
          clearInterval(poll);
          setStatus('error');
          onError?.(data.job?.error_message || 'Scan failed');
        }
      } catch { /* retry silently */ }
    }, 3000);

    fallbackTimerRef.current = poll;
    return () => clearInterval(poll);
  };

  return (
    <div className="w-full max-w-xl mx-auto border border-white/10 bg-black/40 backdrop-blur-md rounded-xl p-8 shadow-2xl">
      <div className="text-center mb-10">
        <div className="relative inline-block">
          <div className="absolute inset-0 border-[3px] border-primary/20 rounded-full animate-ping opacity-20" style={{ animationDuration: '3s' }}></div>
          <div className="bg-primary/10 p-4 rounded-full border border-primary/30 relative">
            {status === 'completed' ? (
              <CheckCircle2 className="w-12 h-12 text-green-400" />
            ) : status === 'error' ? (
              <XCircle className="w-12 h-12 text-red-400" />
            ) : (
              <Loader2 className="w-12 h-12 text-primary animate-spin" />
            )}
          </div>
        </div>
        <h2 className="text-2xl font-bold text-white mt-6 mb-2">
          {status === 'completed' ? 'Analysis Complete' : status === 'error' ? 'Analysis Failed' : 'Analyzing Image'}
        </h2>
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
                {isPast ? <CheckCircle2 className="w-5 h-5" /> : <Icon className="w-5 h-5" />}
              </div>
              <div className="flex-1">
                <span className={`font-medium ${
                  isActive ? 'text-primary' : 
                  isPast ? 'text-green-400' : 'text-white'
                }`}>
                  {isActive ? currentLabel : step.name}
                </span>
                {isActive && status === 'in_progress' && (
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
        {status === 'connecting' ? 'Connecting to notification server...' :
         status === 'completed' ? 'Redirecting to results...' :
         status === 'error' ? 'An error occurred during analysis.' :
         'Live progress via WebSocket — updates are real-time.'}
      </p>
    </div>
  );
};

export default ScanProgress;
