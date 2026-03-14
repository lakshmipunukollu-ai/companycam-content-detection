"""
Two-stage photo analysis pipeline.
Stage 1: Object detection (YOLO or mock) -> bounding boxes + classes
Stage 2: Claude Vision -> semantic classification + quantity estimation + damage assessment
"""
from typing import Dict, Any, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.config import settings
from app.detector.object_detector import ObjectDetector
from app.detector.claude_annotator import ClaudeAnnotator
from app.models.detection import Detection
from app.models.classification import Classification
from app.models.damage_assessment import DamageAssessment
from app.models.photo import Photo


REVIEW_THRESHOLD = 0.7


class PhotoAnalysisPipeline:
    """
    Two-stage detection pipeline:
    1. Object detection (YOLO or mock) for fast bounding box detection
    2. Claude Vision for semantic classification and assessment
    """

    def __init__(self):
        self.object_detector = ObjectDetector(model_path=settings.YOLO_MODEL_PATH)
        self.claude_annotator = ClaudeAnnotator()

    async def analyze(
        self,
        photo: Photo,
        db: Session,
    ) -> Dict[str, Any]:
        """Run the full two-stage analysis pipeline."""
        # Update photo status
        photo.status = "analyzing"
        db.commit()

        try:
            # Stage 1: Object detection
            cv_detections = self.object_detector.detect(
                photo.file_path, photo.photo_type
            )

            # Save CV detections to DB
            db_detections = []
            for det in cv_detections:
                db_det = Detection(
                    photo_id=photo.id,
                    stage="cv",
                    label=det["label"],
                    confidence=det["confidence"],
                    bbox_x=det["bbox"]["x"],
                    bbox_y=det["bbox"]["y"],
                    bbox_w=det["bbox"]["w"],
                    bbox_h=det["bbox"]["h"],
                )
                db.add(db_det)
                db_detections.append(db_det)

            db.flush()

            # Stage 2: Claude Vision annotation
            llm_result = await self.claude_annotator.annotate(
                photo.file_path, cv_detections, photo.photo_type
            )

            # Save classifications
            requires_review = False
            db_classifications = []
            for cls_data in llm_result.get("classifications", []):
                confidence = cls_data.get("confidence", 0.5)
                needs_review = confidence < REVIEW_THRESHOLD
                if needs_review:
                    requires_review = True

                db_cls = Classification(
                    photo_id=photo.id,
                    category=cls_data.get("category", "unknown"),
                    subcategory=cls_data.get("subcategory"),
                    description=cls_data.get("description"),
                    severity=cls_data.get("severity"),
                    quantity_estimate=cls_data.get("quantity_estimate"),
                    unit=cls_data.get("unit"),
                    confidence=confidence,
                    requires_review=needs_review,
                )
                db.add(db_cls)
                db_classifications.append(db_cls)

            # Save damage assessment if present
            db_damage = None
            damage_data = llm_result.get("damage_assessment")
            if damage_data:
                db_damage = DamageAssessment(
                    photo_id=photo.id,
                    damage_type=damage_data.get("damage_type", "unknown"),
                    severity=damage_data.get("severity", "unknown"),
                    location_description=damage_data.get("location_description"),
                    affected_area_pct=damage_data.get("affected_area_pct"),
                    repair_urgency=damage_data.get("repair_urgency"),
                    notes=damage_data.get("notes"),
                )
                db.add(db_damage)

            # Update photo status
            photo.status = "completed"
            db.commit()

            return {
                "detections": db_detections,
                "classifications": db_classifications,
                "damage_assessment": db_damage,
                "requires_human_review": requires_review,
            }

        except Exception as e:
            photo.status = "failed"
            db.commit()
            raise e


# Singleton pipeline instance
pipeline = PhotoAnalysisPipeline()
