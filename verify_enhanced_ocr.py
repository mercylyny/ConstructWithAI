"""
Verification script for Phase 7.3.1: Advanced OCR Pre-processing
Tests the enhanced OCR pipeline on architectural drawing-style images.
"""
import requests
import json
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

BASE_URL = "http://127.0.0.1:8000"
TEST_FILENAME = "ocr_enhanced_test.pdf"

def create_architectural_drawing_pdf():
    """
    Create a mock architectural drawing PDF with construction annotations.
    Simulates typical architectural plan text.
    """
    c = canvas.Canvas(TEST_FILENAME, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "FLOOR PLAN - LEVEL 1")
    
    # Wall labels and dimensions (typical architectural notation)
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, "WALL A 4.50M")
    c.drawString(100, 680, "WALL B 3.20M")
    c.drawString(100, 660, "WALL C 6.00M")
    
    # Height annotation
    c.drawString(100, 620, "WALL HEIGHT 3.0M")
    
    # Additional technical annotations
    c.drawString(100, 580, "EXTERNAL WALL 5.5M")
    c.drawString(100, 560, "W1 2.80M")
    c.drawString(100, 540, "W2 4.10M")
    
    # Dimensions in different formats
    c.drawString(100, 500, "LENGTH 7.25M")
    c.drawString(100, 480, "3.5M X 2.8M")
    
    c.save()
    print(f"[OK] Created test PDF: {TEST_FILENAME}")

def test_enhanced_ocr_pipeline():
    """
    Test the complete pipeline:
    1. Upload PDF
    2. Convert to images
    3. Run enhanced OCR
    4. Verify text extraction quality
    """
    print("\n" + "="*70)
    print("PHASE 7.3.1: ENHANCED OCR VERIFICATION")
    print("="*70)
    
    # Step 1: Create test PDF
    create_architectural_drawing_pdf()
    
    # Step 2: Upload PDF
    print("\n[STEP 1] Uploading PDF...")
    with open(TEST_FILENAME, "rb") as f:
        files = {"file": (TEST_FILENAME, f, "application/pdf")}
        data = {"scale": "1:100"}
        res = requests.post(f"{BASE_URL}/upload/plan", files=files, data=data)
        if res.status_code == 200:
            print("[OK] PDF uploaded successfully")
        else:
            print(f"[FAIL] Upload failed: {res.text}")
            return
    
    # Step 3: Convert PDF to images
    print("\n[STEP 2] Converting PDF to images...")
    res = requests.post(f"{BASE_URL}/analyze/plan/pdf-to-image", 
                       json={"filename": TEST_FILENAME})
    if res.status_code == 200:
        data = res.json()
        print(f"[OK] Converted to {data['page_count']} image(s)")
    else:
        print(f"[FAIL] Conversion failed: {res.text}")
        return
    
    # Step 4: Run enhanced OCR
    print("\n[STEP 3] Running enhanced OCR with preprocessing...")
    res = requests.post(f"{BASE_URL}/analyze/plan/ocr/images",
                       json={"filename": TEST_FILENAME})
    
    if res.status_code == 200:
        data = res.json()
        extracted_text = data.get("extracted_text", "")
        
        print("[OK] OCR completed successfully")
        print("\n" + "-"*70)
        print("EXTRACTED TEXT:")
        print("-"*70)
        print(extracted_text)
        print("-"*70)
        
        # Verification: Check if key terms were extracted
        print("\n[VERIFICATION]")
        test_cases = [
            ("WALL A", "Wall A label"),
            ("4.50", "Dimension 4.50M"),
            ("3.20", "Dimension 3.20M"),
            ("HEIGHT", "Height keyword"),
            ("3.0", "Height value"),
            ("EXTERNAL", "External wall label"),
        ]
        
        passed = 0
        total = len(test_cases)
        
        for term, description in test_cases:
            if term.upper() in extracted_text.upper():
                print(f"[PASS] Found: {description} ({term})")
                passed += 1
            else:
                print(f"[FAIL] Missing: {description} ({term})")
        
        print(f"\n[RESULT] {passed}/{total} checks passed ({passed/total*100:.1f}%)")
        
        if passed >= total * 0.7:  # 70% threshold
            print("[SUCCESS] Enhanced OCR is working effectively!")
        else:
            print("[WARNING] OCR accuracy below expected threshold")
            
    else:
        print(f"[FAIL] OCR failed: {res.text}")
    
    # Cleanup
    if os.path.exists(TEST_FILENAME):
        os.remove(TEST_FILENAME)
        print("\n[OK] Cleaned up test file")

if __name__ == "__main__":
    try:
        test_enhanced_ocr_pipeline()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("VERIFICATION COMPLETE")
    print("="*70 + "\n")
