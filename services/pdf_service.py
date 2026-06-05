import os
import shutil
from pdf2image import convert_from_path
from typing import List

OUTPUT_DIR = os.path.join("outputs", "pdf_images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def convert_pdf_to_images_service(pdf_path: str, filename: str) -> List[str]:
    """
    Converts a PDF file to a list of image paths (PNG).
    Returns the list of absolute paths to the generated images.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    # Attempt to auto-detect Poppler
    poppler_path = None
    potential_paths = [
        r"C:\poppler\Library\bin",
        r"C:\Program Files\poppler-0.68.0\bin",
        r"C:\Program Files (x86)\poppler-0.68.0\bin",
        r"C:\ProgramData\chocolatey\bin"
    ]
    
    if not shutil.which("pdftoppm"):
        for p in potential_paths:
            if os.path.exists(os.path.join(p, "pdftoppm.exe")):
                poppler_path = p
                break
    
    try:
        images = convert_from_path(pdf_path, dpi=150, poppler_path=poppler_path)
    except Exception as e:
        # Re-raise with clear message
        raise RuntimeError(f"PDF conversion failed: {str(e)}")
        
    saved_paths = []
    base_name = os.path.splitext(filename)[0]
    
    for i, image in enumerate(images):
        image_filename = f"{base_name}_page_{i+1}.png"
        image_path = os.path.join(OUTPUT_DIR, image_filename)
        # Using format='PNG'
        image.save(image_path, "PNG")
        saved_paths.append(os.path.abspath(image_path))
        
    return saved_paths
