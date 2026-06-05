import requests
import json

url = "http://127.0.0.1:8000/analyze/plan/ocr/measurements"

# Simulated OCR Text based on the rules we implemented
simulated_text = """
Introduction to plan...
Wall A length 4.5m
Some random text
Wall B = 3.0 m
Garage Wall 5m
Wall C = 6.25m
"""

payload = {
    "filename": "test_plan.png",
    "extracted_text": simulated_text
}

print(f"Testing POST {url}...")
try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("\nSUCCESS! Response:")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        walls = data.get("walls", [])
        if len(walls) >= 3:
            print("\nTEST PASS: Detected multiple walls.")
            # Verify specific values
            found_4_5 = any(w['length_meters'] == 4.5 for w in walls)
            found_3_0 = any(w['length_meters'] == 3.0 for w in walls)
            found_6_25 = any(w['length_meters'] == 6.25 for w in walls)
            
            if found_4_5 and found_3_0 and found_6_25:
                print("TEST PASS: Correctly parsed specific lengths (4.5, 3.0, 6.25).")
            else:
                print("TEST FAIL: Did not find all expected lengths.")
        else:
             print(f"TEST FAIL: Expected at least 3 walls, found {len(walls)}.")

    else:
        print(f"\nFAILED with {response.status_code}:")
        print(response.text)

except Exception as e:
    print(f"\nERROR: {e}")
