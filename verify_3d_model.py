import requests
import json

url = "http://127.0.0.1:8000/model/walls/3d"

payload = {
  "walls": [
    {
      "wall_id": "W1",
      "length": 5.0,
      "height": 3.0,
      "thickness": 0.15,
      "material": "block",
      "position": {
        "x": 0,
        "y": 0,
        "z": 0
      }
    },
    {
      "wall_id": "W2_Thick",
      "length": 4.0,
      "height": 3.0,
      "thickness": 0.20,
      "material": "brick",
      "position": {
        "x": 5,
        "y": 0,
        "z": 0
      }
    }
  ]
}

print(f"Testing 3D Model Endpoint: {url}...")
try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("\nSUCCESS! 3D Model Data Received:")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        # Verify W1 Volume
        # 5 * 3 * 0.15 = 2.25
        w1 = next((w for w in data['walls'] if w['wall_id'] == 'W1'), None)
        if w1 and w1['volume'] == 2.25:
            print("\nTEST PASS: W1 Volume is correct (2.25)")
        else:
             print(f"\nTEST FAIL: W1 Volume incorrect. Got {w1.get('volume') if w1 else 'None'}")
             
        # Verify W2 Volume
        # 4 * 3 * 0.2 = 2.4
        w2 = next((w for w in data['walls'] if w['wall_id'] == 'W2_Thick'), None)
        if w2 and w2['volume'] == 2.4:
            print("TEST PASS: W2 Volume is correct (2.4)")
        else:
             print(f"TEST FAIL: W2 Volume incorrect. Got {w2.get('volume') if w2 else 'None'}")

    else:
        print(f"\nFAILED with {response.status_code}:")
        print(response.text)

except Exception as e:
    print(f"\nERROR: {e}")
