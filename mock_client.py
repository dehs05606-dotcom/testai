"""Mock Gemini client for testing and demonstration purposes."""

import random
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

from gemini_client import GenerationResponse, Message


class MockGeminiClient:
    """Mock client that simulates Gemini API responses for testing."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or "mock_key"
        self.model = model or "mock_model"
        self.chat_history: List[Message] = []
        
        # Mock responses for different types of prompts
        self.mock_responses = {
            "poem": [
                "In lines of code so clean and bright,\nPython shines with pure delight.\nWith syntax simple, logic clear,\nIt makes programming feel so near.\n\nFrom data science to web design,\nPython's power is truly divine.",
                "Serpentine syntax, elegant and clean,\nPython code flows like a dream.\nIndentation guides the way,\nMaking complex simple every day.\n\nLibraries vast, community strong,\nWith Python, you can't go wrong."
            ],
            "story": [
                "Once upon a time, in a world where artificial intelligence had become as common as smartphones, there lived a young programmer named Alex. Alex had always been fascinated by the potential of AI to solve complex problems and make life easier for everyone.",
                "In the year 2025, AI assistants had evolved beyond simple chatbots. They could understand context, learn from interactions, and provide meaningful help across countless domains. This is the story of one such assistant and its journey to understand humanity."
            ],
            "analysis": [
                "Based on the provided text, I can identify several key themes and patterns. The sentiment appears to be generally positive, with undertones of optimism and forward-thinking perspectives.",
                "This text demonstrates a clear structure with well-organized thoughts. The main arguments are supported by relevant examples, and the overall tone is professional and informative."
            ],
            "summary": [
                "This document discusses the key concepts and implementation details of modern AI systems, focusing on practical applications and best practices for development.",
                "The text covers various aspects of software development, including design patterns, testing methodologies, and deployment strategies for scalable applications."
            ],
            "default": [
                "Thank you for your question. Based on the information provided, I can offer several insights and recommendations that might be helpful for your specific use case.",
                "I understand what you're looking for. Let me provide a comprehensive response that addresses your main concerns and offers practical solutions.",
                "That's an interesting topic! Here's my analysis and some suggestions that might help you move forward with your project."
            ]
        }
    
    def _get_mock_response(self, prompt: str) -> str:
        """Generate a mock response based on the prompt content."""
        prompt_lower = prompt.lower()
        
        # Add some delay to simulate API call
        time.sleep(random.uniform(0.5, 1.5))
        
        # Determine response type based on prompt keywords
        if any(word in prompt_lower for word in ["poem", "poetry", "verse"]):
            responses = self.mock_responses["poem"]
        elif any(word in prompt_lower for word in ["story", "tale", "narrative"]):
            responses = self.mock_responses["story"]
        elif any(word in prompt_lower for word in ["analyze", "analysis", "sentiment"]):
            responses = self.mock_responses["analysis"]
        elif any(word in prompt_lower for word in ["summary", "summarize", "brief"]):
            responses = self.mock_responses["summary"]
        else:
            responses = self.mock_responses["default"]
        
        return random.choice(responses)
    
    def generate_text(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        safety_settings: Optional[List[Dict]] = None
    ) -> GenerationResponse:
        """Generate mock text response."""
        
        response_text = self._get_mock_response(prompt)
        
        # Create mock usage metadata
        usage_metadata = {
            "promptTokenCount": len(prompt.split()) * 2,  # Rough estimate
            "candidatesTokenCount": len(response_text.split()) * 2,
            "totalTokenCount": (len(prompt.split()) + len(response_text.split())) * 2
        }
        
        return GenerationResponse(
            text=response_text,
            finish_reason="STOP",
            safety_ratings=[],
            usage_metadata=usage_metadata
        )
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Mock chat functionality."""
        
        # Add system prompt if provided and chat history is empty
        if system_prompt and not self.chat_history:
            self.chat_history.append(Message(role="user", content=system_prompt))
            system_response = self._get_mock_response(system_prompt)
            self.chat_history.append(Message(role="model", content=system_response))
        
        # Add user message to history
        self.chat_history.append(Message(role="user", content=message))
        
        # Generate response based on conversation context
        context = " ".join([msg.content for msg in self.chat_history[-3:]])  # Last 3 messages
        response_text = self._get_mock_response(context)
        
        # Add response to history
        self.chat_history.append(Message(role="model", content=response_text))
        
        return response_text
    
    def clear_chat_history(self):
        """Clear the chat history."""
        self.chat_history.clear()
    
    def get_chat_history(self) -> List[Message]:
        """Get the current chat history."""
        return self.chat_history.copy()
    
    def analyze_text(self, text: str, analysis_type: str = "general") -> str:
        """Mock text analysis."""
        
        analysis_responses = {
            "general": f"This text contains {len(text.split())} words and appears to be well-structured. The main themes include communication, technology, and problem-solving.",
            "sentiment": f"The sentiment of this text is generally positive with a confidence score of {random.randint(70, 95)}%. The tone is professional and informative.",
            "summary": f"Summary: This text discusses key concepts related to {random.choice(['technology', 'business', 'education', 'science'])} with practical applications and examples.",
            "keywords": f"Key terms identified: {', '.join(random.sample(['innovation', 'development', 'analysis', 'implementation', 'strategy', 'solution'], 3))}",
            "translation": "The text appears to be in English and does not require translation."
        }
        
        time.sleep(random.uniform(0.3, 0.8))
        return analysis_responses.get(analysis_type, analysis_responses["general"])
    
    def process_file_content(self, content: str, task: str = "summarize") -> str:
        """Mock file processing."""
        
        word_count = len(content.split())
        
        task_responses = {
            "summarize": f"This document ({word_count} words) discusses important concepts and provides detailed information on the subject matter. Key points include methodology, implementation, and practical applications.",
            "extract_info": f"Key information extracted:\n- Document length: {word_count} words\n- Main topics: Technical implementation, best practices\n- Target audience: Developers and technical professionals",
            "analyze": f"Document analysis:\n- Structure: Well-organized with clear sections\n- Content quality: High, with detailed explanations\n- Readability: Good, appropriate for technical audience",
            "questions": f"Generated questions based on content:\n1. What are the main implementation challenges?\n2. How can these concepts be applied in practice?\n3. What are the key benefits of this approach?"
        }
        
        time.sleep(random.uniform(0.5, 1.2))
        return task_responses.get(task, task_responses["summarize"])