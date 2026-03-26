from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, List
import io
import json
from PIL import Image

from app.selector.strategy_selector import StrategySelector
from app.selector.strategy_registry import StrategyRegistry
from app.integrity.ssim_checker import IntegrityChecker

router = APIRouter()
integrity_checker = IntegrityChecker()

@router.post("/process")
async def neutralize_image(
    file: UploadFile = File(..., description="Image file to neutralize"),
    analysis_results: str = Form(..., description="JSON string from Image Analysis Service"),
    force_strategies: Optional[str] = Form(None, description="Comma-separated list of strategies to force"),
):
    """
    Core neutralization endpoint.
    Retrieves the analysis results, selects the optimal scrubber chain,
    applies them, validates structural integrity, and returns the Safe image.
    """
    # 1. Parse image
    try:
        file_bytes = await file.read()
        image = Image.open(io.BytesIO(file_bytes))
        
        # Ensure we don't accidentally close the image via file pointer
        image.load()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {e}")

    # 2. Parse analysis results
    try:
        results_data = json.loads(analysis_results)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid analysis_results JSON: {e}")

    # 3. Determine Strategy
    try:
        if force_strategies:
            names = [s.strip() for s in force_strategies.split(",") if s.strip()]
            strategy = StrategyRegistry.build_composite(names)
        else:
            strategy = StrategySelector.select_optimal_strategies(results_data)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Strategy selection error: {e}")

    # 4. Apply Neutralization
    try:
        scrubbed_image = strategy.apply(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neutralization failure: {e}")

    # 5. Verify Integrity
    metrics = integrity_checker.evaluate(image, scrubbed_image)
    
    # Optional: If integrity fails terribly, we might want to log it or raise an alert.
    # For now, we return it anyway since a slightly degraded image is better than a payload.

    # 6. Encode for transport
    out_buffer = io.BytesIO()
    # Save using the original format if possible, default to PNG to avoid lossy double-compression
    fmt = image.format or "PNG"
    if fmt == "JPEG":
        scrubbed_image.save(out_buffer, format="JPEG", quality=95)
    else:
        scrubbed_image.save(out_buffer, format="PNG")
        
    out_buffer.seek(0)
    
    # In a full microservices architecture, we could return a multipart response 
    # (the image file + the JSON metrics). FastAPI handles this cleanly using
    # a custom response class, or we can just return the JSON with base64 encoded image.
    # For speed and ease, we'll return a JSON response with base64 for now, 
    # or just the metrics and upload to MinIO directly.
    import base64
    b64_img = base64.b64encode(out_buffer.getvalue()).decode('utf-8')

    # Reconstruct what strategies were actually used
    applied_strategies = []
    if hasattr(strategy, 'strategies'):
        applied_strategies = [s.name for s in strategy.strategies]
    else:
        applied_strategies = [strategy.name]

    return {
        "status": "success",
        "applied_strategies": applied_strategies,
        "integrity_metrics": metrics,
        "mime_type": f"image/{fmt.lower()}",
        "scrubbed_base64": b64_img
    }
