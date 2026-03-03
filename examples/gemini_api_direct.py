"""
Direct Gemini API Integration

Uses the Gemini API directly instead of CLI (which hangs in subprocess).
Reads auth from Gemini CLI config if available.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional

def get_gemini_api_key() -> Optional[str]:
    """Try to get API key from Gemini CLI config or environment."""
    
    # Try environment first
    if "GEMINI_API_KEY" in os.environ:
        return os.environ["GEMINI_API_KEY"]
    
    # Try Gemini CLI config
    config_paths = [
        Path.home() / ".config" / "gemini-cli" / "config.json",
        Path.home() / ".gemini-cli" / "config.json",
        Path(os.getenv("APPDATA", "")) / "gemini-cli" / "config.json",
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    if "apiKey" in config:
                        return config["apiKey"]
            except:
                pass
    
    return None

def call_gemini_api(
    prompt: str,
    model: str = "gemini-pro",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Call Gemini API directly.
    
    Args:
        prompt: The prompt text
        model: Model name (gemini-pro, gemini-1.5-pro, etc.)
        temperature: 0-1, creativity level
        max_tokens: Max output tokens
        api_key: Optional API key (auto-detected if None)
    
    Returns:
        {"success": bool, "output": str, "error": str}
    """
    
    # Get API key
    if api_key is None:
        api_key = get_gemini_api_key()
    
    if not api_key:
        return {
            "success": False,
            "output": None,
            "error": "No API key found. Set GEMINI_API_KEY or configure gemini CLI."
        }
    
    # Build API URL for Gemini API
    # Format: POST https://generativelanguage.googleapis.com/v1beta/models/MODEL:generateContent
    base_url = "https://generativelanguage.googleapis.com/v1beta"
    url = f"{base_url}/models/{model}:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    # Build request
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract text from response
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                text = candidate["content"]["parts"][0].get("text", "")
                return {
                    "success": True,
                    "output": text,
                    "error": None
                }
        
        return {
            "success": False,
            "output": None,
            "error": f"Unexpected response format: {data}"
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "output": None,
            "error": f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "output": None,
            "error": f"Error: {str(e)}"
        }

# Test if run directly
if __name__ == "__main__":
    print("=" * 80)
    print("Testing Direct Gemini API")
    print("=" * 80)
    
    # Check for API key
    api_key = get_gemini_api_key()
    if api_key:
        print(f"\n[OK] Found API key: {api_key[:8]}...")
    else:
        print("\n[WARN] No API key found")
        print("  Set with: gemini config set apiKey YOUR_KEY")
        print("  Or: $env:GEMINI_API_KEY='YOUR_KEY'")
    
    print("\nTesting API call...")
    print("Prompt: 'What is 2+2? Reply with just the number.'")
    
    result = call_gemini_api("What is 2+2? Reply with just the number.")
    
    if result["success"]:
        print(f"\n[OK] Gemini API works!")
        print(f"Response: {result['output']}")
    else:
        print(f"\n[ERROR] {result['error']}")
    
    print("\n" + "=" * 80)
