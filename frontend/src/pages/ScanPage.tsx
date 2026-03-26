import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ScanUploader from '../components/ScanUploader';
import ScanProgress from '../components/ScanProgress';
import { scanApi } from '../lib/api';
import { ShieldCheck, AlertTriangle } from 'lucide-react';

const ScanPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setIsScanning(true);
    setError(null);

    try {
      const result = await scanApi.uploadImage(selectedFile);
      
      if (result.status === 'completed' && result.scan_job_id) {
        // Navigate to the results page carrying the file in memory
        navigate(`/scan/results/${result.scan_job_id}`, { state: { file: selectedFile } });
      } else {
        throw new Error(result.message || "Failed to process image");
      }
    } catch (err: any) {
      console.error("Scan error:", err);
      setError(err.response?.data?.detail || err.message || "An unexpected error occurred during analysis.");
      setIsScanning(false);
      setFile(null);
    }
  };

  return (
    <div className="container mx-auto max-w-5xl py-12 px-4 h-full flex flex-col">
      <div className="mb-10 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <ShieldCheck className="text-primary w-8 h-8" />
            Threat Hunter
          </h1>
          <p className="text-white/60">Upload an image to detect hidden steganographic payloads.</p>
        </div>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center -mt-10">
        {error && (
          <div className="w-full max-w-2xl bg-red-500/10 border border-red-500/30 p-4 rounded-lg mb-8 flex items-center gap-3 text-red-200">
            <AlertTriangle className="text-red-400 flex-shrink-0" />
            <div>
              <p className="font-semibold text-red-400">Analysis Failed</p>
              <p className="text-sm opacity-90">{error}</p>
            </div>
          </div>
        )}

        {isScanning ? (
          <ScanProgress fileName={file?.name || "Suspicious Image.png"} />
        ) : (
          <ScanUploader onFileSelect={handleFileSelect} isLoading={false} />
        )}
      </div>
    </div>
  );
};

export default ScanPage;
