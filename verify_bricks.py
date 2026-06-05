import requests
import json

url = "http://127.0.0.1:8000/estimate/bricks"

payload = {
    "wall_length": 10.0,
    "wall_height": 3.0,
    "brick_type": "clay",
    "unit_price": 0.50,
    # Optional openings area check
    "openings": [
        {"type": "window", "width": 1.0, "height": 1.0}
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
