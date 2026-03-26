"""
Main analysis endpoint — accepts an image file and returns detection results.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.classifiers.ensemble import get_ensemble_classifier
from app.utils.image_loader import load_image_from_bytes, get_image_info
from app.schemas.analysis_request import AnalysisResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".gif", ".webp"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/extract-lsb")
async def extract_lsb_payload(
    file: UploadFile = File(..., description="Image file to extract LSB payload from"),
):
    """
    Attempts to extract human-readable ASCII text hidden in the 
    least significant bits of the image.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    image = load_image_from_bytes(file_bytes)
    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode image file")

    from app.engines.lsb_extractor import LSBExtractor
    payload = LSBExtractor.extract_ascii(image, file_bytes=file_bytes)
    
    return {"status": "success", "extracted_payload": payload}

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(..., description="Image file to analyze for steganography"),
    threshold: float = Query(default=0.65, ge=0.0, le=1.0, description="Detection threshold"),
):
    """
    Analyze a single image for steganographic content.

    Runs the full ensemble detection pipeline:
    - Chi-Square Analysis (30% weight)
    - RS Analysis (25% weight)
    - SPA Analysis (25% weight)
    - DCT Analysis (20% weight)
    - Visual Attack (supplementary)

    Returns a combined score with threat classification.
    """
    # Validate filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    import os
    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file bytes
    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    # Decode image
    image = load_image_from_bytes(file_bytes)
    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode image file")

    # Get image metadata
    img_info = get_image_info(image)

    # Run ensemble analysis
    classifier = get_ensemble_classifier(threshold=threshold)
    result = classifier.analyze(image)

    return AnalysisResponse(
        filename=file.filename,
        is_stego=result.is_stego,
        confidence=result.confidence,
        threat_level=result.threat_level,
        ensemble_score=result.ensemble_score,
        threshold=result.threshold,
        engine_results=result.engine_results,
        detection_methods=result.detection_methods,
        image_info=img_info,
    )
