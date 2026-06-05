import requests
import json
import os

# Define Endpoint
url = "http://127.0.0.1:8000/ai/interpret/ocr"

# 1. Setup: Create a dummy OCR text file to simulate existing data
filename = "ai_test_plan"
txt_path = f"uploads/{filename}.txt"
ocr_content = """
Project: Villa 1
Level: Ground
Height : 3.2m

Details:
Wall A: 5.5m
Wall B = 4.0
Some junk text
Wall C 3m
"""

os.makedirs("uploads", exist_ok=True)
with open(txt_path, "w") as f:
    f.write(ocr_content)
    
print(f"Created dummy OCR file at {txt_path}")

# 2. Call the AI Endpoint
payload = {"filename": filename}

print(f"Calling {url}...")
try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("\nSUCCESS! AI Response Received:")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        # Verify Content
        interp = data.get("interpreted_data", {})
        walls = interp.get("walls", [])
        height = interp.get("assumed_wall_height_m")
        
        # Checks
        if height == 3.2:
             print("TEST PASS: Height detected (3.2)")
        else:
             print(f"TEST FAIL: Height mismatch {height}")
             
        # Check Wall A
        wa = next((w for w in walls if "WALL A" in w['label']), None)
        if wa and wa['length_m'] == 5.5:
            print("TEST PASS: Wall A detected (5.5)")
        else:
            print(f"TEST FAIL: Wall A detection failed. {wa}")

    else:
        print(f"\nFAILED with {response.status_code}:")
        print(response.text)

except Exception as e:
    print(f"\nERROR: {e}")
    
# Cleanup
# os.remove(txt_path) # Keep it for inspection if needed, or remove.
