import os
import pytesseract
from PIL import Image
from typing import List, Tuple

# Import the new preprocessing module
from services.image_preprocessing import preprocess_for_ocr, get_optimized_tesseract_config

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Configuration
PDF_IMAGES_DIR = os.path.join(BASE_DIR, "outputs", "pdf_images")
OCR_TEXT_DIR = os.path.join(BASE_DIR, "outputs", "ocr_text")

# Ensure output directory exists
os.makedirs(OCR_TEXT_DIR, exist_ok=True)

# Auto-detect Tesseract Path
tesseract_cmd = "tesseract"
possible_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
    r"C:\ProgramData\chocolatey\bin\tesseract.exe"
]

import shutil
if not shutil.which("tesseract"):
    for p in possible_paths:
        if os.path.exists(p):
            tesseract_cmd = p
            break

pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

def perform_batch_ocr(pdf_filename: str, use_preprocessing: bool = True) -> Tuple[str, int]:
    """
    Locates all generated images for a PDF, runs OCR on them,
    concatenates the text, and saves it to a file.
    
    Phase 7.3.1 Enhancement:
    - Applies advanced image preprocessing (CLAHE, denoising, thresholding)
    - Uses optimized Tesseract configuration for architectural drawings
    
    Args:
        pdf_filename: Name of the PDF file
        use_preprocessing: If True, apply advanced preprocessing (default: True)
    
    Returns:
        Tuple[str, int]: (extracted_text, number_of_images_processed)
    """
    base_name = os.path.splitext(pdf_filename)[0]
    
    # 1. Find all matching images
    # Pattern: {base_name}_page_{n}.png
    if not os.path.exists(PDF_IMAGES_DIR):
        raise FileNotFoundError(f"Image directory not found: {PDF_IMAGES_DIR}")
        
    all_files = os.listdir(PDF_IMAGES_DIR)
    
    # Filter for images belonging to this PDF
    matching_images = []
    prefix = f"{base_name}_page_"
    
    for f in all_files:
        if f.startswith(prefix) and f.lower().endswith(".png"):
            matching_images.append(f)
            
    if not matching_images:
        return "", 0
        
    # 2. Sort images by page number to maintain text order
    def get_page_number(filename):
        try:
            no_ext = os.path.splitext(filename)[0]
            parts = no_ext.split('_')
            return int(parts[-1])
        except (ValueError, IndexError):
            return 9999

    matching_images.sort(key=get_page_number)
    
    # Get optimized Tesseract configuration
    tesseract_config = get_optimized_tesseract_config() if use_preprocessing else ""
    
    full_text = []
    
    # 3. Process each image with advanced preprocessing
    for img_file in matching_images:
        img_path = os.path.join(PDF_IMAGES_DIR, img_file)
        page_num = get_page_number(img_file)
        
        text_clean = ""
        page_header = f"--- Page {page_num} ---\n"

        try:
            if use_preprocessing:
                # Apply advanced preprocessing pipeline
                preprocessed_img = preprocess_for_ocr(img_path, debug=False)
                text = pytesseract.image_to_string(preprocessed_img, config=tesseract_config)
            else:
                img = Image.open(img_path)
                text = pytesseract.image_to_string(img)
            
            text_clean = text.strip()

            # If preprocessing OCR yields nothing, retry with basic OCR
            if use_preprocessing and len(text_clean) < 10:
                try:
                    img = Image.open(img_path)
                    text = pytesseract.image_to_string(img)
                    text_clean = text.strip()
                except Exception:
                    pass

            if len(text_clean) < 10:
                text_clean += "\n(LOW CONFIDENCE)"

        except Exception as e:
            print(f"Error processing {img_file}: {e}")
            try:
                img = Image.open(img_path)
                text = pytesseract.image_to_string(img)
                text_clean = text.strip()
                if len(text_clean) < 10:
                    text_clean += "\n(LOW CONFIDENCE - fallback OCR)"
            except Exception as fallback_e:
                print(f"Fallback OCR failed for {img_file}: {fallback_e}")
                text_clean = f"(OCR FAILED: {str(e)})"

        full_text.append(page_header + text_clean)

    combined_text = "\n\n".join(full_text)
    
    # 4. Save to file
    output_filename = f"{pdf_filename}.txt"
    output_path = os.path.join(OCR_TEXT_DIR, output_filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(combined_text)
        
    return combined_text, len(matching_images)

def perform_ocr_on_image(image_path: str) -> str:
    """
    Performs OCR on a single image file, applying preprocessing if available.
    Returns the extracted text.
    """
    try:
        # Check if preprocessing is available (imported at top)
        # Use optimized config
        tesseract_config = get_optimized_tesseract_config()
        
        # Apply preprocessing
        preprocessed_img = preprocess_for_ocr(image_path, debug=False)
        text = pytesseract.image_to_string(preprocessed_img, config=tesseract_config)
        
        return text.strip()
    except Exception as e:
        # Fallback to simple open
        try:
             img = Image.open(image_path)
             text = pytesseract.image_to_string(img)
             return text.strip()
        except Exception as e2:
             print(f"OCR Failed for {image_path}: {e2}")
             return ""
