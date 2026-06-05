from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.db import get_db

from pydantic import BaseModel
from services.automation_service import PlanAnalyzer, EstimationEngine
from schemas.estimation import PlanAnalysisResult, EstimationRequest, EstimationResult

router = APIRouter(
    prefix="/pipeline",
    tags=["Automation Pipeline"]
)

class PlanAnalyzeRequest(BaseModel):
    filename: str
    use_qs_fallbacks: bool = True

@router.post("/analyze-plan", response_model=PlanAnalysisResult)
async def analyze_plan(request: PlanAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Step 1: Perform AI Plan Analysis (OCR + Element Detection).
    Returns a Building Summary without calculating costs or materials.
    """
    result = PlanAnalyzer.analyze(request.filename, db, request.use_qs_fallbacks)
    
    if result.status == "FAILED":
        raise HTTPException(status_code=400, detail="Plan analysis failed.")
    
    # --- Persist Building Summary to DB ---
    if result.summary:
        try:
            from models.project import Project
            from models.building_summary import BuildingSummaryRecord
            project = db.query(Project).filter(Project.filename == request.filename).first()
            if project:
                summary = result.summary
                db_summary = BuildingSummaryRecord(
                    project_id=project.id,
                    rooms=summary.rooms,
                    bedrooms=summary.bedrooms,
                    bathrooms=summary.bathrooms,
                    kitchens=summary.kitchens,
                    walls=summary.walls,
                    doors=summary.doors,
                    windows=summary.windows,
                    columns=summary.columns,
                    beams=summary.beams,
                    confidence=summary.confidence,
                )
                db.add(db_summary)
                db.commit()
        except Exception as e:
            db.rollback()
            print(f"Warning: Could not save building summary: {e}")
        
    return result

@router.post("/estimate", response_model=EstimationResult)
async def estimate(request: EstimationRequest, db: Session = Depends(get_db)):
    """
    Step 2: Perform Estimation Pipeline based on a Building Summary.
    This can be triggered after analyze-plan or from a manual input.
    """
    result = EstimationEngine.estimate(request, db)
    
    if result.status == "FAILED":
        raise HTTPException(status_code=400, detail=f"Estimation failed: {result.message}")
        
    return result

import os
@router.get("/download")
async def download_report(filepath: str):
    """
    Downloads a generated report (Excel or PDF).
    """
    # Basic security check to prevent arbitrary file reads
    if not filepath or ".." in filepath:
        raise HTTPException(status_code=400, detail="Invalid filepath")
        
    # If the path is relative, assume it's from the project root
    if not os.path.isabs(filepath):
        # Resolve to absolute
        filepath = os.path.abspath(filepath)
        
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
        
    filename = os.path.basename(filepath)
    return FileResponse(filepath, filename=filename)
