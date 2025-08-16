"""Test script to debug Gemini API response structure."""

import requests
import json
from config import config

def test_api_call():
    """Test a simple API call to understand the response structure."""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.MODEL}:generateContent?key={config.API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "Hello, write a short greeting."}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.8,
            "topK": 40,
            "maxOutputTokens": 100,
        }
    }
    
    headers = {
        "Content-Type": "application/json",
    }
    
    try:
        print("Making API request...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response Data: {json.dumps(response_data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    test_api_call()