"""Web application for Gemini AI Assistant using Flask."""

import os
import json
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

from client_factory import get_client
from utils import read_file, write_file, get_file_info, setup_logging
from config import config

# Setup logging
logger = setup_logging(config.LOG_LEVEL)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS


def get_session_client():
    """Get or create a Gemini client for the session."""
    if 'client_id' not in session:
        session['client_id'] = str(uuid.uuid4())
        session['chat_history'] = []
    
    return get_client()


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html', config=config)


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API endpoint for text generation."""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Get generation parameters
        temperature = data.get('temperature', config.TEMPERATURE)
        max_tokens = data.get('max_tokens', config.MAX_TOKENS)
        
        client = get_session_client()
        response = client.generate_text(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return jsonify({
            'success': True,
            'response': response.text,
            'metadata': {
                'finish_reason': response.finish_reason,
                'usage': response.usage_metadata
            }
        })
    
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat functionality."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        system_prompt = data.get('system_prompt', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        client = get_session_client()
        
        # Load chat history from session
        if 'chat_history' in session:
            for msg in session['chat_history']:
                client.chat_history.append(
                    type('Message', (), {
                        'role': msg['role'],
                        'content': msg['content'],
                        'timestamp': msg.get('timestamp')
                    })()
                )
        
        response = client.chat(message, system_prompt if system_prompt else None)
        
        # Update session chat history
        session['chat_history'] = [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': datetime.now().isoformat()
            }
            for msg in client.chat_history
        ]
        
        return jsonify({
            'success': True,
            'response': response,
            'history_length': len(client.chat_history)
        })
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/clear', methods=['POST'])
def api_clear_chat():
    """Clear chat history."""
    session['chat_history'] = []
    return jsonify({'success': True, 'message': 'Chat history cleared'})


@app.route('/api/chat/history', methods=['GET'])
def api_chat_history():
    """Get chat history."""
    history = session.get('chat_history', [])
    return jsonify({'success': True, 'history': history})


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for text analysis."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        analysis_type = data.get('type', 'general')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        client = get_session_client()
        result = client.analyze_text(text, analysis_type)
        
        return jsonify({
            'success': True,
            'result': result,
            'analysis_type': analysis_type
        })
    
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint for file upload and processing."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        task = request.form.get('task', 'summarize')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process file
        content = read_file(file_path)
        client = get_session_client()
        result = client.process_file_content(content, task)
        
        # Get file info
        file_info = get_file_info(file_path)
        
        return jsonify({
            'success': True,
            'result': result,
            'task': task,
            'file_info': file_info
        })
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def api_config():
    """Get configuration information."""
    return jsonify({
        'app_name': config.APP_NAME,
        'version': config.APP_VERSION,
        'model': config.MODEL,
        'max_tokens': config.MAX_TOKENS,
        'temperature': config.TEMPERATURE,
        'api_key_set': bool(config.API_KEY and config.API_KEY != "your_api_key_here")
    })


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


# Create templates directory and files
def create_templates():
    """Create HTML templates."""
    
    templates_dir = 'templates'
    os.makedirs(templates_dir, exist_ok=True)
    
    # Base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ config.APP_NAME }}{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism.min.css" rel="stylesheet">
    <style>
        .chat-container { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; }
        .message { margin-bottom: 15px; }
        .user-message { text-align: right; }
        .assistant-message { text-align: left; }
        .message-content { display: inline-block; padding: 10px; border-radius: 10px; max-width: 80%; }
        .user-message .message-content { background-color: #007bff; color: white; }
        .assistant-message .message-content { background-color: #f8f9fa; border: 1px solid #ddd; }
        .loading { text-align: center; padding: 20px; }
        .file-info { background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">{{ config.APP_NAME }}</a>
            <span class="navbar-text">v{{ config.APP_VERSION }}</span>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/autoloader/prism-autoloader.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    # Main page template
    index_template = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1>Welcome to {{ config.APP_NAME }}</h1>
        <p class="lead">AI-powered text generation and analysis using Google's Gemini API</p>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>Text Generation</h5>
            </div>
            <div class="card-body">
                <form id="generateForm">
                    <div class="mb-3">
                        <label for="prompt" class="form-label">Prompt</label>
                        <textarea class="form-control" id="prompt" rows="4" placeholder="Enter your prompt here..."></textarea>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <label for="temperature" class="form-label">Temperature</label>
                            <input type="range" class="form-range" id="temperature" min="0" max="1" step="0.1" value="{{ config.TEMPERATURE }}">
                            <small class="text-muted">Current: <span id="tempValue">{{ config.TEMPERATURE }}</span></small>
                        </div>
                        <div class="col-md-6">
                            <label for="maxTokens" class="form-label">Max Tokens</label>
                            <input type="number" class="form-control" id="maxTokens" value="{{ config.MAX_TOKENS }}" min="1" max="8192">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary mt-3">Generate</button>
                </form>
                <div id="generateResult" class="mt-3"></div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>Chat Interface</h5>
            </div>
            <div class="card-body">
                <div id="chatContainer" class="chat-container mb-3"></div>
                <form id="chatForm">
                    <div class="input-group">
                        <input type="text" class="form-control" id="chatMessage" placeholder="Type your message...">
                        <button type="submit" class="btn btn-success">Send</button>
                    </div>
                </form>
                <div class="mt-2">
                    <button id="clearChat" class="btn btn-sm btn-outline-warning">Clear Chat</button>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>Text Analysis</h5>
            </div>
            <div class="card-body">
                <form id="analyzeForm">
                    <div class="mb-3">
                        <label for="analyzeText" class="form-label">Text to Analyze</label>
                        <textarea class="form-control" id="analyzeText" rows="3" placeholder="Enter text to analyze..."></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="analysisType" class="form-label">Analysis Type</label>
                        <select class="form-select" id="analysisType">
                            <option value="general">General Analysis</option>
                            <option value="sentiment">Sentiment Analysis</option>
                            <option value="summary">Summary</option>
                            <option value="keywords">Keywords</option>
                            <option value="translation">Translation</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-info">Analyze</button>
                </form>
                <div id="analyzeResult" class="mt-3"></div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>File Processing</h5>
            </div>
            <div class="card-body">
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="mb-3">
                        <label for="fileInput" class="form-label">Choose File</label>
                        <input type="file" class="form-control" id="fileInput" accept=".txt,.md,.py,.js,.html,.css,.json,.xml,.csv">
                        <small class="text-muted">Supported: .txt, .md, .py, .js, .html, .css, .json, .xml, .csv</small>
                    </div>
                    <div class="mb-3">
                        <label for="fileTask" class="form-label">Task</label>
                        <select class="form-select" id="fileTask">
                            <option value="summarize">Summarize</option>
                            <option value="analyze">Analyze</option>
                            <option value="extract_info">Extract Information</option>
                            <option value="questions">Generate Questions</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-warning">Process File</button>
                </form>
                <div id="uploadResult" class="mt-3"></div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// Utility functions
function showLoading(elementId) {
    document.getElementById(elementId).innerHTML = '<div class="loading"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
}

function showError(elementId, message) {
    document.getElementById(elementId).innerHTML = `<div class="alert alert-danger">${message}</div>`;
}

function showSuccess(elementId, content) {
    document.getElementById(elementId).innerHTML = `<div class="alert alert-success">${content}</div>`;
}

function renderMarkdown(text) {
    return marked.parse(text);
}

// Temperature slider
document.getElementById('temperature').addEventListener('input', function() {
    document.getElementById('tempValue').textContent = this.value;
});

// Text Generation
document.getElementById('generateForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const prompt = document.getElementById('prompt').value.trim();
    if (!prompt) {
        showError('generateResult', 'Please enter a prompt');
        return;
    }
    
    showLoading('generateResult');
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                prompt: prompt,
                temperature: parseFloat(document.getElementById('temperature').value),
                max_tokens: parseInt(document.getElementById('maxTokens').value)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const html = `
                <div class="card">
                    <div class="card-header">Generated Response</div>
                    <div class="card-body">${renderMarkdown(data.response)}</div>
                </div>
            `;
            document.getElementById('generateResult').innerHTML = html;
        } else {
            showError('generateResult', data.error);
        }
    } catch (error) {
        showError('generateResult', 'Network error: ' + error.message);
    }
});

// Chat functionality
let chatHistory = [];

function addMessageToChat(role, content) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = renderMarkdown(content);
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

document.getElementById('chatForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const messageInput = document.getElementById('chatMessage');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    addMessageToChat('user', message);
    messageInput.value = '';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: message})
        });
        
        const data = await response.json();
        
        if (data.success) {
            addMessageToChat('assistant', data.response);
        } else {
            addMessageToChat('assistant', 'Error: ' + data.error);
        }
    } catch (error) {
        addMessageToChat('assistant', 'Network error: ' + error.message);
    }
});

// Clear chat
document.getElementById('clearChat').addEventListener('click', async function() {
    try {
        await fetch('/api/chat/clear', {method: 'POST'});
        document.getElementById('chatContainer').innerHTML = '';
    } catch (error) {
        console.error('Error clearing chat:', error);
    }
});

// Text Analysis
document.getElementById('analyzeForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const text = document.getElementById('analyzeText').value.trim();
    const type = document.getElementById('analysisType').value;
    
    if (!text) {
        showError('analyzeResult', 'Please enter text to analyze');
        return;
    }
    
    showLoading('analyzeResult');
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: text, type: type})
        });
        
        const data = await response.json();
        
        if (data.success) {
            const html = `
                <div class="card">
                    <div class="card-header">${data.analysis_type.charAt(0).toUpperCase() + data.analysis_type.slice(1)} Analysis</div>
                    <div class="card-body">${renderMarkdown(data.result)}</div>
                </div>
            `;
            document.getElementById('analyzeResult').innerHTML = html;
        } else {
            showError('analyzeResult', data.error);
        }
    } catch (error) {
        showError('analyzeResult', 'Network error: ' + error.message);
    }
});

// File Upload
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const task = document.getElementById('fileTask').value;
    
    if (!fileInput.files[0]) {
        showError('uploadResult', 'Please select a file');
        return;
    }
    
    showLoading('uploadResult');
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('task', task);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            const html = `
                <div class="card">
                    <div class="card-header">${task.charAt(0).toUpperCase() + task.slice(1)} Results</div>
                    <div class="card-body">
                        <div class="file-info">
                            <strong>File:</strong> ${data.file_info.name}<br>
                            <strong>Size:</strong> ${data.file_info.size} bytes<br>
                            <strong>Type:</strong> ${data.file_info.mime_type || 'Unknown'}
                        </div>
                        ${renderMarkdown(data.result)}
                    </div>
                </div>
            `;
            document.getElementById('uploadResult').innerHTML = html;
        } else {
            showError('uploadResult', data.error);
        }
    } catch (error) {
        showError('uploadResult', 'Network error: ' + error.message);
    }
});
</script>
{% endblock %}'''
    
    # Write templates
    with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
        f.write(base_template)
    
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(index_template)


if __name__ == '__main__':
    # Create templates if they don't exist
    create_templates()
    
    # Run the application
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )