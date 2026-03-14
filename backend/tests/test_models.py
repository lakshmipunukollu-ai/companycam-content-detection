"""Tests for SQLAlchemy models."""
import uuid
import pytest

from app.models.user import User
from app.models.project import Project
from app.models.photo import Photo
from app.models.detection import Detection
from app.models.classification import Classification
from app.models.damage_assessment import DamageAssessment
from app.models.correction import Correction
from app.auth.jwt_handler import hash_password


def test_user_model(db_session):
    """User model creates with expected fields."""
    user = User(
        email="model@test.com",
        hashed_password=hash_password("pass"),
        full_name="Model Test",
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == "model@test.com"
    assert user.role == "admin"
    assert user.created_at is not None


def test_project_model(db_session, test_user):
    """Project model creates with owner relationship."""
    user, _ = test_user
    project = Project(
        name="Model Project",
        description="Testing",
        owner_id=user.id,
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    assert project.id is not None
    assert project.status == "active"
    assert project.owner_id == user.id


def test_photo_model(db_session, test_project, test_user):
    """Photo model creates with relationships."""
    user, _ = test_user
    photo = Photo(
        project_id=test_project.id,
        uploaded_by=user.id,
        filename="model_test.jpg",
        file_path="/tmp/model_test.jpg",
        photo_type="delivery",
    )
    db_session.add(photo)
    db_session.commit()
    db_session.refresh(photo)

    assert photo.id is not None
    assert photo.status == "pending"
    assert photo.photo_type == "delivery"


def test_detection_model(db_session, test_photo):
    """Detection model stores bounding box data."""
    detection = Detection(
        photo_id=test_photo.id,
        stage="cv",
        label="test_object",
        confidence=0.95,
        bbox_x=10.0,
        bbox_y=20.0,
        bbox_w=100.0,
        bbox_h=50.0,
    )
    db_session.add(detection)
    db_session.commit()
    db_session.refresh(detection)

    assert detection.id is not None
    assert detection.label == "test_object"
    assert detection.confidence == 0.95
    assert detection.bbox_x == 10.0


def test_classification_model(db_session, test_photo):
    """Classification model stores category data."""
    cls = Classification(
        photo_id=test_photo.id,
        category="damage",
        subcategory="wind_damage",
        description="Wind-related shingle loss",
        severity="medium",
        confidence=0.8,
        requires_review=True,
    )
    db_session.add(cls)
    db_session.commit()
    db_session.refresh(cls)

    assert cls.id is not None
    assert cls.category == "damage"
    assert cls.requires_review is True


def test_damage_assessment_model(db_session, test_photo):
    """DamageAssessment model stores damage data."""
    da = DamageAssessment(
        photo_id=test_photo.id,
        damage_type="granule_loss",
        severity="low",
        affected_area_pct=5.0,
        repair_urgency="routine",
    )
    db_session.add(da)
    db_session.commit()
    db_session.refresh(da)

    assert da.id is not None
    assert da.damage_type == "granule_loss"
    assert da.severity == "low"


def test_correction_model(db_session, test_photo, test_detection, test_user):
    """Correction model stores correction data."""
    user, _ = test_user
    correction = Correction(
        detection_id=test_detection.id,
        photo_id=test_photo.id,
        corrected_by=user.id,
        original_label="shingle_bundle",
        corrected_label="ridge_cap",
        correction_type="label",
        notes="Wrong label",
    )
    db_session.add(correction)
    db_session.commit()
    db_session.refresh(correction)

    assert correction.id is not None
    assert correction.original_label == "shingle_bundle"
    assert correction.corrected_label == "ridge_cap"
