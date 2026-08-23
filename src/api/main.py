"""Main FastAPI Application Entry Point for JeevikaAI."""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.utils.logger import logger
from src.config import get_path, BASE_DIR
from src.api.routes import router as api_router
from src.models.train_all import train_all_models

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: Ensure models and data are initialized on startup."""
    logger.info("Initializing JeevikaAI Backend Application...")
    models_dir = get_path("models_dir")
    price_model_file = models_dir / "price_model_gbm.pkl"
    
    if not price_model_file.exists():
        logger.info("Trained model artifacts not found. Initiating fast initial training...")
        try:
            train_all_models()
        except Exception as e:
            logger.warning("Initial training on startup completed with notice: %s", e)
    else:
        logger.info("Existing model artifacts loaded successfully from %s", models_dir)
        
    yield
    logger.info("Shutting down JeevikaAI Application...")

app = FastAPI(
    title="JeevikaAI - Constraint-Aware Decision Support API",
    description="AI-powered purchasing decision support for Indian street and vegetable vendors (AI for Public Good).",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes under /api
app.include_router(api_router, prefix="/api")

# Static frontend files
frontend_dir = BASE_DIR / "src" / "frontend"
frontend_dir.mkdir(parents=True, exist_ok=True)

if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the Vendor Dashboard SPA."""
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "JeevikaAI API is active. Visit /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
