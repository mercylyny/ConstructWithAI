from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class MaterialQuantities(BaseModel):
    """Input quantities for cost estimation"""
    total_bricks_count: int = Field(..., description="Total number of bricks")
    total_mortar_volume_m3: float = Field(..., description="Total mortar volume in cubic meters")

class CustomRates(BaseModel):
    """Optional custom unit rates (UGX)"""
    brick_price_ugx: Optional[float] = Field(None, description="Price per brick")
    cement_bag_price_ugx: Optional[float] = Field(None, description="Price per 50kg bag of cement")
    sand_ton_price_ugx: Optional[float] = Field(None, description="Price per ton of sand")

class CostEstimationRequest(BaseModel):
    """Request body for project cost estimation"""
    quantities: MaterialQuantities
    custom_rates: Optional[CustomRates] = None

class CostLineItem(BaseModel):
    """Single line item in the cost breakdown"""
    item: str
    quantity: float
    unit: str
    rate: float
    amount: float

class CostEstimationResponse(BaseModel):
    """Structured cost estimation response"""
    currency: str = "UGX"
    line_items: List[CostLineItem]
    total_project_cost: float
    context: str = "Uganda (Default)"
