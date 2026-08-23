"""One-click Runner for JeevikaAI Application."""

import sys
import os
import uvicorn
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.utils.logger import logger
from src.data.preprocess import run_preprocessing_pipeline
from src.models.train_all import train_all_models

def main():
    logger.info("==================================================")
    logger.info("Starting JeevikaAI Hackathon Application")
    logger.info("==================================================")
    
    models_dir = BASE_DIR / "models"
    price_model = models_dir / "price_model_gbm.pkl"
    
    if not price_model.exists():
        logger.info("Trained model artifacts missing. Running one-time training...")
        train_all_models()
        logger.info("Models ready!")

    logger.info("Serving interactive Vendor Dashboard at http://127.0.0.1:8000")
    logger.info("API Documentation available at http://127.0.0.1:8000/docs")
    logger.info("==================================================")

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()
