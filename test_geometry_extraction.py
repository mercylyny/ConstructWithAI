"""
Verification: Phase 12.0 - Geometric Wall Extraction
Tests the vision-based wall extraction logic on the sample architectural plan.
"""

from services.geometry_service import extract_geometry_from_image
import json
import os

def test_nansana_geometry():
    print("=" * 80)
    print("TESTING GEOMETRY EXTRACTION: NANSANA LAYOUT_page_1.png")
    print("=" * 80)
    
    # Path to the image generated in previous steps
    img_path = os.path.join("outputs", "pdf_images", "NANSANA LAYOUT_page_1.png")
    
    if not os.path.exists(img_path):
        print(f"Error: Image not found at {img_path}")
        return

    # Run extraction
    result = extract_geometry_from_image(img_path, scale_px_per_m=85.0) # Adjusted scale based on typical 1:100 layout on A3
    
    print(f"\nDetected Walls: {len(result['walls'])}")
    print(f"Detected Rooms: {result['detected_rooms']}")
    print(f"Geometry Quality: {result['geometry_quality']}")
    
    if result['walls']:
        print("\nSample Walls:")
        for wall in result['walls'][:5]:
            print(f"- {wall['wall_id']}: {wall['length_m']}m, {wall['thickness_mm']}mm (Conf: {wall['confidence']})")
    
    # Save to file for user inspection
    with open("geometry_extraction_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nSUCCESS: Result saved to geometry_extraction_result.json")

if __name__ == "__main__":
    try:
        test_nansana_geometry()
    except Exception as e:
        print(f"\n[ERROR] VERIFICATION FAILED: {str(e)}")
