"""
Verification: Phase 12.2 - Wall Opening Detection
Tests the detection of doors and windows on classified walls.
"""

import json
import os
from services.opening_service import detect_openings_on_walls

def test_opening_detection():
    print("=" * 80)
    print("TESTING OPENING DETECTION: NANSANA LAYOUT_page_1.png")
    print("=" * 80)
    
    # Path to image and classified wall results
    img_path = os.path.join("outputs", "pdf_images", "NANSANA LAYOUT_page_1.png")
    classified_walls_path = "semantic_classification_result.json"
    
    if not os.path.exists(img_path):
        print(f"Error: Image not found at {img_path}")
        return
        
    if not os.path.exists(classified_walls_path):
        print(f"Error: Classified walls not found at {classified_walls_path}")
        return

    # Load data
    with open(classified_walls_path, "r") as f:
        classified_data = json.load(f)
        
    walls = classified_data.get("classified_walls", [])
    if not walls:
        print("Error: No walls found in classification results.")
        return

    # Run detection
    result = detect_openings_on_walls(img_path, walls)
    
    print(f"\nTotal Openings Detected: {len(result.openings)}")
    print(f"Detection Quality: {result.opening_detection_quality}")
    
    # Analyze distribution
    types = [o.opening_type for o in result.openings]
    from collections import Counter
    counts = Counter(types)
    
    print("\nOpening Type Distribution:")
    for o_type, count in counts.items():
        print(f"- {o_type}: {count}")
        
    # Sample check
    print("\nSample Openings:")
    for opening in result.openings[:10]:
        print(f"- {opening.opening_id} on {opening.wall_id}: {opening.opening_type}")
        print(f"  Width: {opening.width_m}m, Height: {opening.height_m}m, Conf: {opening.opening_confidence}")
        print(f"  Reasoning: {opening.reasoning}")
    
    # Save results
    output_path = "opening_detection_result.json"
    with open(output_path, "w") as f:
        json.dump(result.dict(), f, indent=2)
    print(f"\nSUCCESS: Results saved to {output_path}")

if __name__ == "__main__":
    try:
        test_opening_detection()
    except Exception as e:
        print(f"\n[ERROR] VERIFICATION FAILED: {str(e)}")
