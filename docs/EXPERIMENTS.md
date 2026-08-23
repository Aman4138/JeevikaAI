# JeevikaAI — Experimental Results & Model Evaluation

This document outlines the machine learning benchmarks, time-series validation setup, and evaluation metrics comparing baseline models against gradient boosting estimators.

---

## 1. Experimental Setup

- **Temporal Split**: Time-aware train/test partition (earlier 80% date-sorted records for training, most recent 20% for out-of-time evaluation).
- **Leakage Prevention**: All rolling averages, trends, and lags strictly computed using shifted past observations (`t-1`, `t-7`, `t-14`).
- **Target Variables**:
  1. `modal_price_rs_kg`: Mandi Wholesale Modal Price (₹/kg).
  2. `units_sold`: Estimated Daily Retail Vendor Demand Signal (kg/day).

---

## 2. Wholesale Price Forecasting Benchmark

| Metric | Linear Regression Baseline | Gradient Boosting Regressor (Improved) | Improvement |
| :--- | :--- | :--- | :--- |
| **$R^2$ Score** | **0.899** | **0.928** | **+2.9%** |
| **MAE (₹/kg)** | **₹2.135** | **₹1.852** | **-13.3% lower error** |
| **RMSE (₹/kg)** | **₹3.106** | **₹2.620** | **-15.6% lower error** |
| **MAPE (%)** | **8.15%** | **7.06%** | **-1.09%** |

### Top Predictive Features (Wholesale Price):
1. `price_lag_1d` (Previous day modal price)
2. `price_rolling_mean_7d` (7-day moving average trend)
3. `month` (Agricultural harvest seasonality)
4. `arrivals_rolling_mean_7d` (Supply-side volume buffer)

---

## 3. Retail Demand Estimation Benchmark

| Metric | Linear Regression Baseline | Gradient Boosting Regressor (Improved) | Improvement |
| :--- | :--- | :--- | :--- |
| **$R^2$ Score** | **0.664** | **0.670** | **+0.6%** |
| **MAE (kg/day)** | **2.719 kg** | **2.710 kg** | **-0.3% lower error** |
| **RMSE (kg/day)** | **3.475 kg** | **3.446 kg** | **-0.8% lower error** |
| **MAPE (%)** | **9.73%** | **9.69%** | **-0.04%** |

### Top Predictive Features (Retail Demand Signal):
1. `sales_rolling_mean_7d` (Recent consumer purchasing momentum)
2. `sales_lag_1d` (Previous day retail sales)
3. `is_weekend` (Saturday/Sunday footfall surge)
4. `price_per_kg` (Retail price elasticity)
5. `precipitation_mm` (Monsoon rain footfall damper)
