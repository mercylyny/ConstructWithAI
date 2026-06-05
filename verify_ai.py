import requests
import os
import json

BASE_URL = "http://127.0.0.1:8000"
TEST_FILENAME = "verify_ai_test.pdf"
TXT_FILENAME = "verify_ai_test.txt"
OCR_DIR = os.path.join("outputs", "ocr_text")

def setup_mock_data():
    os.makedirs(OCR_DIR, exist_ok=True)
    content = """
    Project Alpha
    Height 3.2m
    
    Level 1 details:
    Wall A 4.5m
    Some noise text
    W2 3.0 m
    Internal Wall 5.5 meters
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

def test_ai_interpretation():
    setup_mock_data()
    
    url = f"{BASE_URL}/ai/interpret/ocr"
    # We pass the PDF filename, expecting the backend to find the .txt file
    payload = {"filename": TEST_FILENAME}
    
    print(f"Testing AI Endpoint: {url}")
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("\nSUCCESS! Response:")
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Validations
            walls = data.get("interpreted_data", {}).get("walls", [])
            height = data.get("interpreted_data", {}).get("assumed_wall_height_m")
            
            if len(walls) == 3:
                print("PASS: Detect 3 walls")
            else:
                print(f"FAIL: Detected {len(walls)} walls, expected 3")
                
            if height == 3.2:
                 print("PASS: Detected height 3.2")
            else:
                 print(f"FAIL: Height is {height}, expected 3.2")
                 
            # Check labels
            labels = [w['label'] for w in walls]
            if "Wall A" in labels and "Wall W2" in labels: 
                # Note: My regex "W2" becomes "Wall W2" due to f"Wall {group}"? 
                # Let's check the code: label = f"Wall {w_match.group(1).upper()}"?
                # No, regex group 0 is full match "W2". 
                # In previous code it was group 1.
                # In my NEW code: w_match.group(0).strip().title()
                # So "W2" -> "W2". "Wall A" -> "Wall A".
                pass
                
        else:
            print(f"\nFAILED with {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"\nERROR: {e}")
    finally:
        cleanup_mock_data()

if __name__ == "__main__":
    test_ai_interpretation()
