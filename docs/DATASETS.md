# JeevikaAI — Dataset Integration & Strategy

JeevikaAI integrates three foundational agricultural and meteorological datasets to provide constraint-aware decision support for small vegetable and street vendors in India.

---

## 1. Primary Datasets

### Dataset 1: India Commodity Wise Mandi Dataset
- **Source**: [Kaggle — India Commodity Wise Mandi Dataset](https://www.kaggle.com/datasets/vandeetshah/india-commodity-wise-mandi-dataset) (Agmarknet / Ministry of Agriculture & Farmers Welfare, Govt of India)
- **License**: Open Data / CC BY 4.0
- **Purpose**: Wholesale Mandi Price Signals & Daily Supply Arrivals.
- **Key Columns**:
  - `State`, `District`, `Market` (Mandi Hub)
  - `Commodity`, `Variety`, `Group`
  - `Arrivals (Tonnes)`: Supply-side volume signal.
  - `Min_Price`, `Max_Price`, `Modal_Price` (in Rs./Quintal; normalized by JeevikaAI to Rs./kg).
  - `Reported Date`

### Dataset 2: Agricultural Products Sales Data 2022–2023
- **Source**: [Kaggle — Agricultural Products Sales Data](https://www.kaggle.com/datasets/kdstoys/agricultural-products-sales-data-2022-2023)
- **License**: CC0 Public Domain
- **Purpose**: Retail Vendor Sales Signals & Demand Pattern Estimation.
- **Key Columns**:
  - `Product`, `Category`
  - `Price_per_KG` (Retail consumer price)
  - `Units_Shipped`, `Units_Sold`, `Units_on_Hand` (Daily volume signals)
  - `Supplier_Location`, `Date`

### Dataset 3: Historical Weather Data for Indian Cities (1990–2022)
- **Source**: [Kaggle — Weather Data Indian Cities](https://www.kaggle.com/datasets/vanvalkenberg/historicalweatherdataforindiancities)
- **License**: CC BY-SA 4.0
- **Purpose**: Weather Impact & Footfall Disruption Context.
- **Key Columns**:
  - `City`, `Date`
  - `Temperature_C` (°C)
  - `Precipitation_mm` (Rainfall in mm)
  - `Rain_Indicator` (Binary heavy rain flag)

---

## 2. Data Integration Strategy (Zero False Fabrication)

> [!IMPORTANT]
> **No Blind Joins or Fabricated Rows**:
> 1. Mandi arrivals reflect wholesale market supply volume, **NOT** retail consumer demand.
> 2. Retail sales records reflect street sales demand patterns, **NOT** mandi inventory.
> 3. Therefore, JeevikaAI does not force an artificial 1-to-1 join across mismatched entities. Instead, we use a **modular multi-signal feature pipeline**:
>    - **Price Forecasting Pipeline** trains on Mandi price trends + lagged arrivals + regional seasonal indicators.
>    - **Demand Estimation Pipeline** trains on retail sales velocity + day-of-week surges + price elasticity + weather dampers.
>    - Both ML models feed structured numerical predictions into the **Deterministic Optimization Engine**.

---

## 3. Data Cleaning & Unit Standardization

| Raw Field | Original Unit | Standardized Unit | Transformation Rule |
| :--- | :--- | :--- | :--- |
| `Modal_Price` | Rs. / Quintal | **Rs. / kg (₹/kg)** | `modal_price_rs_quintal / 100.0` |
| `Arrivals` | Tonnes / Quintal | **Metric Tonnes** | Normalized to Metric Tonnes |
| `Units_Sold` | Units / Crates | **Kilograms (kg)** | Calibrated to daily vendor kg demand |
| `Date` | Mixed formats | **ISO 8601 (YYYY-MM-DD)** | `pd.to_datetime()` |
| `Commodity` | Mixed strings | **Normalized MVP Key** | `tomato`, `onion`, `potato` |

---

## 4. File Placement Guide

If running on a new machine with the raw Kaggle CSV files, place them in `data/raw/`:
```
jeevika-ai/
└── data/
    └── raw/
        ├── India_Commodity_Wise_Mandi_Dataset.csv
        ├── Agricultural_Products_Sales_Data_2022_2023.csv
        └── Historical_Weather_Data_Indian_Cities.csv
```
*Note: If raw files are not detected, JeevikaAI automatically initializes a Kaggle-schema compliant benchmark historical dataset.*
