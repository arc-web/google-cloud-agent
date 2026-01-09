"""
Configuration settings for the Google Cloud Manager
"""

import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Ultra-Efficient Google Cloud Manager"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Google Cloud
    google_cloud_project_id: Optional[str] = None
    google_application_credentials: Optional[str] = None
    
    # OpenAI (Optional - can be used as fallback)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2000
    
    # Google Gemini (Primary AI)
    google_api_key: Optional[str] = None
    gemini_model: str = "gemini-pro"
    gemini_max_tokens: int = 2048
    
    # Database
    database_url: str = "sqlite:///./cloud_manager.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Monitoring
    monitoring_enabled: bool = True
    alert_check_interval: int = 300  # 5 minutes
    
    # Self-healing
    self_healing_enabled: bool = True
    auto_fix_threshold: float = 0.8  # 80% confidence
    
    # Workflow
    max_workflow_steps: int = 50
    workflow_timeout: int = 3600  # 1 hour
    
    # Recommendations
    recommendation_frequency: int = 86400  # 24 hours
    cost_optimization_threshold: float = 0.1  # 10% savings
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Validate required settings
def validate_settings():
    """Validate that all required settings are present"""
    required_settings = [
        "google_cloud_project_id",
        "google_api_key"  # Only Gemini is required now
    ]
    
    missing_settings = []
    for setting in required_settings:
        if not getattr(settings, setting):
            missing_settings.append(setting)
    
    if missing_settings:
        raise ValueError(f"Missing required settings: {', '.join(missing_settings)}")

# Validate settings on import
try:
    validate_settings()
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Please set the required environment variables or update your .env file") 