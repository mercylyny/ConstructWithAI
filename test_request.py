import requests
import json

base_url = "http://127.0.0.1:8000"

def test_endpoint(endpoint, payload, test_name):
    print(f"--- Testing {test_name} ---")
    try:
        response = requests.post(f"{base_url}{endpoint}", json=payload)
        if response.status_code == 200:
            print("SUCCESS")
            print(json.dumps(response.json(), indent=2))
        else:
            print("FAILED")
            print(f"Status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"ERROR: {e}")
    print("\n")

# 1. Test Brick Estimate
brick_payload = {
    "wall_length": 5.0,
    "wall_height": 3.0,
    "brick_type": "clay",
    "unit_price": 0.50,
    "openings": [{"type": "window", "width": 1.0, "height": 1.0}]
}
test_endpoint("/estimate/bricks", brick_payload, "Brick Estimate")

# 2. Test Hybrid Estimate
hybrid_payload = {
    "wall_length": 10.0,
    "wall_height": 3.0,
    "brick_unit_price": 0.50,
    "block_unit_price": 1.50,
    "block_type": "6_inch",
    "block_style": "hollow",
    "openings": [
        {"type": "door", "width": 1.0, "height": 2.0}
    ]
}
test_endpoint("/estimate/hybrid", hybrid_payload, "Hybrid Estimate")
