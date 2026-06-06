"""
Advanced image preprocessing for OCR on architectural/construction drawings.
Optimizes images for better text extraction from technical plans.
"""
import cv2
import numpy as np
from PIL import Image
import os

def preprocess_for_ocr(image_path: str, debug=False) -> Image.Image:
    """
    Apply comprehensive preprocessing pipeline for architectural drawing OCR.
    
    Pipeline:
    1. Grayscale conversion
    2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    3. Noise reduction (bilateral filter)
    4. Adaptive thresholding
    5. Morphological operations (optional)
    
    Args:
        image_path: Path to input image
        debug: If True, save intermediate steps
        
    Returns:
        PIL Image ready for OCR
    """
    # Step 1: Load image with OpenCV
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    # Step 2: Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Step 3: Apply CLAHE for contrast enhancement
    # Reduced clipLimit (1.5 vs 2.0) to avoid over-processing thin plan lines
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Step 4: Noise reduction while preserving edges
    # Bilateral filter reduces noise but keeps edges sharp (important for thin lines)
    denoised = cv2.bilateralFilter(enhanced, d=9, sigmaColor=75, sigmaSpace=75)
    
    # Step 5: Adaptive thresholding
    # Increased blockSize to 31 (better for large architectural scans)
    # Increased C to 4 to aggressively remove gray background noise
    binary = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=4
    )
    
    # Step 6: Morphological operations (skip closing for high-res to avoid merging letters)
    # Instead, apply a slight unsharp mask to make text pop
    blur = cv2.GaussianBlur(binary, (0, 0), 3)
    morph = cv2.addWeighted(binary, 1.5, blur, -0.5, 0)
    
    # Step 7: Unconditional upscaling for OCR
    # Tesseract performs significantly better when text height is around 30-40 pixels.
    # Architectural text is often tiny. Scaling by 1.5x gives Tesseract more pixels to work with.
    # However, on Render Free Tier (512MB RAM), scaling large PDFs causes OOM crashes.
    height, width = morph.shape
    scale_factor = 1.0 if os.environ.get("RENDER") else 1.5
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    if scale_factor != 1.0:
        morph = cv2.resize(morph, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    # Debug: Save intermediate steps if requested
    if debug:
        debug_dir = "outputs/ocr_debug"
        os.makedirs(debug_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        cv2.imwrite(f"{debug_dir}/{base_name}_1_gray.png", gray)
        cv2.imwrite(f"{debug_dir}/{base_name}_2_enhanced.png", enhanced)
        cv2.imwrite(f"{debug_dir}/{base_name}_3_denoised.png", denoised)
        cv2.imwrite(f"{debug_dir}/{base_name}_4_binary.png", binary)
        cv2.imwrite(f"{debug_dir}/{base_name}_5_final.png", morph)
    
    # Convert back to PIL Image for pytesseract
    pil_image = Image.fromarray(morph)
    return pil_image

def get_optimized_tesseract_config() -> str:
    """
    Returns Tesseract configuration optimized for architectural floor plans.
    
    Configuration:
    - OEM 1: LSTM neural net mode (best accuracy)
    - PSM 11: Sparse text — best for plans where labels are scattered across the image
              (PSM 6 "uniform block" was wrong and garbled room labels)
    - No character whitelist — allows lowercase room names (kitchen, bedroom, bathroom)
      to be read correctly. The old whitelist stripped lowercase entirely.
    """
    config = (
        "--oem 1 "   # LSTM OCR Engine Mode
        "--psm 11 "  # Sparse text: find as much text as possible in no particular order
        "-c preserve_interword_spaces=1"
    )
    
    return config
