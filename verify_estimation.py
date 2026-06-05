import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"
TEST_FILENAME = "verify_est_test.pdf"
TXT_FILENAME = "verify_est_test.txt"
OCR_DIR = os.path.join("outputs", "ocr_text")

def setup_mock_data():
    os.makedirs(OCR_DIR, exist_ok=True)
    # Mock OCR text designed to test quantities
    # Wall A: 5.0m
    # Height: 3.0m (default/explicit)
    # Area = 15.0
    # Thickness = 0.2
    # Volume = 3.0
    content = """
    Project Estimation Test
    Height 3.0m
    
    Wall A 5.0m
    Wall B 10.0m
    """
    path = os.path.join(OCR_DIR, TXT_FILENAME)
    with open(path, "w") as f:
        f.write(content)
    print(f"Created mock OCR file at {path}")

def cleanup_mock_data():
    path = os.path.join(OCR_DIR, TXT_FILENAME)
    if os.path.exists(path):
        os.remove(path)
        print("Cleaned up mock file.")

def test_estimation():
    setup_mock_data()
    
    url = f"{BASE_URL}/ai/estimate/walls"
    payload = {"filename": TEST_FILENAME}
    
    print(f"Testing Estimation Endpoint: {url}")
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("\nSUCCESS! Response:")
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Validations
            totals = data.get("totals", {})
            total_area = totals.get("total_wall_area_sqm")
            total_vol = totals.get("total_wall_volume_cum")
            
            # Expected:
            # Wall A: 5 * 3 = 15 area, 3.0 vol
            # Wall B: 10 * 3 = 30 area, 6.0 vol
            # Total Area = 45.0
            # Total Vol = 9.0
            
            if total_area == 45.0:
                 print("PASS: Total Area is 45.0")
            else:
                 print(f"FAIL: Total Area is {total_area}, expected 45.0")
                 
            if total_vol == 9.0:
                 print("PASS: Total Volume is 9.0")
            else:
                 print(f"FAIL: Total Volume is {total_vol}, expected 9.0")

        else:
            print(f"\nFAILED with {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"\nERROR: {e}")
    finally:
        cleanup_mock_data()

if __name__ == "__main__":
    test_estimation()
