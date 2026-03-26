from app.api.analyze import router as analyze_router
from app.api.batch import router as batch_router
from app.api.health import router as health_router

__all__ = ["analyze_router", "batch_router", "health_router"]
