from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.supabase_client import supabase_client
from app.api.v1 import auth, scan, neutralize, dnn, admin

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API Gateway for the Stego-Hunter Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:8080", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(scan.router, prefix="/api/v1")
app.include_router(neutralize.router, prefix="/api/v1")
app.include_router(dnn.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.get("/health/db")
def health_db():
    # Attempt a lightweight query to verify Supabase connection
    try:
        # We query the profiles table to see if it responds (could require RLS bypassing for true health check,
        # but a simple select with limit 0 tests connectivity without needing rows or permissions)
        response = supabase_client.table('profiles').select('*').limit(0).execute()
        return {"status": "ok", "message": "Successfully connected to Supabase"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
