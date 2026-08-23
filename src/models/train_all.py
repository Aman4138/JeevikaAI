"""End-to-end ML Training Pipeline: Data -> Feature Engineering -> Training -> Evaluation -> Model Persistence."""

import json
from pathlib import Path
from datetime import datetime
import pandas as pd

from src.utils.logger import logger
from src.config import get_path
from src.data.preprocess import run_preprocessing_pipeline
from src.features.feature_engineering import build_price_features, build_demand_features
from src.models.price_predictor import PricePredictor
from src.models.demand_estimator import DemandEstimator

def train_all_models(force_data_refresh: bool = False):
    """Execute complete ML pipeline and generate metrics report."""
    logger.info("==================================================")
    logger.info("Starting JeevikaAI ML Training Pipeline")
    logger.info("==================================================")

    # 1. Preprocessing
    clean_mandi, clean_sales, clean_weather = run_preprocessing_pipeline(save=True)

    # 2. Feature Engineering
    logger.info("Engineering features for price forecasting...")
    df_price_feats = build_price_features(clean_mandi, clean_weather)

    logger.info("Engineering features for demand estimation...")
    df_demand_feats = build_demand_features(clean_sales, clean_weather)

    # 3. Model Training & Evaluation
    models_dir = get_path("models_dir")
    models_dir.mkdir(parents=True, exist_ok=True)

    # Price Predictor
    price_predictor = PricePredictor()
    price_metrics = price_predictor.train(df_price_feats)
    price_predictor.save(models_dir)

    # Demand Estimator
    demand_estimator = DemandEstimator()
    demand_metrics = demand_estimator.train(df_demand_feats)
    demand_estimator.save(models_dir)

    # 4. Save Metrics & Experiment Log
    all_metrics = {
        "timestamp": datetime.now().isoformat(),
        "commodities_evaluated": ["Tomato", "Onion", "Potato"],
        "price_prediction_model": price_metrics,
        "demand_estimation_model": demand_metrics
    }

    metrics_file = get_path("metrics_file")
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)
    logger.info("Model metrics saved to %s", metrics_file)

    # Append to experiment log
    exp_file = get_path("experiments_log")
    experiment_history = []
    if exp_file.exists():
        try:
            with open(exp_file, "r", encoding="utf-8") as f:
                experiment_history = json.load(f)
        except Exception:
            experiment_history = []

    experiment_history.append({
        "version": f"v1.{len(experiment_history)+1}",
        "timestamp": datetime.now().isoformat(),
        "price_gbm_r2": price_metrics["improved"]["r2"],
        "price_gbm_mae": price_metrics["improved"]["mae"],
        "demand_gbm_r2": demand_metrics["improved"]["r2"],
        "demand_gbm_mae": demand_metrics["improved"]["mae"]
    })

    with open(exp_file, "w", encoding="utf-8") as f:
        json.dump(experiment_history, f, indent=2)
    logger.info("Experiment log updated at %s", exp_file)

    logger.info("==================================================")
    logger.info("JeevikaAI ML Training Pipeline Complete!")
    logger.info("==================================================")
    return all_metrics

if __name__ == "__main__":
    train_all_models()
