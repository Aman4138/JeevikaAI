"""Feature engineering pipeline for Price Prediction and Demand Estimation."""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional
from src.utils.logger import logger

def add_temporal_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Extract calendar and seasonal features."""
    df = df.copy()
    dt = pd.to_datetime(df[date_col])
    
    df["day"] = dt.dt.day
    df["day_of_week"] = dt.dt.dayofweek
    df["month"] = dt.dt.month
    df["year"] = dt.dt.year
    df["week_of_year"] = dt.dt.isocalendar().week.astype(int)
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Indian Agricultural Seasons
    # Kharif / Monsoon: Jun-Sep (6,7,8,9)
    # Rabi / Winter: Oct-Mar (10,11,12,1,2,3)
    # Zaid / Summer: Apr-May (4,5)
    df["season_monsoon"] = df["month"].isin([6, 7, 8, 9]).astype(int)
    df["season_winter"] = df["month"].isin([10, 11, 12, 1, 2, 3]).astype(int)
    df["season_summer"] = df["month"].isin([4, 5]).astype(int)

    return df

def build_price_features(df_mandi: pd.DataFrame, df_weather: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Build leak-free time-series features for Mandi Wholesale Price prediction.
    Target: modal_price_rs_kg (or 1-day ahead modal_price_rs_kg).
    """
    df = df_mandi.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by=["commodity_clean", "market", "date"]).reset_index(drop=True)

    # Group by commodity and market for time-series feature engineering
    feature_dfs = []
    for (comm, market), group in df.groupby(["commodity_clean", "market"]):
        group = group.copy().sort_values(by="date")
        
        # Base price series
        price = group["modal_price_rs_kg"]
        arrivals = group["arrivals_tonnes"] if "arrivals_tonnes" in group.columns else pd.Series(0, index=group.index)

        # Lag features strictly shifting past values (No data leakage!)
        group["price_lag_1d"] = price.shift(1)
        group["price_lag_2d"] = price.shift(2)
        group["price_lag_7d"] = price.shift(7)

        # Rolling statistics strictly on shifted data
        group["price_rolling_mean_7d"] = price.shift(1).rolling(window=7, min_periods=1).mean()
        group["price_rolling_mean_14d"] = price.shift(1).rolling(window=14, min_periods=1).mean()
        group["price_rolling_std_7d"] = price.shift(1).rolling(window=7, min_periods=1).std().fillna(0.0)
        
        # Price trend momentum
        group["price_trend_7d_14d"] = (
            (group["price_rolling_mean_7d"] - group["price_rolling_mean_14d"]) /
            (group["price_rolling_mean_14d"] + 1e-5)
        )

        # Supply / Arrival features
        group["arrivals_lag_1d"] = arrivals.shift(1)
        group["arrivals_rolling_mean_7d"] = arrivals.shift(1).rolling(window=7, min_periods=1).mean()

        feature_dfs.append(group)

    df_featured = pd.concat(feature_dfs, ignore_index=True)
    df_featured = add_temporal_features(df_featured, date_col="date")

    # Merge weather signals if available
    if df_weather is not None and not df_weather.empty:
        df_weather = df_weather.copy()
        df_weather["date"] = pd.to_datetime(df_weather["date"])
        
        # Join by district/city or date
        if "district" in df_featured.columns and "city" in df_weather.columns:
            weather_subset = df_weather[["city", "date", "temperature_c", "precipitation_mm", "rain_indicator"]].drop_duplicates(subset=["city", "date"])
            df_featured = df_featured.merge(
                weather_subset,
                left_on=["district", "date"],
                right_on=["city", "date"],
                how="left"
            )
        else:
            # Fallback: date aggregate
            weather_daily = df_weather.groupby("date")[["temperature_c", "precipitation_mm", "rain_indicator"]].mean().reset_index()
            df_featured = df_featured.merge(weather_daily, on="date", how="left")

    # Impute initial NaNs from shifting with backwards/median fill
    df_featured["price_lag_1d"] = df_featured["price_lag_1d"].fillna(df_featured["modal_price_rs_kg"])
    df_featured["price_lag_2d"] = df_featured["price_lag_2d"].fillna(df_featured["price_lag_1d"])
    df_featured["price_lag_7d"] = df_featured["price_lag_7d"].fillna(df_featured["price_lag_1d"])
    df_featured["price_rolling_mean_7d"] = df_featured["price_rolling_mean_7d"].fillna(df_featured["modal_price_rs_kg"])
    df_featured["price_rolling_mean_14d"] = df_featured["price_rolling_mean_14d"].fillna(df_featured["modal_price_rs_kg"])
    df_featured["price_rolling_std_7d"] = df_featured["price_rolling_std_7d"].fillna(0.0)
    df_featured["price_trend_7d_14d"] = df_featured["price_trend_7d_14d"].fillna(0.0)
    df_featured["arrivals_lag_1d"] = df_featured["arrivals_lag_1d"].fillna(df_featured["arrivals_tonnes"])
    df_featured["arrivals_rolling_mean_7d"] = df_featured["arrivals_rolling_mean_7d"].fillna(df_featured["arrivals_tonnes"])

    # Fill weather missing values gracefully
    if "temperature_c" in df_featured.columns:
        df_featured["temperature_c"] = df_featured["temperature_c"].fillna(28.0)
    if "precipitation_mm" in df_featured.columns:
        df_featured["precipitation_mm"] = df_featured["precipitation_mm"].fillna(0.0)
    if "rain_indicator" in df_featured.columns:
        df_featured["rain_indicator"] = df_featured["rain_indicator"].fillna(0)

    return df_featured

