"""Gemini API client for text generation and chat functionality."""

import json
import logging
import requests
from typing import Dict, List, Optional, Union, Generator
from dataclasses import dataclass
from config import config


@dataclass
class Message:
    """Represents a chat message."""
    role: str  # 'user' or 'model'
    content: str
    timestamp: Optional[str] = None


@dataclass
class GenerationResponse:
    """Represents a generation response from Gemini API."""
    text: str
    finish_reason: Optional[str] = None
    safety_ratings: Optional[List[Dict]] = None
    usage_metadata: Optional[Dict] = None


class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.API_KEY
        self.model = model or config.MODEL
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        self.chat_history: List[Message] = []
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Validate configuration
        if not self.api_key:
            raise ValueError("API key is required")
    
    def _make_request(self, payload: Dict) -> Dict:
        """Make a request to the Gemini API."""
        headers = {
            "Content-Type": "application/json",
        }
        
        url = f"{self.base_url}?key={self.api_key}"
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Handle specific error cases
            if response.status_code == 429:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Rate limit exceeded')
                self.logger.error(f"API quota exceeded: {error_message}")
                raise Exception(f"API quota exceeded: {error_message}")
            
            if response.status_code == 400:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Bad request')
                self.logger.error(f"API bad request: {error_message}")
                raise Exception(f"API bad request: {error_message}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise
    
    def generate_text(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        safety_settings: Optional[List[Dict]] = None
    ) -> GenerationResponse:
        """Generate text using Gemini API."""
        
        generation_config = config.get_generation_config()
        if temperature is not None:
            generation_config["temperature"] = temperature
        if max_tokens is not None:
            generation_config["maxOutputTokens"] = max_tokens
        if top_p is not None:
            generation_config["topP"] = top_p
        if top_k is not None:
            generation_config["topK"] = top_k
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": generation_config
        }
        
        if safety_settings:
            payload["safetySettings"] = safety_settings
        
        try:
            response_data = self._make_request(payload)
            
            if "candidates" not in response_data or not response_data["candidates"]:
                raise ValueError("No candidates in response")
            
            candidate = response_data["candidates"][0]
            
            if "content" not in candidate or "parts" not in candidate["content"]:
                raise ValueError("Invalid response structure")
            
            text = candidate["content"]["parts"][0].get("text", "")
            finish_reason = candidate.get("finishReason")
            safety_ratings = candidate.get("safetyRatings")
            usage_metadata = response_data.get("usageMetadata")
            
            return GenerationResponse(
                text=text,
                finish_reason=finish_reason,
                safety_ratings=safety_ratings,
                usage_metadata=usage_metadata
            )
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            raise
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Send a chat message and get response."""
        
        # Add system prompt if provided and chat history is empty
        if system_prompt and not self.chat_history:
            self.chat_history.append(Message(role="user", content=system_prompt))
            system_response = self.generate_text(system_prompt)
            self.chat_history.append(Message(role="model", content=system_response.text))
        
        # Add user message to history
        self.chat_history.append(Message(role="user", content=message))
        
        # Prepare conversation context
        contents = []
        for msg in self.chat_history:
            contents.append({
                "role": msg.role,
                "parts": [{"text": msg.content}]
            })
        
        payload = {
            "contents": contents,
            "generationConfig": config.get_generation_config()
        }
        
        try:
            response_data = self._make_request(payload)
            
            if "candidates" not in response_data or not response_data["candidates"]:
                raise ValueError("No candidates in response")
            
            candidate = response_data["candidates"][0]
            response_text = candidate["content"]["parts"][0].get("text", "")
            
            # Add response to history
            self.chat_history.append(Message(role="model", content=response_text))
            
            return response_text
            
        except Exception as e:
            self.logger.error(f"Chat failed: {e}")
            raise
    
    def clear_chat_history(self):
        """Clear the chat history."""
        self.chat_history.clear()
    
    def get_chat_history(self) -> List[Message]:
        """Get the current chat history."""
        return self.chat_history.copy()
    
    def analyze_text(self, text: str, analysis_type: str = "general") -> str:
        """Analyze text with specific analysis type."""
        
        analysis_prompts = {
            "general": f"Analyze the following text and provide insights:\n\n{text}",
            "sentiment": f"Analyze the sentiment of the following text:\n\n{text}",
            "summary": f"Provide a concise summary of the following text:\n\n{text}",
            "keywords": f"Extract key words and phrases from the following text:\n\n{text}",
            "translation": f"Detect the language and provide an English translation if needed:\n\n{text}"
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
        response = self.generate_text(prompt)
        return response.text
    
    def process_file_content(self, content: str, task: str = "summarize") -> str:
        """Process file content with specified task."""
        
        task_prompts = {
            "summarize": f"Summarize the following content:\n\n{content}",
            "extract_info": f"Extract key information from the following content:\n\n{content}",
            "analyze": f"Analyze the following content:\n\n{content}",
            "questions": f"Generate questions based on the following content:\n\n{content}"
        }
        
        prompt = task_prompts.get(task, task_prompts["summarize"])
        response = self.generate_text(prompt)
        return response.text