"""Transparent Prototype Risk Scoring System for Vendor Decisions."""

from typing import Dict, Any, List

class RiskEngine:
    """Calculates multi-dimensional risk score and generates transparent factor breakdowns."""

    def evaluate_risk(
        self,
        recommendation_plan: Dict[str, Any],
        weather_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Evaluate overall decision risk (0 - 100) based on:
        1. Budget Utilization / Cash Reserve (0 - 25)
        2. Perishable Capital Exposure (0 - 35)
        3. Stock-to-Demand Oversupply (0 - 25)
        4. Weather / Spoilage Vulnerability (0 - 15)
        """
        budget = recommendation_plan.get("budget", 2000.0)
        investment = recommendation_plan.get("total_investment", 0.0)
        recs = recommendation_plan.get("recommendations", [])
        
        # 1. Budget Utilization Factor (0 - 25 points)
        util_ratio = (investment / budget) if budget > 0 else 0.0
        if util_ratio > 0.95:
            budget_score = 22.0
            budget_factor = "Near 100% budget utilized; leaves minimal liquid cash reserve."
            budget_factor_hi = "लगभग 100% बजट उपयोग; कोई आकस्मिक नकद नहीं बचता।"
        elif util_ratio > 0.80:
            budget_score = 14.0
            budget_factor = "Healthy budget utilization with modest cash reserve."
            budget_factor_hi = "संतुलित बजट उपयोग; थोड़ा नकद सुरक्षित रखा गया है।"
        else:
            budget_score = 6.0
            budget_factor = "Conservative spending; significant cash buffer maintained."
            budget_factor_hi = "सुरक्षित खर्च; पर्याप्त नकद रिज़र्व बचा हुआ है।"

        # 2. Perishable Capital Exposure (0 - 35 points)
        perishable_spend = 0.0
        for item in recs:
            if item.get("shelf_life_days", 7.0) <= 3.0: # e.g. Tomato
                perishable_spend += item.get("estimated_purchase_cost", 0.0)

        perishable_ratio = (perishable_spend / investment) if investment > 0 else 0.0
        if perishable_ratio > 0.50:
            perish_score = 30.0
            perish_factor = f"High allocation ({round(perishable_ratio*100)}%) in highly perishable items (Tomato)."
            perish_factor_hi = f"अत्यधिक खराब होने वाली वस्तुओं (टमाटर) में {round(perishable_ratio*100)}% पूंजी लगी है।"
        elif perishable_ratio > 0.25:
            perish_score = 18.0
            perish_factor = f"Moderate allocation ({round(perishable_ratio*100)}%) in perishables balanced with onion/potato."
            perish_factor_hi = f"टमाटर और टिकाऊ सब्जियों (आलू/प्याज़) में संतुलित आवंटन ({round(perishable_ratio*100)}%)।"
        else:
            perish_score = 8.0
            perish_factor = "Low perishable exposure; mostly invested in durable root vegetables."
            perish_factor_hi = "कम जोखिम; अधिकांश पूंजी टिकाऊ सब्जियों में सुरक्षित है।"

        # 3. Oversupply / Demand Mismatch (0 - 25 points)
        excess_count = 0
        for item in recs:
            total_stock = item.get("total_available_stock_kg", 0.0)
            demand = item.get("estimated_demand_kg", 1.0)
            if total_stock > demand * 1.15:
                excess_count += 1

        if excess_count >= 2:
            oversupply_score = 22.0
            oversupply_factor = "Potential excess stock across multiple items relative to daily demand."
            oversupply_factor_hi = "दैनिक मांग की तुलना में कई वस्तुओं का अधिक स्टॉक होने का जोखिम।"
        elif excess_count == 1:
            oversupply_score = 12.0
            oversupply_factor = "Minor excess buffer in one product category."
            oversupply_factor_hi = "एक वस्तु में हल्का अतिरिक्त स्टॉक।"
        else:
            oversupply_score = 4.0
            oversupply_factor = "Tightly aligned with predicted customer demand."
            oversupply_factor_hi = "अनुमानित मांग के बिल्कुल सटीक और सुरक्षित अनुपात में।"

        # 4. Weather / External Shock (0 - 15 points)
        weather_score = 3.0
        weather_factor = "Normal weather conditions; standard customer footfall expected."
        weather_factor_hi = "सामान्य मौसम; ग्राहकों की सामान्य आवाजाही की उम्मीद।"

        if weather_context:
            rain_risk = weather_context.get("rain_risk", "LOW")
            if rain_risk == "HIGH":
                weather_score = 14.0
                weather_factor = "Heavy rainfall risk: reduced street footfall and faster tomato degradation."
                weather_factor_hi = "भारी बारिश की संभावना: ग्राहकों की कमी और टमाटर जल्दी खराब होने का डर।"
            elif rain_risk == "MEDIUM":
                weather_score = 8.0
                weather_factor = "Scattered rain: minor impact on evening sales."
                weather_factor_hi = "हल्की बारिश: शाम की बिक्री पर मामूली असर पड़ सकता है।"

        total_score = round(budget_score + perish_score + oversupply_score + weather_score, 0)
        total_score = min(100.0, max(0.0, total_score))

        if total_score <= 35:
            risk_level = "LOW"
            risk_level_hi = "कम जोखिम (Low Risk)"
            badge_color = "#10B981"
        elif total_score <= 65:
            risk_level = "MEDIUM"
            risk_level_hi = "मध्यम जोखिम (Medium Risk)"
            badge_color = "#F59E0B"
        else:
            risk_level = "HIGH"
            risk_level_hi = "उच्च जोखिम (High Risk)"
            badge_color = "#EF4444"

        return {
            "risk_score": int(total_score),
            "risk_level": risk_level,
            "risk_level_hi": risk_level_hi,
            "badge_color": badge_color,
            "breakdown": [
                {"factor": "Cash Buffer & Budget", "score": int(budget_score), "max": 25, "reason_en": budget_factor, "reason_hi": budget_factor_hi},
                {"factor": "Perishable Exposure", "score": int(perish_score), "max": 35, "reason_en": perish_factor, "reason_hi": perish_factor_hi},
                {"factor": "Demand Alignment", "score": int(oversupply_score), "max": 25, "reason_en": oversupply_factor, "reason_hi": oversupply_factor_hi},
                {"factor": "Weather Condition", "score": int(weather_score), "max": 15, "reason_en": weather_factor, "reason_hi": weather_factor_hi}
            ],
            "disclaimer": "Prototype decision-support risk indicator. Not a certified financial metric."
        }
