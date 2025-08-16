"""Factory for creating Gemini clients (real or mock)."""

from typing import Optional, Union
from config import config
from gemini_client import GeminiClient
from mock_client import MockGeminiClient


def create_client(api_key: Optional[str] = None, model: Optional[str] = None) -> Union[GeminiClient, MockGeminiClient]:
    """Create a Gemini client (real or mock based on configuration)."""
    
    if config.MOCK_MODE:
        return MockGeminiClient(api_key=api_key, model=model)
    else:
        return GeminiClient(api_key=api_key, model=model)


def get_client() -> Union[GeminiClient, MockGeminiClient]:
    """Get a client instance using default configuration."""
    return create_client()