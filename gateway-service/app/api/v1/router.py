from fastapi import APIRouter
from app.api.v1 import auth, scan, health, neutralize

api_router = APIRouter()

# Include all the sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(scan.router)
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(neutralize.router)

