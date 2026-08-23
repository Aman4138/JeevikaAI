"""Tests for ML Price Forecasting and Demand Estimation."""

import pytest
import pandas as pd
from src.features.feature_engineering import build_price_features, build_demand_features
from src.data.preprocess import run_preprocessing_pipeline
from src.models.price_predictor import PricePredictor
from src.models.demand_estimator import DemandEstimator

@pytest.fixture(scope="module")
def processed_data():
    clean_mandi, clean_sales, clean_weather = run_preprocessing_pipeline(save=False)
    df_price_feats = build_price_features(clean_mandi, clean_weather)
    df_demand_feats = build_demand_features(clean_sales, clean_weather)
    return df_price_feats, df_demand_feats

def test_price_model_training_and_inference(processed_data):
    df_price_feats, _ = processed_data
    predictor = PricePredictor()
    metrics = predictor.train(df_price_feats)

    # Check metrics existence
    assert "baseline" in metrics
    assert "improved" in metrics
    assert metrics["improved"]["r2"] > 0.60
    assert metrics["improved"]["mae"] < 10.0

    # Test single-point inference
    pred = predictor.predict(commodity="tomato", market="Azadpur Mandi")
    assert isinstance(pred, float)
    assert pred > 5.0

def test_demand_model_training_and_inference(processed_data):
    _, df_demand_feats = processed_data
    estimator = DemandEstimator()
    metrics = estimator.train(df_demand_feats)

    assert "baseline" in metrics
    assert "improved" in metrics
    assert metrics["improved"]["r2"] > 0.50

    # Test inference
    est = estimator.estimate(commodity="onion", location="Delhi", retail_price=35.0)
    assert isinstance(est, float)
    assert est > 0.0
