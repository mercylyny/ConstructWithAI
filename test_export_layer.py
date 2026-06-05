"""
Verification test for Export Layer (Phase 7.8)
"""
import os
import csv
from services.export_service import export_boq_to_csv, export_boq_to_excel

print("="*70)
print("TEST: BOQ Export (Excel & CSV)")
print("="*70)

# Mock Data (simulating CostEstimationResponse dict)
test_data = {
    "currency": "UGX",
    "total_project_cost": 1500000.0,
    "line_items": [
        {"item": "Bricks", "quantity": 1000, "unit": "pcs", "rate": 400, "amount": 400000},
        {"item": "Cement", "quantity": 20, "unit": "bags", "rate": 35000, "amount": 700000},
        {"item": "Sand", "quantity": 5, "unit": "tons", "rate": 80000, "amount": 400000}
    ]
}

# 1. CSV Test
print("\n--- Testing CSV Export ---")
try:
    csv_path = export_boq_to_csv(test_data)
    print(f"✅ CSV Generated: {csv_path}")
    
    # Verify content
    with open(csv_path, 'r') as f:
        content = f.read()
        print("Preview:")
        print(content.strip())
        if "TOTAL PROJECT COST" in content and "1500000.0" in content:
            print("✅ Content Verification PASSED")
        else:
            print("❌ Content Verification FAILED")
            
except Exception as e:
    print(f"❌ CSV Error: {e}")

# 2. Excel Test
print("\n--- Testing Excel Export ---")
try:
    xlsx_path = export_boq_to_excel(test_data)
    print(f"✅ Excel Generated: {xlsx_path}")
    if os.path.exists(xlsx_path) and os.path.getsize(xlsx_path) > 0:
         print(f"✅ File exists and size > 0 ({os.path.getsize(xlsx_path)} bytes)")
    else:
         print("❌ File check FAILED")
         
except Exception as e:
    print(f"❌ Excel Error: {e}")
    if "openpyxl" in str(e):
        print("💡 Hint: Ensure openpyxl is installed.")
