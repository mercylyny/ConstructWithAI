from typing import List, Dict, Any
from schemas.learning import LearningAnalysis, LearningResponse, LearnedRule

def extract_learning_patterns(
    original_ocr: str,
    corrections: Dict[str, Any],
    finalized_boq: Dict[str, Any],
    building_context: Dict[str, Any]
) -> LearningResponse:
    """
    Analyzes the delta between AI prediction and human correction to extract reusable rules.
    """
    learned_rules = []
    auto_apply = []
    require_human = []
    
    # 1. OCR Pattern Learning (Character-level)
    ocr_corrections = corrections.get("ocr_text", {})
    for error_str, correct_str in ocr_corrections.items():
        if error_str.upper() != correct_str.upper():
            learned_rules.append(LearnedRule(
                trigger_pattern=error_str,
                action=f"Auto-correct to '{correct_str}'",
                confidence_adjustment=0.15,
                scope="OCR"
            ))
            auto_apply.append(f"OCR string replacement: {error_str} -> {correct_str}")

    # 2. Interpretation Learning (Role Mapping)
    prediction_deltas = corrections.get("interpretation_deltas", [])
    for delta in prediction_deltas:
        # Example: if user habitually changes 'PARTITION' to 'LOAD_BEARING' for specific thicknesses
        if delta['predicted'] == "PARTITION" and delta['corrected'] == "LOAD_BEARING":
            learned_rules.append(LearnedRule(
                trigger_pattern=f"Thickness {delta['thickness']}mm",
                action="Default to LOAD_BEARING for this building type",
                confidence_adjustment=0.2,
                scope="INTERPRETATION"
            ))
            require_human.append(f"Verify Load Bearing status for {delta['thickness']}mm walls in {building_context.get('type', 'Standard')} buildings.")

    # 3. Estimation Bias Learning
    quantity_delta = corrections.get("quantity_bias", 0.0) # e.g., 0.05 for 5% underestimation
    if abs(quantity_delta) > 0.02:
        learned_rules.append(LearnedRule(
            trigger_pattern="Global Volume Calculation",
            action=f"Apply {quantity_delta*100}% variance buffer",
            confidence_adjustment=-0.05,
            scope="ESTIMATION"
        ))
        auto_apply.append(f"Apply {quantity_delta*100}% waste/variance buffer based on past audit.")

    # 4. Systems Note
    note = (
        "Intelligence Update: Patterns identified from verified human audit. "
        "Rules extracted are weighted towards engineering safety and regional construction norms."
    )

    analysis = LearningAnalysis(
        learned_rules=learned_rules,
        future_guidance={
            "auto_apply": auto_apply,
            "require_human": require_human
        },
        engineering_note=note
    )
    
    return LearningResponse(learning_analysis=analysis)
