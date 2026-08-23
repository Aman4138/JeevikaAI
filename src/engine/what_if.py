"""What-If Simulation Engine for scenario stress testing and sensitivity analysis."""

from typing import Dict, Any, List, Optional
from src.engine.optimizer import ConstraintOptimizer
from src.engine.risk_engine import RiskEngine

class WhatIfSimulator:
    """Simulates alternate vendor scenarios and provides side-by-side delta comparisons."""

    def __init__(self):
        self.optimizer = ConstraintOptimizer()
        self.risk_engine = RiskEngine()

    def simulate_scenario(
        self,
        base_budget: float,
        base_inventory: Dict[str, float],
        base_prices: Dict[str, float],
        base_retail_prices: Dict[str, float],
        base_demands: Dict[str, float],
        base_risk_profile: str = "balanced",
        scenario_name: str = "Custom Scenario",
        scenario_budget: Optional[float] = None,
        price_multipliers: Optional[Dict[str, float]] = None,
        demand_multipliers: Optional[Dict[str, float]] = None,
        inventory_override: Optional[Dict[str, float]] = None,
        weather_scenario: Optional[str] = "normal" # "normal", "heavy_rain", "festival_surge"
    ) -> Dict[str, Any]:
        """
        Run baseline vs modified scenario and compute impact deltas.
        """
        # 1. BASELINE RUN
        base_plan = self.optimizer.optimize_purchase_plan(
            budget=base_budget,
            inventory=base_inventory,
            prices=base_prices,
            retail_prices=base_retail_prices,
            demands=base_demands,
            risk_profile=base_risk_profile,
            weather_factor=1.0
        )
        base_risk = self.risk_engine.evaluate_risk(base_plan)

        # 2. SCENARIO ADJUSTMENTS
        scen_budget = base_budget if scenario_budget is None else max(0.0, float(scenario_budget))
        scen_inv = dict(base_inventory)
        if inventory_override:
            for k, v in inventory_override.items():
                scen_inv[k] = max(0.0, float(v))

        scen_prices = dict(base_prices)
        if price_multipliers:
            for k, mult in price_multipliers.items():
                if k in scen_prices:
                    scen_prices[k] = round(scen_prices[k] * float(mult), 1)

        scen_retails = dict(base_retail_prices)
        # If wholesale price changed, update retail default margin proportionally
        for k in scen_prices:
            if scen_prices[k] != base_prices.get(k, scen_prices[k]):
                scen_retails[k] = round(scen_prices[k] * 1.35, 1)

        scen_demands = dict(base_demands)
        if demand_multipliers:
            for k, mult in demand_multipliers.items():
                if k == "all":
                    for p in scen_demands:
                        scen_demands[p] = round(scen_demands[p] * float(mult), 1)
                elif k in scen_demands:
                    scen_demands[k] = round(scen_demands[k] * float(mult), 1)

        weather_factor = 1.0
        weather_ctx = {"rain_risk": "LOW"}
        if weather_scenario == "heavy_rain":
            weather_factor = 0.78 # -22% demand drop
            weather_ctx = {"rain_risk": "HIGH"}
        elif weather_scenario == "festival_surge":
            weather_factor = 1.30 # +30% festival surge
            weather_ctx = {"rain_risk": "LOW"}

        # 3. SCENARIO RUN
        scen_plan = self.optimizer.optimize_purchase_plan(
            budget=scen_budget,
            inventory=scen_inv,
            prices=scen_prices,
            retail_prices=scen_retails,
            demands=scen_demands,
            risk_profile=base_risk_profile,
            weather_factor=weather_factor
        )
        scen_risk = self.risk_engine.evaluate_risk(scen_plan, weather_ctx)

        # 4. COMPUTE DELTAS
        delta_investment = round(scen_plan["total_investment"] - base_plan["total_investment"], 1)
        delta_revenue = round(scen_plan["total_expected_revenue"] - base_plan["total_expected_revenue"], 1)
        delta_profit = round(scen_plan["total_expected_profit"] - base_plan["total_expected_profit"], 1)
        delta_remaining_cash = round(scen_plan["remaining_cash"] - base_plan["remaining_cash"], 1)
        delta_risk_score = scen_risk["risk_score"] - base_risk["risk_score"]

        # Product level deltas
        product_comparisons = []
        base_recs_map = {r["product"]: r for r in base_plan["recommendations"]}
        scen_recs_map = {r["product"]: r for r in scen_plan["recommendations"]}

        for p in ["tomato", "onion", "potato"]:
            b_item = base_recs_map.get(p, {})
            s_item = scen_recs_map.get(p, {})
            product_comparisons.append({
                "product": p,
                "display_name": b_item.get("display_name", p.capitalize()),
                "hindi_name": b_item.get("hindi_name", ""),
                "base_purchase_kg": b_item.get("recommended_purchase_kg", 0.0),
                "scenario_purchase_kg": s_item.get("recommended_purchase_kg", 0.0),
                "delta_kg": round(s_item.get("recommended_purchase_kg", 0.0) - b_item.get("recommended_purchase_kg", 0.0), 1),
                "base_cost": b_item.get("estimated_purchase_cost", 0.0),
                "scenario_cost": s_item.get("estimated_purchase_cost", 0.0),
                "delta_cost": round(s_item.get("estimated_purchase_cost", 0.0) - b_item.get("estimated_purchase_cost", 0.0), 1),
                "base_profit": b_item.get("expected_profit", 0.0),
                "scenario_profit": s_item.get("expected_profit", 0.0),
                "delta_profit": round(s_item.get("expected_profit", 0.0) - b_item.get("expected_profit", 0.0), 1)
            })

        return {
            "scenario_name": scenario_name,
            "baseline": {
                "budget": base_budget,
                "total_investment": base_plan["total_investment"],
                "total_expected_revenue": base_plan["total_expected_revenue"],
                "total_expected_profit": base_plan["total_expected_profit"],
                "remaining_cash": base_plan["remaining_cash"],
                "risk_score": base_risk["risk_score"],
                "risk_level": base_risk["risk_level"],
                "recommendations": base_plan["recommendations"]
            },
            "scenario": {
                "budget": scen_budget,
                "total_investment": scen_plan["total_investment"],
                "total_expected_revenue": scen_plan["total_expected_revenue"],
                "total_expected_profit": scen_plan["total_expected_profit"],
                "remaining_cash": scen_plan["remaining_cash"],
                "risk_score": scen_risk["risk_score"],
                "risk_level": scen_risk["risk_level"],
                "recommendations": scen_plan["recommendations"]
            },
            "deltas": {
                "delta_investment": delta_investment,
                "delta_revenue": delta_revenue,
                "delta_profit": delta_profit,
                "delta_remaining_cash": delta_remaining_cash,
                "delta_risk_score": delta_risk_score,
                "product_comparisons": product_comparisons
            }
        }
