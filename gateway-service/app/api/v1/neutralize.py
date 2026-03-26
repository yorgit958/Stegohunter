from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import Optional
import httpx
import json

from app.api.dependencies import verify_token
from app.core.config import settings
from app.core.supabase_client import service_client

router = APIRouter(prefix="/neutralize", tags=["Neutralization"])

@router.post("")
@router.post("/")
async def submit_neutralize(
    file: UploadFile = File(...),
    scan_result_id: Optional[str] = Form(None),
    analysis_results: str = Form(..., description="JSON string of the original analysis results"),
    force_strategies: Optional[str] = Form(None),
    user_id: str = Depends(verify_token),
):
    """
    Proxies an image to the Neutralization Service for steganography payload scrubbing.
    Records the job and integrity metrics in Supabase.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Read bytes once
    file_bytes = await file.read()
    mime_type = file.content_type or "application/octet-stream"

    # Step 1: Create Neutralization Job Record
    job_id = None
    try:
        job_data = {
            "user_id": user_id,
            "status": "scrubbing",
            "original_path": file.filename,
        }
        if scan_result_id:
            job_data["scan_result_id"] = scan_result_id
            
        job_resp = service_client.table("neutralization_jobs").insert(job_data).execute()
        if job_resp.data:
            job_id = job_resp.data[0]["id"]
    except Exception as e:
        print(f"Warning: Could not create neutralization_job: {e}")

    # Step 2: Forward to Neutralization Service (Port 8002)
    # Get URL from settings horizontally, or construct default
    neutralize_url = getattr(settings, "NEUTRALIZATION_URL", "http://localhost:8002")
    
    try:
        data_payload = {"analysis_results": analysis_results}
        if force_strategies:
            data_payload["force_strategies"] = force_strategies
            
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{neutralize_url}/api/neutralize/process",
                data=data_payload,
                files={"file": (file.filename, file_bytes, mime_type)},
            )
            
            if response.status_code != 200:
                if job_id:
                    service_client.table("neutralization_jobs").update(
                        {"status": "failed"}
                    ).eq("id", job_id).execute()
                raise HTTPException(status_code=502, detail=f"Neutralization Service Error: {response.text}")
                
            result_data = response.json()
            metrics = result_data.get("integrity_metrics", {})
            strategies = result_data.get("applied_strategies", [])
            scrubbed_b64 = result_data.get("scrubbed_base64")

            # Store sanitized output in MinIO
            if scrubbed_b64 and job_id:
                try:
                    import base64
                    from app.core.minio_client import upload_file_bytes
                    raw_bytes = base64.b64decode(scrubbed_b64)
                    upload_file_bytes("sanitized", f"{job_id}_{file.filename}", raw_bytes, mime_type)
                except Exception as e:
                    print(f"Warning: Failed to save sanitized file to MinIO: {e}")
            
    except httpx.ConnectError:
        if job_id:
            service_client.table("neutralization_jobs").update({"status": "failed"}).eq("id", job_id).execute()
        raise HTTPException(status_code=503, detail="Neutralization Service is offline. Expected on port 8002.")

    # Step 3: Complete Database Audit
    if job_id:
        try:
            # Update job status
            service_client.table("neutralization_jobs").update({
                "status": "completed",
                "completed_at": "now()",
                "strategy_used": strategies,
            }).eq("id", job_id).execute()
            
            # Store integrity metrics
            service_client.table("integrity_reports").insert({
                "neutralization_id": job_id,
                "ssim_score": metrics.get("ssim"),
                "psnr_db": metrics.get("psnr_db"),
                "mse": metrics.get("mse"),
                "quality_approved": metrics.get("quality_approved"),
            }).execute()
        except Exception as e:
            print(f"Warning: Failed to log completion metrics to Supabase: {e}")

    # Return safe data to frontend
    return {
        "status": "success",
        "job_id": job_id,
        "applied_strategies": strategies,
        "metrics": metrics,
        "scrubbed_base64": scrubbed_b64,
        "mime_type": result_data.get("mime_type", "image/png"),
    }
