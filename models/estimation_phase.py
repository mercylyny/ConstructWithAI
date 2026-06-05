from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db import Base

class EstimationPhase(Base):
    __tablename__ = "estimation_phases"

    id = Column(Integer, primary_key=True, index=True)
    estimation_id = Column(Integer, ForeignKey("estimations.id"), nullable=False, index=True)
    phase_name = Column(String, nullable=False)
    cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    estimation = relationship("Estimation", back_populates="phases")
