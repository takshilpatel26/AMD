from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers
from .routers import forecast, anomaly, parser, efficiency

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    logger.info("🚀 ML Gateway starting up...")
    logger.info("Loading ML models...")
    # Load ML models here if needed
    yield
    logger.info("👋 ML Gateway shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Gram Meter ML Gateway",
    description="AI/ML Microservice for Smart Energy Analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(forecast.router, prefix="/api/v1/ml/forecast", tags=["Forecasting"])
app.include_router(anomaly.router, prefix="/api/v1/ml/anomaly", tags=["Anomaly Detection"])
app.include_router(parser.router, prefix="/api/v1/ml/parser", tags=["Universal Parser"])
app.include_router(efficiency.router, prefix="/api/v1/ml/efficiency", tags=["Efficiency Scoring"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Gram Meter ML Gateway",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "forecast": "/api/v1/ml/forecast",
            "anomaly": "/api/v1/ml/anomaly",
            "parser": "/api/v1/ml/parser",
            "efficiency": "/api/v1/ml/efficiency"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ml-gateway"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
