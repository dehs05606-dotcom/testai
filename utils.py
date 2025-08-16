"""Utility functions for the Gemini AI Assistant."""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import mimetypes


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration."""
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('gemini_assistant.log')
        ]
    )
    
    return logging.getLogger(__name__)


def read_file(file_path: str) -> str:
    """Read content from a file."""
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine file type
    mime_type, _ = mimetypes.guess_type(file_path)
    
    try:
        if mime_type and mime_type.startswith('text'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            # For binary files, return basic info
            file_size = os.path.getsize(file_path)
            return f"Binary file: {file_path}\nSize: {file_size} bytes\nType: {mime_type or 'unknown'}"
    
    except UnicodeDecodeError:
        # Fallback for files with encoding issues
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()


def write_file(file_path: str, content: str) -> bool:
    """Write content to a file."""
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    
    except Exception as e:
        logging.error(f"Failed to write file {file_path}: {e}")
        return False


def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """Save data as JSON file."""
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return True
    
    except Exception as e:
        logging.error(f"Failed to save JSON file {file_path}: {e}")
        return False


def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Load data from JSON file."""
    
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    except Exception as e:
        logging.error(f"Failed to load JSON file {file_path}: {e}")
        return None


def format_response(response: str, max_width: int = 80) -> str:
    """Format response text for better readability."""
    
    lines = response.split('\n')
    formatted_lines = []
    
    for line in lines:
        if len(line) <= max_width:
            formatted_lines.append(line)
        else:
            # Simple word wrapping
            words = line.split()
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= max_width:
                    current_line += " " + word if current_line else word
                else:
                    if current_line:
                        formatted_lines.append(current_line)
                    current_line = word
            
            if current_line:
                formatted_lines.append(current_line)
    
    return '\n'.join(formatted_lines)


def validate_file_type(file_path: str, allowed_types: List[str]) -> bool:
    """Validate if file type is allowed."""
    
    _, ext = os.path.splitext(file_path.lower())
    return ext in allowed_types


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get file information."""
    
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    stat = os.stat(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    
    return {
        "path": file_path,
        "name": os.path.basename(file_path),
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "mime_type": mime_type,
        "is_text": mime_type and mime_type.startswith('text') if mime_type else False
    }


def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to specified length."""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from markdown-formatted text."""
    
    import re
    
    # Pattern to match code blocks
    pattern = r'```(\w+)?\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    code_blocks = []
    for language, code in matches:
        code_blocks.append({
            "language": language or "text",
            "code": code.strip()
        })
    
    return code_blocks


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    
    import re
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def create_backup(file_path: str) -> Optional[str]:
    """Create a backup of a file."""
    
    if not os.path.exists(file_path):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        return None