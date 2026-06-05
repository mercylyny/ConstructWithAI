from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    filename = Column(String, index=True)
    scale = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="projects")
    walls = relationship("Wall", back_populates="project")
    estimations = relationship("Estimation", back_populates="project")
    building_summaries = relationship("BuildingSummaryRecord", back_populates="project")
