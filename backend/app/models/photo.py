import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    photo_type = Column(String(50), default="general")
    status = Column(String(50), default="pending")
    width = Column(Integer)
    height = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="photos")
    uploader = relationship("User", back_populates="photos")
    detections = relationship("Detection", back_populates="photo", cascade="all, delete-orphan")
    classifications = relationship("Classification", back_populates="photo", cascade="all, delete-orphan")
    corrections = relationship("Correction", back_populates="photo", cascade="all, delete-orphan")
    damage_assessments = relationship("DamageAssessment", back_populates="photo", cascade="all, delete-orphan")
