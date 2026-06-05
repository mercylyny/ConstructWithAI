"""
Verification: Phase 12.1 - Semantic Wall Classification
Tests the classification logic on geometrically extracted walls from geometry_extraction_result.json.
"""

import json
import os
from services.semantic_classification_service import classify_walls_semantically

def test_semantic_classification():
    print("=" * 80)
    print("TESTING SEMANTIC CLASSIFICATION: geometry_extraction_result.json")
    print("=" * 80)
    
    # Path to the geometric results
    geom_path = "geometry_extraction_result.json"
    
    if not os.path.exists(geom_path):
        print(f"Error: Geometric results not found at {geom_path}")
        return

    # Load data
    with open(geom_path, "r") as f:
        geom_data = json.load(f)
        
    walls = geom_data.get("walls", [])
    if not walls:
        print("Error: No walls found in geometric results.")
        return

    # Run classification
    result = classify_walls_semantically(walls)
    
    print(f"\nTotal Walls Classified: {len(result.classified_walls)}")
    print(f"Overall Quality: {result.overall_classification_quality}")
    
    # Analyze distribution
    types = [w.wall_type for w in result.classified_walls]
    from collections import Counter
    counts = Counter(types)
    
    print("\nWall Type Distribution:")
    for w_type, count in counts.items():
        print(f"- {w_type}: {count}")
        
    # Sample check
    print("\nSample Classifications:")
    for wall in result.classified_walls[:10]:
        print(f"- {wall.wall_id}: {wall.wall_type} (Conf: {wall.classification_confidence})")
        print(f"  Reasoning: {wall.reasoning}")
    
    # Save results
    output_path = "semantic_classification_result.json"
    with open(output_path, "w") as f:
        json.dump(result.dict(), f, indent=2)
    print(f"\nSUCCESS: Results saved to {output_path}")

if __name__ == "__main__":
    try:
        test_semantic_classification()
    except Exception as e:
        print(f"\n[ERROR] VERIFICATION FAILED: {str(e)}")
