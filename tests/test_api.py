"""FastAPI Endpoint Integration Tests."""

import pytest
from starlette.testclient import TestClient
from src.api.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_products_endpoint(client):
    res = client.get("/api/products")
    assert res.status_code == 200
    products = res.json()
    assert len(products) == 3
    ids = [p["id"] for p in products]
    assert "tomato" in ids and "onion" in ids and "potato" in ids

def test_locations_endpoint(client):
    res = client.get("/api/locations")
    assert res.status_code == 200
    locs = res.json()
    assert len(locs) >= 3

def test_market_data_endpoint(client):
    res = client.get("/api/market-data?commodity=tomato&city=Delhi")
    assert res.status_code == 200
    data = res.json()
    assert data["commodity"] == "tomato"
    assert data["latest_modal_price_rs_kg"] > 0
    assert "timeseries_14d" in data

def test_model_metrics_endpoint(client):
    res = client.get("/api/model-metrics")
    assert res.status_code == 200
    metrics = res.json()
    assert "price_prediction_model" in metrics
    assert "demand_estimation_model" in metrics

def test_recommend_endpoint(client):
    payload = {
        "budget": 2000.0,
        "inventory": {"tomato": 5.0, "onion": 3.0, "potato": 8.0},
        "location": "Delhi",
        "risk_profile": "balanced",
        "language": "en"
    }
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_investment"] <= 2000.0
    assert data["remaining_cash"] >= 0.0
    assert len(data["recommendations"]) == 3
    assert data["risk_score"] >= 0
    assert "explanation" in data

def test_what_if_endpoint(client):
    payload = {
        "base_request": {
            "budget": 2000.0,
            "inventory": {"tomato": 5.0, "onion": 3.0, "potato": 8.0},
            "location": "Delhi",
            "risk_profile": "balanced",
            "language": "en"
        },
        "scenario_name": "Test Drop",
        "scenario_budget": 1500.0,
        "price_multipliers": {"tomato": 1.20},
        "demand_multipliers": {"all": 0.85}
    }
    res = client.post("/api/what-if", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "deltas" in data
    assert "baseline" in data
    assert "scenario" in data
    assert data["scenario"]["total_investment"] <= 1500.0
