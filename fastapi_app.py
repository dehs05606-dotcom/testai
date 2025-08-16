"""FastAPI application for Gemini AI Assistant."""

import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn

from client_factory import get_client
from gemini_client import Message
from utils import read_file, write_file, get_file_info, setup_logging
from config import config

# Setup logging
logger = setup_logging(config.LOG_LEVEL)

# Initialize FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    description="AI-powered text generation and analysis using Google's Gemini API",
    version=config.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv'}

# In-memory session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}


# Pydantic models
class GenerateRequest(BaseModel):
    prompt: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None


class ChatRequest(BaseModel):
    message: str
    system_prompt: Optional[str] = None
    session_id: Optional[str] = None


class AnalyzeRequest(BaseModel):
    text: str
    type: str = "general"


class GenerateResponse(BaseModel):
    success: bool
    response: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    session_id: str
    history_length: int
    error: Optional[str] = None


class AnalyzeResponse(BaseModel):
    success: bool
    result: str
    analysis_type: str
    error: Optional[str] = None


class FileProcessResponse(BaseModel):
    success: bool
    result: str
    task: str
    file_info: Dict[str, Any]
    error: Optional[str] = None


class ConfigResponse(BaseModel):
    app_name: str
    version: str
    model: str
    max_tokens: int
    temperature: float
    api_key_set: bool


# Dependency functions
def get_session_id() -> str:
    """Generate or get session ID."""
    return str(uuid.uuid4())


def get_gemini_client():
    """Get Gemini client instance."""
    return get_client()


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS


# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gemini AI Assistant</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .api-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .endpoint { background-color: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; }
            .method-get { border-left: 4px solid #28a745; }
            .method-post { border-left: 4px solid #007bff; }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <h1>Gemini AI Assistant API</h1>
            <p class="lead">FastAPI-based AI assistant using Google's Gemini API</p>
            
            <div class="api-section">
                <h3>Available Endpoints</h3>
                
                <div class="endpoint method-post">
                    <h5>POST /api/generate</h5>
                    <p>Generate text from a prompt</p>
                    <small>Body: {"prompt": "string", "temperature": 0.7, "max_tokens": 1000}</small>
                </div>
                
                <div class="endpoint method-post">
                    <h5>POST /api/chat</h5>
                    <p>Chat with the AI assistant</p>
                    <small>Body: {"message": "string", "session_id": "optional"}</small>
                </div>
                
                <div class="endpoint method-post">
                    <h5>POST /api/analyze</h5>
                    <p>Analyze text with specified type</p>
                    <small>Body: {"text": "string", "type": "general|sentiment|summary|keywords|translation"}</small>
                </div>
                
                <div class="endpoint method-post">
                    <h5>POST /api/upload</h5>
                    <p>Upload and process a file</p>
                    <small>Form data: file + task parameter</small>
                </div>
                
                <div class="endpoint method-get">
                    <h5>GET /api/config</h5>
                    <p>Get application configuration</p>
                </div>
                
                <div class="endpoint method-get">
                    <h5>GET /docs</h5>
                    <p>Interactive API documentation (Swagger UI)</p>
                </div>
                
                <div class="endpoint method-get">
                    <h5>GET /redoc</h5>
                    <p>Alternative API documentation (ReDoc)</p>
                </div>
            </div>
            
            <div class="api-section">
                <h3>Quick Links</h3>
                <a href="/docs" class="btn btn-primary me-2">API Documentation</a>
                <a href="/redoc" class="btn btn-secondary">ReDoc</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest, client = Depends(get_gemini_client)):
    """Generate text using Gemini API."""
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        response = client.generate_text(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            top_k=request.top_k
        )
        
        return GenerateResponse(
            success=True,
            response=response.text,
            metadata={
                "finish_reason": response.finish_reason,
                "usage": response.usage_metadata,
                "safety_ratings": response.safety_ratings
            }
        )
    
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return GenerateResponse(success=False, response="", error=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, client = Depends(get_gemini_client)):
    """Chat with the AI assistant."""
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get or create session
        session_id = request.session_id or get_session_id()
        
        # Load chat history from session
        if session_id in sessions:
            session_data = sessions[session_id]
            client.chat_history = [
                Message(role=msg["role"], content=msg["content"])
                for msg in session_data.get("chat_history", [])
            ]
        
        response = client.chat(request.message, request.system_prompt)
        
        # Save chat history to session
        sessions[session_id] = {
            "chat_history": [
                {"role": msg.role, "content": msg.content, "timestamp": datetime.now().isoformat()}
                for msg in client.chat_history
            ]
        }
        
        return ChatResponse(
            success=True,
            response=response,
            session_id=session_id,
            history_length=len(client.chat_history)
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return ChatResponse(
            success=False,
            response="",
            session_id=request.session_id or get_session_id(),
            history_length=0,
            error=str(e)
        )


@app.post("/api/chat/clear")
async def clear_chat(session_id: str):
    """Clear chat history for a session."""
    if session_id in sessions:
        sessions[session_id]["chat_history"] = []
    return {"success": True, "message": "Chat history cleared"}


@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    if session_id in sessions:
        return {"success": True, "history": sessions[session_id].get("chat_history", [])}
    return {"success": True, "history": []}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest, client = Depends(get_gemini_client)):
    """Analyze text with specified analysis type."""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        result = client.analyze_text(request.text, request.type)
        
        return AnalyzeResponse(
            success=True,
            result=result,
            analysis_type=request.type
        )
    
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return AnalyzeResponse(
            success=False,
            result="",
            analysis_type=request.type,
            error=str(e)
        )


@app.post("/api/upload", response_model=FileProcessResponse)
async def upload_file(
    file: UploadFile = File(...),
    task: str = "summarize",
    client = Depends(get_gemini_client)
):
    """Upload and process a file."""
    try:
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process file
        file_content = read_file(file_path)
        result = client.process_file_content(file_content, task)
        
        # Get file info
        file_info = get_file_info(file_path)
        
        return FileProcessResponse(
            success=True,
            result=result,
            task=task,
            file_info=file_info
        )
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return FileProcessResponse(
            success=False,
            result="",
            task=task,
            file_info={},
            error=str(e)
        )


@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    """Get application configuration."""
    return ConfigResponse(
        app_name=config.APP_NAME,
        version=config.APP_VERSION,
        model=config.MODEL,
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
        api_key_set=bool(config.API_KEY and config.API_KEY != "your_api_key_here")
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": config.APP_VERSION
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return {"error": "Endpoint not found", "status_code": 404}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {exc}")
    return {"error": "Internal server error", "status_code": 500}


if __name__ == "__main__":
    uvicorn.run(
        "fastapi_app:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )