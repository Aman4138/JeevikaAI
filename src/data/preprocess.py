"""Data preprocessing and standardization pipeline."""

import os
from pathlib import Path
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd

from src.utils.logger import logger
from src.config import get_path, get_commodities
from src.data.schemas import COMMODITY_MAPPING
from src.data.loader import load_raw_datasets

def match_commodity_name(raw_name: str) -> str:
    """Map arbitrary commodity string to canonical MVP commodity ('tomato', 'onion', 'potato', or 'other')."""
    if not isinstance(raw_name, str):
        return "other"
    s = raw_name.strip().lower()
    for canonical, aliases in COMMODITY_MAPPING.items():
        if any(alias in s for alias in aliases):
            return canonical
    return "other"

def preprocess_mandi_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean, standardize, and unit-convert Mandi dataset.
    Converts Rs./Quintal -> Rs./kg (divide by 100.0).
    """
    df = df.copy()

    # Normalize commodity
    if "commodity" in df.columns:
        df["commodity_clean"] = df["commodity"].apply(match_commodity_name)
    else:
        df["commodity_clean"] = "other"

    # Filter MVP commodities
    df = df[df["commodity_clean"].isin(["tomato", "onion", "potato"])].copy()

    # Parse dates
    df["date"] = pd.to_datetime(df["reported_date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values(by=["commodity_clean", "market", "date"]).reset_index(drop=True)

    # Unit conversions: Rs/Quintal -> Rs/kg
    for price_col in ["modal_price_rs_quintal", "min_price_rs_quintal", "max_price_rs_quintal"]:
        if price_col in df.columns:
            df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
            new_col = price_col.replace("_rs_quintal", "_rs_kg")
            df[new_col] = df[price_col] / 100.0

    # Fallback if modal_price_rs_kg is missing
    if "modal_price_rs_kg" not in df.columns and "modal_price" in df.columns:
        df["modal_price"] = pd.to_numeric(df["modal_price"], errors="coerce")
        # If > 200, assume quintal, else kg
        df["modal_price_rs_kg"] = np.where(df["modal_price"] > 200, df["modal_price"] / 100.0, df["modal_price"])

    # Handle arrivals
    if "arrivals_tonnes" in df.columns:
        df["arrivals_tonnes"] = pd.to_numeric(df["arrivals_tonnes"], errors="coerce").fillna(0.0)
    else:
        df["arrivals_tonnes"] = 0.0

    # Remove duplicates
    subset_cols = ["date", "market", "commodity_clean"]
    subset_cols = [c for c in subset_cols if c in df.columns]
    df = df.drop_duplicates(subset=subset_cols, keep="last")

    # Outlier clipping on price: Rs. 3/kg to Rs. 200/kg
    if "modal_price_rs_kg" in df.columns:
        df["modal_price_rs_kg"] = df["modal_price_rs_kg"].clip(lower=3.0, upper=200.0)

    return df

def preprocess_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize Agricultural Products Sales dataset."""
    df = df.copy()

    # Normalize product
    if "product" in df.columns:
        df["product_clean"] = df["product"].apply(match_commodity_name)
    else:
        df["product_clean"] = "other"

    # Filter MVP commodities
    df = df[df["product_clean"].isin(["tomato", "onion", "potato"])].copy()

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values(by=["product_clean", "supplier_location", "date"]).reset_index(drop=True)

    # Numeric columns
    for num_col in ["price_per_kg", "units_sold", "units_shipped", "units_on_hand"]:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce").clip(lower=0.0)

    # Remove duplicates
    subset_cols = ["date", "supplier_location", "product_clean"]
    subset_cols = [c for c in subset_cols if c in df.columns]
    df = df.drop_duplicates(subset=subset_cols, keep="last")

    return df

def preprocess_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize Indian Cities Weather dataset."""
    df = df.copy()

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values(by=["city", "date"]).reset_index(drop=True)

    if "temperature_c" in df.columns:
        df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="coerce").clip(lower=-5.0, upper=55.0)
    if "precipitation_mm" in df.columns:
        df["precipitation_mm"] = pd.to_numeric(df["precipitation_mm"], errors="coerce").clip(lower=0.0, upper=500.0)

    if "rain_indicator" not in df.columns and "precipitation_mm" in df.columns:
        df["rain_indicator"] = (df["precipitation_mm"] > 2.0).astype(int)

    df = df.drop_duplicates(subset=["city", "date"], keep="last")
    return df

def run_preprocessing_pipeline(save: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Execute complete data loading and preprocessing pipeline."""
    logger.info("Starting data loading and preprocessing pipeline...")
    raw_mandi, raw_sales, raw_weather = load_raw_datasets()

    clean_mandi = preprocess_mandi_data(raw_mandi)
    clean_sales = preprocess_sales_data(raw_sales)
    clean_weather = preprocess_weather_data(raw_weather)

    if save:
        proc_dir = get_path("processed_data_dir")
        proc_dir.mkdir(parents=True, exist_ok=True)
        
        mandi_out = proc_dir / "mandi_cleaned.csv"
        sales_out = proc_dir / "sales_cleaned.csv"
        weather_out = proc_dir / "weather_cleaned.csv"

        clean_mandi.to_csv(mandi_out, index=False)
        clean_sales.to_csv(sales_out, index=False)
        clean_weather.to_csv(weather_out, index=False)
        logger.info("Saved processed datasets to %s", proc_dir)

    logger.info("Mandi Cleaned records: %d", len(clean_mandi))
    logger.info("Sales Cleaned records: %d", len(clean_sales))
    logger.info("Weather Cleaned records: %d", len(clean_weather))

    return clean_mandi, clean_sales, clean_weather

if __name__ == "__main__":
    run_preprocessing_pipeline()
