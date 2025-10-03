import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database - Retool PostgreSQL
    database_url: str = "postgresql://retool:npg_yf3gdzwl4RqE@ep-silent-sun-afdlv6pj.c-2.us-west-2.retooldb.com/retool?sslmode=require"
    
    # Google Gemini Configuration
    gemini_api_key: str = "AIzaSyAZKwC1d_krqu5d6B0j_7xxkxBAkYS0Jfw"
    gemini_model: str = "gemini-2.0-flash-exp"  # Updated to latest model
    max_tokens: int = 1000
    
    # Application Settings
    log_level: str = "INFO"
    upload_dir: str = "uploads"
    
    # CORS Settings for Vercel
    # For production, set to comma-separated list of allowed origins
    cors_origins: str = "https://uw-workbench-portal.vercel.app,https://uw-workbench-jade.vercel.app"
    cors_credentials: bool = True
    cors_methods: str = "*"
    cors_headers: str = "*"
    
    class Config:
        env_file = ".env"


settings = Settings()
