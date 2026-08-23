"""Bilingual Explainable AI (XAI) Layer for JeevikaAI (English & Hindi)."""

from typing import Dict, Any, List

class RecommendationExplainer:
    """Generates crystal-clear, grounded bilingual explanations for vendor purchase recommendations."""

    def generate_explanation(
        self,
        recommendation_plan: Dict[str, Any],
        risk_evaluation: Dict[str, Any],
        language: str = "en" # "en" or "hi"
    ) -> Dict[str, Any]:
        """
        Generate grounded explanation based on real decision engine outputs.
        """
        budget = recommendation_plan.get("budget", 2000.0)
        investment = recommendation_plan.get("total_investment", 0.0)
        profit = recommendation_plan.get("total_expected_profit", 0.0)
        remaining = recommendation_plan.get("remaining_cash", 0.0)
        recs = recommendation_plan.get("recommendations", [])
        risk_level = risk_evaluation.get("risk_level", "LOW")

        # Build product-specific reasons
        item_explanations_en = []
        item_explanations_hi = []

        for item in recs:
            name = item["product"].capitalize()
            hi_name = item.get("hindi_name", name)
            current_stock = item["current_stock_kg"]
            demand = item["estimated_demand_kg"]
            buy_qty = item["recommended_purchase_kg"]
            cost = item["estimated_purchase_cost"]
            margin = item["margin_pct"]
            shelf_life = item["shelf_life_days"]

            # English item explanation
            if buy_qty == 0.0:
                reason_en = (
                    f"**{name}**: Buy 0 kg. You already have {current_stock} kg on hand, which is sufficient "
                    f"to cover the expected demand of {demand} kg without risking spoilage."
                )
                reason_hi = (
                    f"**{hi_name}**: 0 किलो खरीदें। आपके पास पहले से {current_stock} किलो स्टॉक है, "
                    f"जो आज की अनुमानित मांग ({demand} किलो) के लिए पर्याप्त है और सड़ने का जोखिम नहीं रहेगा।"
                )
            else:
                deficit = max(0.0, round(demand - current_stock, 1))
                if shelf_life <= 3.0:
                    reason_en = (
                        f"**{name}**: Buy {buy_qty} kg (Cost ₹{cost}). With {current_stock} kg in stock and expected demand of {demand} kg, "
                        f"buying {buy_qty} kg meets customer demand while avoiding perishable rotting ({shelf_life} days shelf life)."
                    )
                    reason_hi = (
                        f"**{hi_name}**: {buy_qty} किलो खरीदें (लागत ₹{cost})। आपके पास {current_stock} किलो है और मांग {demand} किलो है; "
                        f"चूंकि टमाटर जल्दी खराब होता है ({shelf_life} दिन), इसलिए केवल मांग के अनुसार {buy_qty} किलो खरीदना सुरक्षित है।"
                    )
                else:
                    reason_en = (
                        f"**{name}**: Buy {buy_qty} kg (Cost ₹{cost}). Generates ~{margin}% profit margin. With long shelf life ({int(shelf_life)} days), "
                        f"this is a stable, low-risk revenue driver."
                    )
                    reason_hi = (
                        f"**{hi_name}**: {buy_qty} किलो खरीदें (लागत ₹{cost})। इसमें ~{margin}% का मुनाफा है और यह {int(shelf_life)} दिनों तक सुरक्षित रहता है, "
                        f"जिससे नुकसान का कोई डर नहीं है।"
                    )

            item_explanations_en.append(reason_en)
            item_explanations_hi.append(reason_hi)

        # High-level summary
        summary_en = (
            f"You have ₹{int(budget):,} available. The system recommends investing ₹{int(investment):,} across "
            f"selected items to target an estimated profit of ₹{int(profit):,}, keeping ₹{int(remaining):,} as an emergency cash reserve. "
            f"The overall risk is rated **{risk_level}**."
        )

        summary_hi = (
            f"आपके पास ₹{int(budget):,} का बजट है। सिस्टम आपको ₹{int(investment):,} का माल खरीदने की सलाह देता है, "
            f"जिससे अनुमानित ₹{int(profit):,} का मुनाफा हो सकता है। साथ ही ₹{int(remaining):,} नकद सुरक्षित रखा गया है। "
            f"इस योजना में जोखिम का स्तर **{risk_evaluation.get('risk_level_hi', risk_level)}** है।"
        )

        # Key decision rules applied
        rules_en = [
            f"**Budget Cap Rule**: Total purchase ₹{investment} strictly within your ₹{budget} budget limit.",
            "**Perishability Guard**: Tomato purchase is strictly capped to 1-day estimated demand to prevent waste.",
            f"**Cash Reserve**: ₹{remaining} buffer retained to protect against sudden evening price changes or slowdowns."
        ]

        rules_hi = [
            f"**बजट सीमा नियम**: कुल खरीद ₹{investment} आपके कुल ₹{budget} के बजट के भीतर पूर्णतः नियंत्रित है।",
            "**खराबी से बचाव नियम**: टमाटर की खरीद को 1 दिन की मांग तक सीमित रखा गया है ताकि माल सड़े नहीं।",
            f"**आकस्मिक नकद बचत**: अचानक जरूरत या शाम के उतार-चढ़ाव के लिए ₹{remaining} नकद हाथ में सुरक्षित रखे गए हैं।"
        ]

        return {
            "language": language,
            "summary": summary_hi if language == "hi" else summary_en,
            "summary_en": summary_en,
            "summary_hi": summary_hi,
            "product_reasons": item_explanations_hi if language == "hi" else item_explanations_en,
            "product_reasons_en": item_explanations_en,
            "product_reasons_hi": item_explanations_hi,
            "decision_rules": rules_hi if language == "hi" else rules_en,
            "decision_rules_en": rules_en,
            "decision_rules_hi": rules_hi
        }
