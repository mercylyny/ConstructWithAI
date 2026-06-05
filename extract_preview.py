import os, sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

BASE = r"c:\Users\MERCYLYNY\Desktop\pro"
sys.path.insert(0, BASE)
os.chdir(BASE)

from services.automation_service import PlanAnalyzer

print("Running PlanAnalyzer on Final.pdf (150 DPI)...")
result = PlanAnalyzer.analyze("Final.pdf")
print("======== ANALYSIS RESULTS ========")
print("Status    : " + str(result.status))
print("Rooms     : " + str(result.summary.rooms))
print("Bedrooms  : " + str(result.summary.bedrooms))
print("Kitchens  : " + str(result.summary.kitchens))
print("Bathrooms : " + str(result.summary.bathrooms))
print("Walls     : " + str(result.summary.walls))
print("Doors     : " + str(result.summary.doors))
print("Windows   : " + str(result.summary.windows))
print("Columns   : " + str(result.summary.columns))
print("Stairs    : " + str(result.summary.stairs))
print("Beams     : " + str(result.summary.beams))
print("Confidence: " + str(result.summary.confidence))
print("Message   : " + str(result.message))
print("==================================")
