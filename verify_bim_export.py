import requests
import json
import uuid

url = "http://127.0.0.1:8000/model/walls/bim"

payload = {
  "walls": [
    {
      "wall_id": "W-BIM-01",
      "length": 6.5,
      "height": 3.0,
      "thickness": 0.25,
      "material": "block",
      "position": {
        "x": 10.0,
        "y": 0.0,
        "z": 0.0
      }
    }
  ]
}

print(f"Testing BIM Endpoint: {url}...")
try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("\nSUCCESS! BIM Data Received:")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        # Verify Structure
        walls = data.get('bim_walls', [])
        if not walls:
            print("\nFAIL: No walls returned")
            exit()
            
        w1 = walls[0]
        
        # Check Global ID
        gid = w1.get('global_id')
        try:
            uuid.UUID(gid)
            print(f"\nTEST PASS: Global ID is valid UUID ({gid})")
        except ValueError:
            print(f"\nTEST FAIL: Invalid UUID {gid}")
            
        # Check Entity Type
        if w1.get('entity_type') == "IfcWall":
            print("TEST PASS: Entity Type is IfcWall")
        else:
            print(f"TEST FAIL: Expected IfcWall, got {w1.get('entity_type')}")
            
        # Check Volume
        # 6.5 * 3.0 * 0.25 = 4.875
        vol = w1.get('geometry', {}).get('volume')
        if vol == 4.875:
             print(f"TEST PASS: Volume is correct ({vol})")
        else:
             print(f"TEST FAIL: Volume incorrect. Got {vol}")

    else:
        print(f"\nFAILED with {response.status_code}:")
        print(response.text)

except Exception as e:
    print(f"\nERROR: {e}")
