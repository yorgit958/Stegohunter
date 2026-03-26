import React, { useState } from 'react';
import { UploadCloud, FileType, ShieldCheck, ShieldAlert, Activity, FileKey, XCircle, BrainCircuit } from 'lucide-react';
import { scanApi } from '../lib/api';

const DNNAnalysisPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleScan = async () => {
    if (!file) return;
    try {
      setIsScanning(true);
      setError(null);
      const res = await scanApi.scanDnnModel(file);
      setResult(res);
    } catch (err: any) {
      console.error("DNN Scan Error:", err);
      setError(err.response?.data?.detail || "Failed to analyze neural network model.");
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="container py-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
          <BrainCircuit className="w-8 h-8 text-primary" />
          Neural Network (DNN) Defense
        </h1>
        <p className="text-white/60 mt-2">
          Upload Keras (.h5) or PyTorch (.pt) weights to detect anomalous bitwise distributions caused by embedded steganographic zero-day payloads.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Upload Column */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-black/40 border border-white/5 p-6 rounded-xl shadow-lg relative overflow-hidden group">
            <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label className="flex flex-col items-center justify-center cursor-pointer min-h-[250px] border-2 border-dashed border-white/10 rounded-lg group-hover:border-primary/50 transition-colors">
              <input type="file" className="hidden" accept=".h5,.pt,.pth,.onnx,.safetensors" onChange={handleFileChange} />
              <UploadCloud className="w-12 h-12 text-primary/70 mb-4 group-hover:text-primary transition-colors" />
              <div className="text-center px-4">
                <p className="font-semibold text-white/90 mb-1">Upload Model Weights</p>
                <p className="text-sm text-white/40">Select .h5, .pt, or .onnx files</p>
              </div>
            </label>
            
            {file && (
              <div className="mt-4 p-4 border border-primary/20 bg-primary/5 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-3 overflow-hidden">
                  <FileType className="min-w-6 text-primary" />
                  <div className="truncate">
                    <p className="text-sm font-medium text-white truncate">{file.name}</p>
                    <p className="text-xs text-white/50">{(file.size / (1024*1024)).toFixed(2)} MB</p>
                  </div>
                </div>
                <button onClick={() => setFile(null)} className="text-white/40 hover:text-white p-1">
                  <XCircle className="w-4 h-4" />
                </button>
              </div>
            )}
            
            <button 
              className="mt-4 w-full bg-primary text-black font-semibold py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!file || isScanning}
              onClick={handleScan}
            >
              {isScanning ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-black/20 border-t-black animate-spin" />
                  Parsing Architecture...
                </>
              ) : (
                <>
                  <Activity className="w-4 h-4" /> Analyze Tensors
                </>
              )}
            </button>
          </div>
          
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-200 text-sm rounded-lg flex items-start gap-3">
              <ShieldAlert className="w-5 h-5 shrink-0" />
              {error}
            </div>
          )}
        </div>

        {/* Results Column */}
        <div className="lg:col-span-2 space-y-6">
          {!result && !isScanning && (
             <div className="h-full min-h-[350px] bg-black/40 border border-white/5 rounded-xl flex flex-col items-center justify-center text-white/20 p-8 text-center">
                <FileKey className="w-16 h-16 mb-4 opacity-50" />
                <p className="text-lg">Awaiting Model File</p>
                <p className="text-sm mt-2 max-w-sm">Neural network analysis performs structural unrolling of matrix nodes to statistically prove the absence of high-entropy block ciphers.</p>
             </div>
          )}
          
          {isScanning && (
             <div className="h-full min-h-[350px] bg-black/40 border border-primary/20 rounded-xl flex flex-col items-center justify-center p-8 space-y-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 invert mix-blend-soft-light" />
                <div className="w-24 h-24 relative">
                   <div className="absolute inset-0 rounded-full border-2 border-primary/20" />
                   <div className="absolute inset-0 rounded-full border-t-2 border-primary animate-spin" />
                   <BrainCircuit className="w-10 h-10 text-primary absolute inset-0 m-auto animate-pulse" />
                </div>
                <div className="text-center space-y-2 z-10">
                   <h3 className="text-xl font-bold text-white tracking-widest">DECRYPTING WEIGHT MATRIX</h3>
                   <p className="text-primary font-mono text-xs">Unrolling billions of Float32 parameters from storage...</p>
                </div>
             </div>
          )}

          {result && !isScanning && (
            <div className="space-y-6">
              {/* Verdict Header */}
              <div className={`p-6 border rounded-xl flex items-center justify-between ${result.is_stego ? 'bg-red-500/10 border-red-500/30' : 'bg-green-500/10 border-green-500/30'}`}>
                <div className="flex items-center gap-4">
                  {result.is_stego ? (
                    <div className="p-3 bg-red-500/20 rounded-full"><ShieldAlert className="w-8 h-8 text-red-500" /></div>
                  ) : (
                    <div className="p-3 bg-green-500/20 rounded-full"><ShieldCheck className="w-8 h-8 text-green-500" /></div>
                  )}
                  <div>
                    <p className={`text-sm font-bold tracking-widest uppercase mb-1 ${result.is_stego ? 'text-red-400' : 'text-green-400'}`}>
                      {result.is_stego ? 'Anomalous Payload Detected' : 'Tensors Cryptographically Clean'}
                    </p>
                    <h2 className="text-2xl font-semibold text-white">
                      {result.file_name}
                    </h2>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-black text-white">{result.confidence.toFixed(1)}%</div>
                  <p className="text-white/50 text-xs mt-1 uppercase">Confidence</p>
                </div>
              </div>

              {/* Entropy Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-black/40 border border-white/5 p-4 rounded-xl text-center">
                   <p className="text-white/40 text-[10px] uppercase font-bold tracking-widest mb-1">Global Entropy</p>
                   <p className={`text-xl font-bold font-mono ${result.entropy > 7.9 ? 'text-red-400' : 'text-primary'}`}>{result.entropy.toFixed(3)}</p>
                </div>
                <div className="bg-black/40 border border-white/5 p-4 rounded-xl text-center">
                   <p className="text-white/40 text-[10px] uppercase font-bold tracking-widest mb-1">Execution Time</p>
                   <p className="text-xl font-bold text-white font-mono">{result.execution_time_sec}s</p>
                </div>
                <div className="bg-black/40 border border-white/5 p-4 rounded-xl text-center col-span-2">
                   <p className="text-white/40 text-[10px] uppercase font-bold tracking-widest mb-1">Parameters Parsed</p>
                   <p className="text-xl font-bold text-white font-mono">{result.total_parameters.toLocaleString()}</p>
                </div>
              </div>

              {/* Layer Breakdown */}
              {result.anomalous_layers && result.anomalous_layers.length > 0 && (
                <div className="bg-black/40 border border-white/5 rounded-xl overflow-hidden">
                  <div className="border-b border-white/5 bg-white/5 p-4">
                     <h3 className="font-semibold text-white text-sm">Infected Neural Layers</h3>
                  </div>
                  <div className="p-4 space-y-3 max-h-[300px] overflow-y-auto">
                    {result.anomalous_layers.map((layer: any, i: number) => (
                      <div key={i} className="flex items-center justify-between p-3 rounded bg-red-500/5 border border-red-500/10">
                        <div className="flex bg-black px-2 py-1 rounded font-mono text-xs text-red-300 w-full overflow-hidden shrink mr-4 truncate">
                          {layer.layer_name}
                        </div>
                        <div className="flex gap-4 shrink-0 items-center text-xs">
                          <span className="text-white/60">size: {layer.size}</span>
                          <span className="font-bold text-red-400 bg-red-500/10 px-2 py-1 rounded">E: {layer.entropy.toFixed(3)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DNNAnalysisPage;
