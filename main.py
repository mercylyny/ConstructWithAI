from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from services.auth_service import get_current_user
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import math
import uvicorn
import shutil
import os
import time
import json 
import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from database.db import Base, engine, get_db
from models import project, wall, estimation, user
from models.project import Project
from models.wall import Wall
from models.estimation import Estimation
from models.user import User, PasswordResetToken
from models.building_summary import BuildingSummaryRecord
from models.estimation_phase import EstimationPhase

Base.metadata.create_all(bind=engine)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Third-party library Imports ---
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    pass # Handle if reportlab is missing

try:
    import pytesseract
    from PIL import Image
    # Example for Windows: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except ImportError:
    pass

# Import routers
from routers import ai, pdf, ocr, pipeline, database, auth, upload

# Include Routers
app.include_router(ai.router)
app.include_router(pdf.router)
app.include_router(ocr.router)
app.include_router(pipeline.router)
app.include_router(database.router)
app.include_router(auth.router)
app.include_router(upload.router)

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Ensure generated pdfs directory exists
PDF_DIR = "generated_pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

# --- Pydantic Models ---

class WallSegmentInput(BaseModel):
    wall_id: str
    length_m: float
    height_m: float
    thickness_mm: float
    openings_area_m2: float



class Opening(BaseModel):
    type: str = "generic" 
    width: float    
    height: float   

class BaseWallRequest(BaseModel):
    wall_length: float
    wall_height: float
    openings: List[Opening] = []

class BlockEstimateRequest(BaseWallRequest):
    block_type: str
    block_style: str
    unit_price: float

class BlockEstimateResponse(BaseModel):
    wall_area: float
    openings_area: float
    net_wall_area: float
    block_type: str
    block_style: str
    total_blocks: int
    unit_price: float
    total_cost: float

class BrickEstimateRequest(BaseWallRequest):
    brick_type: str     
    unit_price: float

class BrickEstimateResponse(BaseModel):
    wall_area: float
    openings_area: float
    net_wall_area: float
    brick_type: str
    total_bricks: int
    unit_price: float
    total_cost: float

class HybridEstimateRequest(BaseWallRequest):
    brick_unit_price: float
    block_unit_price: float
    block_type: str
    block_style: str

class HybridEstimateResponse(BaseModel):
    foundation_height: float
    upper_wall_height: float
    foundation_bricks: int
    upper_wall_blocks: int
    total_bricks: int
    total_blocks: int
    brick_cost: float
    block_cost: float
    total_cost: float

# --- Steel Models ---

class SteelColumn(BaseModel):
    length: float
    diameter: str
    quantity_per_column: int

class SteelBeam(BaseModel):
    length: float
    diameter: str
    quantity_per_beam: int

class SteelRing(BaseModel):
    diameter: str
    quantity: int

class SteelEstimateRequest(BaseModel):
    columns: List[SteelColumn] = []
    beams: List[SteelBeam] = []
    rings: List[SteelRing] = []
    unit_price_bars: Dict[str, float] = {}
    unit_price_rings: Dict[str, float] = {}

class SteelEstimateResponse(BaseModel):
    bars_summary: Dict[str, float]
    rings_summary: Dict[str, int]
    bars_cost: Dict[str, float]
    rings_cost: Dict[str, float]
    total_cost: float

# --- Cost Breakdown Models ---

class WallMaterialCost(BaseModel):
    quantity: int
    unit_price: float
    total_cost: float

class MaterialCostBreakdown(BaseModel):
    bricks: WallMaterialCost
    blocks: WallMaterialCost
    steel_bars: Dict[str, float] 
    steel_rings: Dict[str, float]

# --- Full Building Models ---

class WallDefinition(BaseModel):
    type: str 
    wall_length: float
    wall_height: float
    openings: List[Opening] = []
    
    # Optional fields depending on type
    block_type: Optional[str] = None
    block_style: Optional[str] = None
    brick_type: Optional[str] = None
    
    # Prices
    block_unit_price: Optional[float] = 0.0
    brick_unit_price: Optional[float] = 0.0

class FullBuildingRequest(BaseModel):
    walls: List[WallDefinition]
    steel: SteelEstimateRequest

class FullBuildingResponse(BaseModel):
    total_bricks: int
    total_blocks: int
    total_bars: Dict[str, float]
    total_rings: Dict[str, int]
    
    cost_bricks: float
    cost_blocks: float
    cost_bars: Dict[str, float]
    cost_rings: Dict[str, float]
    
    material_cost_breakdown: MaterialCostBreakdown
    
    grand_total: float

