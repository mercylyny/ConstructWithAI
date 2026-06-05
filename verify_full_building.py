import requests
import json

url = "http://127.0.0.1:8000/estimate/full-building"

# Construct a comprehensive payload
payload = {
    "walls": [
        {
            "type": "block",
            "wall_length": 5.0,
            "wall_height": 3.0,
            "block_type": "6_inch",
            "block_style": "hollow",
            "block_unit_price": 1.5,
            "openings": [{"type": "window", "width": 1.0, "height": 1.0}] # -1 sqm
        },
        {
            "type": "hybrid",
            "wall_length": 10.0,
            "wall_height": 3.0,
            "brick_unit_price": 0.5,
            "block_unit_price": 1.5,
            "openings": [{"type": "door", "width": 1.0, "height": 2.1}] # -2.1 sqm from upper blocks
        }
    ],
    "steel": {
        "columns": [
            {"length": 3.0, "diameter": "Y16", "quantity_per_column": 4}
        ],
        "beams": [
            {"length": 5.0, "diameter": "Y12", "quantity_per_beam": 4}
        ],
        "rings": [
            {"diameter": "R8", "quantity": 100}
        ],
        "unit_price_bars": {"Y16": 10.0, "Y12": 8.0},
        "unit_price_rings": {"R8": 2.0}
    }
}

print(f"Testing POST {url}...")
print("Payload Summary:")
print(f"- Walls: {len(payload['walls'])}")
print(f"- Steel: Columns, Beams, Rings")

try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("\nSUCCESS! Response:")
        print(json.dumps(response.json(), indent=2))
        
        # Simple assertions
        data = response.json()
        print(f"\nGrand Total Cost: {data['grand_total']}")
    else:
        print(f"\nFAILED with {response.status_code}:")
        print(response.text)
except requests.exceptions.ConnectionError:
    print("\nERROR: Could not connect to the server (Connection Refused). Is uvicorn running?")
except Exception as e:
    print(f"\nERROR: {e}")
