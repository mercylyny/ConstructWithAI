import requests
import json

url = "http://127.0.0.1:8000/estimate/from-plan"

# Assume we got these lengths from the previous manual analysis
wall_lengths = [5.0, 3.2, 1.5]

payload = {
    "wall_lengths_meters": wall_lengths,
    "wall_height": 3.0,
    "material_type": "hybrid",
    "brick_unit_price": 0.5,
    "block_unit_price": 1.5,
    # Optional openings to subtract from total area
    "openings": [
        {"type": "door", "width": 1.0, "height": 2.0}
    ]
}

print(f"Testing POST {url}...")
print(f"Input Wall Lengths: {wall_lengths} (Sum: {sum(wall_lengths)})")
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
