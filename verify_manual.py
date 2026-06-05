import requests
import json

url = "http://127.0.0.1:8000/analyze/plan/manual"

payload = {
    "filename": "floor_plan_v1.jpg",
    "scale": "1:100",
    "reference_pixel_length": 100.0, # e.g. 100 pixels
    "reference_real_length": 1.0,    # equals 1 meter
    "wall_pixel_lengths": [
        500.0, # Should be 5.0m
        320.0, # Should be 3.2m
        150.0  # Should be 1.5m
    ]
}

print(f"Testing POST {url}...")
print("Payload:", json.dumps(payload, indent=2))

try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("\nSUCCESS! Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\nFAILED with {response.status_code}:")
        print(response.text)
except Exception as e:
    print(f"\nERROR: {e}")
