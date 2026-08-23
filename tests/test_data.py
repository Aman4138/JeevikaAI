"""Tests for Data Ingestion and Preprocessing Pipeline."""

import pytest
import pandas as pd
from pathlib import Path
from src.data.loader import load_raw_datasets
from src.data.preprocess import (
    run_preprocessing_pipeline,
    preprocess_mandi_data,
    preprocess_sales_data,
    preprocess_weather_data,
    match_commodity_name
)

def test_commodity_name_matching():
    assert match_commodity_name("Tomato Hybrid") == "tomato"
    assert match_commodity_name("Red Onion") == "onion"
    assert match_commodity_name("Jyoti Potato") == "potato"
    assert match_commodity_name("Random Fruit") == "other"

def test_data_loading_and_preprocessing():
    # Execute full preprocessing pipeline
    clean_mandi, clean_sales, clean_weather = run_preprocessing_pipeline(save=False)

    assert not clean_mandi.empty
    assert not clean_sales.empty
    assert not clean_weather.empty

    # Verify unit conversion in Mandi: Rs/Quintal -> Rs/kg
    assert "modal_price_rs_kg" in clean_mandi.columns
    # Check that Rs/kg values are realistic (e.g. between 3 and 200)
    assert (clean_mandi["modal_price_rs_kg"] >= 3.0).all()
    assert (clean_mandi["modal_price_rs_kg"] <= 200.0).all()

    # Verify MVP commodities filtered
    assert set(clean_mandi["commodity_clean"].unique()).issubset({"tomato", "onion", "potato"})
    assert set(clean_sales["product_clean"].unique()).issubset({"tomato", "onion", "potato"})