# --- BOQ Models ---

class BOQItem(BaseModel):
    description: str
    quantity: float
    unit: str
    unit_price: float
    total_cost: float

class MasonryWorks(BaseModel):
    bricks: BOQItem
    blocks: BOQItem

class SteelWorks(BaseModel):
    bars: List[BOQItem]
    rings: List[BOQItem]

class CostSummary(BaseModel):
    total_masonry_cost: float
    total_steel_cost: float
    grand_total_cost: float

class BOQResponse(BaseModel):
    masonry_works: MasonryWorks
    steel_works: SteelWorks
    cost_summary: CostSummary

# --- Manual Analysis Models ---

class ManualAnalysisRequest(BaseModel):
    filename: str                  
    scale: str                     
    reference_pixel_length: float  
    reference_real_length: float   
    wall_pixel_lengths: List[float] 

class ManualAnalysisResponse(BaseModel):
    wall_lengths_meters: List[float]
    pixel_to_meter_ratio: float
    message: str

# --- Estimate From Plan Models ---

class EstimateFromPlanRequest(BaseModel):
    wall_lengths_meters: List[float]
    wall_height: float
    material_type: str 
    
    unit_price: Optional[float] = 0.0       
    brick_unit_price: Optional[float] = 0.0 
    block_unit_price: Optional[float] = 0.0 
    
    block_type: Optional[str] = "standard"
    block_style: Optional[str] = "standard"
    brick_type: Optional[str] = "standard"
    
    openings: List[Opening] = []

class EstimateFromPlanResponse(BaseModel):
    total_bricks: int
    total_blocks: int
    cost_bricks: float
    cost_blocks: float
    grand_total: float
    message: str

# --- OCR Models ---

class OCRRequest(BaseModel):
    filename: str 

class OCRResponse(BaseModel):
    filename: str
    extracted_text: str
    message: str

class OCRMeasurementsRequest(BaseModel):
    filename: str
    extracted_text: str

class WallMeasurement(BaseModel):
    wall_name: str
    length_meters: float

class OCRMeasurementsResponse(BaseModel):
    filename: str
    walls: List[WallMeasurement]
    total_walls_detected: int
    message: str

# --- Estimate From OCR Models ---

class EstimateFromOCRRequest(BaseModel):
    filename: str
    wall_height: float
    material_type: str 
    unit_price: float
    brick_unit_price: Optional[float] = 0.0
    block_unit_price: Optional[float] = 0.0

class EstimateFromOCRResponse(BaseModel):
    filename: str
    total_wall_length: float
    material_type: str
    estimated_material_quantity: int 
    estimated_cost: float
    message: str

# --- 3D Modeling Models (Level 6) ---

class WallPosition(BaseModel):
    x: float
    y: float
    z: float

class Wall3DInput(BaseModel):
    wall_id: str
    length: float
    height: float
    thickness: float
    material: str
    position: WallPosition

class Wall3DOutput(Wall3DInput):
    volume: float

class Walls3DRequest(BaseModel):
    walls: List[Wall3DInput]

class Walls3DResponse(BaseModel):
    message: str
    wall_count: int
    walls: List[Wall3DOutput]

# --- BIM Data Models (Level 6.3) ---

class BIMMetadata(BaseModel):
    created_at: str
    source: str = "AI Construction Estimator"

class BIMGeometry(BaseModel):
    length: float
    height: float
    thickness: float
    volume: float

class BIMWall(BaseModel):
    global_id: str
    entity_type: str = "IfcWall"
    geometry: BIMGeometry
    material: str
    position: WallPosition
    metadata: BIMMetadata

class BIMResponse(BaseModel):
    message: str
    wall_count: int
    bim_walls: List[BIMWall]

# --- Logic Helper Functions ---

def calculate_openings_area(openings: List[Opening]) -> float:
    return sum(o.width * o.height for o in openings)

def logic_blocks(wall_length, wall_height, openings, unit_price):
    """Core logic for block calculations."""
    wall_area = wall_length * wall_height
    openings_area = calculate_openings_area(openings)
    
    if openings_area > wall_area:
        raise HTTPException(status_code=400, detail="Openings area exceeds wall area.")
        
    net_wall_area = wall_area - openings_area
    total_blocks = math.ceil(max(0, net_wall_area * 12.5))
    total_cost = total_blocks * unit_price
    
    return {
        "wall_area": wall_area,
        "openings_area": openings_area,
        "net_wall_area": net_wall_area,
        "total_blocks": total_blocks,
        "total_cost": total_cost
    }

