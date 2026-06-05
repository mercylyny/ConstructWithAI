import os
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from schemas.ai import AIInterpretOCRRequest, AIInterpretOCRResponse, InterpretedData, InterpretedWall
from services.ai_interpreter import get_stored_ocr_text, interpret_text_rule_based
from services.ocr_postprocess import postprocess_ocr
from services.semantic_interpreter import interpret_walls
from services.plan_analysis_service import analyze_building_components
from services.ocr_service import perform_batch_ocr, perform_ocr_on_image
from typing import List, Dict, Any
from schemas.classification import PlanClassificationReport
from services.classification_service import classify_drawing_suitability
from schemas.geometry import GeometryExtractionResponse, GeometricWall
from services.geometry_service import extract_geometry_from_image
from schemas.semantic_classification import SemanticClassificationResponse, ClassifiedWall
from services.semantic_classification_service import classify_walls_semantically
from schemas.openings import OpeningDetectionResponse
from services.opening_service import detect_openings_on_walls
from schemas.normalization import NormalizationResponse, WallSegment
from services.normalization_service import normalize_and_segment_walls
from schemas.masonry import MasonryClassificationResponse
from services.masonry_service import classify_masonry_details
from schemas.pipeline_decision import PipelineDecisionResponse
from services.pipeline_decision_service import analyze_pipeline_path
from schemas.trace_report import TraceReportResponse
from services.trace_report_service import generate_pipeline_trace
from schemas.intervention import InterventionAnalysisResponse
from services.intervention_service import analyze_intervention_needs
from schemas.learning import LearningResponse
from services.learning_service import extract_learning_patterns
from schemas.attribution import AttributionResponse
from services.attribution_service import attribute_engineering_evidence
from schemas.phases import PhaseEstimationResponse
from services.phase_estimation_service import estimate_project_phases


router = APIRouter(
    prefix="/ai",
    tags=["AI Interpretation"]
)


def _resolve_ocr_text(filename: str) -> Optional[str]:
    """
    Resolve existing stored OCR text, or regenerate it as a fallback.
    """
    text = get_stored_ocr_text(filename)
    if text:
        return text

    try:
        if filename.lower().endswith(".pdf"):
            text, count = perform_batch_ocr(filename)
            if count > 0 and text:
                return text

        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
            image_path = os.path.join(upload_dir, filename)
            if os.path.exists(image_path):
                return perform_ocr_on_image(image_path)
    except Exception:
        pass

    return None

@router.post("/interpret/ocr", response_model=AIInterpretOCRResponse)
async def interpret_ocr(request: AIInterpretOCRRequest):
    """
    Phase 7.3.3: Semantic interpretation of structured OCR data.
    Uses rule-based AI logic to interpret OCR text and extract wall data.
    
    Process:
    1. Fetch stored OCR text
    2. Apply post-processing (cleaning, structuring)
    3. Apply semantic interpretation (wall detection)
    4. Return structured wall data
    """
    
    text = _resolve_ocr_text(request.filename)
    
    if text is None:
        raise HTTPException(
            status_code=404,
            detail=f"OCR text not found for {request.filename}. Please run OCR analysis first."
        )
    
    processed_data = postprocess_ocr(text)
    
    semantic_result = interpret_walls(
        processed_data['clean_text'],
        processed_data['measurements'],
        processed_data['labels']
    )
    
    walls = [InterpretedWall(label=w['label'], length_m=w['length_m']) 
             for w in semantic_result['walls']]
    
    data = InterpretedData(
        walls=walls,
        assumed_wall_height_m=semantic_result['assumed_wall_height_m']
    )

    detected_elements = analyze_building_components(
        processed_data['clean_text'],
        processed_data['labels'],
        semantic_result['walls']
    )
    
    return AIInterpretOCRResponse(
        filename=request.filename,
        interpreted_data=data,
        detected_elements=detected_elements,
        confidence=semantic_result['confidence'],
        message="AI interpretation complete with semantic analysis."
    )

from schemas.estimation import WallEstimationResponse
from services.estimation_service import calculate_wall_quantities

