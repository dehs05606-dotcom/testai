"""Tests for Gemini client functionality."""

import pytest
from unittest.mock import Mock, patch
import json

from gemini_client import GeminiClient, GenerationResponse, Message


class TestGeminiClient:
    """Test cases for GeminiClient class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = GeminiClient(api_key="test_key", model="test_model")
    
    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.api_key == "test_key"
        assert self.client.model == "test_model"
        assert self.client.chat_history == []
    
    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key."""
        with patch('config.config.API_KEY', ''):
            with pytest.raises(ValueError, match="API key is required"):
                GeminiClient()
    
    @patch('requests.post')
    def test_generate_text_success(self, mock_post):
        """Test successful text generation."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Generated response"}]
                },
                "finishReason": "STOP",
                "safetyRatings": []
            }],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 5,
                "totalTokenCount": 15
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test generation
        response = self.client.generate_text("Test prompt")
        
        assert isinstance(response, GenerationResponse)
        assert response.text == "Generated response"
        assert response.finish_reason == "STOP"
        assert response.usage_metadata is not None
    
    @patch('requests.post')
    def test_generate_text_no_candidates(self, mock_post):
        """Test text generation with no candidates."""
        mock_response = Mock()
        mock_response.json.return_value = {"candidates": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with pytest.raises(ValueError, match="No candidates in response"):
            self.client.generate_text("Test prompt")
    
    @patch('requests.post')
    def test_generate_text_request_error(self, mock_post):
        """Test text generation with request error."""
        mock_post.side_effect = Exception("Network error")
        
        with pytest.raises(Exception):
            self.client.generate_text("Test prompt")
    
    @patch('requests.post')
    def test_chat_functionality(self, mock_post):
        """Test chat functionality."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Chat response"}]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        response = self.client.chat("Hello")
        
        assert response == "Chat response"
        assert len(self.client.chat_history) == 2  # User message + AI response
        assert self.client.chat_history[0].role == "user"
        assert self.client.chat_history[0].content == "Hello"
        assert self.client.chat_history[1].role == "model"
        assert self.client.chat_history[1].content == "Chat response"
    
    def test_clear_chat_history(self):
        """Test clearing chat history."""
        # Add some messages
        self.client.chat_history.append(Message(role="user", content="Test"))
        self.client.chat_history.append(Message(role="model", content="Response"))
        
        assert len(self.client.chat_history) == 2
        
        self.client.clear_chat_history()
        
        assert len(self.client.chat_history) == 0
    
    def test_get_chat_history(self):
        """Test getting chat history."""
        # Add some messages
        msg1 = Message(role="user", content="Test")
        msg2 = Message(role="model", content="Response")
        self.client.chat_history.extend([msg1, msg2])
        
        history = self.client.get_chat_history()
        
        assert len(history) == 2
        assert history[0].role == "user"
        assert history[0].content == "Test"
        assert history[1].role == "model"
        assert history[1].content == "Response"
        
        # Ensure it's a copy
        assert history is not self.client.chat_history
    
    @patch('requests.post')
    def test_analyze_text(self, mock_post):
        """Test text analysis."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Analysis result"}]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.analyze_text("Test text", "sentiment")
        
        assert result == "Analysis result"
        
        # Check that the correct prompt was used
        call_args = mock_post.call_args
        request_data = call_args[1]['json']
        prompt = request_data['contents'][0]['parts'][0]['text']
        assert "sentiment" in prompt.lower()
        assert "Test text" in prompt
    
    @patch('requests.post')
    def test_process_file_content(self, mock_post):
        """Test file content processing."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "File processing result"}]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.process_file_content("File content", "summarize")
        
        assert result == "File processing result"
        
        # Check that the correct prompt was used
        call_args = mock_post.call_args
        request_data = call_args[1]['json']
        prompt = request_data['contents'][0]['parts'][0]['text']
        assert "summarize" in prompt.lower()
        assert "File content" in prompt


class TestMessage:
    """Test cases for Message dataclass."""
    
    def test_message_creation(self):
        """Test message creation."""
        msg = Message(role="user", content="Test message")
        
        assert msg.role == "user"
        assert msg.content == "Test message"
        assert msg.timestamp is None
    
    def test_message_with_timestamp(self):
        """Test message creation with timestamp."""
        timestamp = "2023-01-01T00:00:00"
        msg = Message(role="model", content="Response", timestamp=timestamp)
        
        assert msg.role == "model"
        assert msg.content == "Response"
        assert msg.timestamp == timestamp


class TestGenerationResponse:
    """Test cases for GenerationResponse dataclass."""
    
    def test_response_creation(self):
        """Test response creation."""
        response = GenerationResponse(text="Generated text")
        
        assert response.text == "Generated text"
        assert response.finish_reason is None
        assert response.safety_ratings is None
        assert response.usage_metadata is None
    
    def test_response_with_metadata(self):
        """Test response creation with metadata."""
        usage = {"total_tokens": 100}
        safety = [{"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"}]
        
        response = GenerationResponse(
            text="Generated text",
            finish_reason="STOP",
            safety_ratings=safety,
            usage_metadata=usage
        )
        
        assert response.text == "Generated text"
        assert response.finish_reason == "STOP"
        assert response.safety_ratings == safety
        assert response.usage_metadata == usage