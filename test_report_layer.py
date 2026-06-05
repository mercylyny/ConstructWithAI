"""
Verification test for PDF Report Generation (Phase 7.7)
"""
import os
import requests
from fastapi.testclient import TestClient
from main import app
from schemas.costing import CostEstimationRequest, MaterialQuantities

client = TestClient(app)

print("="*70)
print("TEST: PDF BOQ Generation")
print("="*70)

# Ensure output dir exists
os.makedirs("outputs/reports", exist_ok=True)

# Test Data
payload = {
  "quantities": {
    "total_bricks_count": 5000,
    "total_mortar_volume_m3": 1.5
  },
  "custom_rates": {
    "cement_bag_price_ugx": 35000,
    "sand_ton_price_ugx": 60000
  }
}

print("Sending request to /ai/report/boq/pdf...")
try:
    response = client.post("/ai/report/boq/pdf", json=payload)
    
    if response.status_code == 200:
        print("✅ Response 200 OK")
        print(f"Content-Type: {response.headers['content-type']}")
        
        # Save to verify content visually if needed, though endpoint returns file
        # The TestClient response content is bytes
        if len(response.content) > 1000:
            print(f"✅ Received PDF bytes ({len(response.content)} bytes)")
            
            # Save a local copy to check manually
            with open("test_output_boq.pdf", "wb") as f:
                f.write(response.content)
            print("Saved 'test_output_boq.pdf' for manual inspection.")
            
        else:
            print("❌ PDF content seems too small.")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Exception: {e}")