class EstimationRequest(BaseModel):
    filename: str

@router.post("/estimate/walls", response_model=WallEstimationResponse)
async def estimate_wall_quantities(request: EstimationRequest):
    """
    Automated Quantity Estimation:
    Calculates Area (sqm) and Volume (cum) for interpreted walls.
    
    Process:
    1. Fetch OCR text
    2. Post-processing
    3. Semantic Interpretation
    4. Quantity Calculation
    """
    from services.wall_quantity_calculator import calculate_wall_quantities
    
    # 1. Fetch text
    text = _resolve_ocr_text(request.filename)
    if not text:
        raise HTTPException(
            status_code=404, 
            detail=f"OCR text not found for {request.filename}. Please run OCR analysis first."
        )
        
    # 2. Post-processing
    processed = postprocess_ocr(text)
    
    # 3. Semantic Interpretation
    interpreted = interpret_walls(
        processed['clean_text'],
        processed['measurements'],
        processed['labels']
    )
    
    # 4. Quantity Calculation
    quantities = calculate_wall_quantities(
        interpreted['walls'],
        interpreted['assumed_wall_height_m']
    )
    
    return WallEstimationResponse(
        filename=request.filename,
        walls=quantities['walls'],
        totals=quantities['totals'],
        message="Wall quantity estimation completed successfully using semantic interpretation."
    )

# Phase 7.6: Material Estimation Endpoints
from schemas.materials import MaterialEstimationResponse
from services.material_estimation_service import calculate_material_estimation

@router.post("/estimate/blocks", response_model=MaterialEstimationResponse)
async def estimate_blocks(request: EstimationRequest):
    """
    Phase 7.6: Block Material Estimation
    Calculates block quantities from wall volumes.
    
    Uses:
    - 12.5 blocks per cubic meter
    - 10% wastage allowance
    """
    result = calculate_material_estimation(request.filename, "blocks")
    
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Wall estimation data not available for {request.filename}. Please ensure OCR and interpretation have been completed."
        )
    
    return result

@router.post("/estimate/bricks", response_model=MaterialEstimationResponse)
async def estimate_bricks(request: EstimationRequest):
    """
    Phase 7.6: Brick Material Estimation
    Calculates brick quantities from wall volumes.
    
    Uses:
    - 500 bricks per cubic meter
    - 15% wastage allowance
    """
    result = calculate_material_estimation(request.filename, "bricks")
    
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Wall estimation data not available for {request.filename}. Please ensure OCR and interpretation have been completed."
        )
    
    return result

from schemas.materials import DetailedMaterialResponse, WallSegment
from services.wall_material_service import estimate_wall_materials

@router.post("/estimate/materials/detail", response_model=DetailedMaterialResponse)
async def estimate_materials_detailed(walls: List[WallSegment]):
    """
    Detailed Material Estimation Layer:
    Calculates precise brick and mortar requirements based on structured wall segments.
    
    Inputs:
    - List of wall segments (length, height, thickness, openings)
    
    Assumptions:
    - Brick: 230x75x115mm
    - Mortar: 10mm
    - Coverage: 60 bricks/m2 (scaled by thickness)
    - Mortar: 0.23 m3 per 1000 bricks
    """
    return estimate_wall_materials(walls)

from schemas.costing import CostEstimationRequest, CostEstimationResponse
from services.cost_service import calculate_project_cost

@router.post("/estimate/costs", response_model=CostEstimationResponse)
async def estimate_project_costs(request: CostEstimationRequest):
    """
    Phase 7.6: Cost Estimation Layer
    Converts engineering quantities into a financial Bill of Materials.
    
    Features:
    - Decomposes Mortar (m3) into Cement (bags) and Sand (tons).
    - Applies default Uganda Market Rates (UGX) or accepts custom overrides.
    """
    return calculate_project_cost(request)