def logic_bricks(wall_length, wall_height, openings, unit_price):
    """Core logic for brick calculations."""
    wall_area = wall_length * wall_height
    openings_area = calculate_openings_area(openings)
    
    if openings_area > wall_area:
        raise HTTPException(status_code=400, detail="Openings area exceeds wall area (brick).")
        
    net_wall_area = wall_area - openings_area
    total_bricks = math.ceil(max(0, net_wall_area * 60))
    total_cost = total_bricks * unit_price
    
    return {
        "wall_area": wall_area,
        "openings_area": openings_area,
        "net_wall_area": net_wall_area,
        "total_bricks": total_bricks,
        "total_cost": total_cost
    }

def logic_hybrid(wall_length, wall_height, openings, brick_price, block_price):
    """Core logic for hybrid calculations."""
    FOUNDATION_HEIGHT = 0.6
    
    if wall_height <= FOUNDATION_HEIGHT:
        raise HTTPException(status_code=400, detail="Wall height must be greater than foundation height (0.6m) for hybrid.")

    # 1. Foundation (Bricks)
    foundation_area = wall_length * FOUNDATION_HEIGHT
    foundation_bricks = math.ceil(foundation_area * 60)
    brick_cost = foundation_bricks * brick_price

    # 2. Upper Wall (Blocks)
    upper_wall_height = wall_height - FOUNDATION_HEIGHT
    upper_wall_gross_area = wall_length * upper_wall_height
    
    openings_area = calculate_openings_area(openings)
    
    if openings_area > upper_wall_gross_area:
        raise HTTPException(status_code=400, detail="Openings area exceeds upper wall area (hybrid).")

    upper_wall_net_area = upper_wall_gross_area - openings_area
    upper_wall_blocks = math.ceil(max(0, upper_wall_net_area * 12.5))
    block_cost = upper_wall_blocks * block_price
    
    return {
        "foundation_height": FOUNDATION_HEIGHT,
        "upper_wall_height": upper_wall_height,
        "foundation_bricks": foundation_bricks,
        "upper_wall_blocks": upper_wall_blocks,
        "brick_cost": brick_cost,
        "block_cost": block_cost,
        "total_cost": brick_cost + block_cost
    }

def generate_pdf_boq(boq_data: BOQResponse, filename: str):
    """
    Generate a PDF BOQ using reportlab.
    """
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("BILL OF QUANTITIES (BOQ)", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Date
    date_str = time.strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Generated on: {date_str}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # -- 1. Masonry Works --
    elements.append(Paragraph("1. Masonry Works", styles['Heading2']))
    
    data = [["Description", "Quantity", "Unit", "Unit Price", "Total Cost"]]
    
    # Bricks
    b = boq_data.masonry_works.bricks
    data.append([b.description, b.quantity, b.unit, f"{b.unit_price:,.2f}", f"{b.total_cost:,.2f}"])
    
    # Blocks
    blk = boq_data.masonry_works.blocks
    data.append([blk.description, blk.quantity, blk.unit, f"{blk.unit_price:,.2f}", f"{blk.total_cost:,.2f}"])
    
    t = Table(data, colWidths=[200, 60, 40, 80, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))
    
    # -- 2. Steel Works --
    elements.append(Paragraph("2. Steel Works", styles['Heading2']))
    
    data = [["Description", "Quantity", "Unit", "Unit Price", "Total Cost"]]
    
    for bar in boq_data.steel_works.bars:
        data.append([bar.description, bar.quantity, bar.unit, f"{bar.unit_price:,.2f}", f"{bar.total_cost:,.2f}"])
        
    for ring in boq_data.steel_works.rings:
        data.append([ring.description, ring.quantity, ring.unit, f"{ring.unit_price:,.2f}", f"{ring.total_cost:,.2f}"])
        
    t = Table(data, colWidths=[200, 60, 40, 80, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))
    
    # -- 3. Cost Summary --
    elements.append(Paragraph("3. Cost Summary", styles['Heading2']))
    
    summary_data = [
        ["Total Masonry Cost", f"{boq_data.cost_summary.total_masonry_cost:,.2f}"],
        ["Total Steel Cost", f"{boq_data.cost_summary.total_steel_cost:,.2f}"],
        ["Grand Total Cost", f"{boq_data.cost_summary.grand_total_cost:,.2f}"]
    ]
    
    t = Table(summary_data, colWidths=[300, 160])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'), # Bold Grand Total row
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)

    # Build PDF
    doc.build(elements)

