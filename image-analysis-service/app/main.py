from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.analyze import router as analyze_router
from app.api.health import router as health_router
from app.api.batch import router as batch_router

app = FastAPI(
    title="StegoHunter Image Analysis Service",
    version="1.0.0",
    description="Steganography detection engine using statistical analysis and ensemble classification",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(analyze_router, prefix="/api", tags=["Analysis"])
app.include_router(batch_router, prefix="/api", tags=["Batch"])


@app.get("/")
def root():
    return {
        "service": "StegoHunter Image Analysis",
        "version": "1.0.0",
        "status": "online",
    }
