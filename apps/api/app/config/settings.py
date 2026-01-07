"""
Application Settings
===================
Configuration management for EcoImmo France 2026

Uses Pydantic Settings for type-safe environment variable handling
"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "EcoImmo France 2026"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://ecoimmo:ecoimmo_dev_2026@localhost:5432/ecoimmo_france"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # French Government APIs
    DVF_API_URL: str = "https://data.economie.gouv.fr/api/v2/catalog/datasets/dvf/records"
    ADEME_DPE_API_URL: str = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe-v2-logements-existants"

    # Regulatory Constants (2026)
    ELECTRICITY_CONVERSION_FACTOR: float = 1.9  # New 2026 value
    GAS_CONVERSION_FACTOR: float = 1.0
    FUEL_OIL_CONVERSION_FACTOR: float = 1.0
    WOOD_CONVERSION_FACTOR: float = 0.6

    # GDPR Compliance
    GDPR_ANONYMIZATION_LEVEL: str = "postal_code"  # "postal_code", "commune", "department"
    DATA_RETENTION_DAYS: int = 90

    # EU AI Act Compliance
    EU_AI_ACT_COMPLIANCE: bool = True
    AI_TRANSPARENCY_BADGE: bool = True

    # Mistral AI
    MISTRAL_API_KEY: str = ""
    MISTRAL_MODEL: str = "mistral-large-latest"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
    ]

    # Security
    SECRET_KEY: str = "changeme_in_production"
    API_KEY_HEADER: str = "X-API-Key"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Caching
    CACHE_TTL_DVF: int = 86400  # 24 hours
    CACHE_TTL_DPE: int = 43200  # 12 hours

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
