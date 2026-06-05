from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db import Base

class Estimation(Base):
    __tablename__ = "estimations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    total_bricks = Column(Integer)
    total_mortar_volume = Column(Float)
    total_cost = Column(Float)
    grand_total = Column(Float, default=0.0)
    boq_excel_path = Column(String, nullable=True)
    boq_pdf_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship back to Project
    project = relationship("Project", back_populates="estimations")
    phases = relationship("EstimationPhase", back_populates="estimation")
