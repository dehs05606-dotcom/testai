"""Tests for utility functions."""

import pytest
import os
import tempfile
import json
from unittest.mock import patch, mock_open

from utils import (
    read_file, write_file, save_json, load_json,
    format_response, validate_file_type, get_file_info,
    truncate_text, extract_code_blocks, sanitize_filename
)


class TestFileOperations:
    """Test file operation utilities."""
    
    def test_read_file_success(self):
        """Test successful file reading."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_path = f.name
        
        try:
            content = read_file(temp_path)
            assert content == "Test content"
        finally:
            os.unlink(temp_path)
    
    def test_read_file_not_found(self):
        """Test reading non-existent file."""
        with pytest.raises(FileNotFoundError):
            read_file("non_existent_file.txt")
    
    def test_write_file_success(self):
        """Test successful file writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.txt")
            result = write_file(file_path, "Test content")
            
            assert result is True
            assert os.path.exists(file_path)
            
            with open(file_path, 'r') as f:
                assert f.read() == "Test content"
    
    def test_write_file_create_directory(self):
        """Test file writing with directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "subdir", "test.txt")
            result = write_file(file_path, "Test content")
            
            assert result is True
            assert os.path.exists(file_path)
    
    def test_save_json_success(self):
        """Test successful JSON saving."""
        test_data = {"key": "value", "number": 42}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.json")
            result = save_json(test_data, file_path)
            
            assert result is True
            assert os.path.exists(file_path)
            
            with open(file_path, 'r') as f:
                loaded_data = json.load(f)
                assert loaded_data == test_data
    
    def test_load_json_success(self):
        """Test successful JSON loading."""
        test_data = {"key": "value", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            loaded_data = load_json(temp_path)
            assert loaded_data == test_data
        finally:
            os.unlink(temp_path)
    
    def test_load_json_not_found(self):
        """Test loading non-existent JSON file."""
        result = load_json("non_existent_file.json")
        assert result is None


class TestTextFormatting:
    """Test text formatting utilities."""
    
    def test_format_response_short_text(self):
        """Test formatting short text."""
        text = "Short text"
        result = format_response(text, max_width=80)
        assert result == "Short text"
    
    def test_format_response_long_line(self):
        """Test formatting long line."""
        text = "This is a very long line that should be wrapped because it exceeds the maximum width"
        result = format_response(text, max_width=20)
        
        lines = result.split('\n')
        for line in lines:
            assert len(line) <= 20
    
    def test_format_response_multiple_lines(self):
        """Test formatting multiple lines."""
        text = "Line 1\nLine 2\nVery long line that needs to be wrapped"
        result = format_response(text, max_width=20)
        
        lines = result.split('\n')
        assert "Line 1" in lines
        assert "Line 2" in lines
        
        for line in lines:
            assert len(line) <= 20
    
    def test_truncate_text_short(self):
        """Test truncating short text."""
        text = "Short text"
        result = truncate_text(text, max_length=100)
        assert result == "Short text"
    
    def test_truncate_text_long(self):
        """Test truncating long text."""
        text = "A" * 1000
        result = truncate_text(text, max_length=50)
        assert len(result) == 50
        assert result.endswith("...")
    
    def test_extract_code_blocks(self):
        """Test extracting code blocks from markdown."""
        text = """
        Some text here.
        
        ```python
        def hello():
            print("Hello, World!")
        ```
        
        More text.
        
        ```javascript
        console.log("Hello, World!");
        ```
        
        ```
        Plain code block
        ```
        """
        
        blocks = extract_code_blocks(text)
        
        assert len(blocks) == 3
        assert blocks[0]["language"] == "python"
        assert "def hello():" in blocks[0]["code"]
        assert blocks[1]["language"] == "javascript"
        assert "console.log" in blocks[1]["code"]
        assert blocks[2]["language"] == "text"
        assert "Plain code block" in blocks[2]["code"]


class TestFileValidation:
    """Test file validation utilities."""
    
    def test_validate_file_type_allowed(self):
        """Test validating allowed file types."""
        allowed_types = ['.txt', '.py', '.json']
        
        assert validate_file_type("test.txt", allowed_types) is True
        assert validate_file_type("script.py", allowed_types) is True
        assert validate_file_type("data.json", allowed_types) is True
    
    def test_validate_file_type_not_allowed(self):
        """Test validating not allowed file types."""
        allowed_types = ['.txt', '.py', '.json']
        
        assert validate_file_type("image.jpg", allowed_types) is False
        assert validate_file_type("document.pdf", allowed_types) is False
        assert validate_file_type("archive.zip", allowed_types) is False
    
    def test_validate_file_type_case_insensitive(self):
        """Test case insensitive file type validation."""
        allowed_types = ['.txt', '.py']
        
        assert validate_file_type("TEST.TXT", allowed_types) is True
        assert validate_file_type("Script.PY", allowed_types) is True
    
    def test_get_file_info_existing_file(self):
        """Test getting info for existing file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_path = f.name
        
        try:
            info = get_file_info(temp_path)
            
            assert "error" not in info
            assert info["path"] == temp_path
            assert info["name"] == os.path.basename(temp_path)
            assert info["size"] > 0
            assert "modified" in info
            assert info["mime_type"] == "text/plain"
            assert info["is_text"] is True
        finally:
            os.unlink(temp_path)
    
    def test_get_file_info_non_existent(self):
        """Test getting info for non-existent file."""
        info = get_file_info("non_existent_file.txt")
        assert info["error"] == "File not found"
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test invalid characters
        assert sanitize_filename("file<name>.txt") == "file_name_.txt"
        assert sanitize_filename("file:name.txt") == "file_name.txt"
        assert sanitize_filename('file"name.txt') == "file_name.txt"
        
        # Test leading/trailing spaces and dots
        assert sanitize_filename("  filename.txt  ") == "filename.txt"
        assert sanitize_filename("..filename.txt..") == "filename.txt"
        
        # Test long filename
        long_name = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_name)
        assert len(sanitized) <= 255
        assert sanitized.endswith(".txt")


class TestLogging:
    """Test logging setup."""
    
    @patch('logging.basicConfig')
    @patch('logging.getLogger')
    def test_setup_logging(self, mock_get_logger, mock_basic_config):
        """Test logging setup."""
        from utils import setup_logging
        
        mock_logger = mock_get_logger.return_value
        
        logger = setup_logging("DEBUG")
        
        mock_basic_config.assert_called_once()
        mock_get_logger.assert_called_once()
        assert logger == mock_logger
        
        # Check that basicConfig was called with correct level
        call_args = mock_basic_config.call_args
        assert call_args[1]['level'] == 10  # DEBUG level