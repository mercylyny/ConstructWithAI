
import unittest
from services.fusion_service import fuse_estimation_data
from schemas.estimation import WallQuantity

class TestHybridFusion(unittest.TestCase):
    
    def test_ocr_only(self):
        """Scenario 1: No manual input. OCR walls should return as is (tagged OCR)."""
        ocr_walls = [
            WallQuantity(label="W1", length_m=5.0, height_m=3.0, thickness_m=0.2, area_sqm=15.0, volume_cum=3.0)
        ]
        fused = fuse_estimation_data(ocr_walls, None)
        
        self.assertEqual(len(fused), 1)
        self.assertEqual(fused[0].label, "W1")
        self.assertEqual(fused[0].data_source, "OCR")
        self.assertEqual(fused[0].confidence_weight, 0.7)

    def test_manual_only(self):
        """Scenario 2: Manual input only. Should return Manual walls (tagged MANUAL)."""
        ocr_walls = []
        manual_walls = [
            WallQuantity(label="Pool Wall", length_m=10.0, height_m=2.0, thickness_m=0.3, area_sqm=20.0, volume_cum=6.0)
        ]
        
        fused = fuse_estimation_data(ocr_walls, manual_walls)
        
        self.assertEqual(len(fused), 1)
        self.assertEqual(fused[0].label, "Pool Wall")
        self.assertEqual(fused[0].data_source, "MANUAL")
        self.assertEqual(fused[0].confidence_weight, 1.0)
        
    def test_overlap_fusion(self):
        """Scenario 3: Overlap. Manual should override OCR."""
        ocr_walls = [
            WallQuantity(label="W1", length_m=5.0, height_m=3.0, thickness_m=0.2, area_sqm=15.0, volume_cum=3.0)
        ]
        
        # User corrects W1 length to 6.0m
        manual_walls = [
            WallQuantity(label="W1", length_m=6.0, height_m=3.0, thickness_m=0.2, area_sqm=18.0, volume_cum=3.6)
        ]
        
        fused = fuse_estimation_data(ocr_walls, manual_walls)
        
        self.assertEqual(len(fused), 1)
        w = fused[0]
        self.assertEqual(w.label, "W1")
        self.assertEqual(w.length_m, 6.0) # Manual value
        self.assertEqual(w.data_source, "HYBRID")
        self.assertEqual(w.confidence_weight, 0.95)

    def test_gap_filling(self):
        """Scenario 4: Partial overlap. OCR walls that don't match manual are kept."""
        ocr_walls = [
            WallQuantity(label="W1", length_m=5.0, height_m=3.0, thickness_m=0.2, area_sqm=15.0, volume_cum=3.0),
            WallQuantity(label="W2", length_m=4.0, height_m=3.0, thickness_m=0.2, area_sqm=12.0, volume_cum=2.4)
        ]
        
        # User only provides W3 (new)
        manual_walls = [
            WallQuantity(label="W3", length_m=2.0, height_m=2.0, thickness_m=0.1, area_sqm=4.0, volume_cum=0.4)
        ]
        
        fused = fuse_estimation_data(ocr_walls, manual_walls)
        
        self.assertEqual(len(fused), 3) # W1(OCR), W2(OCR), W3(MANUAL)
        
        # Check W1
        w1 = next(w for w in fused if w.label == "W1")
        self.assertEqual(w1.data_source, "OCR")
        
        # Check W3
        w3 = next(w for w in fused if w.label == "W3")
        self.assertEqual(w3.data_source, "MANUAL")

if __name__ == '__main__':
    unittest.main()
