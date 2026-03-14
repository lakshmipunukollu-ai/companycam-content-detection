"""Seed the database with sample data for development."""
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.project import Project
from app.models.photo import Photo
from app.models.detection import Detection
from app.models.classification import Classification
from app.models.damage_assessment import DamageAssessment
from app.auth.jwt_handler import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if data exists
        if db.query(User).first():
            print("Database already seeded. Skipping.")
            return

        # Create users
        admin = User(
            email="admin@companycam.com",
            hashed_password=hash_password("admin123"),
            full_name="Admin User",
            role="admin",
        )
        contractor = User(
            email="contractor@companycam.com",
            hashed_password=hash_password("contractor123"),
            full_name="John Builder",
            role="contractor",
        )
        reviewer = User(
            email="reviewer@companycam.com",
            hashed_password=hash_password("reviewer123"),
            full_name="Jane Inspector",
            role="reviewer",
        )
        db.add_all([admin, contractor, reviewer])
        db.flush()

        # Create projects
        project1 = Project(
            name="Smith Residence Roof Replacement",
            description="Full roof replacement after hail damage",
            address="123 Oak Street, Denver, CO 80202",
            owner_id=contractor.id,
        )
        project2 = Project(
            name="Johnson Commercial Building",
            description="New construction - commercial roofing",
            address="456 Business Park Dr, Denver, CO 80203",
            owner_id=contractor.id,
        )
        db.add_all([project1, project2])
        db.flush()

        # Create sample photos
        photo1 = Photo(
            project_id=project1.id,
            uploaded_by=contractor.id,
            filename="roof_damage_01.jpg",
            file_path="./uploads/roof_damage_01.jpg",
            photo_type="roof",
            status="completed",
            width=1920,
            height=1080,
        )
        photo2 = Photo(
            project_id=project1.id,
            uploaded_by=contractor.id,
            filename="material_delivery_01.jpg",
            file_path="./uploads/material_delivery_01.jpg",
            photo_type="delivery",
            status="completed",
            width=1920,
            height=1080,
        )
        db.add_all([photo1, photo2])
        db.flush()

        # Create sample detections
        det1 = Detection(
            photo_id=photo1.id, stage="cv", label="damaged_shingle",
            confidence=0.92, bbox_x=120, bbox_y=80, bbox_w=200, bbox_h=150,
        )
        det2 = Detection(
            photo_id=photo1.id, stage="cv", label="hail_dent",
            confidence=0.87, bbox_x=350, bbox_y=200, bbox_w=100, bbox_h=80,
        )
        det3 = Detection(
            photo_id=photo2.id, stage="cv", label="shingle_bundle",
            confidence=0.95, bbox_x=50, bbox_y=100, bbox_w=300, bbox_h=200,
        )
        db.add_all([det1, det2, det3])

        # Create sample classifications
        cls1 = Classification(
            photo_id=photo1.id, category="damage", subcategory="hail_impact",
            description="Hail damage on asphalt shingles", severity="high",
            confidence=0.88, requires_review=False,
        )
        cls2 = Classification(
            photo_id=photo2.id, category="material", subcategory="shingle_bundle",
            description="Bundle of architectural shingles",
            quantity_estimate=12, unit="bundles",
            confidence=0.91, requires_review=False,
        )
        db.add_all([cls1, cls2])

        # Create sample damage assessment
        damage = DamageAssessment(
            photo_id=photo1.id,
            damage_type="hail_impact",
            severity="high",
            location_description="Northeast section near ridge line",
            affected_area_pct=25.5,
            repair_urgency="urgent",
        )
        db.add(damage)

        db.commit()
        print("Database seeded successfully!")
        print("Users: admin@companycam.com/admin123, contractor@companycam.com/contractor123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
