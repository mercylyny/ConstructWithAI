from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import uuid
from pdf2image import convert_from_path

router = APIRouter(
    prefix="/analyze/plan",
    tags=["PDF Processing"]
)

# Configuration
UPLOAD_DIR = "uploads"
OUTPUT_DIR = os.path.join("outputs", "pdf_images")

# Ensure output directory exists (startup logic, but safe to do at module level or in endpoint)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class PDFToImageRequest(BaseModel):
    filename: str

class PDFToImageResponse(BaseModel):
    filename: str
    page_count: int
    image_paths: List[str]
    message: str

@router.post("/pdf-to-image", response_model=PDFToImageResponse)
async def convert_pdf_to_images(request: PDFToImageRequest):
    """
    Converts a previously uploaded PDF into PNG images (300 DPI).
    """
    # 1. Validate Input File
    pdf_path = os.path.join(UPLOAD_DIR, request.filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"File not found: {request.filename}")
    
    if not request.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File is not a PDF")

    try:
        # 2. Convert PDF to Images
        # Attempt to auto-detect Poppler if not in PATH
        poppler_path = None
        
        # Check common locations + the one we found
        potential_paths = [
            r"C:\poppler\Library\bin",
            r"C:\Program Files\poppler-0.68.0\bin",
            r"C:\Program Files (x86)\poppler-0.68.0\bin",
            r"C:\ProgramData\chocolatey\bin"
        ]
        
        # Dynamically search for Poppler in WinGet Packages
        try:
            winget_pkg_dir = os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages")
            if os.path.exists(winget_pkg_dir):
                for folder in os.listdir(winget_pkg_dir):
                    if "poppler" in folder.lower():
                        folder_path = os.path.join(winget_pkg_dir, folder)
                        for root, _, files in os.walk(folder_path):
                            if "pdftoppm.exe" in files:
                                potential_paths.insert(0, root)
                                break
        except Exception:
            pass
        
        images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
        
        saved_image_paths = []
        base_name = os.path.splitext(request.filename)[0]
        
        # 3. Save Each Page
        for i, image in enumerate(images):
            # Generate a consistent name: filename_page_1.png
            image_filename = f"{base_name}_page_{i+1}.png"
            image_path = os.path.join(OUTPUT_DIR, image_filename)
            
            # Save as PNG
            image.save(image_path, "PNG")
            
            # Record absolute/relative path. We return relative path for consistency with other endpoints.
            saved_image_paths.append(image_path)
            
        return PDFToImageResponse(
            filename=request.filename,
            page_count=len(images),
            image_paths=saved_image_paths,
            message="PDF converted to images successfully."
        )

    except Exception as e:
        # Catch-all for pdf2image errors (e.g., Corrupt PDF, Poppler missing)
        raise HTTPException(status_code=500, detail=f"PDF conversion failed: {str(e)}")
