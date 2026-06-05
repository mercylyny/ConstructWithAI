import os
import logging
from typing import Dict, Any, List, Optional
import uuid

from sqlalchemy.orm import Session
from models.project import Project
from models.wall import Wall
from models.estimation import Estimation
from schemas.db_schemas import WallCreate, EstimationCreate
from database.crud import create_project_wall, create_project_estimation

# Import Service Logic
from services.pdf_service import convert_pdf_to_images_service
from services.ocr_service import perform_ocr_on_image
from services.ocr_postprocess import postprocess_ocr
from services.semantic_interpreter import interpret_walls
from schemas.ai import InterpretedWall, InterpretedData
from services.wall_quantity_calculator import calculate_wall_quantities
from services.wall_material_service import estimate_wall_materials
from services.cost_service import calculate_project_cost
from services.confidence_service import analyze_estimation_confidence
from services.readiness_service import analyze_project_readiness
from services.narrative_service import generate_narrative_report
from services.classification_service import classify_drawing_suitability
from services.phase_estimation_service import estimate_project_phases
from schemas.phases import PhaseGroup
from services.export_service import export_boq_to_excel, export_boq_to_csv
from schemas.estimation import BuildingSummary, PlanAnalysisResult, EstimationRequest, EstimationResult, EstimationStageTotal, WallQuantity, PipelineExecutionResult
from schemas.costing import CostEstimationRequest, MaterialQuantities
from schemas.materials import WallSegment
from services.plan_analysis_service import analyze_building_components
from services.fusion_service import fuse_estimation_data
from services.report_service import generate_cost_boq_pdf
from services.yolo_service import detect_architectural_components

logger = logging.getLogger("pipeline")
logger.setLevel(logging.INFO)

UPLOAD_DIR = "uploads"
OCR_OUTPUT_DIR = os.path.join("outputs", "ocr_text")
os.makedirs(OCR_OUTPUT_DIR, exist_ok=True)

def _classify_wall_by_thickness(thickness: float):
    if thickness >= 230:
        return "EXTERNAL", 0.63, f"Greater thickness ({thickness}mm) suggests external/envelope wall"
    elif thickness <= 150:
        return "NON_LOAD_BEARING", 0.77, f"Thin partition ({thickness}mm) typically non-structural"
    elif 150 < thickness < 230:
        if thickness > 200:
            return "LOAD_BEARING", 0.77, "Thicker internal wall suggests structural load-bearing role"
        else:
            return "INTERNAL", 0.77, "Standard internal separation wall"
    return "UNKNOWN", 0.0, ""

