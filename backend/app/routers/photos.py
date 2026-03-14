from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.jwt_handler import get_current_user
from app.models.user import User
from app.models.photo import Photo
from app.models.detection import Detection
from app.models.classification import Classification
from app.models.damage_assessment import DamageAssessment
from app.schemas.photo import (
    PhotoResponse,
    PhotoAnalysisResult,
    DetectionResponse,
    ClassificationResponse,
    DamageAssessmentResponse,
    BBox,
)
from app.services.photo_service import save_photo
from app.detector.pipeline import pipeline

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/upload", response_model=PhotoResponse)
async def upload_photo(
    file: UploadFile = File(...),
    project_id: UUID = Form(...),
    photo_type: str = Form("general"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = await save_photo(file, project_id, photo_type, current_user.id, db)
    return photo


@router.post("/analyze", response_model=PhotoAnalysisResult)
async def analyze_photo(
    photo_id: UUID = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    result = await pipeline.analyze(photo, db)

    detections = _format_detections(result["detections"])
    classifications = _format_classifications(result["classifications"])
    damage_assessments = []
    if result.get("damage_assessment"):
        damage_assessments = [_format_damage(result["damage_assessment"])]

    return PhotoAnalysisResult(
        photo_id=photo.id,
        status=photo.status,
        detections=detections,
        classifications=classifications,
        damage_assessments=damage_assessments,
        requires_human_review=result.get("requires_human_review", False),
    )


@router.get("/{photo_id}", response_model=PhotoResponse)
def get_photo(
    photo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.get("/{photo_id}/results", response_model=PhotoAnalysisResult)
def get_photo_results(
    photo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    db_detections = db.query(Detection).filter(Detection.photo_id == photo_id).all()
    db_classifications = db.query(Classification).filter(Classification.photo_id == photo_id).all()
    db_damages = db.query(DamageAssessment).filter(DamageAssessment.photo_id == photo_id).all()

    detections = _format_detections(db_detections)
    classifications = _format_classifications(db_classifications)
    damage_assessments = [_format_damage(d) for d in db_damages]

    requires_review = any(c.requires_review for c in db_classifications)

    return PhotoAnalysisResult(
        photo_id=photo.id,
        status=photo.status,
        detections=detections,
        classifications=classifications,
        damage_assessments=damage_assessments,
        requires_human_review=requires_review,
    )


@router.get("", response_model=List[PhotoResponse])
def list_photos(
    project_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Photo).filter(Photo.uploaded_by == current_user.id)
    if project_id:
        query = query.filter(Photo.project_id == project_id)
    if status:
        query = query.filter(Photo.status == status)
    return query.order_by(Photo.created_at.desc()).all()


@router.delete("/{photo_id}")
def delete_photo(
    photo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = db.query(Photo).filter(
        Photo.id == photo_id, Photo.uploaded_by == current_user.id
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    db.delete(photo)
    db.commit()
    return {"message": "Photo deleted"}


def _format_detections(detections) -> List[DetectionResponse]:
    return [
        DetectionResponse(
            id=d.id,
            label=d.label,
            confidence=d.confidence,
            bbox=BBox(x=d.bbox_x, y=d.bbox_y, w=d.bbox_w, h=d.bbox_h),
            stage=d.stage,
        )
        for d in detections
    ]


def _format_classifications(classifications) -> List[ClassificationResponse]:
    return [
        ClassificationResponse(
            id=c.id,
            category=c.category,
            subcategory=c.subcategory,
            description=c.description,
            severity=c.severity,
            quantity_estimate=c.quantity_estimate,
            unit=c.unit,
            confidence=c.confidence,
            requires_review=c.requires_review,
        )
        for c in classifications
    ]


def _format_damage(damage) -> DamageAssessmentResponse:
    return DamageAssessmentResponse(
        id=damage.id,
        damage_type=damage.damage_type,
        severity=damage.severity,
        location_description=damage.location_description,
        affected_area_pct=damage.affected_area_pct,
        repair_urgency=damage.repair_urgency,
        notes=damage.notes,
    )