@router.post("/estimate/phases", response_model=PhaseEstimationResponse)
async def estimate_project_phases_route(request: EstimationRequest):
    """
    Phase-based Material Extraction and Cost Breakdown.
    """
    text = _resolve_ocr_text(request.filename)
    if not text:
        raise HTTPException(
            status_code=404,
            detail=f"OCR text not found for {request.filename}. Please run OCR analysis first."
        )

    # Use existing OCR postprocessing to keep phase extraction consistent with the pipeline
    processed = postprocess_ocr(text)
    semantic_result = interpret_walls(
        processed['clean_text'],
        processed['measurements'],
        processed['labels']
    )

    from services.wall_quantity_calculator import calculate_wall_quantities
    walls_quantities = calculate_wall_quantities(
        semantic_result['walls'],
        semantic_result.get('assumed_wall_height_m', 3.0)
    )

    from schemas.materials import WallSegment
    segment_walls = [
        WallSegment(
            wall_id=w['label'],
            length_m=w['length_m'],
            height_m=semantic_result.get('assumed_wall_height_m', 3.0),
            thickness_mm=200.0,
            openings_area_m2=0.0
        )
        for w in semantic_result['walls']
    ]

    mat_result = estimate_wall_materials(segment_walls)
    return estimate_project_phases(request.filename, text, mat_result)

from fastapi.responses import FileResponse
from services.report_service import generate_cost_boq_pdf
import os
import uuid

@router.post("/report/boq/pdf")
async def generate_boq_report(request: CostEstimationRequest):
    """
    Phase 7.7: PDF Reporting Layer
    Generates a downloadable BOQ PDF from cost estimation.
    
    Process:
    1. Calculate Costs (Phase 7.6 logic)
    2. Generate PDF (Phase 7.7 logic)
    3. Return File
    """
    # 1. Calculate Costs
    cost_data = calculate_project_cost(request)
    
    # 2. Define Output Path
    # Ensure dir exists (redundant safety)
    output_dir = "outputs/reports"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"boq_materials_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # 3. Generate PDF
    generate_cost_boq_pdf(cost_data, filepath)
    
    # 4. Return File
    return FileResponse(
        path=filepath, 
        filename=filename, 
        media_type='application/pdf'
    )

from services.export_service import export_boq_to_excel, export_boq_to_csv

@router.post("/export/boq/excel")
async def export_boq_excel(request: CostEstimationResponse):
    """
    Phase 7.8: Export BOQ to Excel
    """
    # Convert Pydantic model to dict for service compatibility
    data = request.dict()
    filepath = export_boq_to_excel(data)
    filename = os.path.basename(filepath)
    
    return FileResponse(
        path=filepath, 
        filename=filename, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@router.post("/export/boq/pdf")
async def export_boq_pdf(request: CostEstimationResponse):
    """
    Phase 7.8: Export BOQ to PDF from existing cost estimates.
    """
    output_dir = "outputs/reports"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"boq_export_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(output_dir, filename)
    generate_cost_boq_pdf(request, filepath)

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='application/pdf'
    )

@router.post("/export/boq/csv")
async def export_boq_csv(request: CostEstimationResponse):
    """
    Phase 7.8: Export BOQ to CSV
    """
    data = request.dict()
    filepath = export_boq_to_csv(data)
    filename = os.path.basename(filepath)
    
    return FileResponse(
        path=filepath, 
        filename=filename, 
        media_type='text/csv'
    )

from services.confidence_service import analyze_estimation_confidence, ConfidenceReport
from typing import Dict, Any

@router.post("/estimate/confidence", response_model=ConfidenceReport)
async def estimate_confidence(data: Dict[str, Any]):
    """
    Phase 7.9: Confidence & Validation Layer
    Analyzes the estimation inputs/outputs (walls, ocr, rates) to provide a confidence score.
    """
    return analyze_estimation_confidence(data)

from services.readiness_service import analyze_project_readiness, ReadinessAssessment

@router.post("/project/readiness", response_model=ReadinessAssessment)
async def check_project_readiness(data: Dict[str, Any]):
    """
    Phase 8.0: Project Readiness & Risk Intelligence Layer
    Evaluates the complete estimation state to determine if the project is ready for execution.
    Returns risks, recommendations, and a readiness score.
    """
    return analyze_project_readiness(data)

