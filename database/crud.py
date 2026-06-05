from sqlalchemy.orm import Session
from models import project, wall, estimation
from schemas import db_schemas

def get_project(db: Session, project_id: int):
    return db.query(project.Project).filter(project.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(project.Project).offset(skip).limit(limit).all()

def create_project(db: Session, proj: db_schemas.ProjectCreate):
    db_project = project.Project(filename=proj.filename, scale=proj.scale)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def create_project_wall(db: Session, db_wall: db_schemas.WallCreate, project_id: int):
    db_item = wall.Wall(**db_wall.model_dump(), project_id=project_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_project_estimation(db: Session, db_est: db_schemas.EstimationCreate, project_id: int):
    db_item = estimation.Estimation(**db_est.model_dump(), project_id=project_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
