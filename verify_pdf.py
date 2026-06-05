import requests
import json
import os

url = "http://127.0.0.1:8000/estimate/boq/pdf"

# Same payload as BOQ test
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
        },
        {
            "type": "hybrid",
            "wall_length": 8.0,
            "wall_height": 3.0,
            "block_style": "solid",
            "brick_unit_price": 0.5,
            "block_unit_price": 1.2,
            "openings": []
        }
    ],
    "steel": {
        "columns": [{"length": 3.0, "diameter": "Y16", "quantity_per_column": 4}],
        "beams": [],
        "rings": [{"diameter": "R8", "quantity": 50}],
        "unit_price_bars": {"Y16": 10.0},
        "unit_price_rings": {"R8": 2.0}
    }
}

print(f"Testing POST {url} for PDF generation...")

try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("\nSUCCESS! Response received.")
        
        # Check if it is a PDF
        content_type = response.headers.get("content-type")
        print(f"Content-Type: {content_type}")
        
        if "application/pdf" in content_type:
            filename = "test_boq.pdf"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"PDF saved to {filename}. Size: {os.path.getsize(filename)} bytes.")
        else:
            print("ERROR: Response is not a PDF")
            print(response.content[:100])
            
    else:
        print(f"\nFAILED with {response.status_code}:")
        print(response.text)
except Exception as e:
    print(f"\nERROR: {e}")
