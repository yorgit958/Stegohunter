from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import httpx

from app.api.dependencies import verify_token
from app.core.config import settings
from app.core.supabase_client import service_client

router = APIRouter(prefix="/dnn", tags=["Deep Neural Network Defense"])

@router.post("/scan")
async def scan_dnn_model(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token),
):
    """
    Proxies an infected Neural Network to the DNN Defense Service.
    We don't cache gigabyte models to MinIO yet due to local storage limits,
    so we stream it directly into the Python Analysis memory envelope.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_bytes = await file.read()
    mime_type = file.content_type or "application/octet-stream"

    # Forward to DNN Defense Service (Port 8003)
    dnn_url = getattr(settings, "DNN_DEFENSE_URL", "http://localhost:8003")
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{dnn_url}/api/analyze-model",
                files={"file": (file.filename, file_bytes, mime_type)},
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail=f"DNN Defense Service Error: {response.text}")
                
            result_data = response.json()
            
            # Log the zero-day threat analysis to Supabase
            try:
                service_client.table("scan_jobs").insert({
                    "user_id": user_id,
                    "status": "completed",
                    "job_type": "dnn_model",
                    "file_name": file.filename,
                    "file_hash_sha256": "bypass", # Skipped for 5GB files to save CPU
                    "file_size_bytes": len(file_bytes),
                    "mime_type": mime_type,
                }).execute()
            except Exception as e:
                print(f"Failed to log DNN scan job: {e}")
                
            return result_data
            
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="DNN Defense Service is offline. Expected on port 8003.")
