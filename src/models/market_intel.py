"""Market Intelligence service for querying Mandi prices, arrivals, and supply trends."""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from src.utils.logger import logger
from src.config import get_path, get_commodities, get_locations

class MarketIntelligence:
    """Provides market signals, modal price history, and supply-side arrivals analysis."""

    def __init__(self, processed_dir: Optional[Path] = None):
        if processed_dir is None:
            processed_dir = get_path("processed_data_dir")
        self.processed_dir = processed_dir
        self.df_mandi: Optional[pd.DataFrame] = None
        self.df_sales: Optional[pd.DataFrame] = None
        self.df_weather: Optional[pd.DataFrame] = None
        self._load_data()

    def _load_data(self):
        mandi_path = self.processed_dir / "mandi_cleaned.csv"
        sales_path = self.processed_dir / "sales_cleaned.csv"
        weather_path = self.processed_dir / "weather_cleaned.csv"

        if mandi_path.exists():
            self.df_mandi = pd.read_csv(mandi_path)
            self.df_mandi["date"] = pd.to_datetime(self.df_mandi["date"])
        if sales_path.exists():
            self.df_sales = pd.read_csv(sales_path)
            self.df_sales["date"] = pd.to_datetime(self.df_sales["date"])
        if weather_path.exists():
            self.df_weather = pd.read_csv(weather_path)
            self.df_weather["date"] = pd.to_datetime(self.df_weather["date"])

    def get_market_summary(self, commodity: str, city_or_market: str = "Delhi") -> Dict[str, Any]:
        """Return comprehensive recent market signals for a commodity and market."""
        comm_clean = commodity.lower().strip()
        commodities = get_commodities()
        comm_meta = commodities.get(comm_clean, {})

        # Default fallback signals
        default_cost = comm_meta.get("default_wholesale_cost_per_kg", 24.0)
        default_retail = comm_meta.get("default_retail_price_per_kg", 35.0)

        summary = {
            "commodity": comm_clean,
            "display_name": comm_meta.get("display_name", commodity.capitalize()),
            "hindi_name": comm_meta.get("hindi_name", ""),
            "market_name": city_or_market,
            "latest_modal_price_rs_kg": default_cost,
            "min_price_rs_kg": round(default_cost * 0.88, 1),
            "max_price_rs_kg": round(default_cost * 1.12, 1),
            "estimated_retail_price_rs_kg": default_retail,
            "price_trend_pct_7d": 2.4,
            "price_trend_direction": "STABLE", # "RISING", "FALLING", "STABLE"
            "recent_arrivals_tonnes": 180.0,
            "arrivals_trend": "NORMAL", # "SURPLUS", "NORMAL", "TIGHT"
            "supply_signal": "Normal mandi supply volume; steady wholesale price.",
            "timeseries_14d": [],
            "weather": {
                "temperature_c": 28.5,
                "precipitation_mm": 0.0,
                "rain_risk": "LOW",
                "condition": "Clear Sky / Dry"
            }
        }

        if self.df_mandi is not None and not self.df_mandi.empty:
            mandi_sub = self.df_mandi[self.df_mandi["commodity_clean"] == comm_clean].copy()
            if not mandi_sub.empty:
                # Filter by market or city if possible
                market_match = mandi_sub[
                    mandi_sub["market"].str.contains(city_or_market, case=False, na=False) |
                    mandi_sub["district"].str.contains(city_or_market, case=False, na=False)
                ]
                if not market_match.empty:
                    mandi_sub = market_match

                mandi_sub = mandi_sub.sort_values(by="date")
                recent_14 = mandi_sub.tail(14)
                
                if len(recent_14) > 0:
                    latest_row = recent_14.iloc[-1]
                    summary["latest_modal_price_rs_kg"] = round(float(latest_row.get("modal_price_rs_kg", default_cost)), 1)
                    summary["min_price_rs_kg"] = round(float(latest_row.get("min_price_rs_kg", summary["latest_modal_price_rs_kg"] * 0.9)), 1)
                    summary["max_price_rs_kg"] = round(float(latest_row.get("max_price_rs_kg", summary["latest_modal_price_rs_kg"] * 1.1)), 1)
                    summary["recent_arrivals_tonnes"] = round(float(latest_row.get("arrivals_tonnes", 150.0)), 1)
                    summary["market_name"] = str(latest_row.get("market", city_or_market))

                    # 7-day trend
                    if len(recent_14) >= 7:
                        p_now = summary["latest_modal_price_rs_kg"]
                        p_7d_ago = float(recent_14.iloc[-7].get("modal_price_rs_kg", p_now))
                        trend_pct = round(((p_now - p_7d_ago) / max(1.0, p_7d_ago)) * 100.0, 1)
                        summary["price_trend_pct_7d"] = trend_pct
                        if trend_pct > 5.0:
                            summary["price_trend_direction"] = "RISING"
                        elif trend_pct < -5.0:
                            summary["price_trend_direction"] = "FALLING"
                        else:
                            summary["price_trend_direction"] = "STABLE"

                    # 14-day history for charts
                    timeseries = []
                    for _, row in recent_14.iterrows():
                        timeseries.append({
                            "date": row["date"].strftime("%b %d"),
                            "modal_price": round(float(row.get("modal_price_rs_kg", default_cost)), 1),
                            "min_price": round(float(row.get("min_price_rs_kg", default_cost * 0.9)), 1),
                            "max_price": round(float(row.get("max_price_rs_kg", default_cost * 1.1)), 1),
                            "arrivals": round(float(row.get("arrivals_tonnes", 100.0)), 1)
                        })
                    summary["timeseries_14d"] = timeseries

        # Retail price alignment
        if self.df_sales is not None and not self.df_sales.empty:
            sales_sub = self.df_sales[self.df_sales["product_clean"] == comm_clean]
            if not sales_sub.empty:
                latest_retail = sales_sub.sort_values(by="date").iloc[-1]
                summary["estimated_retail_price_rs_kg"] = round(float(latest_retail.get("price_per_kg", default_retail)), 1)

        # Weather integration
        if self.df_weather is not None and not self.df_weather.empty:
            weather_match = self.df_weather[self.df_weather["city"].str.contains(city_or_market, case=False, na=False)]
            if not weather_match.empty:
                latest_w = weather_match.sort_values(by="date").iloc[-1]
                t_c = round(float(latest_w.get("temperature_c", 28.0)), 1)
                prcp = round(float(latest_w.get("precipitation_mm", 0.0)), 1)
                is_rain = prcp > 2.0
                summary["weather"] = {
                    "temperature_c": t_c,
                    "precipitation_mm": prcp,
                    "rain_risk": "HIGH" if prcp > 15.0 else ("MEDIUM" if is_rain else "LOW"),
                    "condition": f"Rainfall ({prcp} mm)" if is_rain else f"Clear ({t_c}°C)"
                }

        return summary