def calculate_boq_data(request: FullBuildingRequest) -> BOQResponse:
    """Helper function to calculate BOQ data without sending a response object."""
    # Reuse Full Building Logic
    total_bricks = 0
    total_blocks = 0
    cost_bricks = 0.0
    cost_blocks = 0.0
    
    # --- Masonry Logic ---
    for wall in request.walls:
        if wall.type == "block":
            res = logic_blocks(wall.wall_length, wall.wall_height, wall.openings, wall.block_unit_price or 0.0)
            total_blocks += res["total_blocks"]
            cost_blocks += res["total_cost"]
            
        elif wall.type == "brick":
            res = logic_bricks(wall.wall_length, wall.wall_height, wall.openings, wall.brick_unit_price or 0.0)
            total_bricks += res["total_bricks"]
            cost_bricks += res["total_cost"]
            
        elif wall.type == "hybrid":
            res = logic_hybrid(wall.wall_length, wall.wall_height, wall.openings, 
                               wall.brick_unit_price or 0.0, 
                               wall.block_unit_price or 0.0)
            total_bricks += res["foundation_bricks"]
            total_blocks += res["upper_wall_blocks"]
            cost_bricks += res["brick_cost"]
            cost_blocks += res["block_cost"]
            
    avg_brick_price = cost_bricks / total_bricks if total_bricks > 0 else 0.0
    avg_block_price = cost_blocks / total_blocks if total_blocks > 0 else 0.0

    masonry = MasonryWorks(
        bricks=BOQItem(
            description="Clay/Cement Bricks for foundation/walls",
            quantity=float(total_bricks),
            unit="pcs",
            unit_price=round(avg_brick_price, 2),
            total_cost=cost_bricks
        ),
        blocks=BOQItem(
            description="Concrete Blocks for walls",
            quantity=float(total_blocks),
            unit="pcs",
            unit_price=round(avg_block_price, 2),
            total_cost=cost_blocks
        )
    )

    # --- Steel Logic ---
    s = request.steel
    steel_res = logic_steel(s.columns, s.beams, s.rings, s.unit_price_bars, s.unit_price_rings)
    
    bars_items = []
    for dia, quantity in steel_res["bars_summary"].items():
        cost = steel_res["bars_cost"].get(dia, 0.0)
        u_price = cost / quantity if quantity > 0 else 0.0
        
        bars_items.append(BOQItem(
            description=f"High Yield Steel Bars {dia}",
            quantity=round(quantity, 2),
            unit="m",
            unit_price=round(u_price, 2),
            total_cost=cost
        ))
        
    rings_items = []
    for dia, quantity in steel_res["rings_summary"].items():
        cost = steel_res["rings_cost"].get(dia, 0.0)
        u_price = cost / quantity if quantity > 0 else 0.0
        
        rings_items.append(BOQItem(
            description=f"Steel Rings {dia}",
            quantity=float(quantity),
            unit="pcs",
            unit_price=round(u_price, 2),
            total_cost=cost
        ))
        
    steel = SteelWorks(
        bars=bars_items,
        rings=rings_items
    )
    
    total_masonry = cost_bricks + cost_blocks
    total_steel = steel_res["total_cost"]
    grand_total = total_masonry + total_steel
    
    return BOQResponse(
        masonry_works=masonry,
        steel_works=steel,
        cost_summary=CostSummary(
            total_masonry_cost=total_masonry,
            total_steel_cost=total_steel,
            grand_total_cost=grand_total
        )
    )

def perform_ocr_extraction(filepath: str) -> str:
    """
    Helper function to perform OCR on an image file using Pytesseract.
    Returns the extracted text.
    """
    try:
        # 1. Open image using Pillow
        img = Image.open(filepath)
        
        # 2. Extract text using Pytesseract
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        print(f"OCR Error: {e}")
        # Check for Common Tesseract Not Found error
        if "tesseract is not installed" in str(e) or "tesseract.exe" in str(e):
             return "Error: Tesseract-OCR is not found on the server. Please ensure it is installed and in your PATH."
        return f"Error occurred during OCR: {str(e)}"

