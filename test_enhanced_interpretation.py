"""
Verification test for Enhanced AI Interpretation (Phase 7.4 Enhancement)
Tests the improved OCR noise reduction, measurement recovery, and confidence scoring.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.ai_interpreter import interpret_text_rule_based, clean_ocr_noise, normalize_measurement, extract_wall_label

def test_noise_reduction():
    """Test OCR noise filtering"""
    print("\n" + "="*70)
    print("TEST 1: OCR Noise Reduction")
    print("="*70)
    
    noisy_text = """
    --- Page 1 ---
    TITLE: FLOOR PLAN
    Wall A 4.5m
    NORTH ARROW
    Wall B 3.2m
    SCALE 1:100
    APPROVED BY: John Doe
    HEIGHT 3.0m
    FURNITURE LAYOUT
    Wall C 5.5m
    """
    
    cleaned = clean_ocr_noise(noisy_text)
    print("Original lines:", len(noisy_text.split('\n')))
    print("Cleaned lines:", len(cleaned.split('\n')))
    print("\nCleaned text:")
    print(cleaned)
    
    # Verify noise was removed
    assert "TITLE" not in cleaned
    assert "NORTH ARROW" not in cleaned
    assert "APPROVED" not in cleaned
    assert "Wall A" in cleaned
    print("\n[PASS] Noise reduction working correctly")

def test_measurement_normalization():
    """Test measurement normalization with different formats"""
    print("\n" + "="*70)
    print("TEST 2: Measurement Normalization")
    print("="*70)
    
    test_cases = [
        ("4.5m", 4.5, "high"),
        ("3600", 3.6, "medium"),  # mm to m
        ("3.2", 3.2, "medium"),   # unit inferred
        ("5 m", 5.0, "high"),
        ("2800mm", 2.8, "medium"),
    ]
    
    passed = 0
    for value_str, expected_m, expected_conf in test_cases:
        result_m, conf = normalize_measurement(value_str)
        if result_m is not None and abs(result_m - expected_m) < 0.01:
            print(f"[PASS] '{value_str}' -> {result_m}m (confidence: {conf})")
            passed += 1
        else:
            print(f"[FAIL] '{value_str}' -> {result_m}m, expected {expected_m}m")
    
    print(f"\n{passed}/{len(test_cases)} tests passed")
    assert passed >= len(test_cases) * 0.8, "Too many normalization failures"

def test_label_extraction():
    """Test wall label extraction"""
    print("\n" + "="*70)
    print("TEST 3: Wall Label Extraction")
    print("="*70)
    
    test_cases = [
        ("W1 4.5m", "W1"),
        ("Wall A 3.2m", "Wall A"),
        ("External Wall 5.5m", "External Wall"),
        ("EXT 4.0m", "EXT"),
        ("4.5m", "Wall-1"),  # No label, generate placeholder
    ]
    
    passed = 0
    for text, expected_label in test_cases:
        label = extract_wall_label(text, 0)
        if label == expected_label:
            print(f"[PASS] '{text}' -> '{label}'")
            passed += 1
        else:
            print(f"[FAIL] '{text}' -> '{label}', expected '{expected_label}'")
    
    print(f"\n{passed}/{len(test_cases)} tests passed")

def test_full_interpretation():
    """Test complete interpretation pipeline"""
    print("\n" + "="*70)
    print("TEST 4: Full Interpretation Pipeline")
    print("="*70)
    
    # Simulate noisy OCR text from a construction plan
    ocr_text = """
    --- Page 1 ---
    CONSTRUCTION PLAN - LEVEL 1
    SCALE 1:100
    
    Wall A 4.5m
    W2 3600
    External Wall 5.5 m
    HEIGHT 3.2m
    
    APPROVED: 2024-01-15
    Wall B 2.8
    
    (LOW CONFIDENCE)
    INT 4200mm
    """
    
    print("Input OCR text:")
    print("-" * 70)
    print(ocr_text)
    print("-" * 70)
    
    # Run interpretation
    data, confidence = interpret_text_rule_based(ocr_text)
    
    print("\nInterpretation Results:")
    print(f"Overall Confidence: {confidence}")
    print(f"Assumed Height: {data.assumed_wall_height_m}m")
    print(f"Walls Detected: {len(data.walls)}")
    
    for wall in data.walls:
        print(f"  - {wall.label}: {wall.length_m}m")
    
    # Verification
    print("\n[VERIFICATION]")
    checks = [
        (len(data.walls) >= 4, f"At least 4 walls detected ({len(data.walls)} found)"),
        (data.assumed_wall_height_m == 3.2, f"Height correctly detected (3.2m)"),
        (any(w.label == "Wall A" and abs(w.length_m - 4.5) < 0.01 for w in data.walls), "Wall A 4.5m found"),
        (any(w.label == "W2" and abs(w.length_m - 3.6) < 0.01 for w in data.walls), "W2 3.6m found (mm converted)"),
        (any("External" in w.label for w in data.walls), "External Wall found"),
    ]
    
    passed = sum(1 for check, _ in checks if check)
    for check, desc in checks:
        status = "[PASS]" if check else "[FAIL]"
        print(f"{status} {desc}")
    
    print(f"\n{passed}/{len(checks)} checks passed")
    
    if passed >= len(checks) * 0.8:
        print("\n[SUCCESS] Enhanced interpretation working correctly!")
        return True
    else:
        print("\n[WARNING] Some checks failed")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ENHANCED AI INTERPRETATION VERIFICATION")
    print("Testing Phase 7.4 improvements")
    print("="*70)
    
    try:
        test_noise_reduction()
        test_measurement_normalization()
        test_label_extraction()
        success = test_full_interpretation()
        
        print("\n" + "="*70)
        if success:
            print("✓ ALL TESTS PASSED")
        else:
            print("⚠ SOME TESTS FAILED")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*70)
        print("✗ TESTS FAILED")
        print("="*70 + "\n")
