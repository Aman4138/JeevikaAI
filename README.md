# 🥬 JeevikaAI — AI for Public Good

> **Constraint-Aware AI Decision Making for Indian Street & Vegetable Vendors**  
> *A production-ready Hackathon Prototype built for unserved micro-retailers in India.*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg?style=flat&logo=scikit-learn)](https://scikit-learn.org)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📌 1. Problem Context

In India, millions of street and vegetable vendors operate on thin daily margins with strict cash boundaries (typically ₹500 to ₹5,000). Every morning at 5:00 AM, they must answer six high-stakes questions:
1. **What should I buy today?**
2. **How much should I buy?**
3. **How should I allocate my limited budget?**
4. **What happens if wholesale prices surge?**
5. **What happens if customer demand slumps?**
6. **What if rain hits and vegetables rot?**

### The Core Novelty: Constraint-Aware AI Decision Making
Generic LLM chatbots fail micro-vendors because they hallucinate quantities, ignore hard budget ceilings, and lack real mandi wholesale price context. 

**JeevikaAI** replaces random AI suggestions with **deterministic, mathematically-bounded optimization** that strictly respects vendor constraints:
- **Available Budget**: Total purchasing spend $\sum c_i q_i$ never exceeds available capital $B$.
- **Current Inventory**: Automatically subtracts existing morning stock $I_i$.
- **Perishability Penalties**: Heavily penalizes excess purchase of short shelf-life items (e.g. Tomatoes: 2–3 days) to eliminate waste.
- **Explainable Grounding**: Generates transparent, rule-backed explanations in **English** and **Hindi (हिंदी)**.

---

## 🏗️ 2. System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         JEEVIKA AI ARCHITECTURE                          │
└──────────────────────────────────────────────────────────────────────────┘

     [1. Kaggle Datasets (Real Schemas)]
       ├── Mandi Commodity Prices & Arrivals (Agmarknet)
       ├── Agricultural Products Sales Records (2022-2023)
       └── Indian Cities Weather (1990-2022)
                          │
                          ▼
     [2. Data Preprocessing & Unit Conversion] (`src/data/`)
       ├── Standardizes Rs./Quintal ➔ Rs./kg (divide by 100)
       ├── Name normalization & outlier filtering
       └── Temporal sorting (No data leakage)
                          │
                          ▼
     [3. ML Forecasting Engine] (`src/models/`)
       ├── Mandi Price Forecasting (Baseline vs Gradient Boosting: R²=0.928)
       └── Retail Demand Signal (Baseline vs Gradient Boosting: R²=0.894)
                          │
                          ▼
     [4. Constraint-Aware Decision Engine] (`src/engine/`)
       ├── Objective: Maximize Profit - Risk/Perishability Penalties
       ├── Hard Constraint: Σ (Price_i * Quantity_i) ≤ Available Budget
       └── Prototype Multi-Factor Risk Scoring (LOW / MEDIUM / HIGH)
                          │
                          ▼
     [5. What-If Simulator & Bilingual XAI] (`src/engine/`)
       ├── Dynamic Scenarios (Budget Δ, Price Shock Δ, Weather Slump Δ)
       └── Grounded Reasoning in Plain English & Hindi (हिंदी)
                          │
                          ▼
     [6. FastAPI Backend & Vendor Frontend] (`src/api/` & `src/frontend/`)
       ├── High-contrast, mobile-friendly Indian Vendor Dashboard
       └── Real-time Chart.js Mandi price trends & 1-click Demo Tour
```

---

## 📊 3. Kaggle Datasets & Multi-Signal Integration Strategy

JeevikaAI integrates three Kaggle datasets without fabricating false 1-to-1 joins:
1. **[India Commodity Wise Mandi Dataset](https://www.kaggle.com/datasets/vandeetshah/india-commodity-wise-mandi-dataset)**: Supplies daily wholesale modal prices, min/max bands, and arrival volumes (supply signal).
2. **[Agricultural Products Sales Data 2022–2023](https://www.kaggle.com/datasets/kdstoys/agricultural-products-sales-data-2022-2023)**: Supplies retail demand velocity, units sold, and stock on hand (demand signal).
3. **[Weather Data for Indian Cities](https://www.kaggle.com/datasets/vanvalkenberg/historicalweatherdataforindiancities)**: Supplies temperature and precipitation data to detect footfall and spoilage risks.

*For full dataset documentation and schemas, see [`docs/DATASETS.md`](docs/DATASETS.md).*

---

## 🔬 4. Machine Learning Benchmarks & Evaluation

All models were evaluated using time-aware train/test splitting (prior 80% date-sorted records for training, most recent 20% for out-of-time evaluation) to eliminate look-ahead leakage.

### Wholesale Price Forecasting ($R^2$ & Error Metrics)
| Model | $R^2$ Score | MAE (₹/kg) | RMSE (₹/kg) | MAPE (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Linear Regression (Baseline)** | 0.899 | ₹2.135 | ₹3.106 | 8.15% |
| **Gradient Boosting Regressor (Improved)** | **0.928** | **₹1.852** | **₹2.620** | **7.06%** |

### Retail Demand Estimation Signal
| Model | $R^2$ Score | MAE (kg/day) | RMSE (kg/day) | MAPE (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Linear Regression (Baseline)** | 0.664 | 2.719 kg | 3.475 kg | 9.73% |
| **Gradient Boosting Regressor (Improved)** | **0.670** | **2.710 kg** | **3.446 kg** | **9.69%** |

*For complete experiment history and top predictive features, see [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md).*

---

## 🧮 5. Mathematical Optimization Formulation

The vendor purchase allocation vector $q = [q_1, q_2, \dots, q_n]^T$ is solved via:

$$\max_{q \ge 0} \sum_{i=1}^{n} \Big( p_i \cdot \min(I_i + q_i, \hat{D}_i) - c_i \cdot q_i - \lambda_{\text{risk}} \cdot \omega_i \cdot c_i \cdot \max(0, I_i + q_i - \hat{D}_i) \Big)$$

Subject to:
$$\sum_{i=1}^{n} c_i \cdot q_i \le B \cdot \eta_{\text{target}}$$
$$q_i \ge 0, \quad q_i \in \{0.0, 0.5, 1.0, 1.5, \dots\} \text{ kg}$$

*For the complete mathematical formulation and risk scoring proofs, see [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).*

---

## ⚡ 6. Quickstart & Installation

### Prerequisites
- Python 3.10+
- Modern Web Browser (Chrome, Firefox, Edge, Safari)

### 1. Clone & Setup
```bash
cd scratch/jeevika-ai
pip install -r requirements.txt
```

### 2. Run Complete Application
```bash
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:8000/`**

### 3. Run Automated Tests
```bash
pytest tests/ -v
```

---

## 🎬 7. Live 3-Minute Demo Walkthrough

Click the top **`3-Min Demo Flow`** button in the dashboard or follow this flow:
1. **Baseline Scenario**: Enter Budget `₹2,000`, Stock on hand `5kg Tomato, 3kg Onion, 8kg Potato` -> Click **`GENERATE PURCHASE PLAN`**. Observe how the engine reserves an emergency cash buffer while restricting Tomato purchase to today's demand.
2. **What-If Budget Drop**: Drop budget to `₹1,500` -> The system protects durable onions/potatoes and scales down perishable exposure.
3. **What-If Price Surge**: Increase Tomato price by `+20%` -> The system automatically rebalances capital into high-margin items.
4. **Explainable AI (Hindi & English)**: Toggle to **`हिंदी (Hindi)`** and inspect the grounded reasoning under *"यह सिफारिश क्यों की गई है?"*.

*For the detailed judge presentation script, see [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md).*

---

## ⚖️ 8. Ethical Disclosures & Limitations
1. **Decision Support Estimates**: All figures are prototype decision-support estimates based on historical Kaggle patterns; they do not guarantee commercial profits.
2. **Supply vs Demand**: Wholesale Mandi arrivals represent market supply-side volumes, not direct consumer footfall.
3. **Offline Fallbacks**: If live weather APIs are unavailable, regional historical climate medians are utilized gracefully.
