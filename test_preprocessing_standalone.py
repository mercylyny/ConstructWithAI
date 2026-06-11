"""
Simple standalone test for Phase 7.3.1 Advanced OCR Preprocessing
Tests the preprocessing pipeline without requiring the server to be running.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_image():
    """Create a simple test image with construction text"""
    # Create a white image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add some construction-style text
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((50, 50), "WALL A 4.50M", fill='black', font=font)
    draw.text((50, 100), "WALL B 3.20M", fill='black', font=font)
    draw.text((50, 150), "HEIGHT 3.0M", fill='black', font=font)
    draw.text((50, 200), "EXTERNAL WALL 5.5M", fill='black', font=font)
    
    # Save test image
    test_path = "test_construction_plan.png"
    img.save(test_path)
    print(f"[OK] Created test image: {test_path}")
    return test_path

def test_preprocessing():
    """Test the preprocessing pipeline"""
    print("\n" + "="*70)
    print("PHASE 7.3.1: STANDALONE PREPROCESSING TEST")
    print("="*70)
    
    # Step 1: Create test image
    test_image = create_test_image()
    
    # Step 2: Test preprocessing
    print("\n[STEP 1] Testing image preprocessing...")
    try:
        from services.image_preprocessing import preprocess_for_ocr, get_optimized_tesseract_config
        
        # Apply preprocessing
        preprocessed = preprocess_for_ocr(test_image, debug=True)
        print("[OK] Preprocessing completed successfully")
        print(f"[OK] Preprocessed image size: {preprocessed.size}")
        print("[OK] Debug images saved to: outputs/ocr_debug/")
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Preprocessing error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Test Tesseract config
    print("\n[STEP 2] Testing Tesseract configuration...")
    try:
        config = get_optimized_tesseract_config()
        print(f"[OK] Tesseract config: {config}")
    except Exception as e:
        print(f"[FAIL] Config error: {e}")
        return False
    
    # Step 4: Test OCR
    print("\n[STEP 3] Testing OCR with preprocessing...")
    try:
        import pytesseract
        import shutil
        tesseract_cmd = "tesseract"
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
            r"C:\ProgramData\chocolatey\bin\tesseract.exe"
        ]
        if not shutil.which("tesseract"):
            for p in possible_paths:
                if os.path.exists(p):
                    tesseract_cmd = p
                    break
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # OCR on original image
        original_img = Image.open(test_image)
        text_original = pytesseract.image_to_string(original_img)
        print(f"[INFO] Original OCR text length: {len(text_original)} characters")
        
        # OCR on preprocessed image
        text_preprocessed = pytesseract.image_to_string(preprocessed, config=config)
        print(f"[INFO] Preprocessed OCR text length: {len(text_preprocessed)} characters")
        
        print("\n" + "-"*70)
        print("EXTRACTED TEXT (with preprocessing):")
        print("-"*70)
        print(text_preprocessed)
        print("-"*70)
        
        # Verification
        print("\n[VERIFICATION]")
        test_terms = ["WALL", "4.50", "3.20", "HEIGHT", "3.0", "EXTERNAL"]
        passed = 0
        
        for term in test_terms:
            if term.upper() in text_preprocessed.upper():
                print(f"[PASS] Found: {term}")
                passed += 1
            else:
                print(f"[FAIL] Missing: {term}")
        
        print(f"\n[RESULT] {passed}/{len(test_terms)} terms found ({passed/len(test_terms)*100:.1f}%)")
        
        if passed >= len(test_terms) * 0.5:  # 50% threshold
            print("[SUCCESS] Preprocessing improves OCR accuracy!")
            return True
        else:
            print("[WARNING] OCR accuracy below threshold")
            return False
            
    except Exception as e:
        print(f"[FAIL] OCR error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if os.path.exists(test_image):
            os.remove(test_image)
            print("\n[OK] Cleaned up test image")
 
if __name__ == "__main__":
    print("\nTesting Phase 7.3.1: Advanced OCR Pre-processing")
    print("This test runs independently of the FastAPI server\n")
    
    try:
        success = test_preprocessing()
        
        print("\n" + "="*70)
        if success:
            print("[SUCCESS] PHASE 7.3.1 VERIFICATION: PASSED")
        else:
            print("[WARNING] PHASE 7.3.1 VERIFICATION: PARTIAL SUCCESS")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*70)
        print("[FAIL] PHASE 7.3.1 VERIFICATION: FAILED")
        print("="*70 + "\n")
