from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class PhotoResponse(BaseModel):
    id: UUID
    project_id: UUID
    uploaded_by: UUID
    filename: str
    file_path: str
    photo_type: str
    status: str
    width: Optional[int]
    height: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class BBox(BaseModel):
    x: float
    y: float
    w: float
    h: float


class DetectionResponse(BaseModel):
    id: UUID
    label: str
    confidence: float
    bbox: BBox
    stage: str

    class Config:
        from_attributes = True


class ClassificationResponse(BaseModel):
    id: UUID
    category: str
    subcategory: Optional[str]
    description: Optional[str]
    severity: Optional[str]
    quantity_estimate: Optional[float]
    unit: Optional[str]
    confidence: float
    requires_review: bool

    class Config:
        from_attributes = True


class DamageAssessmentResponse(BaseModel):
    id: UUID
    damage_type: str
    severity: str
    location_description: Optional[str]
    affected_area_pct: Optional[float]
    repair_urgency: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class PhotoAnalysisResult(BaseModel):
    photo_id: UUID
    status: str
    detections: List[DetectionResponse]
    classifications: List[ClassificationResponse]
    damage_assessments: List[DamageAssessmentResponse]
    requires_human_review: bool
