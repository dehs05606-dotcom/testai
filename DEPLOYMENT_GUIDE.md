# Gemini AI Assistant - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Google Gemini API key (optional - mock mode available)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd testai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

### Configuration Options

#### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key
- `GEMINI_MODEL`: Model to use (default: gemini-2.5-pro)
- `MOCK_MODE`: Set to "true" for testing without API key
- `DEBUG`: Enable debug mode
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 12000)

#### Mock Mode
For testing and demonstration without an API key:
```bash
export MOCK_MODE=true
```

## 🖥️ Usage

### Command Line Interface

```bash
# Generate text
python cli.py generate --prompt "Write a poem about AI"

# Interactive chat
python cli.py chat

# Analyze text
python cli.py analyze "Your text here" --type sentiment

# Process files
python cli.py process-file document.txt --task summarize

# View configuration
python cli.py config-info
```

### Web Applications

#### FastAPI (Recommended for APIs)
```bash
python main.py api --host 0.0.0.0 --port 12000
```
- API Documentation: http://localhost:12000/docs
- Interactive UI: http://localhost:12000/

#### Flask (Web Interface)
```bash
python main.py web --host 0.0.0.0 --port 12001
```
- Web Interface: http://localhost:12001/

### Docker Deployment

```bash
# Build image
docker build -t gemini-ai-assistant .

# Run container
docker run -p 12000:12000 -e GEMINI_API_KEY=your_key gemini-ai-assistant

# Using docker-compose
docker-compose up -d
```

## 🧪 Testing

### Run Comprehensive Tests
```bash
python test_complete_app.py
```

### Run Unit Tests
```bash
pytest tests/
```

### Manual Testing
```bash
# Test CLI in mock mode
MOCK_MODE=true python cli.py generate --prompt "Hello world"

# Test API endpoints
curl -X POST "http://localhost:12000/api/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello world"}'
```

## 📊 API Endpoints

### FastAPI Endpoints
- `GET /` - Main page
- `GET /health` - Health check
- `POST /api/generate` - Text generation
- `POST /api/chat` - Chat interface
- `POST /api/analyze` - Text analysis
- `POST /api/upload` - File processing
- `GET /api/config` - Configuration info
- `GET /docs` - API documentation

### Flask Endpoints
- `GET /` - Web interface
- `POST /api/generate` - Text generation
- `POST /api/chat` - Chat interface
- `POST /api/analyze` - Text analysis
- `POST /api/upload` - File upload

## 🔧 Configuration

### API Parameters
- `temperature`: Creativity level (0.0-1.0)
- `max_tokens`: Maximum response length
- `top_p`: Nucleus sampling parameter
- `top_k`: Top-k sampling parameter

### Supported File Types
- Text files: .txt, .md
- Code files: .py, .js, .html, .css
- Data files: .json, .xml, .csv

## 🛠️ Development

### Project Structure
```
testai/
├── main.py              # Main application entry point
├── cli.py               # Command line interface
├── gemini_client.py     # Gemini API client
├── mock_client.py       # Mock client for testing
├── client_factory.py    # Client factory
├── config.py            # Configuration management
├── utils.py             # Utility functions
├── web_app.py           # Flask web application
├── fastapi_app.py       # FastAPI application
├── templates/           # HTML templates
├── tests/               # Test files
└── requirements.txt     # Dependencies
```

### Adding New Features
1. Update the appropriate client (gemini_client.py or mock_client.py)
2. Add CLI commands in cli.py
3. Add API endpoints in fastapi_app.py or web_app.py
4. Add tests in tests/ directory
5. Update documentation

### Environment Setup for Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Set up pre-commit hooks (optional)
pre-commit install

# Run in development mode
export DEBUG=true
export MOCK_MODE=true
python main.py api --reload
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure GEMINI_API_KEY is set correctly
   - Check API key permissions and quotas
   - Use MOCK_MODE=true for testing

2. **Port Conflicts**
   - Change PORT environment variable
   - Use different ports for FastAPI and Flask

3. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration

4. **File Upload Issues**
   - Check file size limits
   - Verify file type is supported
   - Ensure proper permissions

### Debug Mode
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python main.py api
```

### Logs
- Application logs are written to stdout
- Use LOG_LEVEL to control verbosity
- Check server logs for detailed error information

## 📈 Performance

### Optimization Tips
- Use appropriate temperature settings
- Limit max_tokens for faster responses
- Enable caching for repeated requests
- Use connection pooling for high traffic

### Scaling
- Deploy multiple instances behind a load balancer
- Use Redis for session storage
- Implement request queuing for high loads
- Monitor API usage and quotas

## 🔒 Security

### Best Practices
- Keep API keys secure and rotate regularly
- Use HTTPS in production
- Implement rate limiting
- Validate all user inputs
- Use environment variables for secrets

### Production Deployment
- Use a reverse proxy (nginx)
- Enable SSL/TLS certificates
- Set up monitoring and logging
- Implement backup strategies
- Use container orchestration (Kubernetes)

## 📞 Support

For issues and questions:
1. Check this documentation
2. Review the test files for examples
3. Check the API documentation at /docs
4. Review logs for error details

## 🎯 Next Steps

Potential enhancements:
- Add user authentication
- Implement conversation persistence
- Add more file format support
- Create mobile-friendly interface
- Add batch processing capabilities
- Implement caching layer
- Add monitoring and analytics