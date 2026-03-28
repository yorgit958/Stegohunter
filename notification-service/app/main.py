import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.websockets import router as ws_router, redis_listener

app = FastAPI(title="StegoHunter Notification Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the WebSocket router
app.include_router(ws_router)


@app.on_event("startup")
async def startup_event():
    """Launch the Redis PubSub listener as a background task on server boot."""
    asyncio.create_task(redis_listener())
    print("[Notification Service] Started Redis PubSub listener.")


@app.get("/")
def health_check():
    return {"status": "online", "service": "notification", "websocket": True}
