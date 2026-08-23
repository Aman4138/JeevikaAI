"""Schema definitions and column expectations for the 3 Kaggle datasets."""

from typing import Dict, List

# Dataset 1: India Commodity Wise Mandi Dataset (Agmarknet / Kaggle)
MANDI_SCHEMA = {
    "required_columns": [
        "state",
        "district",
        "market",
        "commodity",
        "variety",
        "group",
        "arrivals_tonnes",
        "min_price_rs_quintal",
        "max_price_rs_quintal",
        "modal_price_rs_quintal",
        "reported_date"
    ],
    "raw_column_aliases": {
        "State": "state",
        "District": "district",
        "Market": "market",
        "Market Name": "market",
        "Commodity": "commodity",
        "Variety": "variety",
        "Group": "group",
        "Arrivals (Tonnes)": "arrivals_tonnes",
        "Arrivals": "arrivals_tonnes",
        "Min_Price": "min_price_rs_quintal",
        "Min Price (Rs./Quintal)": "min_price_rs_quintal",
        "Min Price": "min_price_rs_quintal",
        "Max_Price": "max_price_rs_quintal",
        "Max Price (Rs./Quintal)": "max_price_rs_quintal",
        "Max Price": "max_price_rs_quintal",
        "Modal_Price": "modal_price_rs_quintal",
        "Modal Price (Rs./Quintal)": "modal_price_rs_quintal",
        "Modal Price": "modal_price_rs_quintal",
        "Reported Date": "reported_date",
        "Date": "reported_date",
        "Arrival_Date": "reported_date"
    }
}

# Dataset 2: Agricultural Products Sales Data 2022–2023 (Kaggle)
SALES_SCHEMA = {
    "required_columns": [
        "product",
        "category",
        "price_per_kg",
        "units_shipped",
        "units_sold",
        "units_on_hand",
        "supplier_location",
        "date"
    ],
    "raw_column_aliases": {
        "Product": "product",
        "Product Name": "product",
        "Category": "category",
        "Price per KG": "price_per_kg",
        "Price_per_KG": "price_per_kg",
        "Price": "price_per_kg",
        "Units Shipped": "units_shipped",
        "Units_Shipped": "units_shipped",
        "Units Sold": "units_sold",
        "Units_Sold": "units_sold",
        "Units on Hand": "units_on_hand",
        "Units_on_Hand": "units_on_hand",
        "Supplier Location": "supplier_location",
        "Supplier_Location": "supplier_location",
        "Location": "supplier_location",
        "Date": "date",
        "Sale Date": "date"
    }
}

# Dataset 3: Weather Data Indian Cities 1990–2022 (Kaggle)
WEATHER_SCHEMA = {
    "required_columns": [
        "city",
        "date",
        "temperature_c",
        "precipitation_mm",
        "rain_indicator"
    ],
    "raw_column_aliases": {
        "City": "city",
        "city_name": "city",
        "Date": "date",
        "time": "date",
        "Temperature": "temperature_c",
        "tavg": "temperature_c",
        "Temperature_C": "temperature_c",
        "Precipitation": "precipitation_mm",
        "prcp": "precipitation_mm",
        "Precipitation_mm": "precipitation_mm",
        "Rain_Indicator": "rain_indicator"
    }
}

COMMODITY_MAPPING = {
    "tomato": ["tomato", "tomatoes", "tamatar", "local tomato", "hybrid tomato"],
    "onion": ["onion", "onions", "pyaz", "nasik onion", "red onion", "white onion"],
    "potato": ["potato", "potatoes", "aloo", "desi potato", "jyoti potato"]
}
