"""Pydantic V2 Request & Response schemas for JeevikaAI API."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class RecommendRequest(BaseModel):
    budget: float = Field(default=2000.0, ge=0.0, description="Available purchasing capital in INR (₹)")
    inventory: Dict[str, float] = Field(
        default_factory=lambda: {"tomato": 5.0, "onion": 3.0, "potato": 8.0},
        description="Current stock on hand in kg"
    )
    location: str = Field(default="Delhi", description="Vendor market / city location")
    risk_profile: str = Field(default="balanced", description="Risk preference: 'conservative', 'balanced', or 'aggressive'")
    custom_wholesale_prices: Optional[Dict[str, float]] = Field(default=None, description="Optional price overrides (₹/kg)")
    custom_retail_prices: Optional[Dict[str, float]] = Field(default=None, description="Optional retail price overrides (₹/kg)")
    custom_demands: Optional[Dict[str, float]] = Field(default=None, description="Optional expected demand overrides (kg)")
    language: str = Field(default="en", description="'en' for English, 'hi' for Hindi")

class ProductRecommendation(BaseModel):
    product: str
    display_name: str
    hindi_name: str
    icon: str
    color: str
    current_stock_kg: float
    estimated_demand_kg: float
    recommended_purchase_kg: float
    total_available_stock_kg: float
    wholesale_cost_per_kg: float
    retail_selling_price_per_kg: float
    unit_margin_per_kg: Optional[float] = None
    estimated_purchase_cost: float
    expected_sales_kg: float
    expected_revenue: float
    expected_profit: float
    incremental_purchase_profit: Optional[float] = None
    margin_pct: float
    shelf_life_days: float
    item_risk: str
    item_risk_reason: str

class RiskBreakdownItem(BaseModel):
    factor: str
    score: int
    max: int
    reason_en: str
    reason_hi: str

class ExplanationPayload(BaseModel):
    language: str
    summary: str
    summary_en: str
    summary_hi: str
    product_reasons: List[str]
    product_reasons_en: List[str]
    product_reasons_hi: List[str]
    decision_rules: List[str]
    decision_rules_en: List[str]
    decision_rules_hi: List[str]

class RecommendResponse(BaseModel):
    budget: float
    risk_profile: str
    location: str
    total_investment: float
    total_expected_revenue: float
    total_expected_profit: float
    total_incremental_profit: Optional[float] = None
    remaining_cash: float
    roi_pct: float
    risk_score: int
    risk_level: str
    risk_level_hi: str
    badge_color: str
    recommendations: List[ProductRecommendation]
    risk_breakdown: List[RiskBreakdownItem]
    explanation: ExplanationPayload
    disclaimer: str

class WhatIfRequest(BaseModel):
    base_request: RecommendRequest
    scenario_name: str = "Modified Scenario"
    scenario_budget: Optional[float] = None
    price_multipliers: Optional[Dict[str, float]] = None # e.g. {"tomato": 1.20}
    demand_multipliers: Optional[Dict[str, float]] = None # e.g. {"all": 0.85}
    inventory_override: Optional[Dict[str, float]] = None
    weather_scenario: Optional[str] = "normal" # "normal", "heavy_rain", "festival_surge"

class WhatIfResponse(BaseModel):
    scenario_name: str
    baseline: Dict[str, Any]
    scenario: Dict[str, Any]
    deltas: Dict[str, Any]

class MarketDataResponse(BaseModel):
    commodity: str
    display_name: str
    hindi_name: str
    market_name: str
    latest_modal_price_rs_kg: float
    min_price_rs_kg: float
    max_price_rs_kg: float
    estimated_retail_price_rs_kg: float
    price_trend_pct_7d: float
    price_trend_direction: str
    recent_arrivals_tonnes: float
    arrivals_trend: str
    supply_signal: str
    timeseries_14d: List[Dict[str, Any]]
    weather: Dict[str, Any]