class PlanAnalyzer:
    @staticmethod
    def analyze(filename: str, db: Session = None, use_qs_fallbacks: bool = True) -> PlanAnalysisResult:
        result = PlanAnalysisResult(filename=filename, status="RUNNING", summary=BuildingSummary())
        
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            result.status = "FAILED"
            return result

        try:
            # Preprocessing (PDF -> Image)
            image_paths = []
            full_text = ""
            if filename.lower().endswith(".pdf"):
                image_paths = convert_pdf_to_images_service(file_path, filename)
            elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths = [file_path]
            elif filename.lower().endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    full_text = f.read()
            else:
                result.status = "FAILED"
                return result
                
            # OCR Extraction
            if not filename.lower().endswith(".txt"):
                for img_path in image_paths:
                    text = perform_ocr_on_image(img_path)
                    full_text += text + "\n"
                
                text_path = os.path.join(OCR_OUTPUT_DIR, f"{filename}.txt")
                with open(text_path, "w") as f:
                    f.write(full_text)
                
            result.extracted_text = full_text[:200] + "..."
            
            # Semantic Interpretation
            processed_data = postprocess_ocr(full_text)
            semantic_result = interpret_walls(
                processed_data['clean_text'],
                processed_data['measurements'],
                processed_data['labels']
            )
            
            walls = [InterpretedWall(label=w['label'], length_m=w['length_m']) for w in semantic_result['walls']]
            
            # YOLO Object Detection
            yolo_counts = {}
            if image_paths and not filename.lower().endswith(".txt"):
                yolo_counts = detect_architectural_components(image_paths)

            # Use analyze_building_components() with schedule-stripped plan_text
            # for accurate room counting, plus YOLO detections for physical elements
            component_counts = analyze_building_components(
                processed_data['clean_text'],
                processed_data['labels'],
                semantic_result['walls'],
                yolo_counts,
                plan_text=processed_data.get('plan_text')
            )

            bedrooms  = component_counts.get('bedrooms', 0)
            kitchens  = component_counts.get('kitchens', 0)
            bathrooms = component_counts.get('bathrooms', 0)
            doors     = component_counts.get('doors', 0)
            windows   = component_counts.get('windows', 0)
            beams     = component_counts.get('beams', 0)
            columns   = component_counts.get('columns', 0)
            stairs    = component_counts.get('stairs', 0)

            # Total rooms = sum of all habitable spaces detected
            rooms = (
                component_counts.get('rooms', 0) +
                bedrooms + kitchens + bathrooms +
                component_counts.get('living_rooms', 0) +
                component_counts.get('dining_rooms', 0) +
                component_counts.get('stores', 0)
            )

            # Wall count: prefer actual wall segments; if still 0 use measurement-implied
            wall_count = len(walls)
            
            # --- Beginner vs Professional Mode ---
            if use_qs_fallbacks:
                # Use standard Quantity Surveying Rules of Thumb to infer missing elements
                meas_count = len(processed_data.get('measurements', []))
                if rooms == 0:
                    rooms = max(1, meas_count // 4)
                    
                if doors == 0:
                    doors = rooms + 1
                if windows == 0:
                    windows = rooms * 2
                    
                # Ensure openings are physically realistic
                if wall_count > 0:
                    max_openings = int(wall_count * 1.5)
                    if (doors + windows) > max_openings:
                        total = doors + windows
                        doors = max(1, int((doors / total) * max_openings))
                        windows = max(1, int((windows / total) * max_openings))
                
                if bedrooms == 0 and rooms >= 3:
                    bedrooms = max(1, rooms - 2)
                if bathrooms == 0 and rooms >= 2:
                    bathrooms = 1
                
                import math
                if columns == 0 and wall_count > 0:
                    total_wall_length = sum(w.length_m for w in walls)
                    columns = max(4, math.ceil(total_wall_length / 4.0))
                if beams == 0 and wall_count > 0:
                    beams = 1
            
            summary = BuildingSummary(
                rooms=rooms,
                bedrooms=bedrooms,
                kitchens=kitchens,
                bathrooms=bathrooms,
                walls=wall_count,
                doors=doors,
                windows=windows,
                beams=beams,
                columns=columns,
                stairs=stairs,
                confidence=85.0 if wall_count > 0 else 50.0
            )
            
            result.summary = summary
            result.status = "SUCCESS"
            return result
        except Exception as e:
            logger.error(f"PlanAnalysis error: {e}")
            result.status = "FAILED"
            return result


class EstimationEngine:
    @staticmethod
    def estimate(request: EstimationRequest, db: Session = None) -> EstimationResult:
        result = EstimationResult(status="RUNNING")
        
        try:
            summary = request.summary
            
            avg_wall_length = 3.5 
            assumed_wall_height = 3.0
            
            total_wall_length = summary.walls * avg_wall_length
            if summary.walls == 0 and summary.rooms > 0:
                total_wall_length = summary.rooms * 4 * 3.5 
                
            segment_walls = []
            if summary.walls > 0:
                for i in range(summary.walls):
                    segment_walls.append(WallSegment(
                        wall_id=f"W{i+1}",
                        length_m=avg_wall_length,
                        height_m=assumed_wall_height,
                        thickness_mm=200.0,
                        openings_area_m2=0.0
                    ))
            else:
                 segment_walls.append(WallSegment(
                    wall_id="TotalWallPerimeter",
                    length_m=total_wall_length,
                    height_m=assumed_wall_height,
                    thickness_mm=200.0,
                    openings_area_m2=0.0
                ))
            
            mat_result = estimate_wall_materials(segment_walls)
            
            req = CostEstimationRequest(
                quantities=MaterialQuantities(
                    total_bricks_count=mat_result.project_totals.total_bricks_count,
                    total_mortar_volume_m3=mat_result.project_totals.total_mortar_volume_m3
                ),
                custom_rates=None
            )
            cost_result = calculate_project_cost(req)
            
            phase_response = estimate_project_phases(
                filename=request.filename or "Manual_Input", 
                ocr_text="", 
                material_response=mat_result
            )
            
            stage_totals = []
            for phase in phase_response.phases:
                # Preserve detailed material breakdown from phase estimation
                stage_totals.append(EstimationStageTotal(
                    phase_name=phase.phase_name,
                    cost=phase.phase_cost,
                    materials=getattr(phase, 'materials', [])
                ))
            
            result.stages = stage_totals
            result.grand_total = phase_response.total_project_cost
            
            cost_dict = cost_result.dict()
            excel_path = export_boq_to_excel(cost_dict)
            result.boq_excel_path = excel_path
            
            try:
                pdf_dir = os.path.join("outputs", "reports")
                os.makedirs(pdf_dir, exist_ok=True)
                pdf_filename = f"boq_materials_{uuid.uuid4().hex[:8]}.pdf"
                pdf_path = os.path.join(pdf_dir, pdf_filename)
                
                from services.report_service import generate_cost_boq_pdf
                generate_cost_boq_pdf(cost_result, pdf_path)
                result.boq_pdf_path = pdf_path.replace("\\", "/")
            except Exception as pdf_ex:
                logger.warning(f"Failed to generate pipeline PDF report: {pdf_ex}")
            
            result.qs_report_path = result.boq_pdf_path
            
            result.status = "SUCCESS"
            result.message = "Estimation completed successfully."
            
            # --- Auto-save estimation to database ---
            if request.project_id and db:
                try:
                    from models.estimation import Estimation as EstimationModel
                    from models.estimation_phase import EstimationPhase
                    db_estimation = EstimationModel(
                        project_id=request.project_id,
                        total_bricks=mat_result.project_totals.total_bricks_count if mat_result else 0,
                        total_mortar_volume=mat_result.project_totals.total_mortar_volume_m3 if mat_result else 0.0,
                        total_cost=cost_result.total_project_cost if cost_result else 0.0,
                        grand_total=result.grand_total or 0.0,
                        boq_excel_path=result.boq_excel_path,
                        boq_pdf_path=result.boq_pdf_path,
                    )
                    db.add(db_estimation)
                    db.commit()
                    db.refresh(db_estimation)
                    logger.info(f"Estimation ID: {db_estimation.id} saved to project {request.project_id}")
                    
                    # Save phase breakdown
                    if result.stages:
                        for stage in result.stages:
                            db_phase = EstimationPhase(
                                estimation_id=db_estimation.id,
                                phase_name=stage.phase_name,
                                cost=stage.cost,
                            )
                            db.add(db_phase)
                        db.commit()
                        logger.info(f"Saved {len(result.stages)} phases for estimation {db_estimation.id}")
                        
                    # Save walls to DB so dashboard shows wall count
                    from models.wall import Wall as WallModel
                    db.query(WallModel).filter(WallModel.project_id == request.project_id).delete()
                    for seg in segment_walls:
                        w_type, w_conf, w_reason = _classify_wall_by_thickness(seg.thickness_mm)
                        db_wall = WallModel(
                            project_id=request.project_id,
                            wall_id=seg.wall_id,
                            length_m=seg.length_m,
                            height_m=seg.height_m,
                            thickness_mm=seg.thickness_mm,
                            openings_area_m2=seg.openings_area_m2,
                            wall_type=w_type,
                            classification_confidence=w_conf,
                            reasoning=w_reason,
                        )
                        db.add(db_wall)
                    db.commit()
                    logger.info(f"Saved {len(segment_walls)} walls to project {request.project_id}")
                except Exception as db_ex:
                    logger.warning(f"Failed to save estimation to DB: {db_ex}")
                    db.rollback()
            
            return result
        except Exception as e:
            logger.error(f"Estimation error: {e}")
            result.status = "FAILED"
            result.message = str(e)
            return result

class PipelineOrchestrator:
    @staticmethod
    def run_pipeline(filename: str, manual_walls: Optional[List[WallQuantity]] = None, db: Session = None) -> PipelineExecutionResult:
        logger.info(f"Starting pipeline orchestrator for filename: {filename}")
        
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            return PipelineExecutionResult(
                status="FAILED",
                failed_step="Input Validation",
                failure_reason=f"File not found: {filename}"
            )

        # PDF Conversion
        image_paths = []
        if filename.lower().endswith(".pdf"):
            try:
                image_paths = convert_pdf_to_images_service(file_path, filename)
            except Exception as e:
                return PipelineExecutionResult(
                    status="FAILED",
                    failed_step="PDF Conversion",
                    failure_reason=f"Failed to convert PDF: {str(e)}"
                )
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_paths = [file_path]
        elif filename.lower().endswith(".txt"):
            pass
        else:
            return PipelineExecutionResult(
                status="FAILED",
                failed_step="Input Validation",
                failure_reason=f"Unsupported file format: {filename}"
            )

        # OCR Extraction
        full_text = ""
        if filename.lower().endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    full_text = f.read()
            except Exception as e:
                return PipelineExecutionResult(
                    status="FAILED",
                    failed_step="OCR",
                    failure_reason=f"Failed to read text file: {str(e)}"
                )
        else:
            try:
                for img_path in image_paths:
                    text = perform_ocr_on_image(img_path)
                    full_text += text + "\n"
                
                # Save cached OCR text
                text_cache_path = os.path.join(OCR_OUTPUT_DIR, f"{filename}.txt")
                with open(text_cache_path, "w", encoding="utf-8") as f:
                    f.write(full_text)
            except Exception as e:
                return PipelineExecutionResult(
                    status="FAILED",
                    failed_step="OCR",
                    failure_reason=f"OCR processing failed: {str(e)}"
                )

        # OCR Post-processing
        try:
            processed_data = postprocess_ocr(full_text)
        except Exception as e:
            return PipelineExecutionResult(
                status="FAILED",
                failed_step="OCR Post-processing",
                failure_reason=f"Post-processing failed: {str(e)}"
            )

        # Semantic Interpretation
        try:
            semantic_result = interpret_walls(
                processed_data['clean_text'],
                processed_data['measurements'],
                processed_data['labels']
            )
        except Exception as e:
            return PipelineExecutionResult(
                status="FAILED",
                failed_step="Semantic Interpretation",
                failure_reason=f"Semantic interpretation failed: {str(e)}"
            )

        # Quantity Calculation for OCR walls
        try:
            ocr_calculated = calculate_wall_quantities(
                semantic_result['walls'],
                semantic_result['assumed_wall_height_m']
            )
            
            ocr_wall_quantities = []
            for w in ocr_calculated['walls']:
                ocr_wall_quantities.append(WallQuantity(
                    label=w['label'],
                    length_m=w['length_m'],
                    height_m=w['height_m'],
                    thickness_m=w['thickness_m'],
                    area_sqm=w['area_sqm'],
                    volume_cum=w['volume_cum'],
                    data_source="OCR",
                    confidence_weight=0.7
                ))
        except Exception as e:
            return PipelineExecutionResult(
                status="FAILED",
                failed_step="Quantity Calculation",
                failure_reason=f"Failed to calculate OCR wall quantities: {str(e)}"
            )

        # Data Fusion
        try:
            fused_walls = fuse_estimation_data(ocr_wall_quantities, manual_walls)
        except Exception as e:
            return PipelineExecutionResult(
                status="FAILED",
                failed_step="Data Fusion",
                failure_reason=f"Data fusion failed: {str(e)}"
            )

        # Detailed Material Estimation
        try:
            wall_segments = []
            for w in fused_walls:
                wall_segments.append(WallSegment(
                    wall_id=w.label,
                    length_m=w.length_m,
                    height_m=w.height_m,
                    thickness_mm=w.thickness_m * 1000.0,
                    openings_area_m2=0.0
                ))
            mat_result = estimate_wall_materials(wall_segments)
        except Exception as e:
            return PipelineExecutionResult(
                status="FAILED",
                failed_step="Material Estimation",
                failure_reason=f"Material estimation failed: {str(e)}"
            )

        # Cost Calculation
        try:
            cost_req = CostEstimationRequest(
                quantities=MaterialQuantities(
                    total_bricks_count=mat_result.project_totals.total_bricks_count,
                    total_mortar_volume_m3=mat_result.project_totals.total_mortar_volume_m3
                ),
                custom_rates=None
            )
            cost_result = calculate_project_cost(cost_req)
        except Exception as e:
            return PipelineExecutionResult(
                status="FAILED",
                failed_step="Cost Calculation",
                failure_reason=f"Cost calculation failed: {str(e)}"
            )

        # Phases & Stages
        try:
            phase_response = estimate_project_phases(
                filename=filename,
                ocr_text=full_text,
                material_response=mat_result
            )
        except Exception as e:
            return PipelineExecutionResult(
                status="FAILED",
                failed_step="Phase Estimation",
                failure_reason=f"Phase estimation failed: {str(e)}"
            )

        # Confidence Score
        try:
            conf_input = {
                "ocr_text": full_text,
                "walls": [w.model_dump() for w in fused_walls],
                "custom_rates": None,
                "scale_provided": True
            }
            conf_report = analyze_estimation_confidence(conf_input)
        except Exception as e:
            return PipelineExecutionResult(
                status="FAILED",
                failed_step="Confidence Analysis",
                failure_reason=f"Confidence analysis failed: {str(e)}"
            )

        # Readiness Assessment
        try:
            readiness_input = {
                "confidence_score": conf_report.confidence_score,
                "confidence_level": conf_report.confidence_level,
                "warnings": conf_report.warnings,
                "assumptions": conf_report.assumptions,
                "total_project_cost": cost_result.total_project_cost,
                "line_items": [item.model_dump() for item in cost_result.line_items],
                "ocr_text": full_text,
                "walls": [w.model_dump() for w in fused_walls]
            }
            readiness_report = analyze_project_readiness(readiness_input)
        except Exception as e:
            return PipelineExecutionResult(
                status="FAILED",
                failed_step="Readiness Assessment",
                failure_reason=f"Readiness assessment failed: {str(e)}"
            )

        # Narrative & Report Generation
        boq_excel_path = None
        boq_pdf_path = None
        qs_report_path = None
        narrative_report = ""
        
        try:
            report_data = {
                "project_filename": filename,
                "wall_count": len(fused_walls),
                "total_cost": cost_result.total_project_cost,
                "currency": "UGX",
                "line_items": [item.model_dump() for item in cost_result.line_items],
                "readiness_status": readiness_report.readiness_status,
                "readiness_score": readiness_report.readiness_score,
                "confidence_score": conf_report.confidence_score,
                "risks": readiness_report.risks,
                "recommendations": readiness_report.recommendations,
                "assumptions": conf_report.assumptions
            }
            narrative_report = generate_narrative_report(report_data)
            
            excel_data = cost_result.model_dump()
            boq_excel_path = export_boq_to_excel(excel_data)
            
            pdf_dir = os.path.join("outputs", "reports")
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_filename = f"boq_materials_{uuid.uuid4().hex[:8]}.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_filename)
            generate_cost_boq_pdf(cost_result, pdf_path)
            boq_pdf_path = pdf_path.replace("\\", "/")
            qs_report_path = boq_pdf_path
        except Exception as e:
            logger.warning(f"Non-fatal reporting error: {e}")

        # Database Persistence
        if db is not None:
            try:
                db_proj = db.query(Project).filter(Project.filename == filename).first()
                if not db_proj:
                    db_proj = Project(filename=filename, scale="1:100")
                    db.add(db_proj)
                    db.commit()
                    db.refresh(db_proj)
                    
                db.query(Wall).filter(Wall.project_id == db_proj.id).delete()
                db.query(Estimation).filter(Estimation.project_id == db_proj.id).delete()
                db.commit()
                
                for w in fused_walls:
                    thickness_mm = w.thickness_m * 1000.0
                    w_type, w_conf, w_reason = _classify_wall_by_thickness(thickness_mm)
                    db_wall = Wall(
                        project_id=db_proj.id,
                        wall_id=w.label,
                        length_m=w.length_m,
                        height_m=w.height_m,
                        thickness_mm=thickness_mm,
                        openings_area_m2=0.0,
                        wall_type=w_type,
                        classification_confidence=w_conf,
                        reasoning=w_reason,
                    )
                    db.add(db_wall)
                    
                db_est = Estimation(
                    project_id=db_proj.id,
                    total_bricks=mat_result.project_totals.total_bricks_count,
                    total_mortar_volume=mat_result.project_totals.total_mortar_volume_m3,
                    total_cost=cost_result.total_project_cost
                )
                db.add(db_est)
                db.commit()
            except Exception as db_ex:
                db.rollback()
                logger.error(f"Database persistence failed: {db_ex}")

        return PipelineExecutionResult(
            status="SUCCESS",
            wall_count=len(fused_walls),
            total_cost=cost_result.total_project_cost,
            extracted_text=full_text,
            intervention_needed=readiness_report.intervention_needed,
            missing_critical_data=readiness_report.missing_critical_data,
            confidence_breakdown={"overall": conf_report.confidence_score},
            readiness_status=readiness_report.readiness_status,
            readiness_score=readiness_report.readiness_score,
            boq_excel_path=boq_excel_path,
            boq_pdf_path=boq_pdf_path,
            qs_report_path=qs_report_path,
            narrative_report=narrative_report
        )
