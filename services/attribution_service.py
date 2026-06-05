from typing import List, Dict, Any, Optional
from schemas.attribution import AttributedValue, AttributionResponse, EvidenceSource

def attribute_engineering_evidence(
    quantities: List[Dict[str, Any]],
    raw_ocr: str,
    assumptions: List[str],
    overrides: Optional[Dict[str, Any]] = None
) -> AttributionResponse:
    """
    Attaches traceable evidence and risk assessments to each construction value.
    """
    attributed_list = []
    overrides = overrides or {}
    
    for qty in quantities:
        name = qty['name']
        val = qty['value']
        unit = qty['unit']
        
        # Determine Source & Evidence
        evidence = []
        risk_flag = "LOW"
        
        # 1. Check for Human Override
        if name in overrides:
            source = "HUMAN"
            confidence = 1.0
            evidence.append(EvidenceSource(type="text", reference=f"User correction: {overrides[name]}"))
            
        # 2. Check for OCR Extraction
        elif qty.get("ocr_snippet"):
            source = "OCR"
            confidence = qty.get("confidence", 0.8)
            evidence.append(EvidenceSource(type="text", reference=f"Regex match: {qty['ocr_snippet']}"))
            if confidence < 0.6: risk_flag = "MEDIUM"
            
        # 3. Check for Learned Rule
        elif qty.get("applied_rule"):
            source = "LEARNED_RULE"
            confidence = 0.9
            evidence.append(EvidenceSource(type="rule", reference=qty['applied_rule']))
            
        # 4. Fallback to Assumption
        else:
            source = "ASSUMPTION"
            confidence = 0.5
            matching_assumption = next((a for a in assumptions if name.lower() in a.lower()), "Standard engineering default")
            evidence.append(EvidenceSource(type="text", reference=matching_assumption))
            risk_flag = "HIGH"

        attributed_list.append(AttributedValue(
            name=name,
            value=val,
            unit=unit,
            source=source,
            confidence=confidence,
            evidence=evidence,
            risk_flag=risk_flag
        ))

    commentary = (
        "Evidence analysis complete. High-risk values identified where plan annotations were missing, "
        "requiring standard assumption fallbacks. Professional cross-check recommended for all 'HIGH' risk flags."
    )

    return AttributionResponse(
        attributed_values=attributed_list,
        engineering_commentary=commentary
    )
