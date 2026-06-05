"""
Test script for Phase 7.3.2: OCR Post-processing
"""
from services.ocr_postprocess import clean_ocr_text, extract_measurements, extract_labels, postprocess_ocr

# Test data simulating noisy OCR output
raw_ocr_text = """
--- Page 1 ---

FLOOR  PLAN   -   LEVEL  1

Wall A    4.5m
W2  3600mm
External   Wall   240x1200

HEIGHT   3.0m

░░░ ROOM   A ░░░
DOOR  900x2100mm
WINDOW  1200x1500

COLUMN   C1
GRID   LINE   A-A

Dimensions:  10x20m
Scale  1:100

©  2024  Construction  Co.
"""

print("="*70)
print("PHASE 7.3.2: OCR POST-PROCESSING TEST")
print("="*70)

print("\n1. RAW OCR TEXT:")
print("-"*70)
print(raw_ocr_text)
print("-"*70)

# Test cleaning
clean_text = clean_ocr_text(raw_ocr_text)
print("\n2. CLEANED TEXT:")
print("-"*70)
print(clean_text)
print("-"*70)

# Test measurement extraction
measurements = extract_measurements(raw_ocr_text)
print("\n3. EXTRACTED MEASUREMENTS:")
print(f"Found {len(measurements)} measurements:")
for m in measurements:
    print(f"  - {m}")

# Test label extraction
labels = extract_labels(raw_ocr_text)
print("\n4. EXTRACTED LABELS:")
print(f"Found {len(labels)} labels:")
for label in labels:
    print(f"  - {label}")

# Test complete pipeline
result = postprocess_ocr(raw_ocr_text)
print("\n5. COMPLETE PIPELINE RESULT:")
print(f"Clean text length: {len(result['clean_text'])} chars")
print(f"Measurements: {len(result['measurements'])}")
print(f"Labels: {len(result['labels'])}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
