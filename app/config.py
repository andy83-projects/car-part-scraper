"""Configuration settings"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Database - build URL from components
    postgres_user: str = "carparts"
    postgres_password: str = "password"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "carparts"
    
    @property
    def database_url(self) -> str:
        """Build database URL from components"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # AI Provider
    ai_provider: str = "ollama"
    ollama_url: str = "http://ollama.ai.svc.cluster.local:11434"
    ollama_model: str = "llama3.1:8b"
    
    # Scraping
    default_zip_code: str = "07001"
    max_price: int = 500
    search_radius_miles: int = 100
    
    # App
    app_name: str = "4G63 Head Finder"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
