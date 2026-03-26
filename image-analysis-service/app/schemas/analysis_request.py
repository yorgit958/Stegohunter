"""Pydantic schemas for analysis request payloads."""

from pydantic import BaseModel, Field
from typing import Optional


class AnalysisConfig(BaseModel):
    """Optional configuration for the analysis."""
    threshold: float = Field(default=0.65, ge=0.0, le=1.0, description="Detection threshold")
    engines: Optional[list[str]] = Field(default=None, description="Specific engines to run (null = all)")


class AnalysisResponse(BaseModel):
    """Response schema for a single image analysis."""
    filename: str
    is_stego: bool
    confidence: float
    threat_level: str
    ensemble_score: float
    threshold: float
    engine_results: list[dict]
    detection_methods: list[str]
    image_info: dict

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "suspicious_image.png",
                "is_stego": True,
                "confidence": 0.87,
                "threat_level": "high",
                "ensemble_score": 0.78,
                "threshold": 0.65,
                "engine_results": [],
                "detection_methods": ["Chi-Square Analysis", "RS Analysis"],
                "image_info": {"width": 512, "height": 512, "channels": 3},
            }
        }


class BatchAnalysisResponse(BaseModel):
    """Response schema for batch analysis."""
    total_files: int
    analyzed: int
    threats_found: int
    results: list[AnalysisResponse]
