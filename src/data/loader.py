"""Data loader module for discovering and loading raw datasets."""

import os
from pathlib import Path
from typing import Dict, Tuple, Optional
import pandas as pd
from src.utils.logger import logger
from src.config import get_path
from src.data.schemas import MANDI_SCHEMA, SALES_SCHEMA, WEATHER_SCHEMA
from src.data.bootstrap import generate_benchmark_datasets

def find_dataset_file(raw_dir: Path, keywords: list[str]) -> Optional[Path]:
    """Find CSV file matching keywords."""
    if not raw_dir.exists():
        return None
    for file in raw_dir.glob("*.csv"):
        name_lower = file.name.lower()
        if any(kw in name_lower for kw in keywords):
            return file
    return None

def normalize_columns(df: pd.DataFrame, alias_map: Dict[str, str]) -> pd.DataFrame:
    """Normalize DataFrame column names according to alias mapping."""
    rename_dict = {}
    for col in df.columns:
        clean_col = str(col).strip()
        if clean_col in alias_map:
            rename_dict[col] = alias_map[clean_col]
        else:
            # Fallback: snake_case lowercase
            normalized = clean_col.lower().replace(" ", "_").replace(".", "").replace("/", "_").replace("(", "").replace(")", "")
            rename_dict[col] = normalized
    return df.rename(columns=rename_dict)

def load_raw_datasets(raw_dir: Optional[Path] = None, auto_bootstrap: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load raw Mandi, Sales, and Weather datasets.
    If raw files are missing and auto_bootstrap is True, generates Kaggle-schema compliant benchmark data.
    """
    if raw_dir is None:
        raw_dir = get_path("raw_data_dir")

    # Look for files
    mandi_path = find_dataset_file(raw_dir, ["mandi", "commodity", "agmarknet"])
    sales_path = find_dataset_file(raw_dir, ["sales", "agricultural", "products_sales"])
    weather_path = find_dataset_file(raw_dir, ["weather", "temperature", "climate"])

    if (mandi_path is None or sales_path is None or weather_path is None) and auto_bootstrap:
        logger.info("Raw dataset files not fully detected. Bootstrapping benchmark historical dataset...")
        generate_benchmark_datasets(raw_dir)
        mandi_path = find_dataset_file(raw_dir, ["mandi", "commodity"])
        sales_path = find_dataset_file(raw_dir, ["sales", "agricultural"])
        weather_path = find_dataset_file(raw_dir, ["weather", "temperature"])

    if mandi_path is None or not mandi_path.exists():
        raise FileNotFoundError(f"Mandi dataset not found in {raw_dir}. Please place mandi CSV here.")
    if sales_path is None or not sales_path.exists():
        raise FileNotFoundError(f"Sales dataset not found in {raw_dir}. Please place sales CSV here.")
    if weather_path is None or not weather_path.exists():
        raise FileNotFoundError(f"Weather dataset not found in {raw_dir}. Please place weather CSV here.")

    logger.info("Loading Mandi data from: %s", mandi_path.name)
    df_mandi = pd.read_csv(mandi_path, low_memory=False)
    df_mandi = normalize_columns(df_mandi, MANDI_SCHEMA["raw_column_aliases"])

    logger.info("Loading Sales data from: %s", sales_path.name)
    df_sales = pd.read_csv(sales_path, low_memory=False)
    df_sales = normalize_columns(df_sales, SALES_SCHEMA["raw_column_aliases"])

    logger.info("Loading Weather data from: %s", weather_path.name)
    df_weather = pd.read_csv(weather_path, low_memory=False)
    df_weather = normalize_columns(df_weather, WEATHER_SCHEMA["raw_column_aliases"])

    return df_mandi, df_sales, df_weather
