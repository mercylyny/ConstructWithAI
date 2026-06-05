import requests
import json

url = "http://127.0.0.1:8000/estimate/boq"

# Same test payload
payload = {
    "walls": [
        {
            "type": "block",
            "wall_length": 5.0,
            "wall_height": 3.0,
            "block_type": "6_inch",
            "block_style": "hollow",
            "block_unit_price": 1.5,
            "openings": [{"type": "window", "width": 1.0, "height": 1.0}]
        }
    ],
    "steel": {
        "columns": [{"length": 3.0, "diameter": "Y16", "quantity_per_column": 4}],
        "beams": [],
        "rings": [],
        "unit_price_bars": {"Y16": 10.0},
        "unit_price_rings": {}
    }
}

print(f"Testing POST {url}...")
try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("\nSUCCESS! Response:")
        print(json.dumps(response.json(), indent=2))
        
        # Check structure
        data = response.json()
        if "masonry_works" in data and "steel_works" in data and "cost_summary" in data:
            print("\nStructure Validation: PASS")
        else:
            print("\nStructure Validation: FAIL")
    else:
        print(f"\nFAILED with {response.status_code}:")
        print(response.text)
except Exception as e:
    print(f"\nERROR: {e}")
