import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';

interface ScanUploaderProps {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}

const ScanUploader: React.FC<ScanUploaderProps> = ({ onFileSelect, isLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateAndSetFile = (file: File) => {
    setError(null);
    
    // Check type
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      setError("Invalid file type. Only JPEG and PNG are supported.");
      return;
    }
    
    // Check size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError("File is too large. Maximum size is 10MB.");
      return;
    }

    setSelectedFile(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreview(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleScanClick = () => {
    if (selectedFile) {
      onFileSelect(selectedFile);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {!selectedFile ? (
        <div 
          className={`
            relative border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center
            transition-all duration-200 ease-in-out bg-black/40 backdrop-blur-sm
            ${dragActive ? 'border-primary/50 bg-primary/5' : 'border-white/10 hover:border-white/20 hover:bg-white/5'}
            ${error ? 'border-red-500/50 bg-red-500/5' : ''}
          `}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept="image/png, image/jpeg"
            onChange={handleChange}
            disabled={isLoading}
          />
          
          <div className="bg-white/5 p-4 rounded-full mb-4">
            <UploadCloud className="w-10 h-10 text-primary/80" />
          </div>
          
          <h3 className="text-xl font-medium text-white mb-2">
            Drag & Drop your image here
          </h3>
          <p className="text-white/50 mb-6 text-sm text-center max-w-sm">
            Support for JPEG and PNG formats. Algorithms perform best on uncompressed or intact suspect images.
          </p>
          
          <Button type="button" variant="outline" className="border-white/10 hover:bg-white/10" disabled={isLoading}>
            Browse Files
          </Button>

          {error && (
            <div className="absolute bottom-4 flex items-center gap-2 text-red-400 text-sm mt-4 bg-red-400/10 px-4 py-2 rounded-lg">
              <AlertCircle className="w-4 h-4" />
              <span>{error}</span>
            </div>
          )}
        </div>
      ) : (
        <div className="border border-white/10 bg-black/40 backdrop-blur-sm rounded-xl p-6">
          <div className="flex flex-col sm:flex-row gap-6">
            <div className="w-full sm:w-1/3 aspect-square rounded-lg overflow-hidden border border-white/10 bg-black/60 flex items-center justify-center relative group">
              {preview ? (
                <img src={preview} alt="Selected image" className="object-contain w-full h-full" />
              ) : (
                <ImageIcon className="w-10 h-10 text-white/20" />
              )}
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <Button variant="ghost" className="text-white hover:bg-white/20" onClick={handleClear} disabled={isLoading}>
                  Change Image
                </Button>
              </div>
            </div>
            
            <div className="w-full sm:w-2/3 flex flex-col justify-between py-2">
              <div>
                <h3 className="font-medium text-white text-lg truncate mb-1" title={selectedFile.name}>
                  {selectedFile.name}
                </h3>
                <p className="text-white/50 text-sm flex items-center gap-2">
                  <span className="bg-white/10 px-2 py-0.5 rounded text-xs uppercase tracking-wider">{selectedFile.type.split('/')[1]}</span>
                  <span>{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
                </p>
                
                <div className="mt-6 flex flex-col gap-2">
                  <div className="flex items-center gap-2 text-sm text-white/70">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
                    Ready for analysis pipeline
                  </div>
                  <div className="flex items-center gap-2 text-sm text-white/70">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                    CNN + 4 Statistical Engines
                  </div>
                </div>
              </div>
              
              <div className="mt-8 flex gap-3">
                <Button 
                  variant="outline" 
                  className="flex-1 border-white/10 hover:bg-white/10"
                  onClick={handleClear}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button 
                  className="flex-2 bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_20px_rgba(var(--primary),0.3)] transition-all hover:shadow-[0_0_30px_rgba(var(--primary),0.5)]"
                  onClick={handleScanClick}
                  disabled={isLoading}
                >
                  {isLoading ? 'Initializing...' : 'Start Scan'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanUploader;
