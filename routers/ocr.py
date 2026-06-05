from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.ocr_service import perform_batch_ocr
from services.ocr_postprocess import postprocess_ocr

router = APIRouter(
    prefix="/analyze/plan/ocr",
    tags=["OCR Processing"]
)

class BatchOCRRequest(BaseModel):
    filename: str

class BatchOCRResponse(BaseModel):
    filename: str
    number_of_images_processed: int
    extracted_text: str
    clean_text: str
    measurements: List[str]
    labels: List[str]
    message: str

@router.post("/images", response_model=BatchOCRResponse)
async def batch_ocr_images(request: BatchOCRRequest):
    """
    Runs OCR on all pre-generated images for a specific PDF.
    Combines text, applies post-processing, and saves to outputs/ocr_text/{filename}.txt
    
    Phase 7.3.2: Returns structured data including:
    - Raw extracted text
    - Cleaned text
    - Detected measurements
    - Detected labels
    """
    if not request.filename:
         raise HTTPException(status_code=400, detail="Filename is required")

    try:
        # Call OCR service
        text, count = perform_batch_ocr(request.filename)
        
        if count == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"No images found for {request.filename}. Did you run /analyze/plan/pdf-to-image first?"
            )
        
        # Phase 7.3.2: Apply post-processing
        processed_data = postprocess_ocr(text)
            
        return BatchOCRResponse(
            filename=request.filename,
            number_of_images_processed=count,
            extracted_text=text,
            clean_text=processed_data["clean_text"],
            measurements=processed_data["measurements"],
            labels=processed_data["labels"],
            message="Batch OCR completed successfully with structured data extraction."
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
