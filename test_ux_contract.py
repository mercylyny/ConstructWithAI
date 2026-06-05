
import unittest
from services.readiness_service import analyze_project_readiness, ReadinessAssessment

class TestUXContract(unittest.TestCase):
    
    def test_perfect_scenario(self):
        """High confidence, all data -> No intervention"""
        data = {
            "confidence_score": 0.9,
            "total_project_cost": 100000,
            "walls": [{"label": "W1"}],
            "warnings": []
        }
        result = analyze_project_readiness(data)
        self.assertFalse(result.intervention_needed)
        self.assertEqual(len(result.missing_critical_data), 0)
        self.assertEqual(result.readiness_status, "READY")

    def test_low_confidence(self):
        """Low confidence -> Intervention required"""
        data = {
            "confidence_score": 0.4,
            "total_project_cost": 100000,
            "walls": [{"label": "W1"}],
            "warnings": ["blurry"]
        }
        result = analyze_project_readiness(data)
        self.assertTrue(result.intervention_needed)
        self.assertIn("Low Confidence", result.missing_critical_data)

    def test_missing_quantities(self):
        """No walls -> Intervention required"""
        data = {
            "confidence_score": 0.8,
            "total_project_cost": 0, # No quantities basically means no cost usually
            "walls": [],
            "warnings": []
        }
        result = analyze_project_readiness(data)
        self.assertTrue(result.intervention_needed)
        self.assertIn("Measurements", result.missing_critical_data)

if __name__ == '__main__':
    unittest.main()
