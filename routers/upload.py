from fastapi import APIRouter, UploadFile, File, HTTPException
from services.cloudinary_service import upload_file

import os

router = APIRouter(
    prefix="/upload",
    tags=["Uploads"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/plan")
async def upload_document(file: UploadFile = File(...)):
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
        # We need to seek back to 0 or pass the local path. Passing the local path is safest.
        result = upload_file(local_path, folder="construction_ai_uploads", resource_type="auto")
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
