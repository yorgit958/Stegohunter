import React, { useState, useEffect } from 'react';
import { ShieldAlert, SplitSquareHorizontal, Download, CheckCircle, AlertTriangle } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import ScanUploader from '../components/ScanUploader';
import { scanApi } from '../lib/api';

const NeutralizePage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [originalPreview, setOriginalPreview] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);

  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const jobId = searchParams.get('jobId');
  const routerFile = location.state?.file as File | undefined;

  useEffect(() => {
    if (routerFile && !file && !isProcessing && !result) {
      handleFileSelect(routerFile);
    } else if (jobId && !file && !isProcessing && !result) {
      // Memory state empty but Job ID present. Fetch original bytes from MinIO!
      const fetchFromMinIO = async () => {
        try {
          setIsProcessing(true);
          const blob = await scanApi.downloadImage(jobId);
          // Rehydrate a pseudo-File object from the raw network blob
          const fetchedFile = new File([blob], `scan_${jobId}.png`, { type: blob.type || 'image/png' });
          setIsProcessing(false);
          handleFileSelect(fetchedFile);
        } catch (err: any) {
          console.error("MinIO Fetch Error:", err);
          setError("Session expired. Could not auto-download original image from storage bucket. Please re-upload it.");
          setIsProcessing(false);
        }
      };
      fetchFromMinIO();
    }
  }, [routerFile, jobId, file, isProcessing, result]);

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setOriginalPreview(URL.createObjectURL(selectedFile));
    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      // Mock empty analysis results to force a generic robust scrub (Metadata + LSB + Jitter)
      const mockAnalysis = {
        threat_level: "unknown",
        detection_methods: { engines: [], methods_triggered: [] }
      };
      
      const res = await scanApi.neutralizeImage(selectedFile, mockAnalysis);
      setResult(res);
    } catch (err: any) {
      console.error("Neutralize error:", err);
      setError(err.response?.data?.detail || err.message || "Failed to scrub image.");
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadImage = () => {
    if (!result?.scrubbed_base64) return;
    const link = document.createElement("a");
    link.href = `data:${result.mime_type};base64,${result.scrubbed_base64}`;
    link.download = `safe_${file?.name || 'image.png'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="container mx-auto max-w-6xl py-12 px-4 h-full flex flex-col">
      <div className="mb-10 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <SplitSquareHorizontal className="text-primary w-8 h-8" />
            Payload Neutralizer
          </h1>
          <p className="text-white/60">Destroy hidden steganographic payloads while preserving visual fidelity.</p>
        </div>
      </div>

      {error && (
        <div className="w-full bg-red-500/10 border border-red-500/30 p-4 rounded-lg mb-8 flex items-center gap-3 text-red-200">
          <AlertTriangle className="text-red-400 flex-shrink-0" />
          <div>
            <p className="font-semibold text-red-400">Scrubbing Failed</p>
            <p className="text-sm opacity-90">{error}</p>
          </div>
        </div>
      )}

      {!result && !isProcessing && (
        <div className="flex-1 flex flex-col items-center justify-center -mt-10">
          <ScanUploader onFileSelect={handleFileSelect} isLoading={false} />
        </div>
      )}

      {isProcessing && (
        <div className="flex-1 flex flex-col items-center justify-center -mt-10">
          <div className="w-24 h-24 border-4 border-white/10 border-t-primary rounded-full animate-spin mb-6"></div>
          <h2 className="text-2xl font-bold text-white mb-2">Neutralizing Payload</h2>
          <p className="text-white/60">Applying LSB scrubbing and structural noise...</p>
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Original Image */}
            <div className="bg-[#12141D] rounded-xl border border-white/5 overflow-hidden flex flex-col">
              <div className="p-4 border-b border-white/5 bg-white/[0.02]">
                <h3 className="font-semibold text-white/80">Original File (Tainted)</h3>
              </div>
              <div className="p-4 flex-1 flex items-center justify-center bg-black/40 min-h-[300px]">
                {originalPreview && (
                  <img src={originalPreview} alt="Original" className="max-h-[400px] object-contain rounded drop-shadow-lg" />
                )}
              </div>
            </div>

            {/* Scrubbed Image */}
            <div className="bg-[#12141D] rounded-xl border border-primary/20 overflow-hidden flex flex-col relative shadow-[0_0_30px_rgba(0,255,170,0.1)]">
              <div className="p-4 border-b border-white/5 bg-primary/10 flex justify-between items-center">
                <h3 className="font-semibold text-primary flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Sanitized Output
                </h3>
              </div>
              <div className="p-4 flex-1 flex items-center justify-center bg-black/40 min-h-[300px]">
                {result.scrubbed_base64 && (
                  <img 
                    src={`data:${result.mime_type};base64,${result.scrubbed_base64}`} 
                    alt="Scrubbed" 
                    className="max-h-[400px] object-contain rounded drop-shadow-lg" 
                  />
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#12141D] rounded-xl border border-white/5 p-6 md:col-span-2">
              <h3 className="text-lg font-bold text-white mb-4">Integrity Report</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-white/5 border border-white/5 text-center">
                  <p className="text-white/40 text-xs uppercase tracking-wider mb-1">SSIM Score</p>
                  <p className="text-2xl font-bold text-white">
                    {result.metrics?.ssim ? (result.metrics.ssim * 100).toFixed(1) + '%' : 'N/A'}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-white/5 border border-white/5 text-center">
                  <p className="text-white/40 text-xs uppercase tracking-wider mb-1">PSNR</p>
                  <p className="text-2xl font-bold text-white">
                    {result.metrics?.psnr_db ? result.metrics.psnr_db.toFixed(1) + ' dB' : 'N/A'}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-white/5 border border-white/5 text-center">
                  <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Passed Quality</p>
                  <p className={`text-xl font-bold ${result.metrics?.quality_approved ? 'text-primary' : 'text-yellow-500'}`}>
                    {result.metrics?.quality_approved ? 'YES' : 'NO'}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-white/5 border border-white/5 text-center">
                  <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Defenses Applied</p>
                  <p className="text-xl font-bold text-white">{result.applied_strategies?.length || 0}</p>
                </div>
              </div>
              
              <div className="mt-6 flex flex-wrap gap-2">
                {result.applied_strategies?.map((strategy: string) => (
                  <span key={strategy} className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs font-medium text-white/70">
                    {strategy.replace('_', ' ').toUpperCase()}
                  </span>
                ))}
              </div>
            </div>

            <div className="bg-[#12141D] rounded-xl border border-white/5 p-6 flex flex-col justify-center items-center text-center">
              <ShieldAlert className="text-white/20 w-16 h-16 mb-4" />
              <h3 className="text-lg font-bold text-white mb-2">Ready for Deployment</h3>
              <p className="text-sm text-white/60 mb-6">
                All identified spatial and frequency payloads have been mathematically erased from this image.
              </p>
              <button 
                onClick={downloadImage}
                className="w-full py-3 px-4 bg-primary hover:bg-primary/90 text-black font-semibold rounded-lg transition-all flex items-center justify-center gap-2"
              >
                <Download className="w-5 h-5" /> Download Safe Image
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NeutralizePage;
