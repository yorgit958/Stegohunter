from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, BackgroundTasks
from typing import Optional
import os
import hashlib
import httpx
import json

from app.api.dependencies import verify_token
from app.core.config import settings
from app.core.supabase_client import service_client
from app.core.minio_client import upload_file_bytes, download_file_bytes
from fastapi.responses import Response

router = APIRouter(prefix="/scan", tags=["Scanning"])


async def publish_scan_event(user_id: str, scan_job_id: str, step: str, step_index: int, status: str = "in_progress", result: dict = None):
    """Publish a scan progress event to Redis PubSub for WebSocket delivery."""
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        event = {
            "type": "scan_progress",
            "user_id": user_id,
            "scan_job_id": scan_job_id,
            "step": step,
            "step_index": step_index,
            "status": status,
        }
        if result:
            event["result"] = result
        await r.publish("scan_events", json.dumps(event))
        await r.aclose()
    except Exception as e:
        print(f"[Redis Publish] Error: {e}")


async def run_scan_pipeline(user_id: str, scan_job_id: str, file_name: str, file_bytes: bytes, mime_type: str):
    """
    Background task that executes the full scan pipeline:
    1. Upload to MinIO
    2. Forward to Image Analysis Service
    3. Store results in Supabase
    4. Update job status
    Each step publishes progress to Redis for real-time WebSocket updates.
    """
    try:
        # Step 1: Upload to MinIO
        await publish_scan_event(user_id, scan_job_id, "Uploading to secure storage", 0)
        object_name = f"{scan_job_id}_{file_name}"
        upload_file_bytes("originals", object_name, file_bytes, mime_type)

        # Step 2: Forward to Image Analysis Service
        await publish_scan_event(user_id, scan_job_id, "Running AI analysis engines", 1)
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.IMAGE_ANALYSIS_URL}/api/analyze",
                files={"file": (file_name, file_bytes, mime_type)},
            )

            if response.status_code != 200:
                service_client.table("scan_jobs").update({
                    "status": "failed",
                    "error_message": f"Analysis service returned {response.status_code}",
                }).eq("id", scan_job_id).execute()
                await publish_scan_event(user_id, scan_job_id, "Analysis failed", 1, status="error")
                return

            analysis_result = response.json()

        # Step 3: Store results
        await publish_scan_event(user_id, scan_job_id, "Storing analysis results", 2)
        result_data = {
            "scan_job_id": scan_job_id,
            "is_stego": analysis_result.get("is_stego", False),
            "confidence": analysis_result.get("confidence", 0.0),
            "threat_level": analysis_result.get("threat_level", "none"),
            "detection_methods": {
                "engines": analysis_result.get("engine_results", []),
                "methods_triggered": analysis_result.get("detection_methods", []),
            },
            "metadata": {
                "ensemble_score": analysis_result.get("ensemble_score", 0.0),
                "threshold": analysis_result.get("threshold", 0.65),
                "image_info": analysis_result.get("image_info", {}),
            },
        }

        try:
            service_client.table("scan_results").insert(result_data).execute()
        except Exception as e:
            print(f"Warning: Could not store scan results: {e}")

        # Step 4: Update job status to completed
        await publish_scan_event(user_id, scan_job_id, "Finalizing report", 3)
        service_client.table("scan_jobs").update({
            "status": "completed",
            "completed_at": "now()",
        }).eq("id", scan_job_id).execute()

        # Step 5: Push completion event with summary
        await publish_scan_event(user_id, scan_job_id, "Scan complete", 4, status="completed", result={
            "is_stego": analysis_result.get("is_stego", False),
            "threat_level": analysis_result.get("threat_level", "none"),
            "confidence": analysis_result.get("confidence", 0.0),
        })

    except httpx.ConnectError:
        service_client.table("scan_jobs").update({
            "status": "failed",
            "error_message": "Could not connect to Image Analysis Service",
        }).eq("id", scan_job_id).execute()
        await publish_scan_event(user_id, scan_job_id, "Connection failed", 0, status="error")

    except Exception as e:
        service_client.table("scan_jobs").update({
            "status": "failed",
            "error_message": str(e),
        }).eq("id", scan_job_id).execute()
        await publish_scan_event(user_id, scan_job_id, f"Error: {str(e)[:100]}", 0, status="error")


