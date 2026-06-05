import re
import math
from typing import List, Dict, Optional

from schemas.materials import DetailedMaterialResponse
from schemas.phases import PhaseEstimationResponse, PhaseGroup, PhaseMaterialItem
from services.ai_interpreter import normalize_measurement
from services.cost_service import (
    DEFAULT_PRICES_UGX,
    MORTAR_TO_CEMENT_BAGS,
    MORTAR_TO_SAND_TONS,
)


# Default assumptions for structural and roofing estimation
DEFAULT_STEEL_BEAM_RATE_UGX_PER_M = 30000.0
DEFAULT_STEEL_COLUMN_RATE_UGX_PER_PIECE = 180000.0
DEFAULT_STEEL_BEAM_WEIGHT_KG_PER_M = 6.0
DEFAULT_STEEL_COLUMN_WEIGHT_KG = 120.0
DEFAULT_ROOFING_RATE_UGX_PER_M2 = 90000.0
DEFAULT_FOUNDATION_CONCRETE_RATE_UGX_PER_M3 = 520000.0
DEFAULT_FOOTING_DEPTH_M = 0.4
DEFAULT_FOOTING_WIDTH_M = 0.3


def _find_linear_measurement(line: str) -> Optional[float]:
    """Find the first linear measurement on a line and return meters."""
    # Look for explicit area or linear measures and normalize if possible.
    match = re.search(r'(\d+(?:\.\d+)?)\s*(mm|cm|m)\b', line, re.IGNORECASE)
    if match:
        return normalize_measurement(match.group(0))[0]

    # Match values like 3600 without units when near engineering keywords.
    match = re.search(r'\b(\d{3,5})\b', line)
    if match:
        return normalize_measurement(match.group(1) + 'mm')[0]

    return None


