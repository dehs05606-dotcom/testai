"""Configuration management for Gemini AI Assistant."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration class."""
    
    def __init__(self):
        # Gemini API Configuration
        self.API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDxzcuwVpOy_2-Ze61AVduJHUVKTJKiaYc")
        self.MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
        self.BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{self.MODEL}:generateContent"
        
        # Application Configuration
        self.APP_NAME = os.getenv("APP_NAME", "Gemini AI Assistant")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.MOCK_MODE = os.getenv("MOCK_MODE", "False").lower() == "true"
        
        # Web Server Configuration
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "12000"))
        
        # API Configuration
        self.MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))
        self.TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
        self.TOP_P = float(os.getenv("TOP_P", "0.8"))
        self.TOP_K = int(os.getenv("TOP_K", "40"))
        
    def validate(self) -> bool:
        """Validate configuration."""
        if self.MOCK_MODE:
            return True  # Mock mode doesn't require valid API key
        if not self.API_KEY or self.API_KEY == "your_api_key_here":
            return False
        return True
    
    def get_generation_config(self) -> dict:
        """Get generation configuration for API calls."""
        return {
            "temperature": self.TEMPERATURE,
            "topP": self.TOP_P,
            "topK": self.TOP_K,
            "maxOutputTokens": self.MAX_TOKENS,
        }


# Global configuration instance
config = Config()