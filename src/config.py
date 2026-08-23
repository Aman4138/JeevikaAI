"""Configuration manager for JeevikaAI."""

import os
from pathlib import Path
from typing import Dict, Any, List
import yaml

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml with fallback defaults."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    # Built-in fallback config
    return {
        "project": {
            "name": "JeevikaAI",
            "version": "1.0.0",
            "tagline": "Constraint-Aware AI Decision Making for Indian Street & Vegetable Vendors"
        },
        "paths": {
            "raw_data_dir": "data/raw",
            "processed_data_dir": "data/processed",
            "models_dir": "models",
            "metrics_file": "models/model_metrics.json",
            "experiments_log": "models/experiment_log.json",
            "frontend_dir": "src/frontend"
        },
        "commodities": {
            "tomato": {
                "display_name": "Tomato (टमाटर)",
                "hindi_name": "टमाटर",
                "category": "Perishable Vegetable",
                "shelf_life_days": 2.5,
                "spoilage_rate_daily": 0.15,
                "typical_retail_margin_pct": 0.35,
                "default_wholesale_cost_per_kg": 24.0,
                "default_retail_price_per_kg": 35.0,
                "typical_daily_demand_kg": 20.0,
                "unit": "kg",
                "icon": "🍅",
                "color": "#EF4444"
            },
            "onion": {
                "display_name": "Onion (प्याज़)",
                "hindi_name": "प्याज़",
                "category": "Semi-Perishable Vegetable",
                "shelf_life_days": 21.0,
                "spoilage_rate_daily": 0.02,
                "typical_retail_margin_pct": 0.25,
                "default_wholesale_cost_per_kg": 28.0,
                "default_retail_price_per_kg": 38.0,
                "typical_daily_demand_kg": 25.0,
                "unit": "kg",
                "icon": "🧅",
                "color": "#A855F7"
            },
            "potato": {
                "display_name": "Potato (आलू)",
                "hindi_name": "आलू",
                "category": "Staple Non-Perishable Vegetable",
                "shelf_life_days": 35.0,
                "spoilage_rate_daily": 0.01,
                "typical_retail_margin_pct": 0.20,
                "default_wholesale_cost_per_kg": 18.0,
                "default_retail_price_per_kg": 24.0,
                "typical_daily_demand_kg": 30.0,
                "unit": "kg",
                "icon": "🥔",
                "color": "#EAB308"
            }
        },
        "locations": [
            {"id": "delhi_azadpur", "city": "Delhi", "mandi_name": "Azadpur Mandi", "state": "Delhi"},
            {"id": "mumbai_vashi", "city": "Mumbai", "mandi_name": "APMC Vashi", "state": "Maharashtra"},
            {"id": "bengaluru_kolar", "city": "Bengaluru", "mandi_name": "Kolar APMC", "state": "Karnataka"},
            {"id": "nashik_lasalgaon", "city": "Nashik", "mandi_name": "Lasalgaon Mandi", "state": "Maharashtra"},
            {"id": "agra_fatehabad", "city": "Agra", "mandi_name": "Fatehabad Mandi", "state": "Uttar Pradesh"}
        ]
    }

CONFIG = load_config()

def get_path(key: str) -> Path:
    """Resolve path relative to project root."""
    rel_path = CONFIG.get("paths", {}).get(key, "")
    full_path = BASE_DIR / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    return full_path

def get_commodities() -> Dict[str, Any]:
    return CONFIG.get("commodities", {})

def get_locations() -> List[Dict[str, Any]]:
    return CONFIG.get("locations", [])
