import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Correction(Base):
    __tablename__ = "corrections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detection_id = Column(UUID(as_uuid=True), ForeignKey("detections.id", ondelete="CASCADE"))
    photo_id = Column(UUID(as_uuid=True), ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    corrected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    original_label = Column(String(255))
    corrected_label = Column(String(255))
    original_bbox = Column(JSONB)
    corrected_bbox = Column(JSONB)
    correction_type = Column(String(50), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    detection = relationship("Detection", back_populates="corrections")
    photo = relationship("Photo", back_populates="corrections")
    corrector = relationship("User", back_populates="corrections")