from services.narrative_service import generate_narrative_report
from fastapi.responses import PlainTextResponse

@router.post("/report/narrative", response_class=PlainTextResponse)
async def generate_narrative(data: Dict[str, Any]):
    """
    Phase 8.1: Narrative Intelligence
    Generates a professional text-based BOQ Engineer's Report.
    """
    report_text = generate_narrative_report(data)
    return report_text

from services.orchestrator_service import generate_pipeline_status_report

@router.post("/report/pipeline/status", response_class=PlainTextResponse)
async def generate_pipeline_status(data: Dict[str, Any]):
    """
    Phase 8.2: Pipeline Orchestration
    Generates an End-to-End Pipeline Status Report explaining the estimation journey.
    """
    return generate_pipeline_status_report(data)

@router.post("/classify/plan", response_model=PlanClassificationReport)
async def classify_plan(request: AIInterpretOCRRequest):
    """
    Phase 11.0: Plan Analysis Intelligence
    Classifies the drawing suitability and type based on OCR data.
    """
    text = _resolve_ocr_text(request.filename)
    if not text:
        raise HTTPException(
            status_code=404,
            detail=f"OCR text not found for {request.filename}. Please run OCR analysis first."
        )
    return classify_drawing_suitability(request.filename, text)

@router.post("/extract/geometry", response_model=GeometryExtractionResponse)
async def extract_geometry(request: AIInterpretOCRRequest):
    """
    Phase 12.0: Geometric Wall Extraction
    Directly extracts wall geometry from the image using OpenCV.
    """
    # Find image path (assuming page 1 for now or based on filename)
    # Orchestrator saves images to outputs/pdf_images/
    img_dir = os.path.join("outputs", "pdf_images")
    # If the requested file is already an image in uploads, use that
    img_path = os.path.join("uploads", request.filename)
    
    if not os.path.exists(img_path):
        # Fallback to OCR images dir
        base_name = os.path.splitext(request.filename)[0]
        img_path = os.path.join(img_dir, f"{base_name}_page_1.png")

    if not os.path.exists(img_path):
        raise HTTPException(
            status_code=404,
            detail=f"Image for {request.filename} not found. Please run PDF-to-image conversion first."
        )

    return extract_geometry_from_image(img_path)

@router.post("/classify/walls", response_model=SemanticClassificationResponse)
async def classify_walls(walls: List[GeometricWall]):
    """
    Phase 12.1: Semantic Wall Classification
    Classifies a list of GeometricWall objects into functional types.
    """
    # Convert Pydantic models to dicts for the service
    walls_data = [w.dict() for w in walls]
    return classify_walls_semantically(walls_data)

@router.post("/detect/openings", response_model=OpeningDetectionResponse)
async def detect_openings(request: AIInterpretOCRRequest, walls: List[ClassifiedWall]):
    """
    Phase 12.2: Wall Opening Detection
    Detects doors and windows on the provided walls using visual heuristics.
    """
    img_dir = os.path.join("outputs", "pdf_images")
    img_path = os.path.join("uploads", request.filename)
    
    if not os.path.exists(img_path):
        base_name = os.path.splitext(request.filename)[0]
        img_path = os.path.join(img_dir, f"{base_name}_page_1.png")

    if not os.path.exists(img_path):
        raise HTTPException(
            status_code=404,
            detail=f"Image for {request.filename} not found."
        )

    # Convert Pydantic walls to dicts
    walls_dict = [w.dict() for w in walls]
    return detect_openings_on_walls(img_path, walls_dict)

@router.post("/normalize/walls", response_model=NormalizationResponse)
async def normalize_walls(walls: List[Dict[str, Any]]):
    """
    Phase 13.1: Wall Normalization & Segmentation
    Normalizes wall thickness to standard sizes and segments long walls (>6m).
    """
    return normalize_and_segment_walls(walls)

@router.post("/classify/masonry", response_model=MasonryClassificationResponse)
async def classify_masonry(segments: List[Dict[str, Any]]):
    """
    Phase 13.2: Masonry System Classification
    Classifies segments into BRICK/BLOCK and assigns structural roles.
    """
    return classify_masonry_details(segments)

