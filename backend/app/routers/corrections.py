from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.jwt_handler import get_current_user
from app.models.user import User
from app.models.photo import Photo
from app.models.detection import Detection
from app.models.correction import Correction
from app.schemas.correction import CorrectionCreate, CorrectionResponse

router = APIRouter(prefix="/photos", tags=["corrections"])


@router.post("/{photo_id}/corrections", response_model=CorrectionResponse)
def create_correction(
    photo_id: UUID,
    data: CorrectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    original_label = None
    original_bbox = None

    if data.detection_id:
        detection = db.query(Detection).filter(Detection.id == data.detection_id).first()
        if not detection:
            raise HTTPException(status_code=404, detail="Detection not found")
        original_label = detection.label
        original_bbox = {
            "x": detection.bbox_x,
            "y": detection.bbox_y,
            "w": detection.bbox_w,
            "h": detection.bbox_h,
        }

    correction = Correction(
        detection_id=data.detection_id,
        photo_id=photo_id,
        corrected_by=current_user.id,
        original_label=original_label,
        corrected_label=data.corrected_label,
        original_bbox=original_bbox,
        corrected_bbox=data.corrected_bbox,
        correction_type=data.correction_type,
        notes=data.notes,
    )
    db.add(correction)
    db.commit()
    db.refresh(correction)
    return correction


@router.get("/{photo_id}/corrections", response_model=List[CorrectionResponse])
def get_corrections(
    photo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    corrections = (
        db.query(Correction)
        .filter(Correction.photo_id == photo_id)
        .order_by(Correction.created_at.desc())
        .all()
    )
    return corrections
