from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.db import get_db
from models.user import User as UserModel
from database.crud import get_project, get_projects, create_project, create_project_wall, create_project_estimation
from schemas.db_schemas import Project, ProjectCreate, Wall, WallCreate, Estimation, EstimationCreate
from services.auth_service import get_current_user

router = APIRouter(
    prefix="/database",
    tags=["Database Operations"]
)

@router.post("/projects/", response_model=Project)
def create_new_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # Fixed syntax error: removed extra parenthesis after Depends
    return create_project(db=db, proj=project)

@router.get("/projects/", response_model=List[Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user)):
    from models.project import Project as ProjectModel
    # If logged in, return only this user's projects
    if current_user_email:
        db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
        if db_user:
            return db.query(ProjectModel).filter(ProjectModel.user_id == db_user.id).offset(skip).limit(limit).all()
    # Fallback: return all projects (for unauthenticated/admin access)
    return get_projects(db, skip=skip, limit=limit)

@router.get("/projects/{project_id}", response_model=Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.post("/projects/{project_id}/walls/", response_model=Wall)
def create_wall_for_project(project_id: int, wall: WallCreate, db: Session = Depends(get_db)):
    db_project = get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return create_project_wall(db=db, db_wall=wall, project_id=project_id)

@router.post("/projects/{project_id}/estimation")
def save_project_estimation(project_id: int, estimation: EstimationCreate, db: Session = Depends(get_db)):
    """
    Save estimation results linked to a specific project.
    Requirement: Validate project exists, Insert record, Commit, Print ID, Return specific JSON.
    """
    # 1. Validate project exists (Requirement 5 & 7)
    db_project = get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Insert and commit (Requirement 5 & 7)
    try:
        new_estimation = create_project_estimation(db=db, db_est=estimation, project_id=project_id)
        
        # 3. Logging (Requirement 8)
        print(f"Estimation ID: {new_estimation.id} saved successfully")
        
        # 4. Response (Requirement 6)
        return {
            "message": "Estimation saved successfully",
            "estimation_id": new_estimation.id
        }
    except Exception as e:
        # DB error handling (Requirement 7)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

