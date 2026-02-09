"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    INDEX_DIR: str = "./indices"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")  # Default to available model
    OLLAMA_TIMEOUT: int = 900  # 15 минут - увеличен для больших документов
    
    # PageIndex
    PAGEINDEX_MAX_PAGES_PER_NODE: int = 10
    PAGEINDEX_MAX_TOKENS_PER_NODE: int = 20000
    
    # Security
    MAX_FILE_SIZE: int = 104857600  # 100MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf"]
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "*"  # Allow all for development
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create instance
settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.INDEX_DIR, exist_ok=True)

