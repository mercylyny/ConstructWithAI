import math
from typing import Dict, Any, List
from schemas.costing import CostEstimationRequest, CostEstimationResponse, CostLineItem

# Default Uganda Market Rates (UGX) - Current on-ground construction pricing
DEFAULT_PRICES_UGX = {
    "brick": 500.0,           # Per Piece (Burnt Clay)
    "cement_bag": 42000.0,    # Per 50kg Bag
    "sand_ton": 80000.0,      # Per Ton (Lake Sand)
}

# Conversion Factors (Engineering -> Purchase Units)
# Mortar Mix 1:4 Ratio Assumptions:
# 1 m3 Wet Mortar approx requires:
# - ~1.3 m3 Dry Materials
# - Cement: ~300 kg (6 bags) -> Using 7 bags to be conservative
# - Sand: ~1.2 tons
MORTAR_TO_CEMENT_BAGS = 7.0  # Bags per m3 mortar
MORTAR_TO_SAND_TONS = 1.2    # Tons per m3 mortar

def calculate_project_cost(request: CostEstimationRequest) -> CostEstimationResponse:
    """
    Calculates the total project material cost based on provided quantities
    and optional custom rates.
    """
    qty = request.quantities
    rates = request.custom_rates or object() # precise handling below
    
    # 1. Determine Effective Rates
    brick_rate = getattr(rates, 'brick_price_ugx', None) or DEFAULT_PRICES_UGX["brick"]
    cement_rate = getattr(rates, 'cement_bag_price_ugx', None) or DEFAULT_PRICES_UGX["cement_bag"]
    sand_rate = getattr(rates, 'sand_ton_price_ugx', None) or DEFAULT_PRICES_UGX["sand_ton"]
    
    line_items = []
    total_cost = 0.0
    
    # 2. Bricks Calculation
    if qty.total_bricks_count > 0:
        amount = qty.total_bricks_count * brick_rate
        line_items.append(CostLineItem(
            item="Burnt Clay Bricks",
            quantity=qty.total_bricks_count,
            unit="pcs",
            rate=brick_rate,
            amount=amount
        ))
        total_cost += amount
        
    # 3. Mortar Decomposition & Calculation
    if qty.total_mortar_volume_m3 > 0:
        # Cement
        cement_bags = math.ceil(qty.total_mortar_volume_m3 * MORTAR_TO_CEMENT_BAGS)
        cement_amount = cement_bags * cement_rate
        line_items.append(CostLineItem(
            item="Cement (50kg, 1:4 Mix)",
            quantity=cement_bags,
            unit="bags",
            rate=cement_rate,
            amount=cement_amount
        ))
        total_cost += cement_amount
        
        # Sand
        sand_tons = round(qty.total_mortar_volume_m3 * MORTAR_TO_SAND_TONS, 2)
        sand_amount = sand_tons * sand_rate
        line_items.append(CostLineItem(
            item="Lake Sand",
            quantity=sand_tons,
            unit="tons",
            rate=sand_rate,
            amount=sand_amount
        ))
        total_cost += sand_amount
        
    return CostEstimationResponse(
        currency="UGX",
        line_items=line_items,
        total_project_cost=round(total_cost, 2),
        context="Uganda (Default) - Materials Only"
    )
