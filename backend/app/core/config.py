"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "GEPP - Waste Incident Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://gepp_user:gepp_password@localhost:5432/gepp_db"
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://frontend:3000"
    ]
    
    # AI Settings
    AI_MODEL_NAME: str = "all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD: float = 0.75
    
    # Database Seeding
    SEED_DATA: bool = False
    SEED_COUNT: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
