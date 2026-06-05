"""
Production Pipeline Test - Real Construction Plan
Tests the full Phase 10.0-10.3 system with actual PDF
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_pipeline(filename):
    """Run pipeline on real PDF and display results"""
    
    print("=" * 80)
    print(f"TESTING PRODUCTION PIPELINE: {filename}")
    print("=" * 80)
    print("\nPhases Being Tested:")
    print("✓ Phase 10.0: Full Automation (PDF → OCR → Interpretation → Costs)")
    print("✓ Phase 10.2: Data Fusion (Ready for manual overrides)")
    print("✓ Phase 10.3: UX Contract (Intervention flags)")
    print("\n" + "-" * 80)
    
    # Call the pipeline
    print(f"\n⏳ Processing {filename}...")
    print("   [PDF → Images → OCR → AI Interpretation → Quantities → Materials → Costs]")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/pipeline/run",
            json={"filename": filename},
            timeout=120  # 2 minute timeout for processing
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code != 200:
            print(f"\n❌ API Error: {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        
        # Display Results
        print(f"\n{'=' * 80}")
        print("PIPELINE EXECUTION RESULTS")
        print("=" * 80)
        
        print(f"\n📊 STATUS: {result['status']}")
        print(f"⏱️  Processing Time: {elapsed:.2f} seconds")
        
        if result['status'] == 'FAILED':
            print(f"\n❌ Failed at: {result.get('failed_step', 'Unknown')}")
            print(f"   Reason: {result.get('failure_reason', 'Unknown')}")
            return
        
        # Phase 10.0 Results
        print(f"\n🏗️  PHASE 10.0: AUTOMATION RESULTS")
        print(f"   Walls Detected: {result['wall_count']}")
        print(f"   Total Cost: UGX {result['total_cost']:,.0f}")
        print(f"   OCR Text (Preview): {result['extracted_text'][:100]}...")
        
        # Phase 10.3 Results
        print(f"\n🤖 PHASE 10.3: UX CONTRACT & ACCOUNTABILITY")
        print(f"   Intervention Needed: {result['intervention_needed']}")
        
        if result['intervention_needed']:
            print(f"   ⚠️  Missing Critical Data: {', '.join(result['missing_critical_data'])}")
            print(f"   Confidence Breakdown: {result['confidence_breakdown']}")
        else:
            print(f"   ✅ AI handled everything automatically!")
        
        print(f"\n📋 READINESS ASSESSMENT")
        print(f"   Status: {result['readiness_status']}")
        print(f"   Score: {result['readiness_score']:.2f}")
        
        # Reports Generated
        print(f"\n📄 REPORTS GENERATED")
        if result.get('boq_excel_path'):
            print(f"   Excel BOQ: {result['boq_excel_path']}")
        if result.get('narrative_report'):
            print(f"   Narrative Report: Generated ({len(result['narrative_report'])} chars)")
        
        # Full JSON Response
        print(f"\n💾 FULL RESPONSE (JSON)")
        print("-" * 80)
        print(json.dumps(result, indent=2))
        
        # Next Steps Based on Results
        print(f"\n{'=' * 80}")
        print("NEXT STEPS")
        print("=" * 80)
        
        if result['intervention_needed']:
            print("\n🔧 RECOMMENDED ACTIONS:")
            print("   1. Review the missing critical data listed above")
            print("   2. Prepare manual corrections if needed")
            print("   3. Re-run with manual_walls parameter (Phase 10.2)")
            print("\n   Example:")
            print('   POST /pipeline/run')
            print('   {')
            print('     "filename": "' + filename + '",')
            print('     "manual_walls": [')
            print('       {"label": "W1", "length_m": 6.5, "height_m": 3.0, ...}')
            print('     ]')
            print('   }')
        else:
            print("\n✅ ESTIMATION COMPLETE - Ready for Production Use")
            print(f"   Export available at: {result.get('boq_excel_path', 'N/A')}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server")
        print("   Ensure server is running: uvicorn main:app --reload")
    except requests.exceptions.Timeout:
        print("\n⏱️  Request timed out (processing took > 2 minutes)")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == '__main__':
    import sys
    
    # Test with the real PDF
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # Default to NANSANA LAYOUT
        filename = "NANSANA LAYOUT.pdf"
    
    print("\n")
    print("🏗️  CONSTRUCTION ESTIMATION SYSTEM - PRODUCTION TEST")
    print(f"    Testing with: {filename}")
    print("\n")
    
    test_pipeline(filename)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80 + "\n")
