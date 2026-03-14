import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Classification(Base):
    __tablename__ = "classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    photo_id = Column(UUID(as_uuid=True), ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    description = Column(Text)
    severity = Column(String(50))
    quantity_estimate = Column(Float)
    unit = Column(String(50))
    confidence = Column(Float, nullable=False)
    requires_review = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    photo = relationship("Photo", back_populates="classifications")
