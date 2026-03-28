"""
WebSocket Connection Manager + Redis PubSub Listener
Provides real-time scan progress updates to authenticated frontend clients.
"""
import asyncio
import json
import os
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis

router = APIRouter()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class ConnectionManager:
    """Manages active WebSocket connections keyed by user_id."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"[WS] User {user_id[:8]} connected. Total connections: {sum(len(v) for v in self.active_connections.values())}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                ws for ws in self.active_connections[user_id] if ws != websocket
            ]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"[WS] User {user_id[:8]} disconnected.")

    async def send_to_user(self, user_id: str, message: dict):
        """Send a JSON message to all WebSocket connections for a specific user."""
        if user_id in self.active_connections:
            dead = []
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            # Clean up dead connections
            for ws in dead:
                self.active_connections[user_id].remove(ws)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users."""
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time scan progress updates.
    The frontend connects here with the user's ID and receives
    live events pushed from the Gateway via Redis Pub/Sub.
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep the connection alive — listen for client pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


async def redis_listener():
    """
    Background task that subscribes to the 'scan_events' Redis channel
    and routes messages to the appropriate WebSocket connections.
    """
    try:
        redis = aioredis.from_url(REDIS_URL, decode_responses=True)
        pubsub = redis.pubsub()
        await pubsub.subscribe("scan_events")
        print("[Redis PubSub] Subscribed to 'scan_events' channel.")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    payload = json.loads(message["data"])
                    target_user = payload.get("user_id")
                    if target_user:
                        await manager.send_to_user(target_user, payload)
                    else:
                        await manager.broadcast(payload)
                except json.JSONDecodeError:
                    print(f"[Redis PubSub] Invalid JSON: {message['data']}")
    except Exception as e:
        print(f"[Redis PubSub] Connection error: {e}. Retrying in 5s...")
        await asyncio.sleep(5)
        # Retry connection
        asyncio.create_task(redis_listener())