def parse_measurements_simple(text: str) -> List[WallMeasurement]:
    """
    Extract wall measurements from text using simple string rules (NO REGEX).
    """
    walls = []
    
    # Process text line by line
    lines = text.split('\n')
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        line_lower = line_stripped.lower()
        
        # Rule 1: Line must contain "wall"
        if "wall" in line_lower:
            cleaned_line = line_lower.replace("=", " ").replace(":", " ")
            tokens = cleaned_line.split()
            
            length_val = None
            
            for i, token in enumerate(tokens):
                # case 1: "4.5m" 
                if token.endswith("m") and len(token) > 1:
                    val_str = token[:-1] 
                    try:
                        length_val = float(val_str)
                        break
                    except ValueError:
                        pass
                
                # case 2: "3 m"
                if token == "m" and i > 0:
                    prev_token = tokens[i-1]
                    try:
                        length_val = float(prev_token)
                        break
                    except ValueError:
                        pass
            
            if length_val is not None:
                try:
                    wall_idx = tokens.index("wall")
                    if wall_idx + 1 < len(tokens):
                        name_suffix = tokens[wall_idx + 1]
                        wall_name = f"Wall {name_suffix.upper()}"
                    else:
                        wall_name = "Unknown Wall"
                except ValueError:
                    wall_name = "Detected Wall"

                walls.append(WallMeasurement(wall_name=wall_name, length_meters=length_val))
                
    return walls

# --- Routes ---

@app.get("/")
async def root():
    return {"message": "Construction AI backend is running"}

@app.post("/estimate/blocks", response_model=BlockEstimateResponse)
async def estimate_blocks(request: BlockEstimateRequest):
    data = logic_blocks(request.wall_length, request.wall_height, request.openings, request.unit_price)
    return BlockEstimateResponse(
        block_type=request.block_type,
        block_style=request.block_style,
        unit_price=request.unit_price,
        **data
    )

@app.post("/estimate/bricks", response_model=BrickEstimateResponse)
async def estimate_bricks(request: BrickEstimateRequest):
    data = logic_bricks(request.wall_length, request.wall_height, request.openings, request.unit_price)
    return BrickEstimateResponse(
        brick_type=request.brick_type,
        unit_price=request.unit_price,
        **data
    )

@app.post("/estimate/hybrid", response_model=HybridEstimateResponse)
async def estimate_hybrid(request: HybridEstimateRequest):
    data = logic_hybrid(request.wall_length, request.wall_height, request.openings, request.brick_unit_price, request.block_unit_price)
    return HybridEstimateResponse(
        foundation_height=data["foundation_height"],
        upper_wall_height=data["upper_wall_height"],
        foundation_bricks=data["foundation_bricks"],
        upper_wall_blocks=data["upper_wall_blocks"],
        total_bricks=data["foundation_bricks"],
        total_blocks=data["upper_wall_blocks"],
        brick_cost=data["brick_cost"],
        block_cost=data["block_cost"],
        total_cost=data["total_cost"]
    )

@app.post("/estimate/steel", response_model=SteelEstimateResponse)
async def estimate_steel(request: SteelEstimateRequest):
    data = logic_steel(request.columns, request.beams, request.rings, request.unit_price_bars, request.unit_price_rings)
    return SteelEstimateResponse(**data)

@app.post("/estimate/full-building", response_model=FullBuildingResponse)
async def estimate_full_building(request: FullBuildingRequest):
    """
    Aggregate simple walls, hybrid walls, and steel requirements.
    Enhanced with detailed material cost breakdown for better BOQ generation.
    """
    return calculate_boq_data(request)

@app.post("/estimate/boq", response_model=BOQResponse)
async def estimate_boq(request: FullBuildingRequest):
    """
    Generate a Bill of Quantities (BOQ) style estimate.
    """
    return calculate_boq_data(request)

