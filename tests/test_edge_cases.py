"""Edge case robustness tests (zero budget, high prices, missing values, extreme conditions)."""

import pytest
from src.engine.optimizer import ConstraintOptimizer
from src.engine.risk_engine import RiskEngine
from src.engine.what_if import WhatIfSimulator
from src.engine.explainer import RecommendationExplainer

def test_zero_budget():
    opt = ConstraintOptimizer()
    plan = opt.optimize_purchase_plan(
        budget=0.0,
        inventory={"tomato": 5.0, "onion": 3.0, "potato": 8.0},
        prices={"tomato": 24.0, "onion": 28.0, "potato": 18.0},
        retail_prices={"tomato": 35.0, "onion": 38.0, "potato": 24.0},
        demands={"tomato": 20.0, "onion": 25.0, "potato": 30.0}
    )
    assert plan["total_investment"] == 0.0
    assert plan["remaining_cash"] == 0.0
    for item in plan["recommendations"]:
        assert item["recommended_purchase_kg"] == 0.0

def test_minimal_budget():
    opt = ConstraintOptimizer()
    plan = opt.optimize_purchase_plan(
        budget=15.0, # Cannot even buy 1kg onion (₹28)
        inventory={"tomato": 0.0, "onion": 0.0, "potato": 0.0},
        prices={"tomato": 24.0, "onion": 28.0, "potato": 18.0},
        retail_prices={"tomato": 35.0, "onion": 38.0, "potato": 24.0},
        demands={"tomato": 20.0, "onion": 25.0, "potato": 30.0}
    )
    assert plan["total_investment"] <= 15.0
    assert plan["remaining_cash"] >= 0.0

def test_zero_inventory():
    opt = ConstraintOptimizer()
    plan = opt.optimize_purchase_plan(
        budget=2000.0,
        inventory={"tomato": 0.0, "onion": 0.0, "potato": 0.0},
        prices={"tomato": 24.0, "onion": 28.0, "potato": 18.0},
        retail_prices={"tomato": 35.0, "onion": 38.0, "potato": 24.0},
        demands={"tomato": 20.0, "onion": 25.0, "potato": 30.0}
    )
    assert plan["total_investment"] <= 2000.0
    assert plan["total_investment"] > 500.0

def test_extreme_price_spike():
    opt = ConstraintOptimizer()
    # Tomato price jumps to ₹120/kg
    plan = opt.optimize_purchase_plan(
        budget=2000.0,
        inventory={"tomato": 2.0, "onion": 5.0, "potato": 5.0},
        prices={"tomato": 120.0, "onion": 25.0, "potato": 18.0},
        retail_prices={"tomato": 140.0, "onion": 35.0, "potato": 25.0},
        demands={"tomato": 15.0, "onion": 25.0, "potato": 30.0}
    )
    assert plan["total_investment"] <= 2000.0
    # Tomato allocation should be severely reduced
    tomato_rec = next(r for r in plan["recommendations"] if r["product"] == "tomato")
    assert tomato_rec["recommended_purchase_kg"] < 10.0

def test_bilingual_explainer_no_crashes():
    opt = ConstraintOptimizer()
    risk = RiskEngine()
    exp = RecommendationExplainer()

    plan = opt.optimize_purchase_plan(
        budget=2000.0,
        inventory={"tomato": 5.0, "onion": 3.0, "potato": 8.0},
        prices={"tomato": 24.0, "onion": 28.0, "potato": 18.0},
        retail_prices={"tomato": 35.0, "onion": 38.0, "potato": 24.0},
        demands={"tomato": 20.0, "onion": 25.0, "potato": 30.0}
    )
    risk_eval = risk.evaluate_risk(plan)

    exp_en = exp.generate_explanation(plan, risk_eval, language="en")
    exp_hi = exp.generate_explanation(plan, risk_eval, language="hi")

    assert len(exp_en["summary_en"]) > 20
    assert len(exp_hi["summary_hi"]) > 20
    assert len(exp_en["product_reasons_en"]) == 3
    assert len(exp_hi["product_reasons_hi"]) == 3
