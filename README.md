# Gemini AI Assistant

A comprehensive Python application for AI-powered text generation and analysis using Google's Gemini API.

## Features

- **Text Generation**: Generate high-quality text from prompts
- **Interactive Chat**: Conversational AI with context awareness
- **Text Analysis**: Sentiment analysis, summarization, keyword extraction, and translation
- **File Processing**: Upload and analyze various file types
- **Multiple Interfaces**: CLI, Web UI (Flask), and REST API (FastAPI)
- **Comprehensive Testing**: Full test suite with coverage reporting
- **Docker Support**: Containerized deployment with Docker Compose

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dehs05606-dotcom/testai.git
cd testai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API key:
```bash
cp .env.example .env
# Edit .env and set your GEMINI_API_KEY
```

### Usage

#### Command Line Interface
```bash
# Generate text
python main.py cli generate --prompt "Write a story about AI"

# Start interactive chat
python main.py cli chat

# Analyze text
python main.py cli analyze "Your text here" --type sentiment

# Process a file
python main.py cli process-file document.txt --task summarize
```

#### Web Interface
```bash
# Start Flask web application
python main.py web

# Visit http://localhost:12000
```

#### REST API
```bash
# Start FastAPI server
python main.py api

# Visit http://localhost:12000/docs for interactive API documentation
```

## API Endpoints

### Text Generation
```http
POST /api/generate
Content-Type: application/json

{
  "prompt": "Write a story about AI",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

### Chat
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "session_id": "optional-session-id"
}
```

### Text Analysis
```http
POST /api/analyze
Content-Type: application/json

{
  "text": "Text to analyze",
  "type": "sentiment"
}
```

### File Upload
```http
POST /api/upload
Content-Type: multipart/form-data

file: [file]
task: summarize
```

## Configuration

The application can be configured through environment variables or a `.env` file:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-pro

# Application Configuration
APP_NAME=Gemini AI Assistant
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# Web Server Configuration
HOST=0.0.0.0
PORT=12000

# Generation Parameters
TEMPERATURE=0.7
MAX_TOKENS=8192
TOP_P=0.8
TOP_K=40
```

## Docker Deployment

### Using Docker Compose
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Using Docker directly
```bash
# Build the image
docker build -t gemini-assistant .

# Run the container
docker run -p 12000:12000 -e GEMINI_API_KEY=your_key gemini-assistant
```

## Development

### Setup Development Environment
```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .[dev]

# Run tests
python main.py test

# Run tests with coverage
python main.py test --coverage

# Format code
black .

# Lint code
flake8 .
```

### Project Structure
```
testai/
├── main.py              # Main entry point
├── config.py            # Configuration management
├── gemini_client.py     # Gemini API client
├── utils.py             # Utility functions
├── cli.py               # Command line interface
├── web_app.py           # Flask web application
├── fastapi_app.py       # FastAPI application
├── tests/               # Test suite
│   ├── test_gemini_client.py
│   └── test_utils.py
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
└── README.md           # This file
```

## Testing

The application includes a comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_gemini_client.py

# Run with verbose output
pytest -v
```

## API Documentation

When running the FastAPI application, interactive API documentation is available at:
- Swagger UI: `http://localhost:12000/docs`
- ReDoc: `http://localhost:12000/redoc`

## Supported File Types

The application supports processing the following file types:
- Text files (`.txt`, `.md`)
- Code files (`.py`, `.js`, `.html`, `.css`)
- Data files (`.json`, `.xml`, `.csv`)

## Error Handling

The application includes comprehensive error handling:
- API request failures
- Invalid file types
- Configuration errors
- Network timeouts
- Rate limiting

## Security Features

- Input validation and sanitization
- File type restrictions
- Request size limits
- Error message sanitization
- Secure file handling

## Performance Considerations

- Async support in FastAPI
- Request caching
- File size limits
- Connection pooling
- Graceful error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the test examples

## Changelog

### v1.0.0
- Initial release
- Complete Gemini API integration
- CLI, Web, and API interfaces
- Comprehensive test suite
- Docker support
- Full documentation
