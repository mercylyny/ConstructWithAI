import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"
TEST_FILENAME = "material_test.pdf"
TXT_FILENAME = "material_test.txt"
OCR_DIR = os.path.join("outputs", "ocr_text")

def setup_mock_data():
    """Create mock OCR data for testing"""
    os.makedirs(OCR_DIR, exist_ok=True)
    # Simple test case:
    # Wall A: 10m length, 3m height
    # Volume = 10 * 3 * 0.2 = 6 m³
    # Blocks = 6 * 12.5 = 75 blocks (base)
    # Blocks with wastage = 75 * 1.10 = 83 blocks
    # Bricks = 6 * 500 = 3000 bricks (base)
    # Bricks with wastage = 3000 * 1.15 = 3450 bricks
    content = """
    Construction Project Test
    Height 3.0m
    
    Wall A 10.0m
    """
    path = os.path.join(OCR_DIR, TXT_FILENAME)
    with open(path, "w") as f:
        f.write(content)
    print(f"[OK] Created mock OCR file at {path}")

def cleanup_mock_data():
    """Remove mock data"""
    path = os.path.join(OCR_DIR, TXT_FILENAME)
    if os.path.exists(path):
        os.remove(path)
        print("[OK] Cleaned up mock file")

def test_blocks_estimation():
    """Test /ai/estimate/blocks endpoint"""
    print("\n" + "="*60)
    print("TESTING: /ai/estimate/blocks")
    print("="*60)
    
    url = f"{BASE_URL}/ai/estimate/blocks"
    payload = {"filename": TEST_FILENAME}
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("[OK] SUCCESS! Response:")
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Validate calculations
            summary = data.get("summary", {})
            total_blocks = summary.get("total_blocks")
            total_blocks_wastage = summary.get("total_blocks_with_wastage")
            
            # Expected: 75 blocks base, 83 with wastage
            if total_blocks == 75:
                print("[PASS] Total blocks = 75 (correct)")
            else:
                print(f"[FAIL] Total blocks = {total_blocks}, expected 75")
            
            if total_blocks_wastage == 83:
                print("[PASS] Blocks with wastage = 83 (correct)")
            else:
                print(f"[FAIL] Blocks with wastage = {total_blocks_wastage}, expected 83")
        else:
            print(f"[FAIL] FAILED with {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"[ERROR] {e}")

def test_bricks_estimation():
    """Test /ai/estimate/bricks endpoint"""
    print("\n" + "="*60)
    print("TESTING: /ai/estimate/bricks")
    print("="*60)
    
    url = f"{BASE_URL}/ai/estimate/bricks"
    payload = {"filename": TEST_FILENAME}
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("[OK] SUCCESS! Response:")
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Validate calculations
            summary = data.get("summary", {})
            total_bricks = summary.get("total_bricks")
            total_bricks_wastage = summary.get("total_bricks_with_wastage")
            
            # Expected: 3000 bricks base, 3450 with wastage
            if total_bricks == 3000:
                print("[PASS] Total bricks = 3000 (correct)")
            else:
                print(f"[FAIL] Total bricks = {total_bricks}, expected 3000")
            
            if total_bricks_wastage == 3450:
                print("[PASS] Bricks with wastage = 3450 (correct)")
            else:
                print(f"[FAIL] Bricks with wastage = {total_bricks_wastage}, expected 3450")
        else:
            print(f"[FAIL] FAILED with {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 7.6: MATERIAL ESTIMATION VERIFICATION")
    print("="*60)
    
    setup_mock_data()
    
    try:
        test_blocks_estimation()
        test_bricks_estimation()
    finally:
        cleanup_mock_data()
    
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60 + "\n")
