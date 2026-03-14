import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class DamageAssessment(Base):
    __tablename__ = "damage_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    photo_id = Column(UUID(as_uuid=True), ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    damage_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    location_description = Column(Text)
    affected_area_pct = Column(Float)
    repair_urgency = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    photo = relationship("Photo", back_populates="damage_assessments")
