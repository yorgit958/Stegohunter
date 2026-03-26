"""
Batch analysis endpoint — accepts multiple image files.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List
from app.classifiers.ensemble import get_ensemble_classifier
from app.utils.image_loader import load_image_from_bytes, get_image_info
from app.schemas.analysis_request import AnalysisResponse, BatchAnalysisResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".gif", ".webp"}
MAX_BATCH_SIZE = 20


@router.post("/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze(
    files: List[UploadFile] = File(..., description="Multiple image files to analyze"),
    threshold: float = Query(default=0.65, ge=0.0, le=1.0),
):
    """
    Analyze multiple images for steganographic content in a single request.
    Maximum 20 files per batch.
    """
    if len(files) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_BATCH_SIZE} files per batch",
        )

    classifier = get_ensemble_classifier(threshold=threshold)
    results: List[AnalysisResponse] = []
    threats_found = 0
    analyzed = 0

    for file in files:
        import os
        filename = file.filename or "unknown"
        _, ext = os.path.splitext(filename.lower())

        if ext not in ALLOWED_EXTENSIONS:
            continue

        file_bytes = await file.read()
        if len(file_bytes) == 0:
            continue

        image = load_image_from_bytes(file_bytes)
        if image is None:
            continue

        img_info = get_image_info(image)
        result = classifier.analyze(image)
        analyzed += 1

        if result.is_stego:
            threats_found += 1

        results.append(AnalysisResponse(
            filename=filename,
            is_stego=result.is_stego,
            confidence=result.confidence,
            threat_level=result.threat_level,
            ensemble_score=result.ensemble_score,
            threshold=result.threshold,
            engine_results=result.engine_results,
            detection_methods=result.detection_methods,
            image_info=img_info,
        ))

    return BatchAnalysisResponse(
        total_files=len(files),
        analyzed=analyzed,
        threats_found=threats_found,
        results=results,
    )
