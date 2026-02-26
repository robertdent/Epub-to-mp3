"""Ollama text cleanup utilities."""

import json
import subprocess
from pathlib import Path
from typing import Optional

import requests


CLEANUP_PROMPT = """Clean this text for text-to-speech conversion. Follow these rules strictly:

1. Remove page numbers, headers, and footers
2. Keep all dialogue and quotation marks exactly as they are
3. Preserve ALL meaning - do not summarize or rewrite
4. Fix obvious OCR errors if present
5. Keep paragraph structure
6. Return ONLY the cleaned text, no explanations

Text to clean:
{text}"""


def clean_text_with_ollama(
    text: str,
    model: str = "llama2",
    verbose: bool = False
) -> Optional[str]:
    """
    Clean text using Ollama for better TTS output.
    
    Args:
        text: Text to clean
        model: Ollama model name
        verbose: Print verbose output
        
    Returns:
        Cleaned text, or None if cleanup failed
    """
    # Try HTTP API first
    cleaned = _clean_via_http(text, model, verbose)
    if cleaned:
        return cleaned
    
    # Fallback to subprocess
    if verbose:
        print("HTTP API failed, trying subprocess...")
    
    return _clean_via_subprocess(text, model, verbose)


def _clean_via_http(
    text: str,
    model: str,
    verbose: bool = False
) -> Optional[str]:
    """
    Clean text using Ollama's HTTP API.
    
    Args:
        text: Text to clean
        model: Ollama model name
        verbose: Print verbose output
        
    Returns:
        Cleaned text, or None if failed
    """
    try:
        url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": model,
            "prompt": CLEANUP_PROMPT.format(text=text[:4000]),  # Limit length
            "stream": False,
        }
        
        if verbose:
            print(f"Calling Ollama HTTP API with model {model}...")
        
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            cleaned = result.get("response", "").strip()
            
            if cleaned:
                if verbose:
                    print(f"✓ Text cleaned via HTTP ({len(cleaned)} chars)")
                return cleaned
        
    except requests.RequestException as e:
        if verbose:
            print(f"HTTP request failed: {e}")
    except Exception as e:
        if verbose:
            print(f"Error in HTTP cleanup: {e}")
    
    return None


def _clean_via_subprocess(
    text: str,
    model: str,
    verbose: bool = False
) -> Optional[str]:
    """
    Clean text using Ollama subprocess.
    
    Args:
        text: Text to clean
        model: Ollama model name
        verbose: Print verbose output
        
    Returns:
        Cleaned text, or None if failed
    """
    try:
        prompt = CLEANUP_PROMPT.format(text=text[:4000])  # Limit length
        
        cmd = ["ollama", "run", model]
        
        if verbose:
            print(f"Running Ollama subprocess with model {model}...")
        
        result = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=120
        )
        
        if result.returncode == 0 and result.stdout.strip():
            cleaned = result.stdout.strip()
            if verbose:
                print(f"✓ Text cleaned via subprocess ({len(cleaned)} chars)")
            return cleaned
        
    except subprocess.TimeoutExpired:
        if verbose:
            print("Ollama subprocess timed out")
    except Exception as e:
        if verbose:
            print(f"Error in subprocess cleanup: {e}")
    
    return None


def check_ollama_available(verbose: bool = False) -> bool:
    """
    Check if Ollama is available via HTTP API or command line.
    
    Returns:
        True if Ollama is available, False otherwise
    """
    # Try HTTP API
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            if verbose:
                print("✓ Ollama HTTP API available")
            return True
    except requests.RequestException:
        pass
    
    # Try command line
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            if verbose:
                print("✓ Ollama CLI available")
            return True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return False
