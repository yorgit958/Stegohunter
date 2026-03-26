from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import shutil
import tempfile
import time

router = APIRouter()

@router.post("/analyze-model")
async def analyze_model(
    file: UploadFile = File(...),
):
    """
    Receives an AI model weight file (.h5, .pt, .onnx, .safetensors),
    extracts the billion-scale tensor arrays, and runs statistical 
    anomaly detection equations against the Float32 bytes.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    _, ext = os.path.splitext(file.filename.lower())
    supported_exts = {'.h5', '.pt', '.pth', '.onnx', '.safetensors'}
    
    if ext not in supported_exts:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported model format: {ext}. Supported formats: {', '.join(supported_exts)}"
        )

    # DNN Models can be massive (hundreds of MBs). 
    # Must write to a physical temp file for PyTorch/H5Py to parse them efficiently without OOMing.
    fd, temp_path = tempfile.mkstemp(suffix=ext)
    
    try:
        start_time = time.time()
        
        # Stream the massive model file to disk gracefully
        with os.fdopen(fd, 'wb') as out_file:
            shutil.copyfileobj(file.file, out_file)
            
        # --- Dispatch to specific format parser ---
        from app.parsers import get_parser
        from app.analyzers.weight_distribution import WeightDistributionAnalyzer
        
        # 1. Instantiate the correct parser based on file extension
        parser = get_parser(file.filename)
        # We override the path to point to our downloaded temp file
        parser.file_path = temp_path 
        
        # 2. Extract weights and metadata securely
        weights = parser.parse()
        metadata = parser.get_metadata()
        
        # 3. Run LSB Entropy and Statistical Analysis
        analyzer = WeightDistributionAnalyzer(lsb_bits=1)
        analysis_result = analyzer.analyze(weights)
        
        # 4. Format the response
        is_threat = analysis_result["threat_detected"]
        max_ent = analysis_result["max_lsb_entropy"]
        anomalous_layers = [
            {"name": lr["layer"], "entropy": lr["lsb_entropy"]} 
            for lr in analysis_result["layer_results"] if lr["is_anomalous"]
        ]
        total_params = sum(lr["size"] for lr in analysis_result["layer_results"])
        
        elapsed = time.time() - start_time
        
        return {
            "status": "success",
            "file_name": file.filename,
            "execution_time_sec": round(elapsed, 2),
            "is_stego": is_threat,
            "threat_level": "high" if is_threat else "none",
            "confidence": round(float(max_ent), 3) if max_ent > 0 else 1.0, # High entropy = high confidence of stego
            "entropy": round(float(max_ent), 4),
            "total_parameters": total_params,
            "anomalous_layers": anomalous_layers,
            "metadata": metadata
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Model Parsing Error: {str(e)}")
        
    finally:
        # Guarantee massive files are shredded from local disk to prevent storage leaks
        if os.path.exists(temp_path):
            os.remove(temp_path)
