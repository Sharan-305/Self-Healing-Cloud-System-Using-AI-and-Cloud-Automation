"""
Application Configuration Settings
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "Self-Healing Cloud System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # Security & Auth
    SECRET_KEY: str = Field(
        default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        env="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours

    # Database: Defaults to local SQLite for instant setup; supports PostgreSQL via DATABASE_URL
    DATABASE_URL: str = Field(
        default="sqlite:///./self_healing_cloud.db",
        env="DATABASE_URL"
    )

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

    # Monitoring Engine Defaults
    MONITORING_INTERVAL_SECONDS: int = 5
    METRIC_RETENTION_DAYS: int = 7
    AUTO_RECOVERY_GLOBAL_ENABLED: bool = True
    SIMULATION_MODE_DEFAULT: bool = True

    # ML Anomaly Detection Defaults
    ANOMALY_CONTAMINATION: float = 0.05
    ANOMALY_THRESHOLD: float = -0.15

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"


settings = Settings()
