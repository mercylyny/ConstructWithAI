from services.ocr_postprocess import postprocess_ocr
from services.semantic_interpreter import interpret_walls
from services.plan_analysis_service import analyze_building_components

sample_ocr = """200       2.300    2001110001.200       3.300      200
450         40
SWKITCHEN       S       7
S       .              900         M2
3         SHADE              7
N200     1.500      1.300    900.1500.900..200
200       3.500      200       3.300     200
GROUNDFLOORLAYOUTPLANL--03
SCALE1100
"""

result = postprocess_ocr(sample_ocr)
walls_out = interpret_walls(result['clean_text'], result['measurements'], result['labels'])
components = analyze_building_components(result['clean_text'], result['labels'], walls_out['walls'])

print("=== LABELS ===")
for l in result['labels']:
    print("  -", l)

print()
print("=== WALLS FOUND:", len(walls_out['walls']), "===")
for w in walls_out['walls']:
    print("  ", w['label'], ":", w['length_m'], "m")

print()
print("=== COMPONENTS ===")
for k, v in components.items():
    if v:
        print("  ", k, ":", v)

total_length = sum(w['length_m'] for w in walls_out['walls'])
print()
print("Total wall perimeter:", round(total_length, 2), "m")
print("Scale detected:", result['scale_ratio'])
print("Measurements found:", len(result['measurements']))
