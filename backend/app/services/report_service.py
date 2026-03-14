from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models.project import Project
from app.models.photo import Photo
from app.models.classification import Classification
from app.models.damage_assessment import DamageAssessment
from app.models.detection import Detection
from app.models.correction import Correction


def generate_project_report(db: Session, project_id: UUID) -> dict:
    """Generate aggregate report for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Total photos
    total_photos = db.query(Photo).filter(Photo.project_id == project_id).count()

    # Material summary - aggregate quantity by subcategory
    photo_ids = [
        p.id for p in db.query(Photo.id).filter(Photo.project_id == project_id).all()
    ]

    material_summary = []
    if photo_ids:
        materials = (
            db.query(
                Classification.subcategory,
                func.sum(Classification.quantity_estimate).label("total"),
                Classification.unit,
            )
            .filter(
                Classification.photo_id.in_(photo_ids),
                Classification.category == "material",
                Classification.quantity_estimate.isnot(None),
            )
            .group_by(Classification.subcategory, Classification.unit)
            .all()
        )
        for mat in materials:
            material_summary.append({
                "material": mat[0] or "unknown",
                "total_count": float(mat[1] or 0),
                "unit": mat[2],
            })

    # Damage summary
    damage_summary = []
    if photo_ids:
        damages = (
            db.query(
                DamageAssessment.damage_type,
                DamageAssessment.severity,
                func.count(DamageAssessment.id).label("count"),
            )
            .filter(DamageAssessment.photo_id.in_(photo_ids))
            .group_by(DamageAssessment.damage_type, DamageAssessment.severity)
            .all()
        )
        for dmg in damages:
            damage_summary.append({
                "type": dmg[0],
                "severity": dmg[1],
                "count": dmg[2],
            })

    # Correction stats
    total_detections = (
        db.query(Detection).filter(Detection.photo_id.in_(photo_ids)).count()
        if photo_ids
        else 0
    )
    corrections_made = (
        db.query(Correction).filter(Correction.photo_id.in_(photo_ids)).count()
        if photo_ids
        else 0
    )
    accuracy_rate = (
        round(1.0 - (corrections_made / total_detections), 3)
        if total_detections > 0
        else 1.0
    )

    return {
        "project_id": project.id,
        "project_name": project.name,
        "total_photos": total_photos,
        "material_summary": material_summary,
        "damage_summary": damage_summary,
        "correction_stats": {
            "total_detections": total_detections,
            "corrections_made": corrections_made,
            "accuracy_rate": accuracy_rate,
        },
    }