def _find_area_measurement(line: str) -> Optional[float]:
    """Find the first area measurement on a line and return square meters."""
    match = re.search(r'(\d+(?:\.\d+)?)\s*(m2|sqm|sq\.m|square meters|square metres?)\b', line, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None

    # Detect dimensions like 8x10m or 10000x8000mm for roof/slab areas.
    dim_match = re.search(r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)(?:\s*(mm|cm|m))?', line)
    if dim_match:
        v1 = float(dim_match.group(1))
        v2 = float(dim_match.group(2))
        unit = dim_match.group(3)
        if unit:
            if unit.lower() == 'mm':
                v1 /= 1000.0
                v2 /= 1000.0
            elif unit.lower() == 'cm':
                v1 /= 100.0
                v2 /= 100.0
        # If values are large and no unit, assume mm dimensions
        if not unit and (v1 > 30 or v2 > 30):
            v1 /= 1000.0
            v2 /= 1000.0
        return round(v1 * v2, 2)

    return None


def _extract_tagged_items(text: str, keywords: List[str], area: bool = False) -> List[Dict[str, float]]:
    items = []
    for line in text.splitlines():
        lower = line.lower()
        if any(keyword in lower for keyword in keywords):
            value = _find_area_measurement(line) if area else _find_linear_measurement(line)
            if value is not None and value > 0:
                items.append({
                    'description': line.strip(),
                    'value': round(value, 2)
                })
    return items


# Expanded pricing constants for comprehensive sub-items (UGX)
PRICE_EXCAVATION_PER_M3 = 25000.0       # Labor for excavation
PRICE_STEEL_REBAR_PER_KG = 7000.0       # Rebar steel (Y12/R8)
PRICE_GRAVEL_AGGREGATES_PER_TON = 100000.0 # 20mm concrete aggregate
PRICE_ROOF_SHEET_PER_M2 = 55000.0       # Pre-painted G30 corrugated sheet
PRICE_TIMBER_PER_M = 12000.0             # Treated eucalyptus/pine timber
PRICE_ROOF_NAILS_PER_KG = 12000.0       # Nails & washers
PRICE_ROOF_LABOR_PER_M2 = 25000.0       # Installer labor


def _build_foundation_phase(
    total_wall_length: float,
    foundation_items: List[Dict[str, float]]
) -> PhaseGroup:
    """
    Builds the Foundation & Substructure phase.
    Uses detected footing lengths if available, falling back to total wall length footprint.
    """
    materials_list = []
    
    # 1. Footing Length
    footing_length = sum(item['value'] for item in foundation_items)
    if footing_length <= 0:
        footing_length = total_wall_length
        notes_suffix = " (Inferred from wall footprint)"
    else:
        notes_suffix = " (Based on detected plan annotations)"
        
    # 2. Quantities
    excavation_vol = round(footing_length * 0.6 * 0.6, 3)
    footing_concrete_vol = round(footing_length * DEFAULT_FOOTING_WIDTH_M * DEFAULT_FOOTING_DEPTH_M, 3)
    
    # Cement, Sand, Gravel for C20/25 footing concrete
    # Standard mix: 1m3 concrete requires ~6.5 bags cement, 0.5 tons sand, 0.8 tons gravel
    cement_bags = math.ceil(footing_concrete_vol * 6.5)
    sand_tons = round(footing_concrete_vol * 0.5, 2)
    gravel_tons = round(footing_concrete_vol * 0.8, 2)
    
    # Foundation Walling (Assume 0.6m height, standard double skin)
    # double skin has thickness factor ~1.5
    foundation_bricks = math.ceil(footing_length * 0.6 * 60 * 1.5)
    
    # Steel rebar longitudinal (4 bars of Y12 along footing length)
    # Y12 weight is approx 0.888 kg/m
    footing_steel_kg = round(footing_length * 4 * 0.888, 2)
    
    # 3. Line Items & Costs
    # Excavation labor
    exc_cost = round(excavation_vol * PRICE_EXCAVATION_PER_M3, 2)
    materials_list.append(PhaseMaterialItem(
        item='Trench Excavation & Backfilling',
        quantity=excavation_vol,
        unit='m3',
        unit_rate=PRICE_EXCAVATION_PER_M3,
        total_cost=exc_cost,
        notes=f'Manual excavation for footing trench{notes_suffix}.'
    ))
    
    # Concrete footing supply
    conc_cost = round(footing_concrete_vol * DEFAULT_FOUNDATION_CONCRETE_RATE_UGX_PER_M3, 2)
    materials_list.append(PhaseMaterialItem(
        item='C20 Footing Concrete',
        quantity=footing_concrete_vol,
        unit='m3',
        unit_rate=DEFAULT_FOUNDATION_CONCRETE_RATE_UGX_PER_M3,
        total_cost=conc_cost,
        notes=f'Supply & pour of strip footing concrete{notes_suffix}.'
    ))
    
    # Reinforcement steel
    steel_cost = round(footing_steel_kg * PRICE_STEEL_REBAR_PER_KG, 2)
    materials_list.append(PhaseMaterialItem(
        item='Foundation Y12 Reinforcing Steel',
        quantity=footing_steel_kg,
        unit='kg',
        unit_rate=PRICE_STEEL_REBAR_PER_KG,
        total_cost=steel_cost,
        notes=f'Footing steel cage longitudinal bars{notes_suffix}.'
    ))
    
    # Foundation Bricks
    brick_rate = DEFAULT_PRICES_UGX['brick']
    brick_cost = round(foundation_bricks * brick_rate, 2)
    materials_list.append(PhaseMaterialItem(
        item='Foundation Bricks (Burnt Clay)',
        quantity=foundation_bricks,
        unit='pcs',
        unit_rate=brick_rate,
        total_cost=brick_cost,
        notes=f'Substructure walling to ground level{notes_suffix}.'
    ))
    
    # Raw ingredients breakdown for mortar & concrete
    cem_cost = round(cement_bags * DEFAULT_PRICES_UGX['cement_bag'], 2)
    materials_list.append(PhaseMaterialItem(
        item='Cement (50kg bags) - Foundation',
        quantity=cement_bags,
        unit='bags',
        unit_rate=DEFAULT_PRICES_UGX['cement_bag'],
        total_cost=cem_cost,
        notes='Cement for concrete footing and walling mortar.'
    ))
    
    sand_cost = round(sand_tons * DEFAULT_PRICES_UGX['sand_ton'], 2)
    materials_list.append(PhaseMaterialItem(
        item='Lake Sand - Foundation',
        quantity=sand_tons,
        unit='tons',
        unit_rate=DEFAULT_PRICES_UGX['sand_ton'],
        total_cost=sand_cost,
        notes='Lake sand for footing mix & walling mortar.'
    ))
    
    gravel_cost = round(gravel_tons * PRICE_GRAVEL_AGGREGATES_PER_TON, 2)
    materials_list.append(PhaseMaterialItem(
        item='Aggregates / Gravel (20mm)',
        quantity=gravel_tons,
        unit='tons',
        unit_rate=PRICE_GRAVEL_AGGREGATES_PER_TON,
        total_cost=gravel_cost,
        notes='Coarse aggregates for structural footing concrete.'
    ))
    
    phase_cost = round(exc_cost + conc_cost + steel_cost + brick_cost + cem_cost + sand_cost + gravel_cost, 2)
    
    return PhaseGroup(
        phase_name='Foundation / Substructure',
        materials=materials_list,
        phase_cost=phase_cost,
        comments='Complete substructure works including trenching, reinforcing, concrete footing, and foundation walling.'
    )


def _build_masonry_phase(materials: DetailedMaterialResponse) -> PhaseGroup:
    bricks = materials.project_totals.total_bricks_count
    mortar = materials.project_totals.total_mortar_volume_m3
    brick_rate = DEFAULT_PRICES_UGX['brick']
    cement_rate = DEFAULT_PRICES_UGX['cement_bag']
    sand_rate = DEFAULT_PRICES_UGX['sand_ton']

    cement_bags = math.ceil(mortar * MORTAR_TO_CEMENT_BAGS) if mortar > 0 else 0
    sand_tons = round(mortar * MORTAR_TO_SAND_TONS, 2) if mortar > 0 else 0.0
    brick_cost = bricks * brick_rate
    cement_cost = cement_bags * cement_rate
    sand_cost = round(sand_tons * sand_rate, 2)
    phase_cost = round(brick_cost + cement_cost + sand_cost, 2)

    materials_list = []
    if bricks > 0:
        materials_list.append(PhaseMaterialItem(
            item='Burnt Clay Bricks - Superstructure',
            quantity=bricks,
            unit='pcs',
            unit_rate=brick_rate,
            total_cost=brick_cost,
            notes='For superstructure load-bearing and partition walls.'
        ))
    if cement_bags > 0:
        materials_list.append(PhaseMaterialItem(
            item='Cement (50kg bags) - Superstructure',
            quantity=cement_bags,
            unit='bags',
            unit_rate=cement_rate,
            total_cost=cement_cost,
            notes='Calculated for standard 1:4 walling mortar mix.'
        ))
    if sand_tons > 0:
        materials_list.append(PhaseMaterialItem(
            item='Lake Sand - Superstructure',
            quantity=sand_tons,
            unit='tons',
            unit_rate=sand_rate,
            total_cost=sand_cost,
            notes='Lake sand for walling mortar.'
        ))

    return PhaseGroup(
        phase_name='Masonry / Walling',
        materials=materials_list,
        phase_cost=phase_cost,
        comments='Wall materials and masonry-phase mortar decomposition for the superstructure.'
    )


def _build_structural_phase(
    total_wall_length: float,
    beam_items: List[Dict[str, float]],
    column_items: List[Dict[str, float]]
) -> PhaseGroup:
    materials_list = []
    
    # 1. Columns
    total_columns = len(column_items)
    inferred_cols = False
    if total_columns <= 0:
        total_columns = max(4, math.ceil(total_wall_length / 4.0))
        inferred_cols = True
        
    column_notes = "Inferred corner/intersection columns" if inferred_cols else "Detected column annotations"
    
    # 2. Beams / Ring Beams
    total_beam_length = sum(item['value'] for item in beam_items)
    inferred_beams = False
    if total_beam_length <= 0:
        total_beam_length = total_wall_length
        inferred_beams = True
        
    beam_notes = "Inferred tie/ring beam along wall length" if inferred_beams else "Detected beam annotations"
    
    # 3. Quantities
    # Ring beam concrete: width 0.23m, depth 0.30m
    ring_beam_concrete_vol = round(total_beam_length * 0.23 * 0.30, 3)
    
    # Column concrete: assume 200mm x 200mm x 3.0m columns
    column_concrete_vol = round(total_columns * 0.2 * 0.2 * 3.0, 3)
    total_concrete_vol = round(ring_beam_concrete_vol + column_concrete_vol, 3)
    
    # Structural concrete mix raw ingredients
    cement_bags = math.ceil(total_concrete_vol * 7.5) # C25 structural concrete mix (approx 7.5 bags/m3)
    sand_tons = round(total_concrete_vol * 0.45, 2)
    gravel_tons = round(total_concrete_vol * 0.75, 2)
    
    # Reinforcement steel: Y12 longitudinal bars (4 bars per column/beam)
    # Weight per meter = 0.888 kg/m
    column_height_sum = total_columns * 3.0
    beam_length_sum = total_beam_length
    total_steel_m = (column_height_sum * 4) + (beam_length_sum * 4)
    steel_y12_kg = round(total_steel_m * 0.888 * 1.15, 2) # Factoring 15% lap/waste
    
    # Stirrup/Link steel: R8 links spaced at 200mm (0.2m)
    # Link perimeter length is approx 0.8m. R8 weight is 0.395 kg/m
    links_count = math.ceil((column_height_sum / 0.2) + (beam_length_sum / 0.2))
    steel_r8_kg = round(links_count * 0.8 * 0.395 * 1.10, 2) # 10% waste
    
    # 4. Add items
    materials_list.append(PhaseMaterialItem(
        item='Structural Concrete Columns',
        quantity=total_columns,
        unit='pcs',
        unit_rate=DEFAULT_STEEL_COLUMN_RATE_UGX_PER_PIECE,
        total_cost=round(total_columns * DEFAULT_STEEL_COLUMN_RATE_UGX_PER_PIECE, 2),
        notes=f'Supply and pour of reinforced columns ({column_notes}).'
    ))
    
    beam_cost = round(total_beam_length * DEFAULT_STEEL_BEAM_RATE_UGX_PER_M, 2)
    materials_list.append(PhaseMaterialItem(
        item='Tie/Ring Beams',
        quantity=round(total_beam_length, 2),
        unit='m',
        unit_rate=DEFAULT_STEEL_BEAM_RATE_UGX_PER_M,
        total_cost=beam_cost,
        notes=f'Ring beam at wall-plate level ({beam_notes}).'
    ))
    
    steel_y12_cost = round(steel_y12_kg * PRICE_STEEL_REBAR_PER_KG, 2)
    materials_list.append(PhaseMaterialItem(
        item='Longitudinal Steel Rebars (Y12)',
        quantity=steel_y12_kg,
        unit='kg',
        unit_rate=PRICE_STEEL_REBAR_PER_KG,
        total_cost=steel_y12_cost,
        notes='Main reinforcement bars for beams and columns.'
    ))
    
    steel_r8_cost = round(steel_r8_kg * PRICE_STEEL_REBAR_PER_KG, 2)
    materials_list.append(PhaseMaterialItem(
        item='Stirrups & Links (R8)',
        quantity=steel_r8_kg,
        unit='kg',
        unit_rate=PRICE_STEEL_REBAR_PER_KG,
        total_cost=steel_r8_cost,
        notes='Stirrup rings/links for structural safety shear resistance.'
    ))
    
    cem_cost = round(cement_bags * DEFAULT_PRICES_UGX['cement_bag'], 2)
    materials_list.append(PhaseMaterialItem(
        item='Cement (50kg bags) - Structural',
        quantity=cement_bags,
        unit='bags',
        unit_rate=DEFAULT_PRICES_UGX['cement_bag'],
        total_cost=cem_cost,
        notes='Cement for high-strength C25 structural concrete frame.'
    ))
    
    sand_cost = round(sand_tons * DEFAULT_PRICES_UGX['sand_ton'], 2)
    materials_list.append(PhaseMaterialItem(
        item='Lake Sand - Structural',
        quantity=sand_tons,
        unit='tons',
        unit_rate=DEFAULT_PRICES_UGX['sand_ton'],
        total_cost=sand_cost,
        notes='Lake sand for column and beam concrete.'
    ))
    
    gravel_cost = round(gravel_tons * PRICE_GRAVEL_AGGREGATES_PER_TON, 2)
    materials_list.append(PhaseMaterialItem(
        item='Aggregates / Gravel (20mm) - Structural',
        quantity=gravel_tons,
        unit='tons',
        unit_rate=PRICE_GRAVEL_AGGREGATES_PER_TON,
        total_cost=gravel_cost,
        notes='Coarse aggregates for beam/column concrete mix.'
    ))
    
    phase_cost = round(
        (total_columns * DEFAULT_STEEL_COLUMN_RATE_UGX_PER_PIECE) +
        beam_cost + steel_y12_cost + steel_r8_cost + cem_cost + sand_cost + gravel_cost,
        2
    )
    
    return PhaseGroup(
        phase_name='Structural Frame',
        materials=materials_list,
        phase_cost=phase_cost,
        comments='Includes reinforced concrete columns and tie/ring beams providing structural integrity to the wall system.'
    )


def _build_roof_phase(
    total_wall_length: float,
    roof_items: List[Dict[str, float]]
) -> PhaseGroup:
    materials_list = []
    
    # 1. Roof area
    total_area = sum(item['value'] for item in roof_items)
    inferred_roof = False
    if total_area <= 0:
        # Footprint area is roughly 2.5 * total wall length for standard room distributions.
        # Factor 1.25 covers pitch slope and eaves overhang!
        total_area = round((total_wall_length * 2.5) * 1.25, 2)
        inferred_roof = True
        
    roof_notes = "Inferred from wall footprint + overhang + slope" if inferred_roof else "Based on detected plan annotations"
    
    # 2. Material Quantities
    sheets_area = round(total_area * 1.15, 2) # 15% overlap
    timber_length = round(total_area * 8.5, 2) # eucalyptus trusses rafters purlins
    nails_kg = math.ceil(total_area * 0.15)
    
    sheets_cost = round(sheets_area * PRICE_ROOF_SHEET_PER_M2, 2)
    materials_list.append(PhaseMaterialItem(
        item='Roofing Sheets (Pre-painted G30)',
        quantity=sheets_area,
        unit='m2',
        unit_rate=PRICE_ROOF_SHEET_PER_M2,
        total_cost=sheets_cost,
        notes=f'Pre-painted corrugated sheets G30 with 15% overlap ({roof_notes}).'
    ))
    
    timber_cost = round(timber_length * PRICE_TIMBER_PER_M, 2)
    materials_list.append(PhaseMaterialItem(
        item='Treated Eucalyptus/Pine Timber',
        quantity=timber_length,
        unit='m',
        unit_rate=PRICE_TIMBER_PER_M,
        total_cost=timber_cost,
        notes='Treated Eucalyptus/Pine timber (75x50mm, 100x50mm) for framing & purlins.'
    ))
    
    nails_cost = round(nails_kg * PRICE_ROOF_NAILS_PER_KG, 2)
    materials_list.append(PhaseMaterialItem(
        item='Roofing Nails & Washers',
        quantity=nails_kg,
        unit='kg',
        unit_rate=PRICE_ROOF_NAILS_PER_KG,
        total_cost=nails_cost,
        notes='Standard roofing nails and weatherproof rubber washers.'
    ))
    
    labor_cost = round(total_area * PRICE_ROOF_LABOR_PER_M2, 2)
    materials_list.append(PhaseMaterialItem(
        item='Labor for Truss & Roof Sheet Installation',
        quantity=total_area,
        unit='m2',
        unit_rate=PRICE_ROOF_LABOR_PER_M2,
        total_cost=labor_cost,
        notes='Truss assembly, timber installation, alignment, and sheet fixing labor.'
    ))
    
    phase_cost = round(sheets_cost + timber_cost + nails_cost + labor_cost, 2)
    
    return PhaseGroup(
        phase_name='Roofing',
        materials=materials_list,
        phase_cost=phase_cost,
        comments='Complete roofing solution including timber truss fabrication, structural purlins, metal sheet cladding, and roofing nails.'
    )


def _build_finishes_phase(materials: DetailedMaterialResponse) -> PhaseGroup:
    total_wall_area = sum(w.net_area_m2 for w in materials.walls) if materials.walls else 0.0
    render_area = round(total_wall_area * 2.0, 2)
    paint_liters = round(render_area * 0.1, 2)
    plaster_volume = round(render_area * 0.015, 3)

    plaster_rate = 420000.0
    paint_rate = 22000.0

    plaster_cost = round(plaster_volume * plaster_rate, 2)
    paint_cost = round(paint_liters * paint_rate, 2)

    materials_list = []
    if plaster_volume > 0:
        materials_list.append(PhaseMaterialItem(
            item='Cement Plaster (15mm) for Wall Finishes',
            quantity=plaster_volume,
            unit='m3',
            unit_rate=plaster_rate,
            total_cost=plaster_cost,
            notes='Internal and external wall rendering based on wall surface area.'
        ))
    if paint_liters > 0:
        materials_list.append(PhaseMaterialItem(
            item='Wall Paint & Primer',
            quantity=paint_liters,
            unit='L',
            unit_rate=paint_rate,
            total_cost=paint_cost,
            notes='Finish paint allowance for plastered wall surfaces.'
        ))

    phase_cost = round(plaster_cost + paint_cost, 2)
    return PhaseGroup(
        phase_name='Finishes',
        materials=materials_list,
        phase_cost=phase_cost,
        comments='Wall finishes using plaster and paint to prepare surfaces for handover.'
    )


def estimate_project_phases(
    filename: str,
    ocr_text: str,
    material_response: DetailedMaterialResponse
) -> PhaseEstimationResponse:
    """Estimate construction materials by phase using OCR-derived annotations or robust fallbacks."""
    # 1. Total wall length calculation from detailed response
    total_net_area = sum(w.net_area_m2 for w in material_response.walls)
    inferred_wall_height = 3.0
    total_wall_length = round(total_net_area / inferred_wall_height, 2)
    if total_wall_length <= 0:
        total_wall_length = 50.0  # Safe default footprint for standard house

    # 2. Extract OCR items
    beam_items = _extract_tagged_items(ocr_text, ['beam', 'blm'])
    column_items = _extract_tagged_items(ocr_text, ['column', 'col'])
    foundation_items = _extract_tagged_items(ocr_text, ['footing', 'foundation', 'strip footing', 'pad footing'])
    roof_items = _extract_tagged_items(ocr_text, ['roof', 'gable', 'hip', 'ridge', 'eave'], area=True)

    phases: List[PhaseGroup] = []

    # Phase 1: Foundation & Substructure
    foundation_phase = _build_foundation_phase(total_wall_length, foundation_items)
    phases.append(foundation_phase)

    # Phase 2: Masonry / Superstructure Walling
    masonry_phase = _build_masonry_phase(material_response)
    if masonry_phase.materials:
        phases.append(masonry_phase)

    # Phase 3: Structural Frame
    structural_phase = _build_structural_phase(total_wall_length, beam_items, column_items)
    phases.append(structural_phase)

    # Phase 4: Roofing
    roof_phase = _build_roof_phase(total_wall_length, roof_items)
    phases.append(roof_phase)

    # Phase 5: Finishes
    finishes_phase = _build_finishes_phase(material_response)
    if finishes_phase.materials:
        phases.append(finishes_phase)

    # Summary Parts
    summary_parts = []
    if foundation_items:
        summary_parts.append('Explicit Foundation footing annotations detected')
    else:
        summary_parts.append('Foundation estimated using building footprint')
        
    if beam_items or column_items:
        summary_parts.append('Explicit Structural beams/columns detected')
    else:
        summary_parts.append('Structural columns/beams inferred for structural safety')
        
    if roof_items:
        summary_parts.append('Explicit Roof area detected')
    else:
        summary_parts.append('Roofing estimated using standard slope & overhang model')

    total_cost = round(sum(phase.phase_cost for phase in phases), 2)
    detected_phases = [phase.phase_name for phase in phases]
    summary = ' | '.join(summary_parts)

    return PhaseEstimationResponse(
        filename=filename,
        phases=phases,
        total_project_cost=total_cost,
        summary=summary,
        detected_phases=detected_phases
    )

