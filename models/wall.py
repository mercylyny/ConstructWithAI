from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Wall(Base):
    __tablename__ = "walls"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    wall_id = Column(String, index=True)
    length_m = Column(Float)
    height_m = Column(Float)
    thickness_mm = Column(Float)
    openings_area_m2 = Column(Float, default=0.0)
    
    # Semantic Classification Fields
    wall_type = Column(String, default="UNKNOWN")
    classification_confidence = Column(Float, default=0.0)
    reasoning = Column(String, default="")

    # Relationship back to Project
    project = relationship("Project", back_populates="walls")
