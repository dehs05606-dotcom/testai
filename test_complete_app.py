#!/usr/bin/env python3
"""
Comprehensive test script for the Gemini AI Assistant application.
Tests all major functionality including CLI, web API, and FastAPI endpoints.
"""

import os
import sys
import time
import requests
import subprocess
import tempfile
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client_factory import get_client
from config import config

def test_client_functionality():
    """Test the Gemini client functionality."""
    print("🧪 Testing Client Functionality...")
    
    try:
        client = get_client()
        
        # Test text generation
        print("  ✓ Testing text generation...")
        response = client.generate_text("Write a haiku about testing")
        assert response.text, "Text generation failed"
        print(f"    Generated: {response.text[:50]}...")
        
        # Test chat functionality
        print("  ✓ Testing chat functionality...")
        chat_response = client.chat("Hello, how are you?")
        assert chat_response, "Chat functionality failed"
        print(f"    Chat response: {chat_response[:50]}...")
        
        # Test text analysis
        print("  ✓ Testing text analysis...")
        analysis = client.analyze_text("This is a test text for analysis", "sentiment")
        assert analysis, "Text analysis failed"
        print(f"    Analysis: {analysis[:50]}...")
        
        print("✅ Client functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Client functionality test failed: {e}")
        return False

def test_cli_functionality():
    """Test CLI functionality."""
    print("🧪 Testing CLI Functionality...")
    
    try:
        # Test generate command
        print("  ✓ Testing CLI generate command...")
        result = subprocess.run([
            sys.executable, "cli.py", "generate", 
            "--prompt", "Write a short poem about Python",
            "--max-tokens", "100"
        ], capture_output=True, text=True, env={**os.environ, "MOCK_MODE": "true"})
        
        assert result.returncode == 0, f"CLI generate failed: {result.stderr}"
        assert "Generated Response" in result.stdout, "CLI generate output missing"
        print("    CLI generate command works!")
        
        # Test analyze command
        print("  ✓ Testing CLI analyze command...")
        result = subprocess.run([
            sys.executable, "cli.py", "analyze",
            "This is a test text",
            "--type", "sentiment"
        ], capture_output=True, text=True, env={**os.environ, "MOCK_MODE": "true"})
        
        assert result.returncode == 0, f"CLI analyze failed: {result.stderr}"
        print("    CLI analyze command works!")
        
        print("✅ CLI functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ CLI functionality test failed: {e}")
        return False