@router.post("/pipeline/decision", response_model=PipelineDecisionResponse)
async def pipeline_decision(
    ocr_raw: str,
    ocr_cleaned: str,
    confidence: float,
    measurements: List[Dict[str, Any]] = [],
    labels: List[Dict[str, Any]] = []
):
    """
    Phase 14.0: Pipeline Decision Intelligence
    Determines the optimal estimation path based on data quality.
    """
    return analyze_pipeline_path(ocr_raw, ocr_cleaned, measurements, labels, confidence)

@router.post("/report/trace", response_model=TraceReportResponse)
async def pipeline_trace(
    ocr_raw: str,
    ocr_cleaned: str,
    confidence: float,
    readiness: str,
    path_decision: str,
    measurements: List[Any] = [],
    labels: List[Any] = []
):
    """
    Phase 15.0: Pipeline Trace Reporting
    Generates a professional audit report for verification.
    """
    return generate_pipeline_trace(
        ocr_raw, ocr_cleaned, measurements, labels, confidence, readiness, path_decision
    )

@router.post("/intervention/required", response_model=InterventionAnalysisResponse)
async def intervention_required(
    confidence: float,
    ocr_quality: Dict[str, Any],
    readiness: str,
    path_decision: str,
    measurements: List[Any] = []
):
    """
    Phase 16.0: Automated Intervention Intelligence
    Determines if human input is needed for professional safety.
    """
    return analyze_intervention_needs(
        confidence, ocr_quality, measurements, readiness, path_decision
    )

@router.post("/learn", response_model=LearningResponse)
async def ai_learn(
    original_ocr: str,
    corrections: Dict[str, Any],
    finalized_boq: Dict[str, Any],
    building_context: Dict[str, Any]
):
    """
    Phase 17.0: AI Construction Learning Engine
    Extracts patterns from verified human inputs.
    """
    return extract_learning_patterns(original_ocr, corrections, finalized_boq, building_context)

@router.post("/attribute", response_model=AttributionResponse)
async def ai_attribute(
    quantities: List[Dict[str, Any]],
    raw_ocr: str,
    assumptions: List[str],
    overrides: Optional[Dict[str, Any]] = None
):
    """
    Phase 18.0: Engineering Evidence Attribution Engine
    Attaches traceable evidence to construction values.
    """
    return attribute_engineering_evidence(quantities, raw_ocr, assumptions, overrides)

from schemas.failure_analysis import FailureAnalysisRequest, FailureAnalysisResponse
from services.failure_analysis_service import analyze_pipeline_failures

@router.post("/analyze/failures", response_model=FailureAnalysisResponse)
async def analyze_failures(request: FailureAnalysisRequest):
    """
    Phase 19.0: Construction Failure Analysis Engine
    Assesses pipeline failures or low-confidence outputs, classifying them
    into actionable categories to protect downstream engineering processes.
    """
    return analyze_pipeline_failures(request)

from schemas.assumptions import AssumptionsRequest, AssumptionsResponse
from services.assumptions_service import extract_engineering_assumptions

@router.post("/analyze/assumptions", response_model=AssumptionsResponse)
async def analyze_assumptions(request: AssumptionsRequest):
    """
    Phase 20.0: Engineering Assumptions Registry Engine
    Identifies, structures, and documents all assumptions used in quantity
    estimation and cost calculation to ensure absolute transparency.
    """
    return extract_engineering_assumptions(request)

from schemas.workflow import WorkflowOrchestratorRequest, WorkflowOrchestratorResponse
from services.workflow_service import orchestrate_workflow

@router.post("/orchestrate/workflow", response_model=WorkflowOrchestratorResponse)
async def analyze_workflow(request: WorkflowOrchestratorRequest):
    """
    Phase 21.0: Construction Workflow Orchestrator
    Guides users through the estimation process based on data quality,
    enforcing safe engineering practices before allowing BOQ finalization.
    """
    return orchestrate_workflow(request)

