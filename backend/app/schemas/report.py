from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class MaterialSummary(BaseModel):
    material: str
    total_count: float
    unit: Optional[str]


class DamageSummary(BaseModel):
    type: str
    severity: str
    count: int


class CorrectionStats(BaseModel):
    total_detections: int
    corrections_made: int
    accuracy_rate: float


class ProjectReport(BaseModel):
    project_id: UUID
    project_name: str
    total_photos: int
    material_summary: List[MaterialSummary]
    damage_summary: List[DamageSummary]
    correction_stats: CorrectionStats
