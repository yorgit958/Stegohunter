import React, { useEffect, useState } from 'react';
import { Loader2, Terminal, Search } from 'lucide-react';
import { Button } from './ui/button';
import { scanApi } from '../lib/api';

interface PayloadExtractorProps {
  jobId: string;
  autoExtract?: boolean;
}

const PayloadExtractor: React.FC<PayloadExtractorProps> = ({ jobId, autoExtract = false }) => {
  const [extracting, setExtracting] = useState(false);
  const [payload, setPayload] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runExtraction = async () => {
    setExtracting(true);
    setError(null);
    setPayload(null);
    
    try {
      const res = await scanApi.extractPayloadByJobId(jobId);
      setPayload(res.extracted_payload || "No payload decoded.");
    } catch (err: any) {
      console.error("Extraction failed:", err);
      setError(err.response?.data?.detail || "Extraction engine encountered an error.");
    } finally {
      setExtracting(false);
    }
  };

  // Auto-extract when threat is detected
  useEffect(() => {
    if (autoExtract && jobId) {
      runExtraction();
    }
  }, [autoExtract, jobId]);

  return (
    <div className="bg-black/40 rounded p-3 border border-white/5 relative">
      {!payload && !extracting && !error && (
        <Button
          onClick={runExtraction}
          disabled={extracting}
          variant="outline"
          className="bg-white/10 hover:bg-white/20 text-white text-sm border-white/10"
        >
          <Search className="w-4 h-4 mr-2" />
          Extract Payload
        </Button>
      )}

      {extracting && (
        <div className="flex items-center gap-3 py-2">
          <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
          <span className="text-purple-300 text-sm font-medium animate-pulse">
            Scraping LSB bit layer...
          </span>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-500/10 text-red-300 text-xs rounded border border-red-500/20">
          {error}
          <Button
            onClick={runExtraction}
            variant="ghost"
            className="mt-2 text-xs text-red-300 hover:bg-red-500/20 p-1 h-auto"
          >
            Retry
          </Button>
        </div>
      )}

      {payload && (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-green-400 text-xs font-medium">
            <Terminal className="w-4 h-4" />
            Extracted Payload
          </div>
          <div className="p-3 bg-black text-green-400 font-mono text-xs rounded border border-green-500/20 max-h-[150px] overflow-y-auto break-all whitespace-pre-wrap">
            {payload}
          </div>
          <Button
            onClick={runExtraction}
            variant="ghost"
            className="text-xs text-white/50 hover:bg-white/10 p-1 h-auto"
          >
            Re-extract
          </Button>
        </div>
      )}
    </div>
  );
};

export default PayloadExtractor;
