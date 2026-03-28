"""
Admin API endpoints for StegoHunter.

Provides system-wide statistics, user management, audit log access,
and service health monitoring for administrators.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.api.dependencies import verify_token
from app.core.supabase_client import service_client
from app.core.config import settings
import httpx

router = APIRouter(prefix="/admin", tags=["Admin"])


async def _verify_admin(user_id: str = Depends(verify_token)) -> str:
    """Verify user has admin role. Raises 403 if not admin."""
    try:
        res = service_client.table("profiles") \
            .select("role") \
            .eq("id", user_id) \
            .execute()
        if res.data and res.data[0].get("role") == "admin":
            return user_id
    except Exception:
        pass
    raise HTTPException(status_code=403, detail="Admin access required")


class RoleUpdate(BaseModel):
    target_user_id: str
    new_role: str  # "admin" or "analyst"


@router.patch("/users/role")
async def update_user_role(
    body: RoleUpdate,
    user_id: str = Depends(_verify_admin),
):
    """Promote or demote a user. Only admins can use this."""
    if body.new_role not in ("admin", "analyst"):
        raise HTTPException(status_code=400, detail="Role must be 'admin' or 'analyst'")

    # Prevent self-demotion (last remaining admin protection)
    if body.target_user_id == user_id and body.new_role != "admin":
        # Check if there would be zero admins left
        all_admins = service_client.table("profiles") \
            .select("id") \
            .eq("role", "admin") \
            .execute()
        if len(all_admins.data or []) <= 1:
            raise HTTPException(status_code=400, detail="Cannot demote yourself — you are the last admin")

    try:
        res = service_client.table("profiles") \
            .update({"role": body.new_role}) \
            .eq("id", body.target_user_id) \
            .execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True, "user": res.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_system_stats(user_id: str = Depends(_verify_admin)):
    """Get system-wide statistics for the admin dashboard."""
    try:
        # Total scan jobs across ALL users
        all_jobs = service_client.table("scan_jobs") \
            .select("id, status, job_type, created_at, file_size_bytes") \
            .execute()
        jobs = all_jobs.data or []

        total_scans = len(jobs)
        completed = sum(1 for j in jobs if j["status"] == "completed")
        failed = sum(1 for j in jobs if j["status"] == "failed")
        pending = sum(1 for j in jobs if j["status"] in ("pending", "analyzing"))
        image_scans = sum(1 for j in jobs if j.get("job_type") == "image")
        dnn_scans = sum(1 for j in jobs if j.get("job_type") == "dnn_model")
        total_data_bytes = sum(j.get("file_size_bytes", 0) or 0 for j in jobs)

        # Scan results across all users
        all_results = service_client.table("scan_results") \
            .select("is_stego, threat_level") \
            .execute()
        results = all_results.data or []

        threats_found = sum(1 for r in results if r.get("is_stego"))
        clean = sum(1 for r in results if not r.get("is_stego"))

        threat_levels = {
            "critical": sum(1 for r in results if r.get("threat_level") == "critical"),
            "high": sum(1 for r in results if r.get("threat_level") == "high"),
            "medium": sum(1 for r in results if r.get("threat_level") == "medium"),
            "low": sum(1 for r in results if r.get("threat_level") == "low"),
            "none": sum(1 for r in results if r.get("threat_level") == "none"),
        }

        # Total registered users
        all_profiles = service_client.table("profiles") \
            .select("id, role, is_active, created_at") \
            .execute()
        profiles = all_profiles.data or []

        total_users = len(profiles)
        active_users = sum(1 for p in profiles if p.get("is_active"))
        admin_count = sum(1 for p in profiles if p.get("role") == "admin")

        # Neutralization jobs
        all_neutral = service_client.table("neutralization_jobs") \
            .select("id, status") \
            .execute()
        neutral_jobs = all_neutral.data or []
        neutralized_count = sum(1 for n in neutral_jobs if n["status"] == "completed")

        return {
            "scans": {
                "total": total_scans,
                "completed": completed,
                "failed": failed,
                "pending": pending,
                "image_scans": image_scans,
                "dnn_scans": dnn_scans,
                "total_data_processed_mb": round(total_data_bytes / (1024 * 1024), 2),
            },
            "threats": {
                "total_detected": threats_found,
                "clean": clean,
                "levels": threat_levels,
            },
            "users": {
                "total": total_users,
                "active": active_users,
                "admins": admin_count,
            },
            "neutralization": {
                "total_neutralized": neutralized_count,
                "total_jobs": len(neutral_jobs),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def list_users(
    user_id: str = Depends(_verify_admin),
    limit: int = Query(default=50, ge=1, le=200),
):
    """List all users in the system."""
    try:
        res = service_client.table("profiles") \
            .select("id, username, role, is_active, created_at, updated_at") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return {"users": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit-log")
async def get_audit_log(
    user_id: str = Depends(_verify_admin),
    limit: int = Query(default=50, ge=1, le=200),
):
    """Get recent audit log entries."""
    try:
        res = service_client.table("audit_log") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return {"entries": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-scans")
async def get_recent_scans(
    user_id: str = Depends(_verify_admin),
    limit: int = Query(default=10, ge=1, le=50),
):
    """Get recent scans across all users for admin overview."""
    try:
        res = service_client.table("scan_jobs") \
            .select("*, scan_results(is_stego, confidence, threat_level)") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        jobs = res.data or []
        for job in jobs:
            results = job.pop("scan_results", [])
            if results and len(results) > 0:
                job["is_stego"] = results[0].get("is_stego", False)
                job["confidence"] = results[0].get("confidence", 0.0)
                job["threat_level"] = results[0].get("threat_level", "none")
            else:
                job["is_stego"] = None
                job["confidence"] = None
                job["threat_level"] = None

        return {"scans": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def check_services_health(user_id: str = Depends(_verify_admin)):
    """Check health of all microservices."""
    services = {
        "gateway": {"url": "http://localhost:8000", "status": "online"},  # We're already here
        "image_analysis": {"url": settings.IMAGE_ANALYSIS_URL, "status": "unknown"},
        "neutralization": {"url": getattr(settings, "NEUTRALIZATION_URL", "http://localhost:8002"), "status": "unknown"},
        "dnn_defense": {"url": getattr(settings, "DNN_DEFENSE_URL", "http://localhost:8003"), "status": "unknown"},
    }

    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, info in services.items():
            if name == "gateway":
                continue
            try:
                resp = await client.get(f"{info['url']}/")
                services[name]["status"] = "online" if resp.status_code == 200 else "degraded"
            except Exception:
                services[name]["status"] = "offline"

    return {"services": services}