@app.post("/estimate/boq/pdf")
async def estimate_boq_pdf(request: FullBuildingRequest):
    """
    Generate a downloadable PDF BOQ from the exact same logic as /estimate/boq.
    """
    # 1. reuse logic to get data
    boq_data = calculate_boq_data(request)
    
    # 2. define file name
    timestamp = str(int(time.time()))
    filename = f"boq_{timestamp}.pdf"
    filepath = os.path.join(PDF_DIR, filename)
    
    # 3. generate pdf
    try:
        generate_pdf_boq(boq_data, filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
        
    # 4. return as file
    return FileResponse(filepath, media_type='application/pdf', filename=filename)

@app.post("/upload/plan")
async def upload_plan(
    file: UploadFile = File(...),
    scale: str = Form(...),
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user)
):
    """
    Upload a construction plan (PDF or Image) for future analysis.
    """
    print(f"received file.filename: {file.filename}")
    print(f"received scale: {scale}")
    print(f"uploaded by: {current_user_email}")

    # Resolve the user_id from the email in the JWT
    user_id = None
    if current_user_email:
        from models.user import User as UserModel
        db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
        if db_user:
            user_id = db_user.id

    # Check for duplicate filename owned by this user
    existing_project = db.query(Project).filter(
        Project.filename == file.filename,
        Project.user_id == user_id
    ).first()

    # 1. Define the destination path
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # 2. Save the file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
        
    # 3. Database: Create or Update Project record
    try:
        if existing_project:
            existing_project.scale = scale
            new_project = existing_project
            message = "Project updated successfully"
        else:
            new_project = Project(
                filename=file.filename,
                scale=scale,
                user_id=user_id
            )
            db.add(new_project)
            message = "Project saved successfully"
            
        db.commit()
        db.refresh(new_project)
        print(f"Project ID: {new_project.id} saved for user_id={user_id} - {message}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    # Return response
    return {
        "project_id": new_project.id,
        "filename": new_project.filename,
        "scale": new_project.scale,
        "message": message
    }

@app.post("/analyze/plan/manual", response_model=ManualAnalysisResponse)
async def analyze_plan_manual(request: ManualAnalysisRequest):
    """
    Perform manual analysis of a plan by converting pixel measurements to real-world meters.
    """
    if request.reference_pixel_length <= 0:
        raise HTTPException(status_code=400, detail="Reference pixel length must be greater than 0.")
        
    # 1. Calculate the ratio (Meters per Pixel)
    pixel_to_meter_ratio = request.reference_real_length / request.reference_pixel_length
    
    # 2. Convert all wall lengths
    wall_lengths_meters = []
    for px_len in request.wall_pixel_lengths:
        meter_len = px_len * pixel_to_meter_ratio
        wall_lengths_meters.append(round(meter_len, 2))
        
    return ManualAnalysisResponse(
        wall_lengths_meters=wall_lengths_meters,
        pixel_to_meter_ratio=pixel_to_meter_ratio,
        message="Manual measurement completed successfully."
    )

@app.post("/analyze/plan/ocr", response_model=OCRResponse)
async def analyze_plan_ocr(request: OCRRequest):
    """
    Perform basic Optical Character Recognition (OCR) on an uploaded Image.
    PDFs are NOT allowed here (use /analyze/plan/pdf-to-image first).
    Extracts raw text and saves it for AI interpretation.
    """
    # 1. Check for PDF file extension
    if request.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, 
            detail="PDF files are not supported directly. Please use /analyze/plan/pdf-to-image first to convert to images."
        )

    # 2. Locate the file
    file_path = os.path.join(UPLOAD_DIR, request.filename)
    
    # Check if file exists in uploads OR in outputs/pdf_images (if user passes a converted page)
    # The previous simple check only looked in uploads. We should be robust.
    # However, for simplicity and Phase 7.2 requirements, let's assume images are in uploads OR user moves them. 
    # Actually, the user requirement for PDF-2-Image saves to outputs/pdf_images. 
    # So we should check both or rely on absolute path if provided? 
    # The helper `perform_ocr_extraction` takes a filepath.
    # Let's check `uploads` first, and if not found, check `outputs/pdf_images`.
    
    if not os.path.exists(file_path):
        # Check secondary location
        secondary_path = os.path.join("outputs", "pdf_images", request.filename)
        if os.path.exists(secondary_path):
            file_path = secondary_path
        else:
            raise HTTPException(status_code=404, detail=f"File not found: {request.filename}")
    
    # 3. Perform OCR
    extracted_text = perform_ocr_extraction(file_path)
    
    # 4. Persistence: Save text to file for AI Interpretation
    # Save as filename.txt in UPLOAD_DIR (central place for metadata)
    try:
        txt_filename = f"{request.filename}.txt"
        txt_path = os.path.join(UPLOAD_DIR, txt_filename)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
    except Exception as e:
        print(f"Warning: Could not save OCR text file: {e}")
    
    # 5. Return result
    return OCRResponse(
        filename=request.filename,
        extracted_text=extracted_text,
        message="OCR extraction completed and text saved."
    )

