from pydantic import BaseModel
from typing import List

class TraceReport(BaseModel):
    input_quality_summary: str
    pipeline_decisions_taken: str
    assumptions_applied: List[str]
    risks_and_limitations: List[str]
    recommendation: str

class TraceReportResponse(BaseModel):
    trace_report: TraceReport
