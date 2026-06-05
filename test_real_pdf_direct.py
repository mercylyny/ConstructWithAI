"""
Direct Test of Real Construction PDF
Bypasses server to directly test pipeline logic
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.automation_service import PipelineOrchestrator

def test_real_pdf(filename):
    print("=" * 80)
    print(f"TESTING PRODUCTION PIPELINE: {filename}")
    print("=" * 80)
    print("\nPhases Being Tested:")
    print("✓ Phase 10.0: Full Automation (PDF → OCR → Interpretation → Costs)")
    print("✓ Phase 10.2: Data Fusion (Ready for manual overrides)")
    print("✓ Phase 10.3: UX Contract (Intervention flags)")
    print("\n" + "-" * 80)
    
    print(f"\n⏳ Processing {filename}...")
    print("   [PDF → Images → OCR → AI Interpretation → Quantities → Materials → Costs]")
    
    import time
    start_time = time.time()
    
    try:
        # Call pipeline directly
        result = PipelineOrchestrator.run_pipeline(filename)
        
        elapsed = time.time() - start_time
        
        # Display Results
        print(f"\n{'=' * 80}")
        print("PIPELINE EXECUTION RESULTS")
        print("=" * 80)
        
        print(f"\n📊 STATUS: {result.status}")
        print(f"⏱️  Processing Time: {elapsed:.2f} seconds")
        
        if result.status == 'FAILED':
            print(f"\n❌ Failed at: {result.failed_step or 'Unknown'}")
            print(f"   Reason: {result.failure_reason or 'Unknown'}")
            return
        
        # Phase 10.0 Results
        print(f"\n🏗️  PHASE 10.0: AUTOMATION RESULTS")
        print(f"   Walls Detected: {result.wall_count}")
        print(f"   Total Cost: UGX {result.total_cost:,.0f}")
        print(f"   OCR Text (Preview): {result.extracted_text[:150]}...")
        
        # Phase 10.3 Results
        print(f"\n🤖 PHASE 10.3: UX CONTRACT & ACCOUNTABILITY")
        print(f"   Intervention Needed: {result.intervention_needed}")
        
        if result.intervention_needed:
            print(f"   ⚠️  Missing Critical Data: {', '.join(result.missing_critical_data)}")
            print(f"   Confidence Breakdown: {result.confidence_breakdown}")
        else:
            print(f"   ✅ AI handled everything automatically!")
        
        print(f"\n📋 READINESS ASSESSMENT")
        print(f"   Status: {result.readiness_status}")
        print(f"   Score: {result.readiness_score:.2f}")
        
        # Reports Generated
        print(f"\n📄 REPORTS GENERATED")
        if result.boq_excel_path:
            print(f"   Excel BOQ: {result.boq_excel_path}")
        if result.narrative_report:
            print(f"   Narrative Report: Generated ({len(result.narrative_report)} chars)")
            print(f"\n   Preview:")
            print(f"   {result.narrative_report[:300]}...")
        
        # Next Steps
        print(f"\n{'=' * 80}")
        print("NEXT STEPS")
        print("=" * 80)
        
        if result.intervention_needed:
            print("\n🔧 RECOMMENDED ACTIONS:")
            print("   1. Review the missing critical data listed above")
            print("   2. Prepare manual corrections if needed")
            print("   3. Re-run with manual_walls parameter (Phase 10.2)")
        else:
            print("\n✅ ESTIMATION COMPLETE - Ready for Client Review")
            print(f"   Export available at: {result.boq_excel_path or 'N/A'}")
        
        # Save to JSON for verification
        with open("real_plan_result.json", "w") as f:
            import json
            json.dump(result.dict(), f, indent=2)
        print("\n✅ Results saved to real_plan_result.json")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    filename = "NANSANA LAYOUT.pdf"
    
    if not os.path.exists(f"uploads/{filename}"):
        print(f"\n❌ File not found: uploads/{filename}")
        print("\n Available files:")
        for f in os.listdir("uploads"):
            if f.endswith('.pdf'):
                print(f"   - {f}")
        sys.exit(1)
    
    print("\n")
    print("🏗️  CONSTRUCTION ESTIMATION SYSTEM - PRODUCTION TEST")
    print(f"    Testing with Real PDF: {filename}")
    print("\n")
    
    test_real_pdf(filename)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80 + "\n")
