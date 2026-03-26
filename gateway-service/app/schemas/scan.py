"""Pydantic schemas for scan jobs and results."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ScanJobCreate(BaseModel):
    """Schema for creating a scan job."""
    file_name: str
    file_size_bytes: int
    mime_type: Optional[str] = None
    job_type: str = "image"


class ScanJobResponse(BaseModel):
    """Schema for scan job response."""
    id: str
    status: str
    job_type: str
    file_name: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class ScanResultResponse(BaseModel):
    """Schema for scan result response."""
    id: str
    scan_job_id: str
    is_stego: bool
    confidence: float
    threat_level: Optional[str] = None
    detection_methods: Optional[dict] = None
    metadata: Optional[dict] = None
    created_at: Optional[str] = None


class ScanFullResponse(BaseModel):
    """Full response including job info + analysis results."""
    job: ScanJobResponse
    result: Optional[ScanResultResponse] = None
    analysis: Optional[dict] = None
