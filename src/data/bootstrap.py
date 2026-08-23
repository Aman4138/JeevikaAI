"""Bootstrap generator for Kaggle-schema compliant historical datasets."""

import os
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from src.utils.logger import logger
from src.config import get_path, get_locations, get_commodities

def generate_benchmark_datasets(raw_dir: Path = None, force: bool = False):
    """
    Generate realistic benchmark datasets matching exact Kaggle schemas
    covering 2022-01-01 to 2023-12-31 for Delhi, Mumbai, Bengaluru, Nashik, Agra.
    """
    if raw_dir is None:
        raw_dir = get_path("raw_data_dir")
    raw_dir.mkdir(parents=True, exist_ok=True)

    mandi_file = raw_dir / "India_Commodity_Wise_Mandi_Dataset.csv"
    sales_file = raw_dir / "Agricultural_Products_Sales_Data_2022_2023.csv"
    weather_file = raw_dir / "Historical_Weather_Data_Indian_Cities.csv"

    if not force and mandi_file.exists() and sales_file.exists() and weather_file.exists():
        logger.info("Raw datasets already present in %s", raw_dir)
        return

    logger.info("Generating Kaggle-schema compliant historical benchmark data in %s...", raw_dir)
    np.random.seed(42)

    # Date range: 2 years (2022-01-01 to 2023-12-31)
    dates = pd.date_range(start="2022-01-01", end="2023-12-31", freq="D")
    locations = get_locations()
    commodities = ["Tomato", "Onion", "Potato"]

    # 1. GENERATE WEATHER DATA
    weather_rows = []
    for loc in locations:
        city = loc["city"]
        for dt in dates:
            day_of_year = dt.dayofyear
            month = dt.month
            
            # Seasonal temperature simulation
            if city in ["Delhi", "Agra"]:
                # North India extreme seasons
                base_temp = 25.0 + 12.0 * np.sin(2 * np.pi * (day_of_year - 105) / 365.0)
            elif city in ["Mumbai", "Nashik"]:
                # Coastal / Deccan plateau
                base_temp = 28.0 + 5.0 * np.sin(2 * np.pi * (day_of_year - 80) / 365.0)
            else: # Bengaluru
                base_temp = 24.0 + 3.5 * np.sin(2 * np.pi * (day_of_year - 80) / 365.0)
                
            temp = float(np.clip(base_temp + np.random.normal(0, 1.8), 8.0, 46.0))
            
            # Monsoon precipitation (June - September)
            is_monsoon = month in [6, 7, 8, 9]
            if is_monsoon:
                prcp_prob = 0.45 if city in ["Mumbai", "Bengaluru"] else 0.30
                if np.random.rand() < prcp_prob:
                    prcp = float(np.random.exponential(scale=22.0 if city == "Mumbai" else 12.0))
                else:
                    prcp = 0.0
            else:
                prcp = float(np.random.exponential(scale=1.5)) if np.random.rand() < 0.05 else 0.0
                
            rain_indicator = 1 if prcp > 2.5 else 0
            
            weather_rows.append({
                "City": city,
                "Date": dt.strftime("%Y-%m-%d"),
                "Temperature_C": round(temp, 1),
                "Precipitation_mm": round(prcp, 1),
                "Rain_Indicator": rain_indicator
            })

    df_weather = pd.DataFrame(weather_rows)
    df_weather.to_csv(weather_file, index=False)
    logger.info("Saved %d weather records to %s", len(df_weather), weather_file)

    # 2. GENERATE MANDI DATASET
    # Prices in Rs./Quintal (1 Quintal = 100 kg)
    mandi_rows = []
    for loc in locations:
        state = loc["state"]
        market = loc["mandi_name"]
        district = loc["city"]
        
        for comm in commodities:
            if comm == "Tomato":
                base_modal_rs_kg = 22.0
                base_arrivals = 180.0
                variety = "Hybrid"
            elif comm == "Onion":
                base_modal_rs_kg = 26.0
                base_arrivals = 320.0
                variety = "Red Nasik"
            else: # Potato
                base_modal_rs_kg = 17.0
                base_arrivals = 400.0
                variety = "Jyoti Desi"

            for dt in dates:
                month = dt.month
                day_of_year = dt.dayofyear
                
                # Seasonality shocks
                seasonal_multiplier = 1.0
                if comm == "Tomato":
                    # Summer heat / Monsoon supply dip in July-August
                    if month in [6, 7, 8]:
                        seasonal_multiplier = 1.6 + 0.3 * np.sin(np.pi * (month - 6) / 3)
                    elif month in [12, 1, 2]:
                        seasonal_multiplier = 0.8  # Winter surplus
                elif comm == "Onion":
                    # Pre-Kharif lean season in September-November
                    if month in [9, 10, 11]:
                        seasonal_multiplier = 1.5 + 0.2 * np.sin(np.pi * (month - 9) / 3)
                    elif month in [3, 4, 5]:
                        seasonal_multiplier = 0.85 # Rabi harvest
                elif comm == "Potato":
                    # Post-monsoon / cold storage release
                    if month in [8, 9, 10]:
                        seasonal_multiplier = 1.25
                    elif month in [1, 2, 3]:
                        seasonal_multiplier = 0.85 # Fresh harvest

                # Daily fluctuation & inverse arrival elasticity
                noise = np.random.normal(0, 0.08)
                modal_kg = base_modal_rs_kg * seasonal_multiplier * (1.0 + noise)
                modal_kg = max(8.0, modal_kg)
                
                modal_quintal = round(modal_kg * 100.0, 1) # Rs. per Quintal
                min_quintal = round(modal_quintal * np.random.uniform(0.85, 0.95), 1)
                max_quintal = round(modal_quintal * np.random.uniform(1.05, 1.18), 1)
                
                # Arrivals inversely correlated with price shocks
                arrivals = base_arrivals * (1.0 / seasonal_multiplier) * np.random.uniform(0.75, 1.25)
                arrivals = round(max(20.0, arrivals), 1)

                mandi_rows.append({
                    "State": state,
                    "District": district,
                    "Market": market,
                    "Commodity": comm,
                    "Variety": variety,
                    "Group": "Vegetables",
                    "Arrivals (Tonnes)": arrivals,
                    "Min_Price": min_quintal,
                    "Max_Price": max_quintal,
                    "Modal_Price": modal_quintal,
                    "Reported Date": dt.strftime("%Y-%m-%d")
                })

    df_mandi = pd.DataFrame(mandi_rows)
    df_mandi.to_csv(mandi_file, index=False)
    logger.info("Saved %d mandi records to %s", len(df_mandi), mandi_file)

    # 3. GENERATE AG SALES DATASET (Vendor Demand & Stock Signals)
    sales_rows = []
    for loc in locations:
        city = loc["city"]
        for comm in commodities:
            if comm == "Tomato":
                base_sales_kg = 22.0
                base_price_kg = 32.0
            elif comm == "Onion":
                base_sales_kg = 28.0
                base_price_kg = 36.0
            else: # Potato
                base_sales_kg = 32.0
                base_price_kg = 24.0

            for dt in dates:
                day_of_week = dt.dayofweek
                month = dt.month
                
                # Weekend bump (+18% on Sat/Sun)
                is_weekend = 1.18 if day_of_week in [5, 6] else 1.0
                
                # Price markup over wholesale
                retail_price = round(base_price_kg * np.random.uniform(0.92, 1.12), 1)
                
                # Demand signal with price elasticity (-0.4)
                price_ratio = retail_price / base_price_kg
                demand_kg = base_sales_kg * is_weekend * (price_ratio ** -0.4) * np.random.normal(1.0, 0.12)
                units_sold = round(max(5.0, demand_kg), 1)
                
                units_shipped = round(units_sold * np.random.uniform(1.05, 1.35), 1)
                units_on_hand = round(max(2.0, units_shipped - units_sold + np.random.uniform(2.0, 8.0)), 1)

                sales_rows.append({
                    "Product": comm,
                    "Category": "Vegetables",
                    "Price_per_KG": retail_price,
                    "Units_Shipped": units_shipped,
                    "Units_Sold": units_sold,
                    "Units_on_Hand": units_on_hand,
                    "Supplier_Location": city,
                    "Date": dt.strftime("%Y-%m-%d")
                })

    df_sales = pd.DataFrame(sales_rows)
    df_sales.to_csv(sales_file, index=False)
    logger.info("Saved %d sales records to %s", len(df_sales), sales_file)
    logger.info("Historical benchmark dataset generation complete.")

if __name__ == "__main__":
    generate_benchmark_datasets()
