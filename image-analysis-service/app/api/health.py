"""
Health check endpoint for the Image Analysis Service.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Service health check."""
    return {
        "status": "healthy",
        "service": "image-analysis-service",
        "engines": [
            "Chi-Square Analysis",
            "RS Analysis",
            "SPA Analysis",
            "DCT Analysis",
            "Visual Attack",
        ],
    }
