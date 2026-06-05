"""
Verification: Phase 13.1 - Wall Normalization & Segmentation
Tests the normalization of thicknesses and segmentation of long walls.
"""

import json
from services.normalization_service import normalize_and_segment_walls

def test_normalization_and_segmentation():
    print("=" * 80)
    print("TESTING WALL NORMALIZATION & SEGMENTATION")
    print("=" * 80)
    
    # Mock data based on user requirement rules
    mock_walls = [
        {
            "wall_id": "W1",
            "length_m": 10.0,
            "height_m": 3.0,
            "net_area_m2": 30.0,
            "thickness_mm": 225, # Original thickness (to be normalized to 230)
            "confidence": 0.8
        },
        {
            "wall_id": "W2",
            "length_m": 4.5,
            "height_m": 3.0,
            "net_area_m2": 13.5,
            "thickness_mm": 110, # Original thickness (to be normalized to 100)
            "confidence": 0.9
        },
        {
            "wall_id": "W3",
            "length_m": 5.0,
            "height_m": 3.0,
            "net_area_m2": 15.0,
            "thickness_mm": 260, # Deviation > 20mm (to be normalized to 230/300 and flagged)
            "confidence": 0.7
        }
    ]

    # Run service
    result = normalize_and_segment_walls(mock_walls)
    
    print(f"\nTotal Segments Generated: {len(result.wall_segments)}")
    print(f"Segmentation Quality: {result.segmentation_quality}")
    
    # Verify Segmentation of W1 (10m -> 2 segments of 5m)
    w1_segments = [s for s in result.wall_segments if s.parent_wall_id == "W1"]
    print(f"\nW1 Segmentation Check: {len(w1_segments)} segments (Expected 2)")
    for s in w1_segments:
        print(f"- {s.segment_id}: Len={s.segment_length_m}m, Area={s.segment_net_area_m2}m2, Conf={s.segment_confidence}")

    # Verify Normalization of W1 (225mm -> 230mm)
    print(f"\nW1 Normalization: {w1_segments[0].original_thickness_mm}mm -> {w1_segments[0].normalized_thickness_mm}mm")
    
    # Verify Flagging of W3 (260mm -> 230mm, deviation 30mm > 20mm)
    w3_segment = next(s for s in result.wall_segments if s.parent_wall_id == "W3")
    print(f"\nW3 Flagging Check: Normalized={w3_segment.normalized_thickness_mm}mm, Original={w3_segment.original_thickness_mm}mm, Review Flag={w3_segment.review_flag} (Expected True)")

    # Save results
    output_path = "wall_normalization_result.json"
    with open(output_path, "w") as f:
        json.dump(result.dict(), f, indent=2)
    print(f"\nSUCCESS: Results saved to {output_path}")

if __name__ == "__main__":
    test_normalization_and_segmentation()
