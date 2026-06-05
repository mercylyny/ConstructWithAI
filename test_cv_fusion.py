import unittest
from unittest.mock import patch
import os

from services.automation_service import PlanAnalyzer
from schemas.estimation import PlanAnalysisResult

class TestCVFusion(unittest.TestCase):
    def setUp(self):
        self.sample_img = "test_plan_cv.png"
        with open(os.path.join("uploads", self.sample_img), "w") as f:
            f.write("fake image data")

    def tearDown(self):
        if os.path.exists(os.path.join("uploads", self.sample_img)):
            os.remove(os.path.join("uploads", self.sample_img))

    @patch('services.automation_service.perform_ocr_on_image')
    @patch('services.automation_service.detect_architectural_components')
    def test_fusion_with_yolo(self, mock_detect, mock_ocr):
        # Mock OCR returning our text
        mock_ocr.return_value = "Living Room 3500x4000\nBedroom 3.0m x 3.5m\nW1 4.5m"
        
        # Mock YOLO returning counts
        mock_detect.return_value = {
            "doors": 4,
            "windows": 6,
            "stairs": 1,
            "columns": 2
        }

        # Analyze plan
        result = PlanAnalyzer.analyze(self.sample_img, use_qs_fallbacks=False)
        
        self.assertEqual(result.status, "SUCCESS")
        
        # Check YOLO counts took precedence
        self.assertEqual(result.summary.doors, 4)
        self.assertEqual(result.summary.windows, 6)
        self.assertEqual(result.summary.stairs, 1)
        self.assertEqual(result.summary.columns, 2)
        
        # Check that room dimension parsing extracted walls implicitly
        self.assertGreater(result.summary.walls, 0)
        self.assertGreaterEqual(result.summary.rooms, 2)

if __name__ == "__main__":
    unittest.main()
