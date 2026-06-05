import requests
import json

url = "http://127.0.0.1:8000/estimate/steel"

payload = {
    "columns": [
        {"length": 3.0, "diameter": "Y16", "quantity_per_column": 4},
        {"length": 4.0, "diameter": "Y16", "quantity_per_column": 4}
    ],
    "beams": [
        {"length": 5.0, "diameter": "Y12", "quantity_per_beam": 6}
    ],
    "rings": [
        {"diameter": "R8", "quantity": 50},
        {"diameter": "R6", "quantity": 100}
    ],
    "unit_price_bars": {
        "Y16": 10.0, 
        "Y12": 8.0
    },
    "unit_price_rings": {
        "R8": 2.0,
        "R6": 1.5
    }
}

print(f"Testing POST {url}...")
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
