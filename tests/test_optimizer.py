"""Tests for Constraint-Aware Optimizer."""

import pytest
from src.engine.optimizer import ConstraintOptimizer

@pytest.fixture
def optimizer():
    return ConstraintOptimizer()

def test_hard_budget_constraint_enforcement(optimizer):
    budget = 2000.0
    inventory = {"tomato": 5.0, "onion": 3.0, "potato": 8.0}
    prices = {"tomato": 24.0, "onion": 28.0, "potato": 18.0}
    retails = {"tomato": 35.0, "onion": 38.0, "potato": 24.0}
    demands = {"tomato": 20.0, "onion": 25.0, "potato": 30.0}

    plan = optimizer.optimize_purchase_plan(
        budget=budget,
        inventory=inventory,
        prices=prices,
        retail_prices=retails,
        demands=demands,
        risk_profile="balanced"
    )

    # Core constraint checks
    assert plan["total_investment"] <= budget
    assert plan["remaining_cash"] >= 0.0
    assert plan["remaining_cash"] == round(budget - plan["total_investment"], 1)

    for item in plan["recommendations"]:
        assert item["recommended_purchase_kg"] >= 0.0
        assert item["estimated_purchase_cost"] == round(item["recommended_purchase_kg"] * item["wholesale_cost_per_kg"], 1)

def test_inventory_offsets_purchase(optimizer):
    # When vendor already has more inventory than demand, recommended purchase should be 0 kg
    budget = 2000.0
    inventory = {"tomato": 30.0, "onion": 30.0, "potato": 40.0} # high stock
    prices = {"tomato": 24.0, "onion": 28.0, "potato": 18.0}
    retails = {"tomato": 35.0, "onion": 38.0, "potato": 24.0}
    demands = {"tomato": 15.0, "onion": 20.0, "potato": 25.0} # lower demand

    plan = optimizer.optimize_purchase_plan(
        budget=budget,
        inventory=inventory,
        prices=prices,
        retail_prices=retails,
        demands=demands
    )

    for item in plan["recommendations"]:
        assert item["recommended_purchase_kg"] == 0.0
    assert plan["total_investment"] == 0.0
    assert plan["remaining_cash"] == budget
