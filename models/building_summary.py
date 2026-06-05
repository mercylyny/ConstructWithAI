from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db import Base

class BuildingSummaryRecord(Base):
    __tablename__ = "building_summaries"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    rooms = Column(Integer, default=0)
    bedrooms = Column(Integer, default=0)
    bathrooms = Column(Integer, default=0)
    kitchens = Column(Integer, default=0)
    walls = Column(Integer, default=0)
    doors = Column(Integer, default=0)
    windows = Column(Integer, default=0)
    columns = Column(Integer, default=0)
    beams = Column(Integer, default=0)
    stairs = Column(Integer, default=0)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="building_summaries")
