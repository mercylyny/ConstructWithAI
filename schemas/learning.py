from pydantic import BaseModel
from typing import List, Dict, Any

class LearnedRule(BaseModel):
    trigger_pattern: str
    action: str
    confidence_adjustment: float
    scope: str  # OCR | INTERPRETATION | ESTIMATION

class LearningAnalysis(BaseModel):
    learned_rules: List[LearnedRule]
    future_guidance: Dict[str, List[str]]
    engineering_note: str

class LearningResponse(BaseModel):
    learning_analysis: LearningAnalysis
