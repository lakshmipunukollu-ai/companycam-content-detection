from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime


class CorrectionCreate(BaseModel):
    detection_id: Optional[UUID] = None
    correction_type: str  # label, bbox, delete, add
    corrected_label: Optional[str] = None
    corrected_bbox: Optional[Dict[str, float]] = None
    notes: Optional[str] = None


class CorrectionResponse(BaseModel):
    id: UUID
    detection_id: Optional[UUID]
    photo_id: UUID
    corrected_by: UUID
    original_label: Optional[str]
    corrected_label: Optional[str]
    original_bbox: Optional[dict]
    corrected_bbox: Optional[dict]
    correction_type: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