def build_demand_features(df_sales: pd.DataFrame, df_weather: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Build leak-free time-series features for Retail Vendor Demand estimation.
    Target: units_sold (estimated demand signal).
    """
    df = df_sales.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by=["product_clean", "supplier_location", "date"]).reset_index(drop=True)

    feature_dfs = []
    for (prod, loc), group in df.groupby(["product_clean", "supplier_location"]):
        group = group.copy().sort_values(by="date")
        
        sold = group["units_sold"]
        price = group["price_per_kg"]
        stock = group["units_on_hand"] if "units_on_hand" in group.columns else pd.Series(0, index=group.index)

        # Lag features (No data leakage)
        group["sales_lag_1d"] = sold.shift(1)
        group["sales_lag_2d"] = sold.shift(2)
        group["sales_lag_7d"] = sold.shift(7)

        # Rolling means & volatility
        group["sales_rolling_mean_7d"] = sold.shift(1).rolling(window=7, min_periods=1).mean()
        group["sales_rolling_mean_14d"] = sold.shift(1).rolling(window=14, min_periods=1).mean()
        group["sales_rolling_std_7d"] = sold.shift(1).rolling(window=7, min_periods=1).std().fillna(0.0)

        # Price ratio compared to rolling 14d price
        price_rolling = price.shift(1).rolling(window=14, min_periods=1).mean()
        group["price_ratio_to_14d_avg"] = price / (price_rolling + 1e-5)

        # Lagged stock on hand
        group["stock_lag_1d"] = stock.shift(1)

        feature_dfs.append(group)

    df_featured = pd.concat(feature_dfs, ignore_index=True)
    df_featured = add_temporal_features(df_featured, date_col="date")

    # Merge weather signals if available
    if df_weather is not None and not df_weather.empty:
        df_weather = df_weather.copy()
        df_weather["date"] = pd.to_datetime(df_weather["date"])
        
        weather_subset = df_weather[["city", "date", "temperature_c", "precipitation_mm", "rain_indicator"]].drop_duplicates(subset=["city", "date"])
        df_featured = df_featured.merge(
            weather_subset,
            left_on=["supplier_location", "date"],
            right_on=["city", "date"],
            how="left"
        )

    # Impute initial NaNs
    df_featured["sales_lag_1d"] = df_featured["sales_lag_1d"].fillna(df_featured["units_sold"])
    df_featured["sales_lag_2d"] = df_featured["sales_lag_2d"].fillna(df_featured["sales_lag_1d"])
    df_featured["sales_lag_7d"] = df_featured["sales_lag_7d"].fillna(df_featured["sales_lag_1d"])
    df_featured["sales_rolling_mean_7d"] = df_featured["sales_rolling_mean_7d"].fillna(df_featured["units_sold"])
    df_featured["sales_rolling_mean_14d"] = df_featured["sales_rolling_mean_14d"].fillna(df_featured["units_sold"])
    df_featured["sales_rolling_std_7d"] = df_featured["sales_rolling_std_7d"].fillna(0.0)
    df_featured["price_ratio_to_14d_avg"] = df_featured["price_ratio_to_14d_avg"].fillna(1.0)
    df_featured["stock_lag_1d"] = df_featured["stock_lag_1d"].fillna(10.0)

    if "temperature_c" in df_featured.columns:
        df_featured["temperature_c"] = df_featured["temperature_c"].fillna(28.0)
    if "precipitation_mm" in df_featured.columns:
        df_featured["precipitation_mm"] = df_featured["precipitation_mm"].fillna(0.0)
    if "rain_indicator" in df_featured.columns:
        df_featured["rain_indicator"] = df_featured["rain_indicator"].fillna(0)

    return df_featured