def test_fastapi_endpoints():
    """Test FastAPI endpoints."""
    print("🧪 Testing FastAPI Endpoints...")
    
    base_url = "http://localhost:12000"
    
    try:
        # Test health endpoint
        print("  ✓ Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data["status"] == "healthy", "Health status not healthy"
        print("    Health endpoint works!")
        
        # Test generate endpoint
        print("  ✓ Testing generate endpoint...")
        response = requests.post(f"{base_url}/api/generate", json={
            "prompt": "Write a haiku about testing",
            "temperature": 0.7,
            "max_tokens": 100
        }, timeout=10)
        assert response.status_code == 200, f"Generate failed: {response.status_code}"
        data = response.json()
        assert data["success"], f"Generate not successful: {data.get('error')}"
        assert data["response"], "No response text"
        print(f"    Generated: {data['response'][:50]}...")
        
        # Test chat endpoint
        print("  ✓ Testing chat endpoint...")
        response = requests.post(f"{base_url}/api/chat", json={
            "message": "Hello, how are you?"
        }, timeout=10)
        assert response.status_code == 200, f"Chat failed: {response.status_code}"
        data = response.json()
        assert data["success"], f"Chat not successful: {data.get('error')}"
        assert data["response"], "No chat response"
        print(f"    Chat response: {data['response'][:50]}...")
        
        # Test analyze endpoint
        print("  ✓ Testing analyze endpoint...")
        response = requests.post(f"{base_url}/api/analyze", json={
            "text": "This is a test text for analysis",
            "type": "sentiment"
        }, timeout=10)
        assert response.status_code == 200, f"Analyze failed: {response.status_code}"
        data = response.json()
        assert data["success"], f"Analyze not successful: {data.get('error')}"
        assert data["result"], "No analysis result"
        print(f"    Analysis: {data['result'][:50]}...")
        
        # Test config endpoint
        print("  ✓ Testing config endpoint...")
        response = requests.get(f"{base_url}/api/config", timeout=5)
        assert response.status_code == 200, f"Config failed: {response.status_code}"
        data = response.json()
        assert "app_name" in data, "Config missing app_name"
        print("    Config endpoint works!")
        
        print("✅ FastAPI endpoints tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ FastAPI endpoints test failed: {e}")
        return False

def test_flask_endpoints():
    """Test Flask web application endpoints."""
    print("🧪 Testing Flask Web Endpoints...")
    
    base_url = "http://localhost:12001"
    
    try:
        # Test main page
        print("  ✓ Testing main page...")
        response = requests.get(base_url, timeout=5)
        assert response.status_code == 200, f"Main page failed: {response.status_code}"
        assert "Gemini AI Assistant" in response.text, "Main page content missing"
        print("    Main page works!")
        
        # Test generate endpoint
        print("  ✓ Testing Flask generate endpoint...")
        response = requests.post(f"{base_url}/api/generate", json={
            "prompt": "Write a haiku about testing",
            "temperature": 0.7,
            "max_tokens": 100
        }, timeout=10)
        assert response.status_code == 200, f"Generate failed: {response.status_code}"
        data = response.json()
        assert data["success"], f"Generate not successful: {data.get('error')}"
        print(f"    Generated: {data['response'][:50]}...")
        
        # Test chat endpoint
        print("  ✓ Testing Flask chat endpoint...")
        response = requests.post(f"{base_url}/api/chat", json={
            "message": "Hello, how are you?"
        }, timeout=10)
        assert response.status_code == 200, f"Chat failed: {response.status_code}"
        data = response.json()
        assert data["success"], f"Chat not successful: {data.get('error')}"
        print(f"    Chat response: {data['response'][:50]}...")
        
        print("✅ Flask web endpoints tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Flask web endpoints test failed: {e}")
        return False

def test_file_operations():
    """Test file processing functionality."""
    print("🧪 Testing File Operations...")
    
    try:
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test file for processing.\nIt contains multiple lines.\nAnd some sample content for analysis.")
            test_file_path = f.name
        
        try:
            # Test CLI file processing
            print("  ✓ Testing CLI file processing...")
            result = subprocess.run([
                sys.executable, "cli.py", "process-file",
                test_file_path,
                "--task", "summarize"
            ], capture_output=True, text=True, env={**os.environ, "MOCK_MODE": "true"})
            
            assert result.returncode == 0, f"CLI file processing failed: {result.stderr}"
            print("    CLI file processing works!")
            
            # Test FastAPI file upload
            print("  ✓ Testing FastAPI file upload...")
            with open(test_file_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                data = {'task': 'summarize'}
                response = requests.post("http://localhost:12000/api/upload", 
                                       files=files, data=data, timeout=10)
            
            assert response.status_code == 200, f"File upload failed: {response.status_code}"
            result_data = response.json()
            assert result_data["success"], f"File upload not successful: {result_data.get('error')}"
            print(f"    File processing result: {result_data['result'][:50]}...")
            
        finally:
            # Clean up test file
            os.unlink(test_file_path)
        
        print("✅ File operations tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Comprehensive Application Tests")
    print("=" * 50)
    
    # Set mock mode for testing
    os.environ["MOCK_MODE"] = "true"
    
    tests = [
        ("Client Functionality", test_client_functionality),
        ("CLI Functionality", test_cli_functionality),
        ("FastAPI Endpoints", test_fastapi_endpoints),
        ("Flask Web Endpoints", test_flask_endpoints),
        ("File Operations", test_file_operations),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Tests...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
        if success:
            passed += 1
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The application is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())