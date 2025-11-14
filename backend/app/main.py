"""
Main FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import init_db
from app.modules.incidents.routes import router as incidents_router
from app.modules.analytics.routes import router as analytics_router
from app.modules.ai.routes import router as ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    setup_logging()
    logger.info("Starting application", environment=settings.ENVIRONMENT)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized successfully")
    
    # Seed database if enabled
    if settings.SEED_DATA:
        logger.info(f"Seeding enabled - will create {settings.SEED_COUNT} incidents")
        try:
            from app.seed_data import DataSeeder
            seeder = DataSeeder()
            await seeder.seed_database(count=settings.SEED_COUNT)
        except Exception as e:
            logger.error(f"Failed to seed database: {e}")
            # Don't fail startup if seeding fails
    
    # AI models will be lazy-loaded on first use to avoid blocking startup
    logger.info("Application ready - AI models will load on first request")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title="Waste Incident Reporting & AI Insight Platform",
    description="Enterprise-grade waste incident management system with offline AI capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(incidents_router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI Insights"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Waste Incident Reporting & AI Insight Platform",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
