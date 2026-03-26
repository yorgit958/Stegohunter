import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { scanApi } from '../lib/api';
import { 
  ShieldCheck, ShieldAlert, ShieldX, AlertTriangle, 
  ArrowLeft, FileImage, Shield, Cpu, Clock, Activity 
} from 'lucide-react';
import { Button } from '../components/ui/button';

const ScanResultPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const routerFile = location.state?.file as File | undefined;
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const fetchResults = async () => {
      if (!id) return;
      try {
        const response = await scanApi.getJob(id);
        setData(response);
      } catch (err: any) {
        console.error("Error fetching job:", err);
        setError(err.response?.data?.detail || "Failed to load scan results.");
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin text-primary w-10 h-10 border-4 border-current border-t-transparent rounded-full" />
      </div>
    );
  }

  if (error || !data || !data.job) {
    return (
      <div className="container mx-auto py-12 px-4 flex flex-col items-center">
        <div className="bg-red-500/10 border border-red-500/30 p-6 rounded-lg max-w-lg text-center">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-red-200 mb-2">Result Not Found</h2>
          <p className="text-red-200/80 mb-6">{error || "The scan job could not be retrieved."}</p>
          <Button onClick={() => navigate('/scan')} variant="outline" className="border-red-500/30 hover:bg-red-500/20 text-red-200">
            Start New Scan
          </Button>
        </div>
      </div>
    );
  }

  const { job, results } = data;
  const result = results?.[0]; // Get the most recent/only result
  
  // Danger formatting
  const isThreat = result?.is_stego;
  const threatLevel = result?.threat_level || 'none';
  
  const getThreatColor = (level: string) => {
    switch(level) {
      case 'critical': return 'text-red-500 bg-red-500/10 border-red-500/30';
      case 'high': return 'text-orange-500 bg-orange-500/10 border-orange-500/30';
      case 'medium': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30';
      case 'low': return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
      default: return 'text-green-500 bg-green-500/10 border-green-500/30';
    }
  };

  const getThreatIcon = (level: string) => {
    switch(level) {
      case 'critical': 
      case 'high': return <ShieldX className="w-12 h-12 text-red-500" />;
      case 'medium': return <ShieldAlert className="w-12 h-12 text-yellow-500" />;
      default: return <ShieldCheck className="w-12 h-12 text-green-500" />;
    }
  };

  const threatColor = getThreatColor(threatLevel);
  const scoreRaw = result?.metadata?.ensemble_score || 0;
  const scorePercent = (scoreRaw * 100).toFixed(1);

  return (
    <div className="container mx-auto max-w-6xl py-8 px-4">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/scan')} className="hover:bg-white/10 rounded-full">
            <ArrowLeft className="w-5 h-5 text-white/70" />
          </Button>
          <h1 className="text-2xl font-bold text-white">Analysis Report</h1>
        </div>
        
        {isThreat && (
          <Button onClick={() => navigate(`/neutralize?jobId=${job.id}`, { state: { file: routerFile } })} className="bg-red-600 hover:bg-red-700 text-white shadow-[0_0_15px_rgba(220,38,38,0.4)]">
            <Shield className="w-4 h-4 mr-2" />
            Neutralize Payload
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Summary & Image */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          {/* Threat Plaque */}
          <div className={`p-6 rounded-2xl border flex flex-col items-center justify-center text-center backdrop-blur-sm shadow-xl transition-all ${threatColor}`}>
            <div className="bg-black/20 p-4 rounded-full mb-4">
              {getThreatIcon(threatLevel)}
            </div>
            <h2 className="text-3xl font-bold uppercase tracking-wider mb-1">
              {threatLevel === 'none' ? 'Clean' : threatLevel}
            </h2>
            <p className="text-current opacity-80 uppercase text-sm tracking-widest font-semibold">
              Threat Level
            </p>
            
            <div className="mt-6 pt-6 border-t border-current/20 w-full">
              <div className="text-4xl font-black">{scorePercent}%</div>
              <p className="text-current opacity-70 text-sm mt-1">Confidence Score</p>
            </div>
          </div>

          {/* Artifact Preview */}
          <div className="bg-black/40 border border-white/10 rounded-xl overflow-hidden shadow-lg flex flex-col items-center justify-center p-2 min-h-[200px]">
             {routerFile ? (
                <img src={URL.createObjectURL(routerFile)} alt="Artifact" className="max-h-[250px] object-contain rounded border border-white/5" />
             ) : (
                <img src={job ? `http://localhost:8000/api/v1/scan/jobs/${job.id}/download` : ''} alt="Artifact" className="max-h-[250px] object-contain rounded border border-white/5" 
                   onError={(e) => {
                     (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM1NTUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cmVjdCB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHg9IjMiIHk9IjMiIHJ4PSIyIiByeT0iMiI+PC9yZWN0PjxjaXJjbGUgY3g9IjEwIiBjeT0iMTAiIHI9IjIiPjwvY2lyY2xlPjxwb2x5bGluZSBwb2ludHM9IjIxIDE1IDE2IDEwIDUgMjEiPjwvcG9seWxpbmU+PC9zdmc+';
                   }}
                />
             )}
          </div>

          {/* File Meta */}
          <div className="bg-black/40 border border-white/10 rounded-xl p-5">
            <h3 className="text-white font-medium mb-4 flex items-center gap-2">
              <FileImage className="w-4 h-4 text-primary" />
              File Details
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-white/50">Name</span>
                <span className="text-white truncate max-w-[150px]" title={job.file_name}>{job.file_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/50">Size</span>
                <span className="text-white">{(job.file_size_bytes / 1024).toFixed(1)} KB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/50">Scanned</span>
                <span className="text-white">{new Date(job.created_at).toLocaleTimeString()}</span>
              </div>
              <div className="flex justify-between pt-3 border-t border-white/10">
                <span className="text-white/50">Job ID</span>
                <span className="text-white/50 font-mono text-xs">{job.id.substring(0, 8)}...</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Engine Breakdowns */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="bg-black/40 border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary" />
                Detection Engines
              </h3>
              <span className="px-3 py-1 bg-white/5 text-white/50 text-xs rounded-full border border-white/10">
                Ensemble Mode Active
              </span>
            </div>

            <div className="space-y-6">
              {result?.detection_methods?.engines?.map((engine: any, i: number) => {
                const score = engine.score * 100;
                // High score > 65% is red, > 40% is yellow, else green
                const color = score > 65 ? 'bg-red-500' : score > 40 ? 'bg-yellow-500' : 'bg-green-500';
                
                return (
                  <div key={i}>
                    <div className="flex justify-between items-end mb-2">
                      <span className="text-white font-medium flex items-center gap-2">
                        {engine.is_cnn && <Cpu className="w-4 h-4 text-purple-400" />}
                        {engine.engine}
                        {engine.is_cnn && <span className="text-[10px] bg-purple-500/20 text-purple-300 px-1.5 py-0.5 rounded ml-1">DEEP LEARNING</span>}
                      </span>
                      <span className="text-white/80 font-mono text-sm">{score.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-black/50 h-2.5 rounded-full overflow-hidden border border-white/5 cursor-crosshair relative group">
                      <div 
                        className={`h-full ${color} rounded-full transition-all duration-1000 ease-out`}
                        style={{ width: `${Math.max(score, 1)}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
              
              {!result?.detection_methods?.engines?.length && (
                <div className="text-center py-8 text-white/40">
                  No detailed engine metrics available.
                </div>
              )}
            </div>
            
            <div className="mt-8 p-4 bg-primary/5 hover:bg-primary/10 transition-colors border border-primary/20 rounded-lg">
              <h4 className="text-primary font-medium mb-1">Ensemble Decision Strategy</h4>
              <p className="text-white/60 text-sm leading-relaxed mb-4">
                The final confidence score ({scorePercent}%) represents a True-Positive Max Confidence. Instead of watering down detections with a plain average, the engine identifies the highest probability of tampering across all spatial, frequency, and Deep Learning nodes. A single critical hit above 65% flags the file.
              </p>
              
              {/* LSB Extraction Tool */}
              <div className="mt-4 pt-4 border-t border-primary/20">
                <h4 className="text-white font-medium mb-2 flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-purple-400" />
                  Payload Extractor
                </h4>
                <p className="text-white/50 text-xs mb-3">Attempt to chronologically scrape standard ASCII text from the Least Significant Bit layer.</p>
                
                <div className="bg-black/40 rounded p-3 border border-white/5 relative">
                  <input 
                    type="file" 
                    id="extract-file" 
                    className="hidden" 
                    accept="image/*"
                    onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      try {
                        const evt = e.target as HTMLInputElement;
                        evt.disabled = true;
                        
                        const label = document.getElementById('extract-label');
                        if (label) label.innerText = "Extracting Bits...";
                        
                        const res = await scanApi.extractPayload(file);
                        
                        const output = document.getElementById('payload-output');
                        if (output) {
                          output.innerText = res.extracted_payload || "No payload decoded.";
                          output.classList.remove('hidden');
                        }
                        
                        if (label) label.innerText = "Re-Upload Image to Extract";
                        evt.disabled = false;
                      } catch (err: any) {
                        const label = document.getElementById('extract-label');
                        if (label) label.innerText = "Extraction Failed. Try Again.";
                        const evt = e.target as HTMLInputElement;
                        evt.disabled = false;
                      }
                    }}
                  />
                  <label 
                    htmlFor="extract-file" 
                    id="extract-label"
                    className="inline-block bg-white/10 hover:bg-white/20 text-white text-sm py-1.5 px-3 rounded cursor-pointer transition-colors mb-3"
                  >
                    Upload Image to Extract Payload
                  </label>
                  
                  <div id="payload-output" className="hidden mt-2 p-3 bg-black text-green-400 font-mono text-xs rounded border border-green-500/20 max-h-[150px] overflow-y-auto break-all">
                    {/* Decoded content drops here */}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScanResultPage;
