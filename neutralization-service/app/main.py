import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import neutralize

app = FastAPI(
    title="StegoHunter Neutralization Service",
    description="Microservice dedicated to scrubbing steganographic payloads from images.",
    version="1.0.0",
)

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core neutralization routes
app.include_router(neutralize.router, prefix="/api/neutralize", tags=["Neutralization"])

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "StegoHunter Neutralization Service",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
