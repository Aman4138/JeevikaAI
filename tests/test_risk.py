"""Tests for Risk Evaluation and Scoring Engine."""

import pytest
from src.engine.optimizer import ConstraintOptimizer
from src.engine.risk_engine import RiskEngine

def test_risk_scoring_bounds():
    opt = ConstraintOptimizer()
    risk = RiskEngine()

    plan = opt.optimize_purchase_plan(
        budget=2000.0,
        inventory={"tomato": 5.0, "onion": 3.0, "potato": 8.0},
        prices={"tomato": 24.0, "onion": 28.0, "potato": 18.0},
        retail_prices={"tomato": 35.0, "onion": 38.0, "potato": 24.0},
        demands={"tomato": 20.0, "onion": 25.0, "potato": 30.0}
    )

    eval_res = risk.evaluate_risk(plan)
    assert 0 <= eval_res["risk_score"] <= 100
    assert eval_res["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert len(eval_res["breakdown"]) == 4

def test_heavy_rain_risk_escalation():
    opt = ConstraintOptimizer()
    risk = RiskEngine()

    plan = opt.optimize_purchase_plan(
        budget=2000.0,
        inventory={"tomato": 5.0, "onion": 3.0, "potato": 8.0},
        prices={"tomato": 24.0, "onion": 28.0, "potato": 18.0},
        retail_prices={"tomato": 35.0, "onion": 38.0, "potato": 24.0},
        demands={"tomato": 20.0, "onion": 25.0, "potato": 30.0}
    )

    normal_risk = risk.evaluate_risk(plan, {"rain_risk": "LOW"})
    rain_risk = risk.evaluate_risk(plan, {"rain_risk": "HIGH"})

    assert rain_risk["risk_score"] > normal_risk["risk_score"]
