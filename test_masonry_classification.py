"""
Verification: Phase 13.2 - Masonry System Classification
Tests the classification of wall segments into BRICK/BLOCK and roles.
"""

import json
from services.masonry_service import classify_masonry_details

def test_masonry_classification():
    print("=" * 80)
    print("TESTING MASONRY SYSTEM CLASSIFICATION")
    print("=" * 80)
    
    # Mock data with various thicknesses
    mock_segments = [
        {
            "segment_id": "W1-S1",
            "parent_wall_id": "W1",
            "normalized_thickness_mm": 230, # BRICK | LOAD_BEARING
            "segment_confidence": 0.8
        },
        {
            "segment_id": "W2-S1",
            "parent_wall_id": "W2",
            "normalized_thickness_mm": 100, # BLOCK | PARTITION
            "segment_confidence": 0.9
        },
        {
            "segment_id": "W3-S1",
            "parent_wall_id": "W3",
            "normalized_thickness_mm": 300, # BLOCK | STRUCTURAL
            "segment_confidence": 0.7
        },
        {
            "segment_id": "W4-S1",
            "parent_wall_id": "W4",
            "normalized_thickness_mm": 200, # BLOCK | LOAD_BEARING
            "segment_confidence": 0.85
        }
    ]

    # Run service
    result = classify_masonry_details(mock_segments)
    
    print(f"\nTotal Segments Classified: {len(result.classified_segments)}")
    print(f"Project Masonry System: {result.project_masonry_system} (Expected: HYBRID)")
    
    # Verify Individual Classifications
    for seg in result.classified_segments:
        print(f"- {seg.segment_id}: Type={seg.masonry_type}, Role={seg.masonry_role}, Conf={seg.confidence}")

    # Assertions for verification
    w1 = next(s for s in result.classified_segments if s.segment_id == "W1-S1")
    assert w1.masonry_type == "BRICK"
    assert w1.masonry_role == "LOAD_BEARING"
    
    w2 = next(s for s in result.classified_segments if s.segment_id == "W2-S1")
    assert w2.masonry_type == "BLOCK"
    assert w2.masonry_role == "PARTITION"
    
    w3 = next(s for s in result.classified_segments if s.segment_id == "W3-S1")
    assert w3.masonry_type == "BLOCK"
    assert w3.masonry_role == "STRUCTURAL"
    
    assert result.project_masonry_system == "HYBRID"

    # Save results
    output_path = "masonry_classification_result.json"
    with open(output_path, "w") as f:
        json.dump(result.dict(), f, indent=2)
    print(f"\nSUCCESS: Results saved to {output_path}")

if __name__ == "__main__":
    try:
        test_masonry_classification()
    except Exception as e:
        print(f"\n[ERROR] VERIFICATION FAILED: {str(e)}")
