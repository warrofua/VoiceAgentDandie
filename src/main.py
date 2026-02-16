"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.config import get_settings
from src.api.routes import router
from src.database.connection import engine, Base
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="ABA Voice Agent API",
    description="Voice agent for ABA therapy insurance handling",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["voice"])
# Serve basic UI from static directory
ui_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting ABA Voice Agent API")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # Create temp directory for audio files
    import os
    os.makedirs("temp_audio", exist_ok=True)
    logger.info("Temp audio directory created")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down ABA Voice Agent API")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ABA Voice Agent API",
        "version": "0.1.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
