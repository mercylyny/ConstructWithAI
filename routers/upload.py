from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from services.auth_service import get_current_user
from services.cloudinary_service import upload_file
from models.user import User as UserModel
from models.project import Project as ProjectModel
import os

router = APIRouter(
    prefix="/upload",
    tags=["Uploads"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/plan")
async def upload_document(
    file: UploadFile = File(...),
    scale: str = Form(default="1:100"),
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user)
):
    """
    Endpoint to upload a floor plan directly to Cloudinary.
    Returns the secure URL and public_id.
    """
    try:
        # 1. Save locally for AI/OCR tools to use
        local_path = os.path.join(UPLOAD_DIR, file.filename)
        content = await file.read()
        with open(local_path, "wb") as f:
            f.write(content)

        # 2. Upload to Cloudinary
        result = upload_file(local_path, folder="construction_ai_uploads", resource_type="auto")
        
        # 3. Create Project in Database if user is authenticated
        project_id = None
        if current_user_email:
            db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
            if db_user:
                # Check if project already exists for this user to avoid duplicates
                db_project = db.query(ProjectModel).filter(
                    ProjectModel.user_id == db_user.id,
                    ProjectModel.filename == file.filename
                ).first()
                
                if not db_project:
                    db_project = ProjectModel(
                        user_id=db_user.id,
                        filename=file.filename,
                        scale=scale,
                        # Add fields if available in model, else just filename and scale
                    )
                    db.add(db_project)
                    db.commit()
                    db.refresh(db_project)
                project_id = db_project.id

        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "project_id": project_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