@app.post("/analyze/plan/ocr/measurements", response_model=OCRMeasurementsResponse)
async def analyze_plan_ocr_measurements(request: OCRMeasurementsRequest):
    """
    Parse wall measurements from previously extracted OCR text.
    Also saves the measurements to a file for future automatic estimation.
    """
    
    # 1. Parse using helper
    detected_walls = parse_measurements_simple(request.extracted_text)
    
    # 2. Save measurements to file (Persistence for next step)
    # File format: uploads/{filename}_measurements.json
    try:
        data_to_save = {
            "filename": request.filename,
            "walls": [w.dict() for w in detected_walls]
        }
        json_path = os.path.join(UPLOAD_DIR, f"{request.filename}_measurements.json")
        with open(json_path, "w") as f:
            json.dump(data_to_save, f)
    except Exception as e:
        print(f"Warning: Could not save measurements file: {e}")

    # 3. Return result
    return OCRMeasurementsResponse(
        filename=request.filename,
        walls=detected_walls,
        total_walls_detected=len(detected_walls),
        message="Measurements extracted successfully from OCR text."
    )

@app.post("/estimate/from-ocr", response_model=EstimateFromOCRResponse)
async def estimate_from_ocr(request: EstimateFromOCRRequest):
    """
    Automatically generate construction estimates directly from OCR-derived wall measurements.
    
    It looks for the saved measurements file from the previous step.
    """
    
    # 1. Load measurement data corresponding to the filename
    json_path = os.path.join(UPLOAD_DIR, f"{request.filename}_measurements.json")
    
    if not os.path.exists(json_path):
        raise HTTPException(
            status_code=404, 
            detail=f"No measurement data found for {request.filename}. Please run /analyze/plan/ocr/measurements first."
        )
    
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            walls_data = data.get("walls", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading measurement data: {e}")
        
    if not walls_data:
        raise HTTPException(status_code=400, detail="No walls found in measurement data.")
    
    # 2. Extract wall lengths
    total_len = sum(w["length_meters"] for w in walls_data)
    
    # 3. Reuse existing estimation logic
    estimated_quantity = 0
    estimated_cost = 0.0
    
    if request.material_type == "block":
        # logic_blocks returns dictionary with keys: total_blocks, total_cost
        res = logic_blocks(total_len, request.wall_height, [], request.unit_price)
        estimated_quantity = res["total_blocks"]
        estimated_cost = res["total_cost"]
        
    elif request.material_type == "brick":
        # logic_bricks returns: total_bricks, total_cost
        res = logic_bricks(total_len, request.wall_height, [], request.unit_price)
        estimated_quantity = res["total_bricks"]
        estimated_cost = res["total_cost"]
    
    elif request.material_type == "hybrid":
        p_brick = request.brick_unit_price if request.brick_unit_price else request.unit_price
        p_block = request.block_unit_price if request.block_unit_price else request.unit_price
        
        res = logic_hybrid(total_len, request.wall_height, [], p_brick, p_block)
        estimated_quantity = res["total_bricks"] + res["total_blocks"]
        estimated_cost = res["total_cost"]
        
    else:
        raise HTTPException(status_code=400, detail=f"Unknown material type: {request.material_type}")

    # 4. Return response
    return EstimateFromOCRResponse(
        filename=request.filename,
        total_wall_length=total_len,
        material_type=request.material_type,
        estimated_material_quantity=estimated_quantity,
        estimated_cost=estimated_cost,
        message="Estimate generated automatically from OCR measurements."
    )

@app.post("/model/walls/3d", response_model=Walls3DResponse)
async def model_walls_3d(request: Walls3DRequest):
    """
    Generate basic 3D data for walls, preparing for future BIM and visualization.
    
    This endpoint does NOT render graphics. It calculates geometry and 
    structures the data so it can be exported to CAD/BIM software later.
    """
    
    walls_output = []
    
    for wall in request.walls:
        # Calculate Volume: V = L * H * T
        # Volume analysis is crucial for:
        # 1. Concrete volume estimation (filling hollow blocks)
        # 2. Plastering area calculation (Surface Area)
        # 3. Thermal mass calculations in advanced energy models
        
        volume = wall.length * wall.height * wall.thickness
        
        # In a real app, we might also transform local coordinates to world coordinates here.
        # For now, we pass the position through.
        
        walls_output.append(Wall3DOutput(
            wall_id=wall.wall_id,
            length=wall.length,
            height=wall.height,
            thickness=wall.thickness,
            material=wall.material,
            position=wall.position,
            volume=round(volume, 3)
        ))
        
    return Walls3DResponse(
        message="3D wall data stored successfully",
        wall_count=len(walls_output),
        walls=walls_output
    )

@app.post("/model/walls/bim", response_model=BIMResponse)
async def model_walls_bim(request: Walls3DRequest):
    """
    Generate IFC/BIM-ready data from 3D wall geometry.
    Prepares data for future export to IFC/Revit/Blender.
    """
    bim_walls = []
    
    for wall in request.walls:
        # Reuse logic: Calculate Volume
        volume = wall.length * wall.height * wall.thickness
        
        # Generate BIM specific data
        gid = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        bim_wall = BIMWall(
            global_id=gid,
            entity_type="IfcWall",
            geometry=BIMGeometry(
                length=wall.length,
                height=wall.height,
                thickness=wall.thickness,
                volume=round(volume, 3)
            ),
            material=wall.material,
            position=wall.position,
            metadata=BIMMetadata(
                created_at=timestamp,
                source="AI Construction Estimator"
            )
        )
        bim_walls.append(bim_wall)
        
    return BIMResponse(
        message="BIM wall data generated successfully",
        wall_count=len(bim_walls),
        bim_walls=bim_walls
    )

@app.post("/estimate/from-plan", response_model=EstimateFromPlanResponse)
async def estimate_from_plan(request: EstimateFromPlanRequest):
    """
    Generate an estimate directly from manual plan analysis data (list of wall lengths).
    """
    
    # 1. Calculate Total Wall Length from the list
    total_wall_length = sum(request.wall_lengths_meters)
    
    total_bricks = 0
    total_blocks = 0
    cost_bricks = 0.0
    cost_blocks = 0.0
    
    # 2. Branch Logic based on Material Type
    
    if request.material_type == "block":
        res = logic_blocks(
            total_wall_length, 
            request.wall_height, 
            request.openings, 
            request.unit_price or 0.0
        )
        total_blocks = res["total_blocks"]
        cost_blocks = res["total_cost"]
        
    elif request.material_type == "brick":
        res = logic_bricks(
            total_wall_length, 
            request.wall_height, 
            request.openings, 
            request.unit_price or 0.0
        )
        total_bricks = res["total_bricks"]
        cost_bricks = res["total_cost"]
        
    elif request.material_type == "hybrid":
        res = logic_hybrid(
            total_wall_length, 
            request.wall_height, 
            request.openings, 
            request.brick_unit_price or 0.0, 
            request.block_unit_price or 0.0
        )
        total_bricks = res["foundation_bricks"]
        total_blocks = res["upper_wall_blocks"]
        cost_bricks = res["brick_cost"]
        cost_blocks = res["block_cost"]
    
    else:
        raise HTTPException(status_code=400, detail="Invalid material_type. Choose 'block', 'brick', or 'hybrid'.")
        
    # 3. Construct Response
    return EstimateFromPlanResponse(
        total_bricks=total_bricks,
        total_blocks=total_blocks,
        cost_bricks=cost_bricks,
        cost_blocks=cost_blocks,
        grand_total=cost_bricks + cost_blocks,
        message=f"Estimate generated for {len(request.wall_lengths_meters)} walls using {request.material_type} construction."
    )

@app.post("/project/{project_id}/walls")
async def save_project_walls(
    project_id: int,
    walls: List[WallSegmentInput],
    db: Session = Depends(get_db)
):
    """
    Save multiple wall segments linked to a specific project.
    """
    # 1. Check if project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Insert multiple Wall records
    saved_count = 0
    try:
        for w_input in walls:
            # Check for existing wall to avoid duplicates
            existing_wall = db.query(Wall).filter(
                Wall.project_id == project_id,
                Wall.wall_id == w_input.wall_id
            ).first()
            
            if existing_wall:
                # Update existing (Real-world optional behavior)
                existing_wall.length_m = w_input.length_m
                existing_wall.height_m = w_input.height_m
                existing_wall.thickness_mm = w_input.thickness_mm
                existing_wall.openings_area_m2 = w_input.openings_area_m2
            else:
                # Create new
                new_wall = Wall(
                    project_id=project_id,
                    wall_id=w_input.wall_id,
                    length_m=w_input.length_m,
                    height_m=w_input.height_m,
                    thickness_mm=w_input.thickness_mm,
                    openings_area_m2=w_input.openings_area_m2
                )
                db.add(new_wall)
            saved_count += 1
            
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {
        "message": "Walls saved successfully",
        "count": saved_count
    }



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