@router.post("")
@router.post("/")
async def submit_scan(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token),
):
    """
    Non-blocking scan pipeline:
    1. Validate the uploaded file
    2. Create a scan_job record in Supabase (status='analyzing')
    3. Instantly return the scan_job_id to the frontend
    4. Execute the heavy AI analysis in the background
    5. Push real-time progress to the user via Redis → WebSocket
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    _, ext = os.path.splitext(file.filename.lower())
    allowed = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".gif", ".webp"}
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # Read file bytes
    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(file_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    # Calculate file hash
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    mime_type = file.content_type or "application/octet-stream"

    # Create scan_job in Supabase immediately
    try:
        job_response = service_client.table("scan_jobs").insert({
            "user_id": user_id,
            "status": "analyzing",
            "job_type": "image",
            "file_name": file.filename,
            "file_hash_sha256": file_hash,
            "file_size_bytes": len(file_bytes),
            "mime_type": mime_type,
        }).execute()

        if not job_response.data:
            raise Exception("Failed to create scan job record")

        scan_job = job_response.data[0]
        scan_job_id = scan_job["id"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Enqueue the heavy pipeline as a background task
    background_tasks.add_task(
        run_scan_pipeline,
        user_id, scan_job_id, file.filename, file_bytes, mime_type
    )

    # Return instantly — the frontend will track progress via WebSocket
    return {
        "status": "analyzing",
        "scan_job_id": scan_job_id,
        "file_name": file.filename,
        "file_hash": file_hash,
        "file_size": len(file_bytes),
        "message": "Scan queued. Track progress via WebSocket.",
    }


@router.get("/jobs")
async def list_scan_jobs(
    user_id: str = Depends(verify_token),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """List scan jobs for the authenticated user, with scan results joined."""
    try:
        response = service_client.table("scan_jobs") \
            .select("*, scan_results(is_stego, confidence, threat_level)") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()

        jobs = response.data or []
        
        # Flatten the nested scan_results into each job for easier frontend consumption
        for job in jobs:
            results = job.pop("scan_results", [])
            if results and len(results) > 0:
                job["is_stego"] = results[0].get("is_stego", False)
                job["confidence"] = results[0].get("confidence", 0.0)
                job["threat_level"] = results[0].get("threat_level", "none")
            else:
                job["is_stego"] = None  # No results yet
                job["confidence"] = None
                job["threat_level"] = None

        return {"jobs": jobs, "total": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_scan_job(
    job_id: str,
    user_id: str = Depends(verify_token),
):
    """Get a specific scan job with its results."""
    try:
        # Get the scan job
        job_response = service_client.table("scan_jobs") \
            .select("*") \
            .eq("id", job_id) \
            .eq("user_id", user_id) \
            .execute()

        if not job_response.data:
            raise HTTPException(status_code=404, detail="Scan job not found")

        job = job_response.data[0]

        # Get related scan results
        results_response = service_client.table("scan_results") \
            .select("*") \
            .eq("scan_job_id", job_id) \
            .execute()

        return {
            "job": job,
            "results": results_response.data or [],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}/download")
async def download_scan_file(
    job_id: str,
    user_id: str = Depends(verify_token),
):
    """Download the original file from MinIO."""
    try:
        job_response = service_client.table("scan_jobs") \
            .select("file_name, mime_type") \
            .eq("id", job_id) \
            .eq("user_id", user_id) \
            .execute()

        if not job_response.data:
            raise HTTPException(status_code=404, detail="Scan job not found")
            
        file_name = job_response.data[0]["file_name"]
        mime_type = job_response.data[0]["mime_type"]
        object_name = f"{job_id}_{file_name}"
        
        file_bytes = download_file_bytes("originals", object_name)
        if not file_bytes:
            raise HTTPException(status_code=404, detail="File could not be found in storage.")
            
        return Response(content=file_bytes, media_type=mime_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_scan_stats(
    user_id: str = Depends(verify_token),
):
    """Get scanning statistics for the dashboard."""
    try:
        # Total scans
        all_jobs = service_client.table("scan_jobs") \
            .select("id, status") \
            .eq("user_id", user_id) \
            .execute()

        jobs = all_jobs.data or []
        total_scans = len(jobs)
        completed = sum(1 for j in jobs if j["status"] == "completed")

        # Get results for threat count
        all_results = service_client.table("scan_results") \
            .select("is_stego, threat_level, scan_job_id") \
            .execute()

        # Filter to user's jobs
        user_job_ids = {j["id"] for j in jobs}
        user_results = [r for r in (all_results.data or []) if r["scan_job_id"] in user_job_ids]

        threats_found = sum(1 for r in user_results if r.get("is_stego"))
        clean = sum(1 for r in user_results if not r.get("is_stego"))

        return {
            "total_scans": total_scans,
            "completed": completed,
            "threats_found": threats_found,
            "clean": clean,
            "threat_levels": {
                "critical": sum(1 for r in user_results if r.get("threat_level") == "critical"),
                "high": sum(1 for r in user_results if r.get("threat_level") == "high"),
                "medium": sum(1 for r in user_results if r.get("threat_level") == "medium"),
                "low": sum(1 for r in user_results if r.get("threat_level") == "low"),
                "none": sum(1 for r in user_results if r.get("threat_level") == "none"),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract")
async def extract_payload(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token),
):
    """Proxy image to Image Analysis Service for LSB payload extraction"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_bytes = await file.read()
    mime_type = file.content_type or "application/octet-stream"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.IMAGE_ANALYSIS_URL}/api/extract-lsb",
                files={"file": (file.filename, file_bytes, mime_type)},
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Image Analysis Service extraction error: {response.text}",
                )

            return response.json()
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Image Analysis Service is offline.")


@router.get("/extract/{job_id}")
async def extract_payload_by_job(
    job_id: str,
    user_id: str = Depends(verify_token),
):
    """
    Extract LSB payload from an already-scanned image. 
    Fetches the original file from MinIO by job_id, forwards it 
    to the Image Analysis Service extraction engine. No re-upload needed.
    """
    try:
        # Verify job belongs to user
        job_response = service_client.table("scan_jobs") \
            .select("file_name, mime_type") \
            .eq("id", job_id) \
            .eq("user_id", user_id) \
            .execute()

        if not job_response.data:
            raise HTTPException(status_code=404, detail="Scan job not found")

        file_name = job_response.data[0]["file_name"]
        mime_type = job_response.data[0]["mime_type"] or "application/octet-stream"
        object_name = f"{job_id}_{file_name}"

        # Fetch file from MinIO
        file_bytes = download_file_bytes("originals", object_name)
        if not file_bytes:
            raise HTTPException(status_code=404, detail="Original file not found in storage.")

        # Forward to Image Analysis Service for extraction
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.IMAGE_ANALYSIS_URL}/api/extract-lsb",
                files={"file": (file_name, file_bytes, mime_type)},
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Extraction engine error: {response.text}",
                )

            return response.json()

    except HTTPException:
        raise
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Image Analysis Service is offline.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

