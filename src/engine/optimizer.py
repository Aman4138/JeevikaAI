"""Constraint-Aware Decision & Optimization Engine for Indian Street Vendors."""

from typing import Dict, Any, List, Optional
import numpy as np
from scipy.optimize import minimize

from src.utils.logger import logger
from src.config import get_commodities, load_config

class ConstraintOptimizer:
    """
    Mathematical optimization engine for vendor inventory purchase decisions.
    Maximizes expected profit while enforcing hard budget constraints,
    penalizing perishable waste, and respecting current stock and risk preferences.
    """

    def __init__(self):
        self.commodities_meta = get_commodities()
        self.config = load_config()

    def optimize_purchase_plan(
        self,
        budget: float,
        inventory: Dict[str, float],
        prices: Dict[str, float], # Wholesale cost per kg
        retail_prices: Dict[str, float], # Retail selling price per kg
        demands: Dict[str, float], # Expected demand in kg
        risk_profile: str = "balanced", # "conservative", "balanced", "aggressive"
        weather_factor: float = 1.0 # Demand scaling due to weather (e.g. 0.85 for rain)
    ) -> Dict[str, Any]:
        """
        Solve constrained allocation problem:
        max_q sum_i [ p_i * min(I_i + q_i, D_i) - c_i * q_i - penalty_waste_i ]
        s.t. sum_i c_i * q_i <= Budget
             q_i >= 0
        """
        # Clean inputs and handle edge cases
        budget = max(0.0, float(budget))
        risk_profile = risk_profile.lower() if risk_profile in ["conservative", "balanced", "aggressive"] else "balanced"
        risk_params = self.config.get("optimizer", {}).get("risk_profiles", {}).get(risk_profile, {
            "safety_stock_factor": 1.0,
            "perishability_penalty_weight": 1.0,
            "budget_utilization_target": 0.95
        })

        products = ["tomato", "onion", "potato"]
        
        # Prepare vectors
        inv_vec = []
        cost_vec = []
        retail_vec = []
        demand_vec = []
        waste_penalty_vec = []

        for p in products:
            meta = self.commodities_meta.get(p, {})
            
            # Existing inventory
            inv = max(0.0, float(inventory.get(p, 0.0)))
            inv_vec.append(inv)

            # Wholesale cost (Rs/kg)
            cost = max(1.0, float(prices.get(p, meta.get("default_wholesale_cost_per_kg", 24.0))))
            cost_vec.append(cost)

            # Retail selling price (Rs/kg)
            default_retail = cost * (1.0 + meta.get("typical_retail_margin_pct", 0.30))
            retail = max(cost + 0.5, float(retail_prices.get(p, default_retail)))
            retail_vec.append(retail)

            # Effective expected demand adjusted for weather & risk profile
            raw_demand = max(0.0, float(demands.get(p, meta.get("typical_daily_demand_kg", 20.0))))
            effective_demand = raw_demand * weather_factor * risk_params.get("safety_stock_factor", 1.0)
            demand_vec.append(effective_demand)

            # Perishability waste penalty weight
            spoilage_rate = meta.get("spoilage_rate_daily", 0.05)
            penalty_weight = spoilage_rate * risk_params.get("perishability_penalty_weight", 1.0) * cost
            waste_penalty_vec.append(penalty_weight)

        inv_arr = np.array(inv_vec)
        cost_arr = np.array(cost_vec)
        retail_arr = np.array(retail_vec)
        demand_arr = np.array(demand_vec)
        waste_pen_arr = np.array(waste_penalty_vec)

        # Handle zero or minimal budget edge case immediately
        if budget < 1.0:
            return self._format_response(products, np.zeros(len(products)), inv_arr, cost_arr, retail_arr, demand_arr, budget, risk_profile)

        effective_budget_cap = budget * risk_params.get("budget_utilization_target", 0.98)

        # Upper bounds for search: cannot buy more than needed to cover deficit + slight safety
        deficits = np.maximum(0.0, demand_arr - inv_arr)
        max_quantities = []
        for i in range(len(products)):
            # Max affordable or 2x deficit
            afford_max = effective_budget_cap / cost_arr[i]
            demand_bound = deficits[i] * 1.5 + 5.0
            max_quantities.append(max(0.0, min(afford_max, demand_bound)))

        # Define negative profit objective function for SciPy minimizer
        def objective(q):
            total_stock = inv_arr + q
            expected_sales = np.minimum(total_stock, demand_arr)
            excess_stock = np.maximum(0.0, total_stock - demand_arr)
            
            revenue = np.sum(retail_arr * expected_sales)
            purchase_cost = np.sum(cost_arr * q)
            waste_loss = np.sum(waste_pen_arr * excess_stock)
            
            net_profit = revenue - purchase_cost - waste_loss
            return -net_profit # Minimizing negative profit

        # Constraints & bounds
        bounds = [(0.0, max_quantities[i]) for i in range(len(products))]
        constraints = [
            {"type": "ineq", "fun": lambda q: effective_budget_cap - np.sum(cost_arr * q)} # Budget cap: cap - sum(c*q) >= 0
        ]

        # Initial guess: fill deficits proportional to budget
        initial_q = np.zeros(len(products))
        total_deficit_cost = np.sum(cost_arr * deficits)
        if total_deficit_cost > 0:
            scale = min(1.0, effective_budget_cap / total_deficit_cost)
            initial_q = deficits * scale
        
        # Optimize using SLSQP
        try:
            res = minimize(
                objective,
                initial_q,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"maxiter": 200, "ftol": 1e-4}
            )
            q_opt = np.maximum(0.0, res.x)
        except Exception as e:
            logger.warning("Optimization solver error: %s. Using heuristic greedy allocation.", e)
            q_opt = self._greedy_allocation(deficits, cost_arr, retail_arr, demand_arr, inv_arr, effective_budget_cap)

        # Enforce discrete vendor step (round to nearest 0.5 kg)
        q_discrete = np.round(q_opt * 2) / 2.0

        # Strict budget validation check: scale down if rounding exceeded budget
        total_spend = np.sum(cost_arr * q_discrete)
        if total_spend > budget:
            # Scale down proportionally
            ratio = (budget * 0.98) / total_spend
            q_discrete = np.floor((q_discrete * ratio) * 2) / 2.0
            q_discrete = np.maximum(0.0, q_discrete)

        return self._format_response(products, q_discrete, inv_arr, cost_arr, retail_arr, demand_arr, budget, risk_profile)

    def _greedy_allocation(self, deficits, costs, retails, demands, invs, budget_cap):
        """Deterministic greedy heuristic allocation as robust fallback."""
        margins = (retails - costs) / costs
        # Rank commodities by return on investment
        rankings = np.argsort(-margins)
        
        q = np.zeros(len(deficits))
        rem_budget = budget_cap

        for idx in rankings:
            needed = deficits[idx]
            if needed > 0 and rem_budget > 0:
                cost = costs[idx]
                qty_to_buy = min(needed, rem_budget / cost)
                q[idx] = qty_to_buy
                rem_budget -= qty_to_buy * cost

        return q

    def _format_response(self, products, q_arr, inv_arr, cost_arr, retail_arr, demand_arr, budget, risk_profile):
        """Construct detailed structured recommendation payload."""
        recommendations = []
        total_investment = 0.0
        total_expected_revenue = 0.0
        total_expected_profit = 0.0
        total_incremental_profit = 0.0

        for i, prod in enumerate(products):
            meta = self.commodities_meta.get(prod, {})
            qty = float(round(q_arr[i], 1))
            cost_per_kg = float(round(cost_arr[i], 1))
            retail_per_kg = float(round(retail_arr[i], 1))
            current_stock = float(round(inv_arr[i], 1))
            exp_demand = float(round(demand_arr[i], 1))
            
            purchase_cost = round(qty * cost_per_kg, 1)
            total_stock = current_stock + qty
            units_expected_sold = min(total_stock, exp_demand)
            expected_revenue = round(units_expected_sold * retail_per_kg, 1)
            
            # Unit margin per kg
            unit_margin = round(retail_per_kg - cost_per_kg, 1)
            
            # Incremental profit specifically from new purchase
            incremental_profit = round(qty * unit_margin, 1)
            
            # Total accounting profit from all units sold (Revenue - COGS)
            cogs = round(units_expected_sold * cost_per_kg, 1)
            item_profit = round(expected_revenue - cogs, 1)
            
            margin_pct = round((unit_margin / cost_per_kg) * 100, 1) if cost_per_kg > 0 else 0.0

            # Item risk assessment
            shelf_life = meta.get("shelf_life_days", 7.0)
            if shelf_life <= 3.0 and (total_stock > exp_demand * 1.1):
                item_risk = "HIGH"
                item_risk_reason = "High perishability: total stock exceeds estimated daily demand."
            elif shelf_life <= 3.0:
                item_risk = "MEDIUM"
                item_risk_reason = "Short shelf-life (2-3 days). Recommended quantity strictly matches daily demand."
            else:
                item_risk = "LOW"
                item_risk_reason = "Stable shelf-life. Minimal spoilage risk."

            rec_item = {
                "product": prod,
                "display_name": meta.get("display_name", prod.capitalize()),
                "hindi_name": meta.get("hindi_name", ""),
                "icon": meta.get("icon", "🥬"),
                "color": meta.get("color", "#10B981"),
                "current_stock_kg": current_stock,
                "estimated_demand_kg": exp_demand,
                "recommended_purchase_kg": qty,
                "total_available_stock_kg": round(total_stock, 1),
                "wholesale_cost_per_kg": cost_per_kg,
                "retail_selling_price_per_kg": retail_per_kg,
                "unit_margin_per_kg": unit_margin,
                "estimated_purchase_cost": purchase_cost,
                "expected_sales_kg": round(units_expected_sold, 1),
                "expected_revenue": expected_revenue,
                "expected_profit": item_profit,
                "incremental_purchase_profit": incremental_profit,
                "margin_pct": margin_pct,
                "shelf_life_days": shelf_life,
                "item_risk": item_risk,
                "item_risk_reason": item_risk_reason
            }
            recommendations.append(rec_item)
            
            total_investment += purchase_cost
            total_expected_revenue += expected_revenue
            total_expected_profit += item_profit
            total_incremental_profit += incremental_profit

        total_investment = round(total_investment, 1)
        total_expected_revenue = round(total_expected_revenue, 1)
        total_expected_profit = round(total_expected_profit, 1)
        total_incremental_profit = round(total_incremental_profit, 1)
        remaining_cash = round(max(0.0, budget - total_investment), 1)
        roi_pct = round((total_expected_profit / total_investment * 100.0), 1) if total_investment > 0 else 0.0

        return {
            "budget": budget,
            "risk_profile": risk_profile,
            "total_investment": total_investment,
            "total_expected_revenue": total_expected_revenue,
            "total_expected_profit": total_expected_profit,
            "total_incremental_profit": total_incremental_profit,
            "remaining_cash": remaining_cash,
            "roi_pct": roi_pct,
            "recommendations": recommendations,
            "disclaimer": "All figures are prototype decision-support estimates based on historical patterns and vendor constraints."
        }
