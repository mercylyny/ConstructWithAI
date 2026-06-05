import requests
import json

url = "http://127.0.0.1:8000/estimate/full-building"

# Payload provided by the user
payload = {
  "walls": [
    {
      "type": "block",
      "wall_length": 10,
      "wall_height": 3,
      "openings": [
        { "width": 1, "height": 2 }
      ],
      "block_type": "6inch",
      "block_style": "stretcher",
      "brick_type": None,
      "block_unit_price": 3500,
      "brick_unit_price": 0
    },
    {
      "type": "brick",
      "wall_length": 6,
      "wall_height": 3,
      "openings": [],
      "block_type": None,
      "block_style": None,
      "brick_type": "clay",
      "block_unit_price": 0,
      "brick_unit_price": 500
    }
  ],
  "steel": {
    "columns": [],
    "beams": [],
    "rings": [],
    "unit_price_bars": {
      "12mm": 18000
    },
    "unit_price_rings": {
      "8mm": 12000
    }
  }
}

print(f"Testing POST {url} with user provided payload...")

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
