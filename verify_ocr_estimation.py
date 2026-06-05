import requests
import json
import os

# Define Endpoints
measurements_url = "http://127.0.0.1:8000/analyze/plan/ocr/measurements"
estimate_url = "http://127.0.0.1:8000/estimate/from-ocr"

# 1. Simulate Measurements Step (This saves the file)
# Simulated OCR Text
simulated_text = """
Wall A length 10m
Wall B = 5 m
"""

measurements_payload = {
    "filename": "test_persistence.png",
    "extracted_text": simulated_text
}

print(f"Step 1: Storing measurements via {measurements_url}...")
try:
    response = requests.post(measurements_url, json=measurements_payload)
    if response.status_code == 200:
        print("Measurements Stored Successfully.")
        print(response.json())
        data = response.json()
        print(f"Detected {data.get('total_walls_detected')} walls.")
    else:
        print(f"Measurements Failed: {response.text}")
        exit()
except Exception as e:
    print(f"Error: {e}")
    exit()
    
# 2. Call Automatic Estimation (This reads the file)
estimate_payload = {
    "filename": "test_persistence.png",
    "wall_height": 3.0,
    "material_type": "block",
    "unit_price": 2.0
}

print(f"\nStep 2: Requesting Estimate via {estimate_url}...")
try:
    response = requests.post(estimate_url, json=estimate_payload)
    if response.status_code == 200:
        print("\nSUCCESS! Automatic Estimate Received:")
        est_data = response.json()
        print(json.dumps(est_data, indent=2))
        
        # Verify Calculation
        # Total length should be 10 + 5 = 15m
        # Area = 15 * 3 = 45 sqm
        # Blocks = 45 * 12.5 = 562.5 -> ceil -> 563 blocks
        # Cost = 563 * 2.0 = 1126.0
        
        expected_qty = 563
        actual_qty = est_data.get("estimated_material_quantity")
        
        if actual_qty == expected_qty:
            print(f"\nTEST PASS: Quantity {actual_qty} matches expected {expected_qty}.")
        else:
            print(f"\nTEST FAIL: Quantity {actual_qty} != expected {expected_qty}.")
            
    else:
        print(f"\nFAILED with {response.status_code}:")
        print(response.text)

except Exception as e:
    print(f"\nERROR: {e}")
    
# Cleanup
try:
    file_path = "uploads/test_persistence.png_measurements.json"
    if os.path.exists(file_path):
        os.remove(file_path)
        print("\nCleaned up json file.")
except:
    pass
